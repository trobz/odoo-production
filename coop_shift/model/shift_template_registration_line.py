# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
# @author Julien WESTE
# @author Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import datetime

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF

STATES = [
    ("cancel", "Cancelled"),
    ("draft", "Unconfirmed"),
    ("open", "Confirmed"),
    ("done", "Attended"),
    ("absent", "Absent"),
    ("waiting", "Waiting"),
    ("excused", "Excused"),
    ("replaced", "Replaced"),
    ("replacing", "Replacing"),
]


class ShiftTemplateRegistrationLine(models.Model):
    _name = "shift.template.registration.line"
    _description = "Attendee Line"
    _order = "date_begin desc"

    registration_id = fields.Many2one(
        "shift.template.registration",
        required=True,
        ondelete="cascade",
    )
    date_begin = fields.Date("Begin Date", required=True)
    date_end = fields.Date("End Date")
    state = fields.Selection(STATES, default="open")
    shift_registration_ids = fields.One2many(
        "shift.registration",
        "tmpl_reg_line_id",
    )
    partner_id = fields.Many2one(
        related="registration_id.partner_id", store=True, readonly=False
    )
    shift_template_id = fields.Many2one(
        related="registration_id.shift_template_id", readonly=False
    )
    shift_ticket_id = fields.Many2one(
        related="registration_id.shift_ticket_id", readonly=False
    )
    is_current = fields.Boolean(string="Current", compute="_compute_current")
    is_past = fields.Boolean(string="Past", compute="_compute_current")
    is_future = fields.Boolean(string="Future", compute="_compute_current")

    leave_id = fields.Many2one("shift.leave")

    # constraints Section
    @api.constrains("date_begin", "date_end")
    def _check_dates(self):
        for leave in self:
            if leave.date_end and leave.date_end < leave.date_begin:
                raise ValidationError(
                    self.env._("Stop Date should be greater than Start Date.")
                )
            leave._check_over_lap()

    def _check_over_lap(self):
        self.ensure_one()
        lines = self.partner_id.tmpl_reg_line_ids
        for line in lines:
            if (
                line.id != self.id
                and (not self.date_end or line.date_begin <= self.date_end)
                and (not line.date_end or line.date_end >= self.date_begin)
            ):
                raise ValidationError(
                    self.env._(
                        "You can't register this line because it would "
                        "create an overlap with another line for this member.\n\n"
                        "Line: %(line_begin)s - %(line_end)s\n"
                        "Overlap: %(overlap_begin)s - %(overlap_end)s"
                    )
                    % {
                        "line_begin": self.date_begin,
                        "line_end": self.date_end,
                        "overlap_begin": line.date_begin,
                        "overlap_end": line.date_end,
                    }
                )

    def _compute_current(self):
        for line in self:
            now = fields.Date.context_today(self)
            line.is_current = False
            line.is_past = False
            line.is_future = False
            if line.date_begin and line.date_begin > now:
                line.is_future = True
            elif line.date_end and line.date_end < now:
                line.is_past = True
            else:
                line.is_current = True

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            begin = vals.get("date_begin")
            end = vals.get("date_end")
            if begin:
                # convert to datetime
                begin = fields.Date.from_string(begin).strftime(DF) + " 00:00:00"
                begin = self.env["ir.fields.converter"]._str_to_datetime(
                    None, None, begin
                )[0]

            if end:
                # convert to datetime
                end = fields.Date.from_string(end).strftime(DF) + " 00:00:00"
                end = self.env["ir.fields.converter"]._str_to_datetime(None, None, end)[
                    0
                ]

            st_reg_id = vals.get("registration_id")
            if not st_reg_id:
                registration_id = self.env["shift.template.registration"].search(
                    [
                        ("partner_id", "=", vals.get("partner_id")),
                        ("shift_template_id", "=", vals.get("shift_template_id")),
                    ],
                    limit=1,
                )
                st_reg_id = registration_id and registration_id.id or False
                vals["registration_id"] = st_reg_id
            if not st_reg_id:
                registration_id = (
                    self.env["shift.template.registration"]
                    .with_context(no_default_line=True)
                    .create(
                        {
                            "shift_template_id": vals.get("shift_template_id"),
                            "partner_id": vals.get("partner_id"),
                            "shift_ticket_id": vals.get("shift_ticket_id", False),
                        }
                    )
                )
                st_reg_id = registration_id.id
                vals["registration_id"] = st_reg_id

            st_reg = self.env["shift.template.registration"].browse(st_reg_id)
            partner = st_reg.partner_id

            # Get shifts affected by this registratation line
            shift_domain = [
                ("shift_template_id", "=", st_reg.shift_template_id.id),
                ("state", "!=", "done"),
            ]
            if begin:
                # F#T66337 - [Chaudron] BdM:
                # date of the first service prior to subscription date
                # Don't take into account shifts in the past
                today = fields.Datetime.to_string(
                    fields.Datetime.context_timestamp(self, fields.Datetime.now())
                )
                shift_domain.append(("date_begin", ">", max(begin, today)))
            if end:
                shift_domain.append(("date_end", "<", end))
            shifts = self.env["shift.shift"].search(shift_domain)

            # Compute registrations to create
            v = {"partner_id": partner.id, "state": vals.get("state", "open")}

            created_registrations = []
            for shift in shifts:
                ticket_id = shift.shift_ticket_ids.filtered(
                    lambda t, s=st_reg.shift_ticket_id: t.product_id == s.product_id
                )
                if ticket_id:
                    ticket_id = ticket_id[0]
                else:
                    shift.write(
                        {
                            "shift_ticket_ids": [
                                (
                                    0,
                                    0,
                                    {
                                        "name": st_reg.shift_ticket_id.name,
                                        "product_id": (
                                            st_reg.shift_ticket_id.product_id.id,
                                        ),
                                        "seats_max": st_reg.shift_ticket_id.seats_max,
                                    },
                                )
                            ]
                        }
                    )
                    ticket_id = shift.shift_ticket_ids.filtered(
                        lambda t, s=st_reg.shift_ticket_id: t.product_id == s.product_id
                    )[0]
                values = dict(
                    v,
                    **{
                        "shift_id": shift.id,
                        "shift_ticket_id": ticket_id.id,
                        "template_created": True,
                    },
                )
                created_registrations.append((0, 0, values))

            vals["shift_registration_ids"] = created_registrations
        return super(
            ShiftTemplateRegistrationLine, self.with_context(creation_in_progress=True)
        ).create(vals_list)

    def _validate_leave_change(self, line):
        bypass_leave_change_check = self._context.get(
            "bypass_leave_change_check", False
        )
        if not bypass_leave_change_check and line.leave_id:
            raise ValidationError(
                self.env._(
                    "You cannot make changes on this template registration. "
                    "Please make your changes directly on the leave recorded "
                    "for this period. You will need to cancel it then set to "
                    "draft before you can make required changes.\n\n"
                    "Registration: (ID: %(registration_id)s) - %(partner_name)s"
                )
                % {
                    "registration_id": line.id,
                    "partner_name": line.partner_id.name,
                }
            )

    def _normalize_write_dates(self, vals, line):
        state = vals.get("state", line.state)
        begin = vals.get("date_begin", line.date_begin)
        end = vals.get("date_end", line.date_end)

        if isinstance(end, str):
            end = fields.Date.from_string(end)
        if isinstance(begin, str):
            begin = fields.Date.from_string(begin)

        if isinstance(begin, datetime.datetime):
            begin = begin.date()
        if isinstance(end, datetime.datetime):
            end = end.date()

        if isinstance(begin, str):
            begin = fields.Date.from_string(begin)
        if isinstance(end, str):
            end = fields.Date.from_string(end)

        return state, begin, end

    def _apply_existing_registration_updates(self, line, state, begin, end):
        for shift_registration in line.shift_registration_ids:
            shift = shift_registration.shift_id

            if shift.state == "done":
                continue

            if shift_registration.state in ["draft", "open", "waiting"]:
                if (not begin or shift.date_begin.date() >= begin) and (
                    not end or shift.date_end.date() <= end
                ):
                    shift_registration.state = state
                else:
                    shift_registration.unlink()
            elif not (
                (not begin or shift.date_begin.date() >= begin)
                and (not end or shift.date_end.date() <= end)
            ):
                if shift_registration.state == "cancel":
                    shift_registration.unlink()
                else:
                    state_dict = {
                        "cancel": "Cancelled",
                        "draft": "Unconfirmed",
                        "open": "Confirmed",
                        "done": "Attended",
                        "absent": "Absent",
                        "waiting": "Waiting",
                        "excused": "Excused",
                        "replaced": "Replaced",
                        "replacing": "Replacing",
                    }
                    raise ValidationError(
                        self.env._(
                            "Cannot process because of the attendance: \n"
                            "- Registration: (ID: %(registration_id)s, "
                            "State: %(registration_state)s) %(registration)s\n"
                            "- Shift: %(shift)s \n"
                            "- Partner: %(partner)s"
                        )
                        % {
                            "registration_id": shift_registration.id,
                            "registration_state": state_dict.get(
                                shift_registration.state
                            ),
                            "registration": shift_registration.display_name,
                            "shift": shift_registration.shift_id.display_name,
                            "partner": shift_registration.partner_id.display_name,
                        }
                    )

    def _create_missing_registrations(self, line, state, begin, end):
        shift_registration_obj = self.env["shift.registration"]
        template_registration = line.registration_id
        partner = template_registration.partner_id

        shifts = template_registration.shift_template_id.shift_ids.filtered(
            lambda shift, begin_date=begin, end_date=end: (
                (not begin_date or shift.date_begin.date() >= begin_date)
                and (not end_date or shift.date_end.date() <= end_date)
                and (shift.state not in ("done", "cancel"))
            )
        )

        today = fields.Datetime.context_timestamp(self, fields.Datetime.now())
        template_ticket_product = template_registration.shift_ticket_id.product_id
        for shift in shifts:
            found = partner_found = False
            for registration in shift.registration_ids:
                if registration.partner_id == partner:
                    partner_found = registration
                if registration.tmpl_reg_line_id == line:
                    found = True
                    break

            if not found:
                if partner_found:
                    partner_found.tmpl_reg_line_id = line
                    partner_found.state = state
                elif shift.date_begin.date() >= today.date():
                    ticket_id = shift.shift_ticket_ids.filtered(
                        lambda ticket, product=template_ticket_product: (
                            ticket.product_id == product
                        )
                    )[0]
                    values = {
                        "partner_id": partner.id,
                        "state": state,
                        "shift_id": shift.id,
                        "shift_ticket_id": ticket_id.id,
                        "tmpl_reg_line_id": line.id,
                        "template_created": True,
                    }
                    shift_registration_obj.create(values)

    def write(self, vals):
        res = super().write(vals)
        self.mapped(lambda s: s.partner_id).sudo()._compute_registration_counts()
        for line in self:
            self._validate_leave_change(line)
            state, begin, end = self._normalize_write_dates(vals, line)
            self._apply_existing_registration_updates(line, state, begin, end)
            self._create_missing_registrations(line, state, begin, end)
        return res

    def unlink(self):
        for strl in self:
            for reg in strl.shift_registration_ids:
                reg.unlink()
        return super().unlink()
