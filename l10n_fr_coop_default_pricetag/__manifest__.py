# Copyright (C) 2020-Today: Druidoo (<https://www.druidoo.io>)
{
    "name": "l10n fr Coop Default Price Tag",
    "version": "18.0.1.0.0",
    "category": "Product",
    "author": "La Louve, Druidoo",
    "website": "https://github.com/AwesomeFoodCoops/odoo-production",
    "license": "AGPL-3",
    "depends": [
        "l10n_fr_department",
        "coop_default_pricetag",
        "coop_membership",
    ],
    "data": [
        "views/view_product_template.xml",
        "views/view_res_partner.xml",
    ],
    "auto_install": True,
}
