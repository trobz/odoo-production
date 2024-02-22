# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models, fields, _


class Partner(models.Model):
    _inherit = 'res.partner'

    is_forbidden = fields.Boolean(string="Forbidden member")

    @api.onchange("is_forbidden")
    def onchange_is_forbidden(self):
        user = self.env.user
        if self.is_forbidden and not user.has_group(
                'coop_membership_forbidden.group_member_forbidden_manager'):
            self.is_forbidden = False

    @api.depends("is_forbidden")
    def _compute_working_state(self):
        super()._compute_working_state()
        partners = self.filtered("is_forbidden")
        partners.update({"working_state": "blocked"})

    @api.depends("is_forbidden")
    def _compute_error_message(self):
        records = self.filtered("is_forbidden")
        super(Partner, self-records)._compute_error_message()
        for record in records:
            record.error_message = _("Interdit d’entrée dans le magasin. Merci de contacter un salarié")
