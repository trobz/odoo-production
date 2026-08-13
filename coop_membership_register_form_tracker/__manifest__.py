# Copyright (C) 2025-Today: Trobz (<https://trobz.com/>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Track Source from Membership Registration Form",
    "version": "18.0.1.0.0",
    "category": "Custom",
    "summary": "Track UTM source from membership discovery meeting registration form",
    "author": "Trobz, La Louve",
    "website": "https://github.com/AwesomeFoodCoops/odoo-production",
    "license": "AGPL-3",
    "depends": ["coop_membership", "utm"],
    "data": [
        "security/ir.model.access.csv",
        "views/res_partner_view.xml",
        "views/utm.xml",
        "views/web_templates.xml",
    ],
    "installable": True,
}
