{
    "name": "Coop PoS Custom",
    "version": "18.0.1.0.0",
    "category": "Custom",
    "author": "Trobz, La Louve",
    "website": "https://github.com/AwesomeFoodCoops/odoo-production",
    "license": "LGPL-3",
    "depends": [
        "point_of_sale",
        "pos_sale",
        "coop_point_of_sale",
        "purchase_compute_order",
        "pos_order_return",
    ],
    "data": [
        "security/res_groups.xml",
        "views/purchase_compute_order_views.xml",
    ],
    "assets": {
        "point_of_sale._assets_pos": [
            "coop_pos_custom/static/src/js/control_buttons.esm.js",
            "coop_pos_custom/static/src/js/partner_list.esm.js",
            "coop_pos_custom/static/src/js/res_partner.esm.js",
            "coop_pos_custom/static/src/js/product_product.esm.js",
            "coop_pos_custom/static/src/js/product_screen.esm.js",
            "coop_pos_custom/static/src/xml/control_buttons.xml",
        ],
    },
    "installable": True,
}
