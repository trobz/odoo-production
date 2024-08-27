# Copyright (C) Nguyen Minh Chien (chien@trobz.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models, fields


class ShiftTemplateTicket(models.Model):
    _inherit = 'shift.template.ticket'

    shift_max_available_seats = fields.Selection(
        selection=[
            ("manual", "Add Maximum available ABCD/FTOP seats manually"),
            ("auto", "Calculate Maximum available ABCD/FTOP seats automatically based on Maximum Attendees Number")
        ],
        string="Maximum available ABCD/FTOP seats",
        related="shift_template_id.shift_max_available_seats"
    )

    def _check_propagated_seats(self):
        self.ensure_one()
        res = super()._check_propagated_seats()
        if res:
            res = self.shift_max_available_seats != "auto"
        return res
