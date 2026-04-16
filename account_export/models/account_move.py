from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    exported = fields.Boolean(default=False)
