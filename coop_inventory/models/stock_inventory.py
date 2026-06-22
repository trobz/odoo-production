# Copyright (C) 2024-Today: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import Command, api, models
from odoo.exceptions import ValidationError


class InventoryAdjustmentsGroup(models.Model):
    _inherit = "stock.inventory"

    def action_state_to_in_progress(self):
        self.ensure_one()
        if self.product_selection != "lot" or not self.lot_ids or not self.product_ids:
            return super().action_state_to_in_progress()

        location_op = "child_of" if not self.exclude_sublocation else "in"
        conflicting_quants = self.env["stock.quant"].search(
            [
                ("location_id", location_op, self.location_ids.ids),
                ("to_do", "=", True),
                ("product_id", "in", self.product_ids.ids),
                ("lot_id", "in", self.lot_ids.ids),
            ]
        )
        if conflicting_quants:
            blocking = self.env["stock.inventory"].search(
                [
                    ("stock_quant_ids", "in", conflicting_quants.ids),
                    ("state", "=", "in_progress"),
                ]
            )
            if blocking:
                raise ValidationError(
                    self.env._(
                        "There are active adjustments for the requested products: "
                        "%(names)s. Blocking adjustments: %(blocking_names)s",
                        names=self._get_quant_joined_names(
                            conflicting_quants, "product_id"
                        ),
                        blocking_names=", ".join(blocking.mapped("name")),
                    )
                )

        quants = self._get_quants(self.location_ids)
        self.write(
            {"state": "in_progress", "stock_quant_ids": [Command.set(quants.ids)]}
        )
        quants.write(
            {
                "to_do": True,
                "user_id": self.responsible_id,
                "inventory_date": self.date,
                "current_inventory_id": self.id,
            }
        )


class ReportStockInventoryGroup(models.AbstractModel):
    _name = "report.coop_inventory.report_stock_inventory_group"
    _description = "Inventory Count Sheet Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        inventories = self.env["stock.inventory"].browse(docids)
        quants = inventories.mapped("stock_quant_ids")
        return {
            "doc_ids": quants.ids,
            "doc_model": "stock.quant",
            "docs": quants,
        }
