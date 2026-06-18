{
    "name": "Coop PoS Access Control Buttons",
    "version": "18.0.1.0.0",
    "category": "Custom",
    "author": "Trobz, La Louve",
    "website": "https://github.com/AwesomeFoodCoops/odoo-production",
    "license": "LGPL-3",
    "depends": [
        "point_of_sale",
    ],
    "data": [
        "security/res_groups.xml",
        "security/ir.model.access.csv",
    ],
    "assets": {
        "point_of_sale._assets_pos": [
            "coop_pos_access/static/src/js/control_buttons.esm.js",
            "coop_pos_access/static/src/xml/control_buttons.xml",
        ],
    },
    "installable": True,
}
