# Copyright (C) Nguyen Minh Chien (chien@trobz.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ShiftRegistration(models.Model):
    _inherit = 'shift.registration'

    is_makeup = fields.Boolean()

    def _is_replacing_makeup_shift(self):
        self.ensure_one()
        return (
            self.exchange_state == "replacing"
            and self.exchange_replaced_reg_id
            and self.exchange_replaced_reg_id.is_makeup
        )
