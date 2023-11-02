# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import models, api


class ShiftTemplateRegistration(models.Model):
    _inherit = 'shift.template.registration'

    @api.model
    def create(self, vals):
        record = super().create(vals)
        record.shift_ticket_id.shift_template_id._update_ticket_seats_max()
        return record

    @api.multi
    def write(self, vals):
        tickets = self.env["shift.template.ticket"]
        if vals.get("shift_ticket_id") or vals.get("state"):
            tickets = self.mapped("shift_ticket_id")
        res = super().write(vals)
        if tickets:
            if vals.get("shift_ticket_id"):
                tickets |= self.mapped("shift_ticket_id")
            tickets.mapped("shift_template_id")._update_ticket_seats_max()
        return res

    @api.multi
    def unlink(self):
        tickets = self.mapped("shift_ticket_id")
        res = super().unlink()
        tickets.mapped("shift_template_id")._update_ticket_seats_max()
        return res
