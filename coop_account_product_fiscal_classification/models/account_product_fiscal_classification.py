from odoo import fields, models


class AccountProductFiscalClassification(models.Model):
    _inherit = "account.product.fiscal.classification"

    income_account_id = fields.Many2one("account.account")
    expense_account_id = fields.Many2one("account.account")
    # Make tax required
    sale_tax_ids = fields.Many2many(required=True)
    purchase_tax_ids = fields.Many2many(required=True)
