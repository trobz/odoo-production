from odoo import fields, models


class EventTicket(models.Model):
    _inherit = "event.event.ticket"

    is_discovery_meeting_event = fields.Boolean(
        string="Discovery Meeting Event", store=True
    )
