# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{
    "name": "Coop Membership Extension Limit",
    "version": "18.0.1.0.0",
    "category": "Custom",
    "summary": "Limit the number of extension for each member",
    "author": "La Louve, Trobz",
    "website": "https://github.com/AwesomeFoodCoops/odoo-production",
    "license": "AGPL-3",
    "depends": ["coop_membership", "coop_badge_reader"],
    "data": [
        "views/res_config_view.xml",
        "views/view_shift_extension.xml",
        "data/email_template_data.xml",
    ],
    "demo": [],
    "installable": True,
    "pre_init_hook": "pre_init_hook",
}
