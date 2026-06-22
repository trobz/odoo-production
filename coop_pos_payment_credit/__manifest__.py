# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Coop POS Payment Credit",
    "version": "18.0.1.0.0",
    "category": "Point Of Sale",
    "author": "Trobz, La Louve",
    "website": "https://github.com/AwesomeFoodCoops/odoo-production",
    "license": "AGPL-3",
    "depends": [
        "pos_payment_credit",
    ],
    "assets": {
        "point_of_sale._assets_pos": [
            "coop_pos_payment_credit/static/src/xml/payment_lines.xml",
            "coop_pos_payment_credit/static/src/js/payment_screen.esm.js",
        ],
    },
    "installable": True,
}
