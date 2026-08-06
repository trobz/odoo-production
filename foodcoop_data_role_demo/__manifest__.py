{
    "name": "Demo Roles for Foodcoop",
    "version": "18.0.1.0.0",
    "category": "Trobz Standard Modules",
    "author": "Trobz, La Louve",
    "website": "https://github.com/AwesomeFoodCoops/odoo-production",
    "license": "AGPL-3",
    "pre_init_hook": "pre_init_hook",
    "post_init_hook": "post_init_hook",
    "depends": [
        "foodcoop_data_role",
    ],
    "data": [
        "data/res_users.xml",
    ],
    "installable": True,
    "application": False,
}
