# Copyright (C) 2017-Today: La Louve (<http://www.lalouve.net/>)
# @author: Julien Weste (julien.weste@akretion.com)
# Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Coop - Print Badge",
    "version": "18.0.1.0.0",
    "category": "Custom",
    "summary": "Print partner's badge",
    "author": "La Louve",
    "website": "https://github.com/AwesomeFoodCoops/odoo-production",
    "depends": [
        "coop_membership",
        "coop_capital_certificate",
    ],
    "data": [
        "security/res_groups.xml",
        "data/report_paperformat.xml",
        "data/res_company_data.xml",
        "views/view_res_partner.xml",
        "views/badge_to_print_views.xml",
        "views/res_config_settings_view.xml",
        "views/actions.xml",
        "views/menu.xml",
        "report/coop_print_badge_report.xml",
        "report/report_printbadge.xml",
    ],
    "demo": [
        "demo/res_partner.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "coop_print_badge/static/src/scss/badge_to_distribute.scss",
        ],
        "web.report_assets_common": [
            "coop_print_badge/static/src/css/badge.css",
        ],
        "web.report_assets_pdf": [
            "coop_print_badge/static/src/css/badge.css",
        ],
    },
    "license": "AGPL-3",
    "installable": True,
}
