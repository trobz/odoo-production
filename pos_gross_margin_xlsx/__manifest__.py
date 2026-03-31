{
    "name": "POS Gross Margin Report",
    "version": "18.0.1.0.0",
    "category": "Point Of Sale",
    "summary": "Point Of Sale Gross Margin Report",
    "author": "Trobz, La Louve",
    "website": "https://github.com/AwesomeFoodCoops/odoo-production",
    "license": "AGPL-3",
    "depends": [
        "coop_point_of_sale",
        "report_xlsx",
    ],
    "data": [
        "security/ir.model.access.csv",
        "report/report_gross_margin_xlsx.xml",
        "wizard/gross_margin_xlsx_wizard.xml",
    ],
    "installable": True,
}
