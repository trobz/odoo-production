# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Point Of Sale - Meal Voucher: Glue to Payment Terminal",
    "summary": "This module is glue module between Meal Voucher and Payment Terminal",
    "version": "12.0.1.0.0",
    "category": "Point of Sale",
    "author": "Trobz",
    "website": "https://trobz.com",
    "license": "AGPL-3",
    "depends": [
        "pos_meal_voucher_custom",
        "pos_payment_terminal"
    ],
    "data": [
        "views/templates.xml",
    ],
    "installable": True,
    "auto_install": True,
}
