# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

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
        default="manual",
        inverse="_inverse_shift_max_available_seats",
    )

    def _inverse_shift_max_available_seats(self):
        templates = self.env["shift.template"].search([("company_id", "in", self.ids)])
        templates._update_shift_max_available_seats()
        templates._update_ticket_seats_max()
        shifts = self.env["shift.shift"].search(
            [("company_id", "in", self.ids), ("state", "in", ("draft", "confirm"))]
        )
        shifts._update_shift_max_available_seats()
        shifts._update_ticket_seats_max()
