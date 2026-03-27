##############################################################################
#
#    Purchase - Package Quantity Module for Odoo
#    Copyright (C) 2016-Today Akretion (https://www.akretion.com)
#    @author Julien WESTE
#    @author Sylvain LE GAL (https://twitter.com/legalsylvain)
#    Copyright (C) 2020-Today: Druidoo (<https://www.druidoo.io>)
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

from odoo import fields, models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    def _apply_inventory(self):
        # Build date map before super() clears inventory fields
        context_datetime = self.env.context.get("inventory_datetime")
        quant_dates = {}
        for quant in self:
            if context_datetime:
                quant_dates[quant.id] = context_datetime
            elif quant.inventory_date:
                quant_dates[quant.id] = quant.inventory_date

        if not quant_dates:
            return super()._apply_inventory()

        last_move = self.env["stock.move"].search([], order="id desc", limit=1)
        last_move_id = last_move.id if last_move else 0
        res = super()._apply_inventory()

        # Restore dates overwritten by _action_done()
        new_moves = self.env["stock.move"].search(
            [
                ("is_inventory", "=", True),
                ("id", ">", last_move_id),
                ("product_id", "in", [q.product_id.id for q in self]),
            ]
        )
        product_date = {}
        for quant in self:
            if quant.id in quant_dates:
                product_date[quant.product_id.id] = quant_dates[quant.id]
        for move in new_moves:
            move_date = product_date.get(move.product_id.id)
            if move_date:
                move.write({"date": move_date})
                move.move_line_ids.write({"date": move_date})
        return res

    def _get_inventory_move_values(
        self,
        qty,
        location_id,
        location_dest_id,
        package_id=False,
        package_dest_id=False,
    ):
        vals = super()._get_inventory_move_values(
            qty,
            location_id,
            location_dest_id,
            package_id=package_id,
            package_dest_id=package_dest_id,
        )

        inventory_datetime = self.env.context.get("inventory_datetime")
        if inventory_datetime:
            move_date = inventory_datetime
        elif self.inventory_date:
            move_date = self.inventory_date
        else:
            move_date = fields.Datetime.now()

        vals["date"] = move_date
        if vals.get("move_line_ids") and vals["move_line_ids"][0][2] is not None:
            vals["move_line_ids"][0][2]["date"] = move_date
        return vals
