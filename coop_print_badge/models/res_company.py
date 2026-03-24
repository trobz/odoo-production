from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval


class ResCompany(models.Model):
    _inherit = "res.company"

    reprint_change_field_ids = fields.Many2many(
        "ir.model.fields",
        string="Fields trigger badge reprinting",
        domain=[("model_id.model", "=", "res.partner")],
        default=lambda self: self.get_trigger_badge_reprint_fields(),
    )

    @api.model
    def get_trigger_badge_reprint_fields(self):
        field_str = self.env['ir.config_parameter'].sudo().get_param(
            'reprint_change_field_ids', '[]')
        field_ids = safe_eval(field_str)
        if not field_ids:
            # Default fields to trigger badge reprinting
            field_ids = self.env['ir.model.fields'].search(
                [
                    ('model_id.model', '=', 'res.partner'),
                    ('name', 'in', ['image_1920', 'name']),
                ]
            ).ids
        return field_ids
