{
    "name": "Data for Foodcoop in France",
    "version": "18.0.1.0.0",
    "category": "Trobz Standard Modules",
    "summary": "French-specific data for Foodcoop",
    "author": "Trobz, La Louve",
    "website": "https://github.com/AwesomeFoodCoops/odoo-production",
    "depends": [
        "coop_membership",
        "pos_payment_credit",
    ],
    "data": [
        "views/view_res_partner.xml",
    ],
    "license": "AGPL-3",
    "post_init_hook": "post_init_hook",
}
