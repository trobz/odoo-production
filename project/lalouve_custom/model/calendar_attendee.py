from odoo import models


class CalendarAttendee(models.Model):
    _inherit = 'calendar.attendee'

    def _send_mail_to_attendees(self, mail_template, force_send=False):
        """Skip invitation emails for events with 'Prevent change' enabled."""
        attendees = self.filtered(lambda x: not x.event_id.prevent_change)
        if not attendees:
            return False
        return super(CalendarAttendee, attendees)._send_mail_to_attendees(
            mail_template, force_send
        )
