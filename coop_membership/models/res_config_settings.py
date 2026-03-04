from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    # description = fields.Char(
    #     config_parameter="account_export.description",
    # )
    # notice = fields.Char(
    #     config_parameter="account_export.notice",
    # )
    discovery_meeting_captcha_site_key = fields.Char(
        config_parameter="captcha_site_key",
    )
    discovery_meeting_captcha_secret_key = fields.Char(
        config_parameter="captcha_secret_key",
    )
    discovery_meeting_description = fields.Html(
        related="company_id.discovery_meeting_description",
        readonly=False,
    )
    discovery_meeting_notice = fields.Html(
        related="company_id.discovery_meeting_notice",
        readonly=False,
    )
    discovery_meeting_event_stage_ids = fields.Many2many(
        "event.stage",
        related="company_id.discovery_meeting_event_stage_ids",
        readonly=False,
    )
    email_meeting_contact = fields.Char(
        related="company_id.email_meeting_contact",
        readonly=False,
    )
    company_name = fields.Char(
        string="Company Name",
        related="company_id.company_name",
        readonly=False,
    )
    shift_leave_remind_days = fields.Integer(
        "Leve Reminder Days",
        config_parameter="coop_membership.leave_reminder_days",
    )
    max_nb_associated_people = fields.Integer(
        "Maximum Associated People",
        config_parameter="coop_membership.max_nb_associated_people",
    )
    associated_people_available = fields.Selection(
        [("unlimited", "Unlimited"), ("limited", "Limited")],
        config_parameter="coop_membership.associated_people_available",
        default="unlimited",
    )
    contact_us_messages = fields.Html(
        string="Contact Us Message",
        related="company_id.contact_us_message",
        translate=True,
        readonly=False,
    )
    max_registrations_per_day = fields.Integer(
        string="FTOP Max. Registration per day",
        related="company_id.max_registrations_per_day",
        readonly=False,
    )
    max_registration_per_period = fields.Integer(
        string="FTOP Max. Registration per period",
        related="company_id.max_registration_per_period",
        readonly=False,
    )
    number_of_days_in_period = fields.Integer(
        string="FTOP Registration period",
        related="company_id.number_of_days_in_period",
        readonly=False,
    )
    maximum_active_days = fields.Integer(
        related="company_id.maximum_active_days",
        readonly=False,
    )
    members_office_open_hours = fields.Text(
        related="company_id.members_office_open_hours",
        string="Members Office Open Hours",
        translate=True,
        readonly=False,
    )

    @api.constrains("number_of_days_in_period")
    def _check_positive_number_of_days_in_period(self):
        for config in self:
            if config.number_of_days_in_period < 0:
                raise ValidationError(
                    _(
                        "The FTOP Max. Registration per period "
                        "number must be a positive number !"
                    )
                )

    @api.constrains("max_nb_associated_people")
    def _check_positive_number_of_associated_people(self):
        for rec in self:
            if rec.max_nb_associated_people < 0:
                raise ValidationError(
                    _(
                        "The maximum number of associated people must be a "
                        "positive number !"
                    )
                )
