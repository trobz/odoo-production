# Copyright (C) Nguyen Minh Chien (chien@trobz.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class Partner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def check_makeup_shift(self):
        self.ensure_one()
        return (
            self.shift_type == "standard" and
            self.cooperative_state != "up_to_date" and
            self.final_standard_point < 0
        )
