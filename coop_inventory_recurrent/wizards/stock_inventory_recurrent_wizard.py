# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from odoo import Command, fields, models


class StockInventoryRecurrentWizard(models.TransientModel):
    _name = "stock.inventory.recurrent.wizard"
    _description = "Recurrent Inventory"

    category_group_ids = fields.Many2many(
        "stock.inventory.category.group",
        "stock_inventory_recurrent_category_group_rel",
        string="Category Groups",
    )

    def _get_internal_locations(self):
        return self.env["stock.location"].search(
            [("usage", "=", "internal"), ("company_id", "=", self.env.company.id)]
        )

    def action_execute(self):
        self.ensure_one()
        locations = self._get_internal_locations()
        inventories = self.env["stock.inventory"]
        new_inventories = self.env["stock.inventory"]
        for categ_group in self.category_group_ids:
            for line in categ_group.line_ids:
                existing = self.env["stock.inventory"].search(
                    [
                        ("category_id", "=", line.category_id.id),
                        ("state", "=", "in_progress"),
                    ],
                    limit=1,
                )
                if existing:
                    if existing.category_group_line_id != line:
                        existing.category_group_line_id = line
                    inventories |= existing
                else:
                    inventory = self.env["stock.inventory"].create(
                        {
                            "name": line.category_id.name,
                            "product_selection": "category",
                            "category_id": line.category_id.id,
                            "category_group_line_id": line.id,
                            "location_ids": [Command.set(locations.ids)],
                        }
                    )
                    new_inventories |= inventory
                    inventories |= inventory
        for inventory in new_inventories:
            inventory.action_state_to_in_progress()
        tree_view_id = self.env.ref("stock_inventory.view_inventory_group_tree").id
        form_view_id = self.env.ref("stock_inventory.view_inventory_group_form").id
        return {
            "name": self.env._("Physical Inventory"),
            "type": "ir.actions.act_window",
            "res_model": "stock.inventory",
            "view_mode": "list,form",
            "views": [(tree_view_id, "list"), (form_view_id, "form")],
            "domain": [("id", "in", inventories.ids)],
            "target": "current",
        }
