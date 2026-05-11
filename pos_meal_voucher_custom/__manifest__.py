# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Point Of Sale - Meal Voucher: customization",
    "summary": "Handle meal vouchers in Point of Sale: Set payment amount",
    "version": "18.0.1.0.0",
    "category": "Point of Sale",
    "author": "Trobz, La Louve",
    "website": "https://github.com/OCA/pos",
    "license": "AGPL-3",
    "depends": [
        "pos_meal_voucher",
    ],
    "assets": {
        "point_of_sale._assets_pos": [
            "pos_meal_voucher_custom/static/src/payment_screen/**/*",    
        ],
    },
    "installable": True,
}
