from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    export_wrong_reconciliation = fields.Boolean(
        help="Consider this journal to export wrong reconcilation entries"
    )
