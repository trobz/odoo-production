from odoo import api, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.depends("name", "ref")
    @api.depends_context("partner_display_only_ref")
    def _compute_display_name(self):
        if not self.env.context.get("partner_display_only_ref"):
            return super()._compute_display_name()
        for partner in self:
            partner.display_name = partner.ref or partner.name
