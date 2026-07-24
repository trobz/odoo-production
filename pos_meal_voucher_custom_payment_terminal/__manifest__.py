# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Point Of Sale - Meal Voucher: Glue to Payment Terminal",
    "summary": "This module is glue module between Meal Voucher and Payment Terminal",
    "version": "18.0.1.0.0",
    "category": "Point of Sale",
    "author": "Trobz, La Louve",
    "website": "https://github.com/AwesomeFoodCoops/odoo-production",
    "license": "AGPL-3",
    "depends": ["pos_meal_voucher_custom", "pos_payment_terminal"],
    "assets": {
        "point_of_sale._assets_pos": [
            "pos_meal_voucher_custom_payment_terminal/static/src/js/payment_screen.esm.js",
            "pos_meal_voucher_custom_payment_terminal/static/src/js/payment_terminal.esm.js",
        ],
    },
    "installable": True,
    "auto_install": True,
}
