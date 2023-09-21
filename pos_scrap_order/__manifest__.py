# Copyright (C) Nguyen Minh Chien (chien@trobz.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Pos Scrap Order",
    "version": "12.0.1.0.0",
    "category": "Point Of Sale",
    "summary": """Create scrap order from POS screen""",
    "author": "Trobz",
    "website": "https://trobz.com",
    "license": "AGPL-3",
    "depends": [
        "point_of_sale",
        "stock"
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/assets.xml",
        "views/pos_config.xml",
    ],
    'qweb': ['static/src/xml/screen.xml'],
}
