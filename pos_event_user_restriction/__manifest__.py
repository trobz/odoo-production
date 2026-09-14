# Copyright 2026 Trobz
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "POS Event - Restricted Users Access",
    "summary": "Grant restricted POS users the access rights required to "
    "sell event tickets from the Point of Sale",
    "version": "18.0.1.0.0",
    "development_status": "Beta",
    "category": "Point of Sale",
    "author": "Trobz, La Louve",
    "website": "https://github.com/AwesomeFoodCoops/odoo-production",
    "license": "LGPL-3",
    "depends": [
        "pos_event",
        "pos_user_restriction",
    ],
    "data": [
        "security/ir.model.access.csv",
    ],
    "installable": True,
    "auto_install": True,
}
