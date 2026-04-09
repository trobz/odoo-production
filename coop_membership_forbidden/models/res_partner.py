# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class Partner(models.Model):
    _inherit = "res.partner"

    is_forbidden = fields.Boolean(string="Forbidden member")

    @api.depends("is_forbidden")
    def _compute_working_state(self):
        forbidden_partners = self.filtered("is_forbidden")
        for partner in forbidden_partners:
            partner.update({"working_state": "blocked"})
        return super(Partner, self - forbidden_partners)._compute_working_state()

    @api.depends("is_forbidden")
    def _compute_error_message(self):
        forbidden_partners = self.filtered("is_forbidden")
        for partner in forbidden_partners:
            partner.error_message = self.env._(
                "Interdit d'entrer dans le magasin. Veuillez contacter un salarié"
            )
        return super(Partner, self - forbidden_partners)._compute_error_message()
