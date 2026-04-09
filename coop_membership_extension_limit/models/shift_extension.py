# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.exceptions import UserError


class ShiftExtension(models.Model):
    _inherit = "shift.extension"

    is_new = fields.Boolean(default=True, copy=False)

    @api.model_create_multi
    def create(self, vals_list):
        extensions = super().create(vals_list)
        extensions._check_create_permission()
        return extensions

    def write(self, vals):
        res = super().write(vals)
        self._check_create_permission()
        return res

    def _check_create_permission(self):
        company = self.env.user.company_id
        if (
            not company.member_extension_limit
            or not company.member_extension_limit_type_ids
        ):
            return
        if self.env.user.has_group("coop_shift.group_shift_manager"):
            return
        partners = (
            self.filtered("is_new")
            .mapped("partner_id")
            .filtered(
                lambda partner: partner.cooperative_state
                in ("alert", "suspended", "delay")
            )
        )
        if not partners:
            return
        args = [
            ("partner_id", "in", partners.ids),
            ("is_new", "=", True),
            ("type_id", "in", company.member_extension_limit_type_ids.ids),
        ]
        raw_data = self.read_group(args, ["partner_id"], ["partner_id"])
        result = {
            data["partner_id"][0]: (data["partner_id_count"]) for data in raw_data
        }
        for partner in partners:
            extension_count = result.get(partner.id, 0)
            if extension_count > company.member_extension_limit_count:
                raise UserError(
                    self.env._(
                        "This member has received %s consecutive extensions, "
                        "which is the maximum. They cannot benefit from any additional "
                        "ones until their make-up sessions have been completed.",
                        company.member_extension_limit_count,
                    )
                )
            elif extension_count == company.member_extension_limit_count - 1:
                self._send_warn_limit_email(partner)

    def _send_warn_limit_email(self, partner):
        mail_template = self.env.ref(
            "coop_membership_extension_limit.email_extension_limited",
            raise_if_not_found=False,
        )
        if not mail_template:
            return
        mail_template.send_mail(partner.id, force_send=False)
