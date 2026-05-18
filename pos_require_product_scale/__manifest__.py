# Copyright 2019-2020 Coop IT Easy SCRLfs
# 	    Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Require Product To Be Scaled in POS",
    "version": "18.0.1.0.0",
    "author": "Trobz, La Louve",
    "website": "https://github.com/AwesomeFoodCoops/odoo-production",
    "license": "AGPL-3",
    "category": "Point of Sale",
    "summary": """
        A popup is shown if product need to weight with scale for one or more order
        lines when clicking on "Payment" button.
    """,
    "depends": [
        "point_of_sale",
    ],
    "data": [
        "views/pos_config.xml",
    ],
    "assets": {
        "point_of_sale._assets_pos": [
            "pos_require_product_scale/static/src/js/screens.esm.js",
        ],
        "web.assets_tests": [
            "pos_require_product_scale/static/tests/tours/pos_require_product_scale_tour.esm.js",
        ],
    },
    "installable": True,
}
