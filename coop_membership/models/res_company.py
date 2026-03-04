# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.fr/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    discovery_meeting_description = fields.Html()
    discovery_meeting_notice = fields.Html()
    discovery_meeting_event_stage_ids = fields.Many2many(
        "event.stage",
        string="Discovery Meeting Event Stages",
        default=lambda self: self.get_default_discovery_meeting_event_stages(),
    )
    contact_us_message = fields.Html(
        translate=True,
        default=lambda self: self.get_default_message(),
    )
    max_registrations_per_day = fields.Integer(default=2)
    max_registration_per_period = fields.Integer(default=5)
    number_of_days_in_period = fields.Integer(default=28)
    maximum_active_days = fields.Integer(default=180)
    email_meeting_contact = fields.Char()
    company_name = fields.Char(string="Other Name")
    members_office_open_hours = fields.Text(
        translate=True,
        default=lambda self: self.get_default_timing(),
    )

    @api.model
    def get_default_discovery_meeting_event_stages(self):
        stage_ids = (
            self.env.ref("event.event_stage_booked", raise_if_not_found=False)
            | self.env.ref("event.event_stage_announced", raise_if_not_found=False)
        ).ids
        return stage_ids

    @api.model
    def get_default_message(self):
        return f"""Hello,<br/>Please contact an employee or go at the members\'
        office for administrative reasons.<br/>
        Cordially, {self.env.user.company_id.name} team"""

    @api.model
    def get_default_timing(self):
        return """Tuesday: 1:30 p.m. - 4 p.m. \n
        Wednesday to Friday: 1:30 p.m. - 8 p.m.
        \n Saturday: 10 a.m. - 4 p.m."""
