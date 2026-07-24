# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    prevent_signup_email = fields.Boolean(
        related="company_id.prevent_signup_email",
        readonly=False,
    )
