from datetime import datetime, timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.osv import expression


class ShiftRegistration(models.Model):
    _inherit = "shift.registration"

    exchange_replaced_reg_id = fields.Many2one(
        "shift.registration",
        "Exchange Registration Replaced",
        required=False,
        help="The old shift registration of the member before exchange",
    )
    exchange_replacing_reg_id = fields.Many2one(
        "shift.registration",
        "Exchange Registration Replacing",
        required=False,
        help="The new shift registration of the member after exchange",
    )

    @api.model_create_multi
    def create(self, vals_list):
        # To check constrains limit of registration in module coop_membership
        return super(ShiftRegistration, self.with_context(check_limit=True)).create(
            vals_list
        )

    @api.model
    def get_coordinators(self, shift_regis_id=None, get_alias_coordinator=False):
        # Function return name of the coordinators with format:
        #   A, B, C, D

        # @param shift_id: Use to call function in js.
        shift = (
            shift_regis_id
            and self.browse(shift_regis_id)
            and self.browse(shift_regis_id).shift_id
            or self.shift_id
        )
        coordinators = shift.user_ids and shift.user_ids.mapped("name") or []

        # Get alias coordinator
        alias_coordinator = self.env["memberspace.alias"].search(
            [
                ("shift_id", "=", shift.shift_template_id.id),
                ("type", "=", "coordinator"),
            ],
            limit=1,
        )
        alias_coordinator = (
            alias_coordinator.alias_id.display_name if alias_coordinator else ""
        )
        coordinators = ", ".join(coordinators) if coordinators else ""
        if get_alias_coordinator:
            return coordinators, alias_coordinator
        return coordinators

    @api.model
    def create_proposal(self, src_registration_id, des_registration_id, src_shift_id):
        if not ((src_registration_id or src_shift_id) and des_registration_id):
            raise UserError(
                self.env._(
                    "Source Shift Registration and "
                    + "Destination Shift Registration are require."
                )
            )
        if src_registration_id == des_registration_id:
            raise UserError(
                self.env._(
                    "Source Shift Registration and "
                    + "Destination Shift Registration must be different."
                )
            )
        proposal = self.env["proposal"].create(
            {
                "src_shift_id": src_shift_id,
                "src_registration_id": src_registration_id,
                "des_registration_id": des_registration_id,
                "state": "in_progress",
            }
        )
        user_partner = self.env.user.partner_id
        proposal.sudo().with_context(user_partner=user_partner).do_proposal()

    def remove_shift_regis_from_market(self):
        for record in self:
            proposals = self.env["proposal"].search(
                [
                    "|",
                    ("src_registration_id", "=", record.id),
                    ("des_registration_id", "=", record.id),
                ]
            )
            if any(proposal.state == "accept" for proposal in proposals):
                raise UserError(
                    self.env._("Your exchange was done, you cannot remove it.")
                )
            proposals.filtered(lambda r: r.state == "in_progress").write(
                {"state": "cancel"}
            )
            exchange_state = "draft"
            if record.exchange_replaced_reg_id:
                exchange_state = "replacing"
            record.write({"exchange_state": exchange_state})

    def add_shift_regis_to_market(self):
        for record in self:
            if not record.check_exchangable():
                icp_sudo = self.env["ir.config_parameter"].sudo()
                shift_exchange_duration = int(
                    icp_sudo.get_param("coop.shift.shift_exchange_duration", 24)
                )
                return {
                    "code": 0,
                    "msg": self.env._(
                        "You cannot propose to change the shift within"
                        " %s hours before the beginning of the shift.",
                        shift_exchange_duration,
                    ),
                }
            record.write(
                {
                    "exchange_state": "in_progress",
                    "exchange_replacing_reg_id": False,
                }
            )
        return {
            "code": 1,
        }

    def shifts_to_proposal(self):
        user = self.env.user
        partner = user.partner_id
        self.ensure_one()
        shifts = self.search(
            [
                ("partner_id", "=", partner.id),
                ("state", "!=", "cancel"),
                ("exchange_state", "=", "in_progress"),
                ("exchange_replacing_reg_id", "=", False),
                (
                    "date_begin",
                    ">=",
                    datetime.now(),
                ),
            ],
            order="date_begin",
        )
        rs = []
        for shift in shifts:
            exist_proposal = self.env["proposal"].search(
                [
                    ("state", "not in", ["cancel", "refuse", "accept"]),
                    "|",
                    "&",
                    ("src_registration_id", "=", self.id),
                    ("des_registration_id", "=", shift.id),
                    "&",
                    ("src_registration_id", "=", shift.id),
                    ("des_registration_id", "=", self.id),
                ],
                limit=1,
            )
            if not exist_proposal:
                date_begin = user.get_time_by_user_lang(
                    shift.date_begin,
                    ["%A, %d %B %Hh%M", "%HH%M"],
                    lang=user.lang + ".utf8",
                )
                rs.append(
                    {
                        "id": shift.id,
                        "date": date_begin[0],
                        "hour": date_begin[1],
                    }
                )
        return rs

    @api.model
    def shifts_to_confirm(self, src_registration_id, des_registration_id, src_shift_id):
        user = self.env.user
        src_shift = dest_shift = {}
        datas = []
        if src_shift_id:
            src_shift = self.env["shift.shift"].browse(src_shift_id)
        if not src_shift and src_registration_id:
            src_registration = self.env["shift.registration"].browse(
                src_registration_id
            )
            if src_registration:
                src_shift = src_registration.shift_id
        if des_registration_id:
            des_registration = self.env["shift.registration"].browse(
                des_registration_id
            )
            if des_registration:
                dest_shift = des_registration.shift_id
        if src_shift and dest_shift:
            for shift in [src_shift, dest_shift]:
                date_begin = user.get_time_by_user_lang(
                    shift.date_begin,
                    ["%A, %d %B %Hh%M", "%HH%M"],
                    lang=user.lang + ".utf8",
                )
                datas.append(
                    {
                        "id": shift.id,
                        "date": date_begin[0],
                        "hour": date_begin[1],
                    }
                )
        if datas:
            msg = self.env._(
                "You are about to cancel your participation to shift %s "
                "and replace it with a participation to shift %s. "
                "Are you sure that you want to do them?",
                datas[1]["date"],
                datas[0]["date"],
            )
            return 1, msg
        else:
            msg = self.env._("No shift is selected")
        return 0, msg

    def check_exchangable(self):
        self.ensure_one()
        icp_sudo = self.env["ir.config_parameter"].sudo()
        shift_exchange_duration = int(
            icp_sudo.get_param("coop.shift.shift_exchange_duration", 24)
        )
        date_begin = self.date_begin - timedelta(hours=shift_exchange_duration)
        if date_begin < fields.Datetime.now():
            return False
        return True

    def check_cancellable_ftop_shift(self):
        self.ensure_one()
        icp_sudo = self.env["ir.config_parameter"].sudo()
        duration = int(
            icp_sudo.get_param("coop_memberspace.ftop_shift_cancellation_duration", 24)
        )
        date_begin = self.date_begin - timedelta(hours=duration)
        if date_begin < fields.Datetime.now():
            return False
        return True

    def check_cancel_ftop_shift(self):
        for record in self:
            if not record.check_cancellable_ftop_shift():
                icp_sudo = self.env["ir.config_parameter"].sudo()
                duration = int(
                    icp_sudo.get_param(
                        "coop_memberspace.ftop_shift_cancellation_duration", 24
                    )
                )
                return {
                    "code": 0,
                    "msg": self.env._(
                        "You cannot cancel the shift within"
                        " %s hours before the beginning of the shift",
                        duration,
                    ),
                }
        return {
            "code": 1,
            "data": {
                "msg": self.env._(
                    "You are about to cancel your participation to the shift"
                ),
                "confirm_msg": self.env._("Are you sure that you want to do it?"),
                "confirm_btn_label": self.env._("Confirm"),
            },
        }

    def do_cancel_ftop_shift(self):
        mail_template = self.env.ref("coop_memberspace.shift_registration_cancel_email")
        for registration in self:
            if registration.check_cancellable_ftop_shift():
                registration.button_reg_cancel()
                mail_template.send_mail(registration.id)
        return True

    @api.model
    def get_upcoming(self, partner, args=None):
        if args is None:
            args = []
        args += [
            ("partner_id", "=", partner.id),
            ("state", "not in", ["cancel"]),
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

    def get_extra_domain_on_market(self, args, check_replacing=True):
        args2 = [
            ("state", "!=", "cancel"),
            ("exchange_state", "=", "in_progress"),
        ]
        if check_replacing:
            args2.append(("exchange_replacing_reg_id", "=", False))
        return expression.AND([args, args2])

    def get_my_next_shift_headers(self):
        """Return column definitions for the 'my next shift' table.

        Each entry is a dict with:
          - key (str): column identifier,
            used as the name and data-col attributes on <td>/<th>
          - label (str): displayed column header
          - css_class (str, optional): CSS class on the <th>

        Override this in an inheriting module to add, remove or rename columns.
        The 'exchange' column cell content is rendered by the sub-template
        ``coop_memberspace.my_next_shift_exchange_cell``.
        """
        return [
            {"key": "date", "label": self.env._("Date"), "css_class": ""},
            {"key": "hour", "label": self.env._("Hour"), "css_class": ""},
            {
                "key": "exchange",
                "label": self.env._("Exchange"),
                "css_class": "text-center",
            },
        ]

    def get_my_next_shift_row_data(self, user):
        """Return per-row data dict for the 'my next shift' table.

        Override this in an inheriting module to add extra keys that map to
        additional columns declared in ``get_my_next_shift_headers``.
        The 'exchange' key is intentionally absent here; that cell is rendered
        by the sub-template ``coop_memberspace.my_next_shift_exchange_cell``.
        """
        self.ensure_one()
        date_begin = user.get_time_by_user_lang(
            self.date_begin,
            ["%A, %d %B", "%HH%M"],
            lang=(self.env.lang or user.lang or "fr_FR") + ".utf8",
        )
        line_through = self.state in ("waiting", "cancel")
        return {
            "css_style": (
                "-webkit-text-decoration-line: line-through;"
                "text-decoration-line: line-through;"
            )
            if line_through
            else "",
            "date": date_begin[0] if date_begin else "",
            "hour": date_begin[1] if date_begin else "",
        }
