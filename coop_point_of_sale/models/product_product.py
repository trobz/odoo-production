# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    force_unavailable_in_pos = fields.Boolean()

    def write(self, vals):
        if vals.get("force_unavailable_in_pos"):
            vals["force_unavailable_in_pos"] = False
        return super().write(vals)

    def check_pos_session_running(self):
        pos_sessions = self.env["pos.session"].search(
            [("state", "in", ["opening_control", "opened"])]
        )
        return not pos_sessions

    @api.onchange("available_in_pos")
    def onchange_available_in_pos(self):
        if not self.available_in_pos and not self.sudo().check_pos_session_running():
            self.force_unavailable_in_pos = True
            self.available_in_pos = True

    def confirm_unavailable_in_pos(self):
        self.available_in_pos = self._context.get("confirm")
        self.force_unavailable_in_pos = False
