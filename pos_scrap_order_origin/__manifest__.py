# Copyright (C) Trobz (<https://trobz.com/>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "POS Scrap Order Origin",
    "version": "18.0.1.0.1",
    "category": "Point Of Sale",
    "summary": "Create scrap order from POS screen with Reason Tag",
    "author": "Trobz, La Louve",
    "website": "https://github.com/AwesomeFoodCoops/odoo-production",
    "license": "AGPL-3",
    "depends": ["pos_scrap_order"],
    "data": [
        "security/ir.model.access.csv",
        "views/pos_config.xml",
        "views/stock_scrap_reason_tag_views.xml",
    ],
    "assets": {
        "point_of_sale._assets_pos": [
            "pos_scrap_order_origin/static/src/scss/**/*",
            "pos_scrap_order_origin/static/src/app/**/*",
        ]
    },
    "auto_install": True,
    "installable": True,
}
