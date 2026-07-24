# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{
    "name": "Auth Sigup Email",
    "version": "18.0.1.0.0",
    "category": "Custom",
    "summary": "Configure to prevent sending signup email",
    "author": "Trobz, La Louve",
    "website": "https://github.com/AwesomeFoodCoops/odoo-production",
    "license": "AGPL-3",
    "depends": ["auth_signup"],
    "data": [
        "views/res_config_view.xml",
    ],
    "installable": True,
}
