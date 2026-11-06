# Copyright (C) 2024-Today: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.exceptions import ValidationError


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
            "report_date": inventories[0].date or fields.Datetime.now(),
        }


class InventoryAdjustmentsGroup(models.Model):
    _inherit = "stock.inventory"

    def _check_blocking_adjustments_on_requested_locations(self, quants):
        if quants:
            blocking_inventories = self.env["stock.inventory"].search(
                [
                    ("stock_quant_ids", "in", quants.ids),
                    ("state", "=", "in_progress"),
                    ("id", "!=", self.id),
                ]
            )
            if blocking_inventories:
                blocking_names = ", ".join(blocking_inventories.mapped("name"))
                names = ""
                if self.product_selection == "category" and self.category_id:
                    names = self.category_id.display_name
                    message = self.env._(
                        "There's already an Adjustment in Process "
                        "using requested Category: %(names)s. "
                        "Blocking adjustments: %(blocking_names)s",
                        names=names,
                        blocking_names=blocking_names,
                    )
                else:
                    names = self._get_quant_joined_names(quants, "location_id")
                    message = self.env._(
                        "There's already an Adjustment in Process "
                        "using one requested Location: %(names)s. "
                        "Blocking adjustments: %(blocking_names)s",
                        names=names,
                        blocking_names=blocking_names,
                    )
                raise ValidationError(message)

    def action_state_to_in_progress(self):
        self.ensure_one()
        if self.product_selection != "category" or not self.category_id:
            return super().action_state_to_in_progress()
        quants = self._get_quants(self.location_ids)
        self._check_blocking_adjustments_on_requested_locations(quants)
        self.write(
            {
                "state": "in_progress",
                "stock_quant_ids": [(6, 0, quants.ids)],
            }
        )
        quants.write(
            {
                "to_do": True,
                "user_id": self.responsible_id,
                "inventory_date": self.date,
                "current_inventory_id": self.id,
            }
        )
        return True

    def action_print_report_inventory(self):
        self.ensure_one()
        return self.env.ref(
            "coop_inventory.action_report_stock_inventory_group"
        ).report_action(self)
