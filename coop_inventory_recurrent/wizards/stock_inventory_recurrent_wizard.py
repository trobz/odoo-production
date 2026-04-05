# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from odoo import Command, fields, models
from odoo.exceptions import UserError


class StockInventoryRecurrentWizard(models.TransientModel):
    _name = "stock.inventory.recurrent.wizard"
    _description = "Recurrent Inventory"

    category_group_ids = fields.Many2many(
        "stock.inventory.category.group",
        "stock_inventory_recurrent_category_group_rel",
        string="Category Groups",
    )

    def action_execute(self):
        self.ensure_one()
        all_category_ids = self.category_group_ids.mapped("line_ids.category_id").ids
        existing_in_progress = self.env["stock.inventory"].search(
            [("category_id", "in", all_category_ids), ("state", "=", "in_progress")]
        )
        if existing_in_progress:
            names = ", ".join(existing_in_progress.mapped("name"))
            raise UserError(
                self.env._(
                    "The following inventories are already in progress: %(names)s. "
                    "Please validate or cancel them before generating new ones.",
                    names=names,
                )
            )
        inventories = self.env["stock.inventory"]
        new_inventories = self.env["stock.inventory"]
        for categ_group in self.category_group_ids:
            for line in categ_group.line_ids:
                inventory = self.env["stock.inventory"].create(
                    {
                        "name": line.category_id.name,
                        "product_selection": "category",
                        "category_id": line.category_id.id,
                        "category_group_line_id": line.id,
                        "location_ids": [Command.set(categ_group.location_id.ids)],
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
