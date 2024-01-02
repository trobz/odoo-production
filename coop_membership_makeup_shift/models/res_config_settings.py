# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models, fields, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    shift_makeup = fields.Boolean(
        related="company_id.shift_makeup",
        readonly=False,
    )
