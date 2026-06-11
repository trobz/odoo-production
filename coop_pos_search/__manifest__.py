{
    "name": "Coop PoS Exact-match Search",
    "version": "18.0.1.0.0",
    "category": "Custom",
    "author": "Trobz, La Louve",
    "website": "https://github.com/AwesomeFoodCoops/odoo-production",
    "license": "LGPL-3",
    "depends": [
        "point_of_sale",
        "coop_point_of_sale",
    ],
    "assets": {
        "point_of_sale._assets_pos": [
            "coop_pos_search/static/src/js/product_product.esm.js",
            "coop_pos_search/static/src/js/product_screen.esm.js",
            "coop_pos_search/static/src/js/res_partner.esm.js",
            "coop_pos_search/static/src/js/partner_list.esm.js",
        ],
    },
    "installable": True,
}
