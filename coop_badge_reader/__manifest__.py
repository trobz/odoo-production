# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# Copyright (C) 2020-Today: Druidoo (<https://www.druidoo.io>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{
    "name": "Coop Badge Reader",
    "version": "18.0.1.0.0",
    "category": "Custom",
    "summary": "Provide light Ionic Apps to read user Badge",
    "author": "La Louve, Druidoo",
    "website": "https://github.com/AwesomeFoodCoops/odoo-production",
    "license": "AGPL-3",
    "depends": ["base", "coop_shift", "coop_membership"],
    "data": [
        "data/mail_template.xml",
        "security/ir_module_category.xml",
        "security/res_groups.xml",
        "security/ir.model.access.csv",
        "views/view_res_partner.xml",
        "views/view_res_partner_alert.xml",
        "views/view_res_partner_move.xml",
        "views/view_shift_extension_type.xml",
        "views/action.xml",
        "views/menu.xml",
        "views/badge_reader_assets_index.xml",
    ],
    "demo": [
        "demo/res_partner.xml",
        "demo/res_users.xml",
        "demo/res_groups.xml",
        "demo/res_partner_move.xml",
        "demo/res_partner_alert.xml",
        "demo/shift_extension_type.xml",
    ],
    "installable": True,
    "assets": {
        "web.assets_backend": [
            "coop_badge_reader/static/src/app/**/*",
            "coop_badge_reader/static/src/components/**/*",
        ],
        "web.assets_unit_tests": [
            "coop_badge_reader/static/src/tests/**/*",
        ],
        "coop_badge_reader.assets_prod": [
            ("include", "web._assets_helpers"),
            ("include", "web._assets_primary_variables"),
            ("include", "web._assets_frontend_helpers"),
            "web/static/lib/jquery/jquery.js",
            "web/static/src/scss/pre_variables.scss",
            "web/static/lib/bootstrap/scss/_variables.scss",
            "web/static/lib/bootstrap/scss/_variables-dark.scss",
            "web/static/lib/bootstrap/scss/_maps.scss",
            ("include", "web._assets_bootstrap_frontend"),
            ("include", "web._assets_bootstrap_backend"),
            "/web/static/lib/odoo_ui_icons/*",
            "/web/static/lib/bootstrap/scss/_functions.scss",
            "/web/static/lib/bootstrap/scss/_mixins.scss",
            "/web/static/lib/bootstrap/scss/utilities/_api.scss",
            "web/static/src/libs/fontawesome/css/font-awesome.css",
            ("include", "web._assets_core"),
            # Badge Reader App and its components
            "coop_badge_reader/static/src/app/**/*",
            "coop_badge_reader/static/src/components/**/*",
        ],
    },
}
