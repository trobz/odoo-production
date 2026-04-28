# Copyright (C) Nguyen Minh Chien (chien@trobz.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ShiftTemplate(models.Model):
    _inherit = "shift.template"

    shift_max_available_seats = fields.Selection(
        selection=[
            ("manual", "Add Maximum available ABCD/FTOP seats manually"),
            (
                "auto",
                "Calculate Maximum available ABCD/FTOP seats"
                " automatically based on Maximum Attendees Number",
            ),
        ],
        string="Maximum available ABCD/FTOP seats",
    )
    seats_max = fields.Integer(inverse="_inverse_seats_max")

    @api.model
    def default_get(self, fs):
        res = super().default_get(fs)
        shift_max_available_seats = (
            self.env.user.company_id.shift_max_available_seats or "manual"
        )
        res.update(
            {
                "shift_max_available_seats": shift_max_available_seats,
                "seats_availability": shift_max_available_seats == "manual"
                and "unlimited"
                or "limited",
            }
        )
        return res

    def _inverse_seats_max(self):
        self._update_ticket_seats_max()

    def _update_shift_max_available_seats(self):
        for record in self:
            record.shift_max_available_seats = (
                record.company_id.shift_max_available_seats
            )
            if record.company_id.shift_max_available_seats == "auto":
                record.seats_availability = "limited"

    def _update_ticket_seats_max(self):
        for record in self:
            if record.shift_max_available_seats == "manual":
                continue
            seats_reserved = sum(record.mapped("shift_ticket_ids.seats_reserved"))
            seats_max = record.seats_max
            for ticket in record.shift_ticket_ids:
                new_seats_max = max(
                    seats_max - seats_reserved + ticket.seats_reserved, 0
                )
                if ticket.seats_max != new_seats_max:
                    ticket.seats_max = new_seats_max
