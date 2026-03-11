# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.exceptions import ValidationError

from ..date_tools import conflict_period


class ShiftLeave(models.Model):
    _name = "shift.leave"
    _description = "Shift Leave"
    _order = "start_date desc, partner_id asc"

    LEAVE_STATE_SELECTION = [
        ("draft", "Draft"),
        ("done", "Done"),
        ("cancel", "Canceled"),
    ]

    name = fields.Char(compute="_compute_name", store=True)

    type_id = fields.Many2one(
        comodel_name="shift.leave.type",
        string="Type",
        required=True,
    )

    partner_id = fields.Many2one(
        string="Partner",
        comodel_name="res.partner",
        required=True,
    )

    start_date = fields.Date(
        string="Begin Date",
        required=True,
    )

    stop_date = fields.Date(
        help="Last day of the period, during wich the partner is not"
        " available to work.",
    )

    state = fields.Selection(selection=LEAVE_STATE_SELECTION, default="draft")

    partner_state = fields.Selection(
        string="Partner State",
        related="type_id.state",
        readonly=True,
        store=True,
        help=" State"
        " of the people during the leave.\n * 'Exempted' : The customer"
        " can buy.\n * 'On vacation' : The customer can not buy.",
    )

    other_leave_ids = fields.One2many(
        comodel_name="shift.leave", string="Leaves", compute="_compute_other_leave_ids"
    )

    duration = fields.Integer(
        compute="_compute_duration",
        store=True,
        help="Duration (in Days)",
    )

    require_stop_date = fields.Boolean(related="type_id.require_stop_date")

    shift_template_registration_line_ids = fields.One2many(
        "shift.template.registration.line", "leave_id"
    )

    # Compute Section
    @api.depends("start_date", "stop_date")
    def _compute_duration(self):
        for leave in self:
            if not (leave.start_date and leave.stop_date):
                leave.duration = False
            else:
                leave.duration = (leave.stop_date - leave.start_date).days + 1

    @api.depends("partner_id", "type_id")
    def _compute_name(self):
        for leave in self:
            if leave.partner_id and leave.type_id:
                leave.name = f"{leave.type_id.name} - {leave.partner_id.name}"
            else:
                leave.name = ""

    @api.depends("partner_id.leave_ids")
    def _compute_other_leave_ids(self):
        for leave in self:
            leave.other_leave_ids = leave.partner_id.leave_ids - leave

    # constraints Section
    @api.constrains("start_date", "stop_date")
    def _check_dates(self):
        for leave in self:
            if leave.stop_date and leave.stop_date < leave.start_date:
                raise ValidationError(
                    self.env._("Stop Date should be greater than Start Date.")
                )

    @api.constrains("start_date", "stop_date", "partner_id", "state")
    def _check_partner_leaves(self):
        for leave in self:
            if leave.state == "cancel":
                continue
            other_leaves = leave.partner_id.leave_ids.filtered(
                lambda r, _l=leave: r.id != _l.id and r.state != "cancel"
            )
            for other_leave in other_leaves:
                if conflict_period(
                    leave.start_date,
                    leave.stop_date,
                    other_leave.start_date,
                    other_leave.stop_date,
                )["conflict"]:
                    raise ValidationError(
                        self.env._(
                            "The partner has an incompatible draft of done leave\n"
                            " * start date : %(start_date)s\n"
                            " * stop date : %(stop_date)s\n"
                        )
                        % {
                            "start_date": other_leave.start_date,
                            "stop_date": other_leave.stop_date
                            or self.env._("Undefined"),
                        }
                    )

    def copy_data(self, default=None):
        raise ValidationError(
            self.env._("You can not duplicate a leave : Unimplemented Feature.")
        )

    def unlink(self):
        for leave in self:
            if leave.state == "done":
                raise ValidationError(
                    self.env._("You can not unlink leaves in a done state.")
                )
        return super().unlink()

    def button_cancel(self):
        for leave in self:
            if leave.state == "done":
                leave.state = "cancel"
                leave.shift_template_registration_line_ids.with_context(
                    bypass_leave_change_check=True
                ).write({"state": "open"})
                leave.shift_template_registration_line_ids = False

    def button_draft(self):
        for leave in self:
            if leave.state == "cancel":
                leave.state = "draft"
