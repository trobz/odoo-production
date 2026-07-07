{
    "name": "Roles for Foodcoop - POS Cashlogy",
    "version": "18.0.1.0.0",
    "category": "Trobz Standard Modules",
    "description": """
        Extends foodcoop_data_role with POS Automatic Cash Drawer (Cashlogy) access.
        Install only on coops using the Cashlogy cash drawer device.
    """,
    "author": "Trobz",
    "website": "https://github.com/AwesomeFoodCoops/odoo-production",
    "depends": [
        "foodcoop_data_role",
        "pos_automatic_cashdrawer_cashlogy",
    ],
    "data": [
        "data/res_users_role.xml",
    ],
    "installable": True,
    "application": False,
    "license": "AGPL-3",
}
