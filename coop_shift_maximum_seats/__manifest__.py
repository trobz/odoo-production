# Copyright (C) Nguyen Minh Chien (chien@trobz.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Shift: Maximum Available Seats",
    "version": "18.0.1.0.0",
    "category": "Tools",
    "summary": "Policy to set the Maximum Available Seats for Shift and Shift Template",
    "author": "Trobz, La Louve",
    "website": "https://github.com/AwesomeFoodCoops/odoo-production",
    "license": "AGPL-3",
    "depends": [
        "coop_membership",
        "coop_memberspace",
    ],
    "data": [
        "views/shift_template_view.xml",
        "views/shift_shift_view.xml",
        "views/res_config_view.xml",
    ],
}
