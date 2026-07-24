# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Pos Access Right Customization",
    "summary": """
        Pos Access Right Customization.""",
    "version": "18.0.1.0.0",
    "license": "LGPL-3",
    "author": "Trobz, La Louve",
    "website": "https://github.com/AwesomeFoodCoops/odoo-production",
    "depends": ["pos_access_right"],
    "assets": {
        "point_of_sale._assets_pos": [
            "pos_access_right_custom/static/src/js/pos_access_right.esm.js",
        ],
    },
}
