# Copyright (C) Nguyen Minh Chien (chien@trobz.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Makeup Shift for Standard Member",
    "version": "18.0.1.0.0",
    "category": "Tools",
    "summary": """""",
    "author": "Trobz, La Louve",
    "website": "https://github.com/AwesomeFoodCoops/odoo-production",
    "license": "AGPL-3",
    "depends": [
        "coop_memberspace",
    ],
    "data": [
        "views/res_config_view.xml",
        "views/my_work.xml",
        "views/my_work_makeup_shift.xml",
    ],
    "demo": [],
    "assets": {
        "web.assets_frontend": [
            "coop_membership_makeup_shift/static/src/js/programmer_makeup_shift.esm.js",
        ],
    },
}
