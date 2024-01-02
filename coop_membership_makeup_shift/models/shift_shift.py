# Copyright (C) Nguyen Minh Chien (chien@trobz.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models, _


class ShiftShift(models.Model):
    _inherit = 'shift.shift'

    @api.multi
    def register_makeup_shift(self):
        self.ensure_one()
        tickets = self.shift_ticket_ids.filtered(
            lambda t: t.shift_type == "standard" and t.seats_available > 0
        )
        if not tickets:
            return 0, _("No seat is available for this shift.")
        partner = self.env.user.partner_id
        if not (partner.shift_type == "standard" and \
                partner.cooperative_state == "alert" and \
                    partner.final_standard_point < 0):
            return 0, _("Warning! You can't register to a make-up shift because your actual status is `{}`. "
                        "Make-up shift registration are dedicated to members who were priviously absent."
                        ).format(partner._fields["cooperative_state"].convert_to_export(
                            partner.cooperative_state, partner))

        vals = {
            'state': 'draft',
            'partner_id': partner.id,
            'shift_id': self.id,
            'shift_ticket_id': tickets[0].id,
            'related_extension_id': False
        }
        self.env["shift.registration"].sudo().create(vals)
        return 1, ""
