# Copyright (C) Nguyen Minh Chien (chien@trobz.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Pos Scrap Order",
    "version": "18.0.1.0.0",
    "category": "Point Of Sale",
    "summary": """Create scrap order from POS screen""",
    "author": "Trobz, La Louve",
    "website": "https://github.com/AwesomeFoodCoops/odoo-production",
    "license": "AGPL-3",
    "depends": ["point_of_sale", "stock"],
    "data": [
        "security/ir.model.access.csv",
        "views/pos_config.xml",
    ],
    "installable": True,
    "assets": {
        "point_of_sale._assets_pos": [
            "pos_scrap_order/static/src/css/**/*",
            "pos_scrap_order/static/src/app/**/*",
        ],
    },
}
