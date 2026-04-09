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
        config_extensions = company.member_extension_limit_type_ids
        config_limit = company.member_extension_limit_count
        if not company.member_extension_limit or not config_extensions:
            return
        if self.env.user.has_group("coop_shift.group_shift_manager"):
            return
        checked_extensions = self.filtered(
            lambda ext: ext.is_new and ext.type_id in config_extensions
        )
        if not checked_extensions:
            return
        partners = checked_extensions.mapped("partner_id").filtered(
            lambda partner: partner.cooperative_state in ("alert", "suspended", "delay")
        )
        if not partners:
            return
        result = self._read_group_extension_type(config_extensions, partners)
        for extension in checked_extensions:
            partner = extension.partner_id
            extension_count = result.get(partner.id, 0)
            if extension_count > config_limit:
                raise UserError(
                    self.env._(
                        "This member has received %s consecutive extensions, "
                        "which is the maximum. They cannot benefit from any additional "
                        "ones until their make-up sessions have been completed.",
                        config_limit,
                    )
                )
            elif extension_count == config_limit - 1:
                self._send_warn_limit_email(partner)

    def _send_warn_limit_email(self, partner):
        mail_template = self.env.ref(
            "coop_membership_extension_limit.email_extension_limited",
            raise_if_not_found=False,
        )
        if not mail_template:
            return
        mail_template.send_mail(partner.id, force_send=False)

    def _read_group_extension_type(self, extension_types, partners):
        args = [
            ("partner_id", "in", partners.ids),
            ("is_new", "=", True),
            ("type_id", "in", extension_types.ids),
        ]
        raw_data = self.read_group(args, ["partner_id"], ["partner_id"])
        return {data["partner_id"][0]: (data["partner_id_count"]) for data in raw_data}
