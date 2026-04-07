{
    "name": "Account Export",
    "summary": "Export account move lines for accounting software",
    "version": "18.0.1.0.0",
    "category": "Accounting & Finance",
    "author": "Druidoo, La Louve, Trobz",
    "website": "https://github.com/AwesomeFoodCoops/odoo-production",
    "license": "AGPL-3",
    "depends": [
        "base",
        "account",
        "mail",
        "uom",
        "report_xlsx_helper",
    ],
    "data": [
        "views/account_view.xml",
        "views/export_view.xml",
        "security/account_export_security.xml",
        "security/ir.model.access.csv",
        "views/res_partner_view.xml",
        "reports/account_export_xls.xml",
    ],
}
