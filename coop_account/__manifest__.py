# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)

{
    "name": "Coop Account",
    "version": "18.0.1.0.0",
    "category": "Accounting",
    "summary": "Coop Account",
    "author": "La Louve, Druidoo, Odoo Community Association (OCA)",
    "website": "https://github.com/AwesomeFoodCoops/odoo-production",
    "license": "AGPL-3",
    "depends": [
        "account",
        "queue_job",
        "account_tax_balance",
        "account_reconcile_oca",
        "account_statement_base",
        "purchase_unreconciled",
        "barcodes_generator_partner",
    ],
    "data": [
        "security/ir.model.access.csv",
        "view/view_account_bank_statement.xml",
        "view/account_journal_view.xml",
        "view/view_account_move.xml",
        "view/view_account_move_line.xml",
        "view/view_account_payment.xml",
        "view/view_account_account.xml",
        "view/menu.xml",
        "wizard/view_bank_statement_line_reconcile_wizard.xml",
        "wizard/view_unmatch_bank_statement_wizard.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "coop_account/static/src/js/export_wrong_reconciliation_move_lines.esm.js",
        ],
    },
    "installable": True,
    "pre_init_hook": "pre_init_hook",
}
