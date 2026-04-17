from datetime import datetime

from odoo import api, models


class ShiftRegistration(models.Model):
    _inherit = "shift.registration"

    def check_shift_regis_cancelable(self):
        for record in self:
            if record.state in ("waiting", "cancel"):
                return False
        return True

    def cancel_shift_regis_from_market(self):
        if not self.check_shift_regis_cancelable():
            return 0, ""
        mail_template = self.env.ref("coop_memberspace.shift_registration_cancel_email")
        for record in self:
            # Cancel registration
            record.with_context(bypass_reason=1).button_reg_cancel()
            mail_template.send_mail(record.id)
        return 1, ""

    @api.model
    def get_upcoming(self, partner, args=None):
        # Count the cancelled registrations also.
        if args is None:
            args = []
        args += [
            ("partner_id", "=", partner.id),
            (
                "date_begin",
                ">=",
                datetime.now(),
            ),
        ]

        shift_upcomming = self.sudo().search(
            args,
            order="date_begin",
        )
        return shift_upcomming
