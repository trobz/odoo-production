##############################################################################
#
#    Purchase - Package Quantity Module for Odoo
#    Copyright (C) 2019-Today: La Louve (<https://cooplalouve.fr>)
#    Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
#    Copyright (C) 2016-Today Akretion (https://www.akretion.com)
#    License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
#    @author Julien WESTE
#    @author Sylvain LE GAL (https://twitter.com/legalsylvain)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):
        self.ensure_one()
        if self.purchase_id:
            todo_moves = self.env["stock.move"]
            created_po_lines = {}
            for move in self.move_ids_without_package:
                if not move.purchase_line_id:
                    key = (move.product_id.id, move.product_uom.id)
                    if key in created_po_lines:
                        po_line = created_po_lines[key]
                        move.purchase_line_id = po_line.id
                        po_line.with_context(skip_move_create=True).write(
                            {"product_qty": po_line.product_qty + move.product_uom_qty}
                        )
                    else:
                        # Reuse existing PO line if its original move was
                        # deleted (no active moves left linked to it)
                        orphan_pol = self.purchase_id.order_line.filtered(
                            lambda pol, p=move.product_id, u=move.product_uom: (
                                pol.product_id == p
                                and pol.product_uom == u
                                and not pol.move_ids.filtered(
                                    lambda m: m.state not in ("cancel",)
                                )
                            )
                        )[:1]
                        if orphan_pol:
                            move.purchase_line_id = orphan_pol.id
                            orphan_pol.with_context(skip_move_create=True).write(
                                {"product_qty": move.product_uom_qty}
                            )
                            created_po_lines[key] = orphan_pol
                        else:
                            po_line = self.prepare_vals_order_line(move)
                            if po_line:
                                created_po_lines[key] = po_line
                    todo_moves |= move
            if todo_moves:
                todo_moves.filtered(lambda m: m.state == "draft")._action_confirm()
        return super().button_validate()

    def prepare_vals_order_line(self, diff_pack_op):
        """
        This method prepares vals to build order line when user add
        more pack operation to stock picking manually.
        To make the stock match with PO to create right invoice
        """
        self.ensure_one()
        if self.purchase_id:
            # Create new po line
            po_line = (
                self.env["purchase.order.line"]
                .with_context(skip_move_create=True)
                .create(
                    {
                        "order_id": self.purchase_id.id,
                        "product_id": diff_pack_op.product_id.id,
                        "product_uom": diff_pack_op.product_uom.id,
                        "date_planned": self.purchase_id.date_planned,
                        "price_unit": 0.00,
                        "product_qty": 0.00,
                        "name": "",
                    }
                )
            )
            # Trigger correct description and prices from supplier
            po_line.onchange_product_id()
            # Update quantities and other values
            # These fields are overwritten by onchange_product_id, so we set
            # them here
            po_line.with_context(skip_move_create=True).write(
                {
                    "product_qty": diff_pack_op.product_uom_qty,
                    "package_qty": diff_pack_op.package_qty,
                    "date_planned": self.purchase_id.date_planned,
                }
            )
            # Link to move
            diff_pack_op.purchase_line_id = po_line.id
            # Pos comment
            self.purchase_id.message_post(
                body=self.env._(
                    "Purchase items: %s with %s qty. were created from "
                    "incoming shipment (%s).",
                    diff_pack_op.product_id.display_name,
                    diff_pack_op.package_qty,
                    self.origin,
                )
            )
            return po_line
