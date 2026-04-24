# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, models


class ShiftRegistration(models.Model):
    _inherit = "shift.registration"

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records.mapped("shift_ticket_id").mapped("shift_id")._update_ticket_seats_max()
        return records

    def write(self, vals):
        tickets = self.env["shift.ticket"]
        if vals.get("shift_ticket_id") or vals.get("state"):
            tickets = self.mapped("shift_ticket_id")
        res = super().write(vals)
        if tickets:
            if vals.get("shift_ticket_id"):
                tickets |= self.mapped("shift_ticket_id")
            tickets.mapped("shift_id")._update_ticket_seats_max()
        return res

    def unlink(self):
        tickets = self.mapped("shift_ticket_id")
        res = super().unlink()
        tickets.mapped("shift_id")._update_ticket_seats_max()
        return res
