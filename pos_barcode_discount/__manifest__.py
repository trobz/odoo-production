# Copyright (C) 2025-Today: Trobz (<http://www.trobz.com/>)

{
    "name": "POS Barcode Discount",
    "version": "18.0.1.0.0",
    "category": "Point Of Sale",
    "summary": "Search Products",
    "author": "Trobz, La Louve",
    "website": "https://github.com/AwesomeFoodCoops/odoo-production",
    "license": "AGPL-3",
    "depends": ["point_of_sale"],
    "data": [
        "data/default_barcode_patterns.xml",
        "views/res_config_settings_views.xml",
    ],
    "assets": {
        "point_of_sale._assets_pos": [
            "pos_barcode_discount/static/src/js/screens.esm.js",
        ]
    },
    "installable": True,
}
