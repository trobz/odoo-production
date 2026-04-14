# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    show_advance_service = fields.Boolean(
        string="Show schedule an advance service", default=True
    )
