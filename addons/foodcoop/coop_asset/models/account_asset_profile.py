from odoo import fields, models


class AccountAssetProfile(models.Model):
    _inherit = "account.asset.profile"

    journal_id = fields.Many2one(domain="[('company_id', '=', company_id)]")
