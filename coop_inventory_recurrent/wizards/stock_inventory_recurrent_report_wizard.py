# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from odoo import Command, api, fields, models


class StockInventoryRecurrentReportWizard(models.TransientModel):
    _name = "stock.inventory.recurrent.report.wizard"
    _description = "Recurrent Inventory Report"

    inventory_ids = fields.Many2many(
        "stock.inventory",
        "stock_inventory_recurrent_report_rel",
        string="Inventory Adjustments",
        default=lambda self: self._get_default_inventories(),
    )

    @api.model
    def _get_default_inventories(self):
        ctx = self._context
        if ctx.get("active_ids") and ctx.get("active_model") == "stock.inventory":
            return [Command.set(ctx["active_ids"])]
        return []

    def action_print(self):
        self.ensure_one()
        action = self.env.ref(
            "coop_inventory_recurrent.action_report_inventory_recurrent"
        )
        inventories = self.inventory_ids.sorted(lambda i: i.name)
        return action.report_action(inventories, config=False)
