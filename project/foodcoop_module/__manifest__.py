{
    "name": "Project Foodcoop Installer",
    "version": "18.0.1.0.0",
    "category": "Trobz Standard Modules",
    "summary": "Installer of the Foodcoop system",
    "author": "Trobz, La Louve",
    "website": "https://github.com/AwesomeFoodCoops/odoo-production",
    "depends": [
        "auth_signup",
        "base_user_role",
    ],
    "data": [
        "security/res_groups.xml",
        "security/ir.model.access.csv",
        "menu/admin_menu.xml",
        "views/res_users_views.xml",
    ],
    "installable": True,
    "application": True,
    "license": "AGPL-3",
}
