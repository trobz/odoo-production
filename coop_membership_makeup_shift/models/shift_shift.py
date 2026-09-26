# Copyright (C) Nguyen Minh Chien (chien@trobz.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ShiftShift(models.Model):
    _inherit = "shift.shift"

    def register_makeup_shift(self):
        self.ensure_one()
        if self.state == "cancel":
            return 0, self.env._("This shift is not available for registration.")
        if self.date_begin <= fields.Datetime.now():
            return 0, self.env._("You cannot register for a shift that has already started.")
        tickets = self.shift_ticket_ids.filtered(
            lambda t: t.shift_type == "standard" and t.seats_available > 0
        )
        if not tickets:
            return 0, self.env._("No seat is available for this shift.")
        partner = self.env.user.partner_id
        if not partner.check_makeup_shift():
            english_label = dict(partner.WORKING_STATE_SELECTION).get(
                partner.cooperative_state, partner.cooperative_state
            )
            state_label = self.env._(english_label)
            return 0, self.env._(
                "Warning! You can't register to a make-up shift because"
                " your actual status is `{}`. Make-up shift registration"
                " are dedicated to members who were priviously absent."
            ).format(state_label)

        already_registered = (
            self.env["shift.registration"]
            .sudo()
            .search(
                [("shift_id", "=", self.id), ("partner_id", "=", partner.id)],
                limit=1,
            )
        )
        if already_registered:
            return 0, self.env._(
                "Warning! This member is already registered on this shift."
            )

        vals = {
            "state": "draft",
            "partner_id": partner.id,
            "shift_id": self.id,
            "shift_ticket_id": tickets[0].id,
            "related_extension_id": False,
            "is_makeup": True,
        }
        self.env["shift.registration"].sudo().with_context(
            makeup_registration=True
        ).create(vals)
        return 1, ""
