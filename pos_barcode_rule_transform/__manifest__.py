# Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
# @author: Iván Todorovich
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Point of Sale - Barcode Rule Transform",
    "version": "18.0.1.0.0",
    "category": "Point Of Sale",
    "summary": "Transforms the value read in the barcode with a JS expression",
    "author": "Druidoo, Odoo Community Association (OCA), La Louve",
    "website": "https://github.com/AwesomeFoodCoops/odoo-production",
    "license": "AGPL-3",
    "depends": ["point_of_sale"],
    "data": ["views/barcode_rule.xml"],
    "demo": ["demo/demo.xml"],
    "assets": {
        "point_of_sale._assets_pos": [
            "pos_barcode_rule_transform/static/src/js/barcode.esm.js",
        ],
    },
    "installable": True,
}
