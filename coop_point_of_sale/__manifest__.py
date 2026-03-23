# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Coop - Point of Sale Custom views",
    "version": "18.0.1.0.0",
    "category": "Custom",
    "summary": """
        Customize Point of Sale Display
        Custom Barcode Rules for Coop article weight and price.
    """,
    "author": "La Louve, Druidoo",
    "website": "https://github.com/AwesomeFoodCoops/odoo-production",
    "license": "AGPL-3",
    "depends": [
        "point_of_sale",
        "pos_price_to_weight",
        "coop_membership",
        "pos_transfer_account",
        "pos_order_remove_line",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/barcode_rule.xml",
        "views/view_pos_order.xml",
        "views/view_pos_session.xml",
        "views/view_pos_order_line.xml",
        "views/view_pos_config_settings.xml",
        "views/view_pos_category.xml",
        "views/view_product_template.xml",
    ],
    "assets": {
        "point_of_sale._assets_pos": [
            "coop_point_of_sale/static/src/overrides/components/**/*",
            "coop_point_of_sale/static/src/overrides/screens/**/*",
        ],
        "web.assets_tests": [
            "coop_point_of_sale/static/tests/tours/**/*",
        ],
    },
    "installable": True,
}
