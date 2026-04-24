# Copyright (C) Nguyen Minh Chien (chien@trobz.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ShiftTicket(models.Model):
    _inherit = "shift.ticket"

    shift_max_available_seats = fields.Selection(
        selection=[
            ("manual", "Add Maximum available ABCD/FTOP seats manually"),
            (
                "auto",
                "Calculate Maximum available ABCD/FTOP seats automatically based on Maximum Attendees Number",
            ),
        ],
        string="Maximum available ABCD/FTOP seats",
        related="shift_id.shift_max_available_seats",
    )
