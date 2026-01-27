# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Point of Sale - Quick Logout",
    "version": "18.0.1.0.0",
    "category": "Sales/Point Of Sale",
    "summary": "Allow PoS user to logout quickly after user changed",
    "license": "AGPL-3",
    "author": "La Louve, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/pos",
    "depends": ["point_of_sale"],
    "assets": {
        "point_of_sale._assets_pos": [
            "pos_quick_logout/static/src/js/pos_quick_logout.esm.js",
            "pos_quick_logout/static/src/xml/pos_quick_logout.xml",
        ],
    },
    "installable": True,
}
