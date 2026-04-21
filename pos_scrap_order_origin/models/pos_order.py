# Copyright (C) Nguyen Minh Chien (chien@trobz.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, models


class PosOrder(models.Model):
    _inherit = "pos.order"

    @api.model
    def create_scrap_from_ui(self, order, default_vals={}):
        if not order.get("scrap_origin_id"):
            msg = {
                "title": _("Error!"),
                "body": _("You have to add the default scrap origin first."),
            }
            return {"scrap_ids": [], "msg": msg}
        default_vals.update({"scrap_origin_id": order.get("scrap_origin_id")})
        return super().create_scrap_from_ui(order, default_vals)
