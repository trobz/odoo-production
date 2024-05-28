# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models, fields, _
from odoo.exceptions import UserError


class ShiftExtension(models.Model):
    _inherit = 'shift.extension'

    is_new = fields.Boolean(default=True, copy=False)

    @api.model
    def create(self, vals):
        extension = super().create(vals)
        extension._check_create_permission()
        return extension

    def _check_create_permission(self):
        company = self.env.user.company_id
        if (not company.member_extension_limit or 
            not company.member_extension_limit_type_ids
        ):
            return
        if self.env.user.has_group("coop_shift.group_shift_manager"):
            return
        partners = self.filtered("is_new").mapped("partner_id").filtered(
            lambda p: p.cooperative_state in ("alert", "suspended", "delay")
        )
        if not partners:
            return
        args = [
            ("partner_id", "in", partners.ids),
            ("is_new", "=", True),
            ("type_id", "in", company.member_extension_limit_type_ids.ids)
        ]
        raw_data = self.read_group(
            args, ["partner_id"], ["partner_id"]
        )
        result = {
            data['partner_id'][0]: (
                data['partner_id_count']
            ) for data in raw_data
        }
        for partner in partners:
            extension_count = result.get(partner.id, 0)
            if extension_count > company.member_extension_limit_count:
                raise UserError(_("Ce membre a reçu %s extensions consécutives, le maximum."
                                  "Il ne peut en bénéficier d'aucune autre avant que ses "
                                  "rattrapages n'aient été effectués."
                                  ) % (
                                      company.member_extension_limit_count
                                ))
            elif extension_count == company.member_extension_limit_count - 1:
                self._send_warn_limit_email(partner)

    def _send_warn_limit_email(self, partner):
        mail_template = self.env.ref(
            "coop_membership_extension_limit.email_extension_limited",
            False
        )
        if not mail_template:
            return
        mail_template.send_mail(partner.id, force_send=False)
