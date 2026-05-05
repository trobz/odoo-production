# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class Website(models.Model):
    _inherit = "website"

    payment_term_id = fields.Many2one(
        "account.payment.term", string="Default Payment Term"
    )
