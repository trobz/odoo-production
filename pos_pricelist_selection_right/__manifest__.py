{
    "name": "Point of Sale - Restrict Pricelists to Partner",
    "summary": "Restrict the pricelists to the partner"
    " displayed in the Point of Sale front-end UI",
    "version": "18.0.1.0.0",
    "category": "Point of Sale",
    "author": "La Louve, Trobz",
    "website": "https://github.com/AwesomeFoodCoops/odoo-production",
    "license": "AGPL-3",
    "depends": [
        "point_of_sale",
    ],
    "assets": {
        "point_of_sale._assets_pos": [
            "pos_pricelist_selection_right/static/src/**/*",
        ],
    },
    "installable": True,
}
