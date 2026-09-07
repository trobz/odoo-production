# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Point of Sale Payment Credit > Require Manager PIN",
    "version": "18.0.1.0.0",
    "summary": "Require manager PIN to validate orders with credit payment",
    "category": "Point Of Sale",
    "author": "Trobz, La Louve",
    "website": "https://github.com/AwesomeFoodCoops/odoo-production",
    "license": "AGPL-3",
    "depends": [
        "pos_payment_credit",
    ],
    "data": [
        "views/res_users_views.xml",
    ],
    "assets": {
        "point_of_sale._assets_pos": [
            "pos_payment_credit_pin/static/src/**/*",
        ],
    },
    "installable": True,
}
