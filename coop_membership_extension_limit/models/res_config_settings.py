# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    member_extension_limit = fields.Boolean(
        related="company_id.member_extension_limit",
        readonly=False,
    )
    member_extension_limit_count = fields.Integer(
        related="company_id.member_extension_limit_count",
        readonly=False,
    )
    member_extension_limit_type_ids = fields.Many2many(
        related="company_id.member_extension_limit_type_ids",
        readonly=False,
    )
