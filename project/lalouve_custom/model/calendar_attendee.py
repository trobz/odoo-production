from odoo import models


class CalendarAttendee(models.Model):
    _inherit = 'calendar.attendee'

    def _send_mail_to_attendees(
        self, template_xmlid, force_send=False, force_event_id=None
    ):
        """Overwrite this function in order to check "Prevent Changes" """
        res = False
        attendees = self.filtered(lambda x: not x.event_id.prevent_change)
        if not attendees:
            return res

        return super(CalendarAttendee, attendees)._send_mail_to_attendees(
            template_xmlid, force_send, force_event_id
        )
