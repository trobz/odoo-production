# Copyright (C) Trobz (<https://trobz.com/>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class PosOrder(models.Model):
    _inherit = "pos.order"

    @api.model
    def create_scrap_from_ui(self, order, default_vals=None):
        default_vals = default_vals or {}
        tag_id = default_vals.pop("scrap_reason_tag_id", None)
        if not tag_id:
            return {
                "scrap_ids": [],
                "msg": {
                    "title": self.env._("Error!"),
                    "body": self.env._("You must select a scrap reason tag."),
                },
            }
        default_vals["scrap_reason_tag_ids"] = [(4, tag_id)]
        return super().create_scrap_from_ui(order, default_vals)
