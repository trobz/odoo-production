# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields

class ResCompany(models.Model):
    _inherit = 'res.company'

    prevent_signup_email = fields.Boolean(default=True)
