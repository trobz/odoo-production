# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
# @author Julien WESTE
# @author Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime, timedelta

import pytz

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.osv import expression

# this variable is used for shift confirmation. It tells how many days before
# its date_begin a shift is confirmed
SHIFT_CONFIRMATION_DAYS = 5


class ShiftShift(models.Model):
    _inherit = "event.event"
    _name = "shift.shift"
    _description = "Shift"

    @api.model
    def _default_shift_mail_ids(self):
        return [
            (
                0,
                0,
                {
                    "interval_unit": "now",
                    "interval_type": "after_sub",
                    "template_id": self.env.ref("coop_shift.shift_subscription"),
                },
            )
        ]

    name = fields.Char(
        string="Shift Name",
        related="shift_template_id.name",
        translate=False,
        store=True,
    )
    shift_template_id = fields.Many2one(
        "shift.template", string="Shift Template", ondelete="restrict"
    )
    event_mail_ids = fields.One2many(default=None, string="Even Mail Schedule")
    shift_mail_ids = fields.One2many(
        "shift.mail",
        "shift_id",
        string="Mail Schedule",
        default=lambda self: self._default_shift_mail_ids(),
    )
    shift_type_id = fields.Many2one(
        "shift.type",
        string="Shift Category",
        required=False,
        readonly=False,
    )
    week_number = fields.Integer(
        compute="_compute_week_number",
        store=True,
    )
    week_name = fields.Char(
        string="Week",
        compute="_compute_week_name",
        store=True,
    )
    week_list = fields.Selection(
        [
            ("MO", "Monday"),
            ("TU", "Tuesday"),
            ("WE", "Wednesday"),
            ("TH", "Thursday"),
            ("FR", "Friday"),
            ("SA", "Saturday"),
            ("SU", "Sunday"),
        ],
        "Weekday",
    )
    registration_ids = fields.One2many(
        "shift.registration",
        "shift_id",
        string="Attendees",
        readonly=False,
    )
    seats_availability = fields.Selection(
        [("limited", "Limited"), ("unlimited", "Unlimited")],
        required=True,
        default="unlimited",
    )
    seats_min = fields.Integer(
        string="Minimum Attendees",
        help="For each event you can define a minimum reserved seats "
        "(number of attendees), if it does not reach the mentioned "
        "registrations the event can not be confirmed (keep 0 to "
        "ignore this rule)",
    )

    seats_reserved = fields.Integer(compute="_compute_seats_shift")
    seats_available = fields.Integer(compute="_compute_seats_shift")
    seats_unconfirmed = fields.Integer(compute="_compute_seats_shift")
    seats_used = fields.Integer(compute="_compute_seats_shift")
    seats_expected = fields.Integer(compute="_compute_seats_shift")
    auto_confirm = fields.Boolean(
        string="Confirmation not required", compute="_compute_auto_confirm"
    )
    event_ticket_ids = fields.One2many(default=lambda rec: rec._default_tickets())
    shift_ticket_ids = fields.One2many(
        "shift.ticket",
        "shift_id",
        string="Shift Ticket",
        default=lambda rec: rec._default_shift_tickets(),
        copy=True,
    )
    # date_tz = fields.Selection('_tz_get', string='Timezone', default=False)
    date_begin = fields.Datetime(
        compute="_compute_date_begin", store=True, required=False
    )
    date_begin_tz = fields.Datetime(string="Begin Date Time")
    date_end = fields.Datetime(compute="_compute_date_end", store=True, required=False)
    date_end_tz = fields.Datetime(string="End Date Time")
    date_without_time = fields.Date(
        string="Date",
        compute="_compute_begin_date_fields_stored",
        store=True,
    )
    begin_date_string = fields.Char(
        string="Begin Date",
        compute="_compute_begin_date_fields_stored",
        store=True,
    )
    begin_date_without_time_string = fields.Char(
        string="Begin Date for mail without time",
        compute="_compute_begin_date_fields_display",
    )
    begin_time = fields.Float(
        string="Start Time",
        compute="_compute_begin_date_fields_stored",
        store=True,
    )
    begin_time_string = fields.Char(
        string="Begin Time", compute="_compute_begin_date_fields_display"
    )
    end_time = fields.Float(
        string="End Time (Hours)",
        compute="_compute_end_time",
        store=True,
    )
    end_time_string = fields.Char(string="End Time", compute="_compute_end_time_string")
    user_ids = fields.Many2many(
        "res.partner",
        "res_partner_shift_shift_rel",
        "shift_template_id",
        "partner_id",
        string="Shift Leaders",
    )
    user_id = fields.Many2one("res.partner", default=False)
    seats_max = fields.Integer()

    # TODO: consider to replace it by stage_id as event.event
    state = fields.Selection(
        selection=lambda self: self._get_state_selection(),
        string="Status",
        default="draft",
        required=True,
        copy=False,
    )
    question_ids = fields.One2many(compute=False)
    color = fields.Integer("Kanban Color Index")

    def _get_state_selection(self):
        state_selection = [
            ("draft", "Unconfirmed"),
            ("cancel", "Cancelled"),
            ("confirm", "Confirmed"),
            ("done", "Done"),
        ]
        return state_selection

    @api.constrains("shift_template_id", "date_begin", "company_id")
    def _check_uniq_date_shift(self):
        for shift in self:
            args = [
                ("shift_template_id", "=", shift.shift_template_id.id),
                ("date_begin", "=", shift.date_begin),
                ("company_id", "=", shift.company_id.id),
            ]
            existed = self.env["shift.shift"].search(args, limit=2)
            if len(existed) >= 2:
                raise UserError(
                    self.env._(
                        "The same template cannot be planned several time "
                        "at the same date !"
                    )
                )

    @api.depends("shift_template_id", "date_without_time")
    def _compute_week_number(self):
        records_with_date = self.filtered("date_without_time")
        records_without_date = self - records_with_date
        # Records without date have no week_number
        records_without_date.write({"week_number": False})
        # Records with date get computed week number
        data = self.env["shift.template"]._get_week_number_multi(
            records=records_with_date,
            field_name="date_without_time",
        )
        for rec in self:
            week_number = data.get(rec.id)
            if not week_number:
                rec.week_number = False
            else:
                rec.week_number = week_number

    @api.depends("week_number")
    def _compute_week_name(self):
        for shift in self:
            if shift.week_number:
                shift.week_name = shift.shift_template_id._number_to_letters(
                    shift.week_number
                )
            else:
                shift.week_name = False

    @api.model
    def name_search(self, name, args=None, operator="ilike", limit=100):
        args = args or []
        domain = []
        if name:
            domain = [
                "|",
                ("begin_date_string", operator, name),
                ("name", operator, name),
            ]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ["&", "!"] + domain[1:]
        args = expression.AND([args, domain])
        empty_name = False
        return super().name_search(
            name=empty_name, args=args, operator=operator, limit=limit)

    @api.depends("name", "date_begin")
    def _compute_display_name(self):
        for shift in self:
            shift.display_name = shift.name + (
                shift.begin_date_string and (" " + shift.begin_date_string) or ""
            )

    @api.model
    def _default_tickets(self):
        return None

    @api.model
    def _default_shift_tickets(self):
        try:
            product = self.env.ref("coop_shift.product_product_shift_standard")
            product2 = self.env.ref("coop_shift.product_product_shift_ftop")
            return [
                {
                    "name": self.env._("Standard"),
                    "product_id": product.id,
                    "price": 0,
                },
                {
                    "name": self.env._("FTOP"),
                    "product_id": product2.id,
                    "price": 0,
                },
            ]
        except ValueError:
            return self.env["shift.ticket"]

    def _compute_auto_confirm(self):
        for shift in self:
            shift.auto_confirm = False

    @api.model
    def _default_event_mail_ids(self):
        return None

    @api.depends("seats_max", "registration_ids.state")
    def _compute_seats_shift(self):
        """Determine reserved, available, reserved but unconfirmed and used
        seats."""
        # initialize fields to 0
        for shift in self:
            shift.seats_unconfirmed = shift.seats_reserved = shift.seats_used = (
                shift.seats_available
            ) = 0
        # aggregate registrations by shift and by state
        if self.ids:
            state_field = {
                "draft": "seats_reserved",
                "open": "seats_reserved",
                "replacing": "seats_reserved",
                "done": "seats_used",
            }
            query = """ SELECT shift_id, state, count(shift_id)
                        FROM shift_registration
                        WHERE shift_id IN %s
                        AND state IN ('draft', 'open', 'done', 'replacing')
                        GROUP BY shift_id, state
                    """
            self._cr.execute(query, (tuple(self.ids),))
            for shift_id, state, num in self._cr.fetchall():
                shift = self.browse(shift_id)
                shift[state_field[state]] += num
        # compute seats_available
        for shift in self:
            if shift.seats_max > 0:
                shift.seats_available = shift.seats_max - (
                    shift.seats_reserved + shift.seats_used
                )
            shift.seats_expected = (
                shift.seats_unconfirmed + shift.seats_reserved + shift.seats_used
            )

    @api.model
    def _done_writable_fields(self):
        """List of fields that can be written on if confirmed"""
        return [
            "state_in_holiday",
            "single_holiday_id",
            "long_holiday_id",
            "week_number",
            "week_name",
        ]

    def write(self, vals):
        special = self._context.get("special", False)
        if any(shift.state == "done" for shift in self):
            ignore_fields = self._done_writable_fields()
            for field in vals.keys():
                if field in ignore_fields:
                    break
                raise UserError(
                    self.env._("You can only repercute changes on draft shifts.")
                )
        res = super().write(vals)
        if special:
            for field in special:
                if field == "shift_ticket_ids":
                    for shift in self:
                        template = shift.shift_template_id
                        ftop_ticket = template.shift_ticket_ids.filtered(
                            lambda t: t.shift_type == "ftop"
                        )
                        standard_ticket = template.shift_ticket_ids.filtered(
                            lambda t: t.shift_type == "standard"
                        )
                        ftop_seats_max = ftop_ticket and ftop_ticket[0].seats_max
                        standard_seats_max = (
                            standard_ticket and standard_ticket[0].seats_max
                        )
                        for ticket in shift.shift_ticket_ids:
                            if ticket.shift_type == "ftop":
                                ticket.seats_max = ftop_seats_max
                            if ticket.shift_type == "standard":
                                ticket.seats_max = standard_seats_max
        return res

    @api.onchange("shift_template_id")
    def _onchange_template_id(self):
        if self.shift_template_id:
            self.name = self.shift_template_id.name
            self.user_ids = self.shift_template_id.user_ids
            self.shift_type_id = self.shift_template_id.shift_type_id
            self.week_number = self.shift_template_id.week_number
            cur_date = (
                self.date_begin
                and self.date_begin.date()
                or self.shift_template_id.start_date
            )
            self.date_begin = cur_date + timedelta(
                hours=self.shift_template_id.start_time
            )
            self.end_time = cur_date + timedelta(hours=self.shift_template_id.end_time)
            cur_attendees = [r.partner_id.id for r in self.registration_ids]
            vals = []
            for attendee in self.shift_template_id.registration_ids:
                if attendee.id not in cur_attendees:
                    vals.append(
                        (
                            0,
                            0,
                            {
                                "partner_id": attendee.id,
                                "state": "draft",
                                "email": attendee.email,
                                "phone": attendee.phone,
                                "name": attendee.name,
                                "shift_id": self.id,
                            },
                        )
                    )
                self.registration_ids = vals

    @api.depends("date_begin_tz")
    def _compute_date_begin(self):
        tz_name = self._context.get("tz") or self.env.user.tz
        if not tz_name:
            raise UserError(
                self.env._("You can not create Shift if your timezone is not defined.")
            )
        context_tz = pytz.timezone(tz_name)
        for shift in self:
            if shift.date_begin_tz:
                start_date_object_tz = fields.Datetime.from_string(shift.date_begin_tz)
                utc_timestamp = pytz.utc.localize(start_date_object_tz, is_dst=False)
                start_date_object = utc_timestamp.astimezone(context_tz)
                # Replace code hour after tz - hour
                # start_date = start_date_object_tz + timedelta(
                #     hours=start_date_object_tz.hour - start_date_object.hour)
                # By date after tz - date
                delta = start_date_object_tz.replace(
                    tzinfo=None
                ) - start_date_object.replace(tzinfo=None)
                hours = delta.days * 24 + delta.seconds / 3600
                start_date = start_date_object_tz + timedelta(hours=hours)
                # ===========================
                shift.date_begin = "%s-%02d-%02d %02d:%02d:%02d" % (
                    start_date.year,
                    start_date.month,
                    start_date.day,
                    start_date.hour,
                    start_date.minute,
                    start_date.second,
                )

    @api.depends("date_end_tz")
    def _compute_date_end(self):
        tz_name = self._context.get("tz") or self.env.user.tz
        if not tz_name:
            raise UserError(
                self.env._("You can not create Shift if your timezone is not defined.")
            )
        context_tz = pytz.timezone(tz_name)
        for shift in self:
            if shift.date_end_tz:
                end_date_object_tz = fields.Datetime.from_string(shift.date_end_tz)
                utc_timestamp = pytz.utc.localize(end_date_object_tz, is_dst=False)
                end_date_object = utc_timestamp.astimezone(context_tz)
                # Replace code hour after tz - hour
                # end_date = end_date_object_tz + timedelta(
                #     hours=end_date_object_tz.hour - end_date_object.hour)
                # By date after tz - date
                delta = end_date_object_tz.replace(
                    tzinfo=None
                ) - end_date_object.replace(tzinfo=None)
                hours = delta.days * 24 + delta.seconds / 3600
                end_date = end_date_object_tz + timedelta(hours=hours)
                # ===========================
                shift.date_end = "%s-%02d-%02d %02d:%02d:%02d" % (
                    end_date.year,
                    end_date.month,
                    end_date.day,
                    end_date.hour,
                    end_date.minute,
                    end_date.second,
                )

    @api.depends("date_begin_tz")
    def _compute_begin_date_fields_stored(self):
        for shift in self:
            if shift.date_begin_tz:
                start_date_object_tz = shift.date_begin_tz
                shift.begin_time = start_date_object_tz.hour + (
                    start_date_object_tz.minute / 60.0
                )
                shift.begin_date_string = "%02d/%02d/%s " "%02d:%02d" % (
                    start_date_object_tz.day,
                    start_date_object_tz.month,
                    start_date_object_tz.year,
                    start_date_object_tz.hour,
                    start_date_object_tz.minute,
                )
                shift.date_without_time = "%s-%02d-%02d" % (
                    start_date_object_tz.year,
                    start_date_object_tz.month,
                    start_date_object_tz.day,
                )

    @api.depends("date_begin_tz")
    def _compute_begin_date_fields_display(self):
        for shift in self:
            if shift.date_begin_tz:
                start_date_object_tz = shift.date_begin_tz
                shift.begin_time_string = "%02d:%02d" % (
                    start_date_object_tz.hour,
                    start_date_object_tz.minute,
                )
                shift.begin_date_without_time_string = "%02d/%02d/%s" % (
                    start_date_object_tz.day,
                    start_date_object_tz.month,
                    start_date_object_tz.year,
                )

    @api.depends("date_end")
    def _compute_end_time(self):
        tz_name = self._context.get("tz") or self.env.user.tz
        if not tz_name:
            raise UserError(
                self.env._("You can not create Shift if your timezone is not defined.")
            )
        for shift in self:
            if shift.date_end:
                utc_timestamp = pytz.utc.localize(shift.date_end, is_dst=False)
                context_tz = pytz.timezone(tz_name)
                start_date_object_tz = utc_timestamp.astimezone(context_tz)
                shift.end_time = start_date_object_tz.hour + (
                    start_date_object_tz.minute / 60.0
                )

    @api.depends("date_end")
    def _compute_end_time_string(self):
        tz_name = self._context.get("tz") or self.env.user.tz
        if not tz_name:
            raise UserError(
                self.env._("You can not create Shift if your timezone is not defined.")
            )
        for shift in self:
            if shift.date_end:
                utc_timestamp = pytz.utc.localize(shift.date_end, is_dst=False)
                context_tz = pytz.timezone(tz_name)
                start_date_object_tz = utc_timestamp.astimezone(context_tz)
                shift.end_time_string = "%02d:%02d" % (
                    start_date_object_tz.hour,
                    start_date_object_tz.minute,
                )

    def button_draft(self):
        shifts = self.filtered(lambda s: s.state in ["cancel", "done"])
        shifts.write({"state": "draft"})

    def button_cancel(self):
        shifts = self.filtered(lambda s: s.state in ["draft", "confirm"])
        if any("done" in shift.mapped("registration_ids.state") for shift in shifts):
            raise UserError(
                self.env._(
                    "There are already attendees who attended this shift. "
                    "Please reset it to draft if you want to cancel this shift."
                )
            )
        shifts.mapped("registration_ids").write({"state": "cancel"})
        shifts.write({"state": "cancel"})

    def button_done(self):
        self.write({"state": "done"})

    def button_confirm(self):
        self.write({"state": "confirm"})

    @api.model
    def run_shift_confirmation(self):
        # This method is called by the cron task
        day_nb = int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("shift.confirmation_days", SHIFT_CONFIRMATION_DAYS)
        )
        compare_date = fields.Date.to_string(datetime.today() + timedelta(days=day_nb))
        shifts = self.env["shift.shift"].search(
            [("state", "=", "draft"), ("date_begin", "<=", compare_date)]
        )
        shifts.button_confirm()

    def _recompute_week_number_async(self):
        NUM_RECORDS_PER_JOB = 200
        chunked = [
            self[i : i + NUM_RECORDS_PER_JOB]
            for i in range(0, len(self), NUM_RECORDS_PER_JOB)
        ]
        # Create jobs
        for _chunk in chunked:
            self.with_delay()._job_recompute_week_number_async()
        return True

    def _job_recompute_week_number_async(self):
        self._compute_week_number()
