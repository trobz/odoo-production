from odoo import api, fields, models


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
        image_field = self.env.ref("base.field_res_partner__image_1920")
        name_field = self.env.ref("base.field_res_partner__name")
        return [image_field.id, name_field.id]
