# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
# @author Julien WESTE
# @author Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.exceptions import UserError


class ShiftRegistration(models.Model):
    _inherit = "event.registration"
    _name = "shift.registration"
    _description = "Attendee"
    _order = "shift_ticket_id,name"

    shift_type = fields.Selection(
        string="Shift type",
        related="shift_ticket_id.shift_type",
        store=True,
    )

    event_id = fields.Many2one(required=False)
    shift_id = fields.Many2one(
        "shift.shift",
        string="Shift",
        required=True,
        ondelete="cascade",
    )
    email = fields.Char(readonly=True, related="partner_id.email")
    phone = fields.Char(readonly=True, related="partner_id.phone")
    name = fields.Char(readonly=True, related="partner_id.name", store=True)
    partner_id = fields.Many2one(string="Contact", required=True)
    user_ids = fields.Many2many("res.partner", related="shift_id.user_ids")
    shift_ticket_id = fields.Many2one(
        "shift.ticket", "Shift Ticket", required=True, ondelete="cascade"
    )
    shift_ticket_product_id = fields.Many2one(
        "product.product",
        "Ticket Product",
        related="shift_ticket_id.product_id",
        store=True,
    )
    state = fields.Selection(
        selection_add=[
            ("open", "Registered"),
            ("absent", "Absent"),
            ("waiting", "Waiting"),
            ("excused", "Excused"),
            ("replaced", "Replaced"),
            ("replacing", "Replacing"),
        ],
        ondelete={
            "absent": lambda records: records.write({"state": "draft"}),
            "waiting": lambda records: records.write({"state": "draft"}),
            "excused": lambda records: records.write({"state": "draft"}),
            "replaced": lambda records: records.write({"state": "draft"}),
            "replacing": lambda records: records.write({"state": "draft"}),
        },
        default="draft",
    )
    tmpl_reg_line_id = fields.Many2one(
        "shift.template.registration.line", "Template Registration Line"
    )
    date_open = fields.Datetime(
        string="Registration Date",
        readonly=True,
        default=lambda self: fields.Datetime.now(),
    )
    date_begin = fields.Datetime(related="shift_id.date_begin", store=True)
    date_end = fields.Datetime(related="shift_id.date_end")
    replacing_reg_id = fields.Many2one(
        "shift.registration", "Replacing Registration", required=False
    )
    replaced_reg_id = fields.Many2one(
        "shift.registration", "Replaced Registration", required=False
    )
    template_created = fields.Boolean("Created by a Template", default=False)
    is_related_shift_ftop = fields.Boolean(
        compute="_compute_is_related_shift_ftop", store=False
    )

    replacing_partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Replacing Member",
        related="replacing_reg_id.partner_id",
        store=True,
    )

    exchange_state = fields.Selection(
        [
            ("draft", "Draft"),
            ("in_progress", "In Progress"),
            ("replacing", "Replacing"),
            ("replaced", "Replaced"),
        ],
        string="Exchange Status",
        default="draft",
    )

    is_technical = fields.Boolean(compute="_compute_is_technical", store=True)

    _sql_constraints = [
        (
            "shift_registration_uniq",
            "unique (shift_id, partner_id)",
            "This partner is already registered on this Shift !",
        ),
    ]

    @api.depends("shift_id.shift_template_id.is_technical")
    def _compute_is_technical(self):
        for registration in self:
            registration.is_technical = (
                registration.shift_id.shift_template_id.is_technical
            )

    def _compute_is_related_shift_ftop(self):
        """
        @Function to compute the value for field `is_related_shift_ftop`
            Set value to True if related Shift is in type of FTOP, and False
            otherwise
        """
        for registration in self:
            registration.is_related_shift_ftop = (
                registration.shift_id
                and registration.shift_id.shift_type_id
                and registration.shift_id.shift_type_id.is_ftop
            )

    def button_reg_absent(self):
        for reg in self:
            if reg.shift_id.date_begin <= fields.Datetime.now():
                reg.state = "absent"
            else:
                raise UserError(
                    self.env._(
                        "You must wait for the starting day of the "
                        "shift to do this action."
                    )
                )

    def button_reg_excused(self):
        for reg in self:
            if reg.shift_id.date_begin <= fields.Datetime.now():
                reg.state = "excused"
            else:
                raise UserError(
                    self.env._(
                        "You must wait for the starting day of the "
                        "shift to do this action."
                    )
                )

    def do_draft(self):
        self.update({"state": "draft"})

    def confirm_registration(self):
        self.update({"state": "open"})

        # auto-trigger after_sub (on subscribe) mail schedulers, if needed
        for reg in self:
            if reg.exchange_state == "replacing":
                continue
            onsubscribe_schedulers = reg.shift_id.shift_mail_ids.filtered(
                lambda s: s.interval_type == "after_sub"
            )
            onsubscribe_schedulers.execute()

    def button_reg_close(self):
        """Close Registration"""
        self.ensure_one()
        if self.state in ("cancel", "absent"):
            return
        today = fields.Datetime.now()
        if self.date_begin <= today and self.shift_id.state in ["confirm", "entry"]:
            self.write(
                {
                    "state": "done",
                    "date_closed": today,
                }
            )
        elif self.shift_id.state == "draft":
            raise UserError(
                self.env._(
                    "You must wait the event confirmation " "before doing this action."
                )
            )
        else:
            raise UserError(
                self.env._(
                    "You must wait the event starting " "day before doing this action."
                )
            )

    def button_reg_cancel(self):
        self.update({"state": "cancel"})

    @api.onchange("shift_id")
    def onchange_shift_id(self):
        FTOP_product = self.env.ref("coop_shift.product_product_shift_ftop")
        for reg in self:
            reg.shift_ticket_id = reg.shift_id.shift_ticket_ids.filtered(
                lambda t: t.product_id == FTOP_product
            )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("template_created", False):
                shift_ticket_id = vals.get("shift_ticket_id", False)
                shift_ticket = self.env["shift.ticket"].browse(shift_ticket_id)
                if (
                    shift_ticket
                    and shift_ticket.shift_type != "standard"
                    and shift_ticket.seats_max
                    and shift_ticket.seats_available <= 0
                ):
                    raise UserError(
                        self.env._("No more available seats for this ticket")
                    )
        regs = super().create(vals_list)
        for reg in regs:
            if reg.shift_id.state == "confirm":
                reg.confirm_registration()
                # Restore the state
                if reg.tmpl_reg_line_id and reg.state != reg.tmpl_reg_line_id.state:
                    reg.state = reg.tmpl_reg_line_id.state
        return regs

    @api.constrains("event_ticket_id", "state")
    def _check_ticket_seats_limit(self):
        return True
