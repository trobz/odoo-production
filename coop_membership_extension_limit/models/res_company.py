# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    member_extension_limit = fields.Boolean(default=True)
    member_extension_limit_count = fields.Integer(default=6)
    member_extension_limit_type_ids = fields.Many2many(
        "shift.extension.type",
        "res_company_extension_type",
        "company_id",
        "extension_type_id",
        string="Extension Types",
    )
