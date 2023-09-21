# Copyright (C) Nguyen Minh Chien (chien@trobz.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Pos Scrap Order Origin",
    "version": "12.0.1.0.0",
    "category": "Point Of Sale",
    "summary": """Create scrap order from POS screen with Origin""",
    "author": "Trobz",
    "website": "https://trobz.com",
    "license": "AGPL-3",
    "depends": [
        "pos_scrap_order",
        "stock_scrap_origin"
    ],
    "data": [
        "views/assets.xml",
        "views/pos_config.xml",
    ],
    "qweb": ["static/src/xml/screen.xml"],
    "auto_install": True,
}
