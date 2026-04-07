from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    property_account_receivable_software = fields.Char(
        "Account Receivable (Software)",
        size=17,
        help="Receivable account in your accounting software",
    )
    property_account_payable_software = fields.Char(
        "Account Payable (Software)",
        size=17,
        help="Payable account in your accounting software",
    )
