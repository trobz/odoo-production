# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Point of Sale Payment Credit > Ticket",
    "version": "18.0.1.0.0",
    "category": "Point Of Sale",
    "author": "Trobz, La Louve",
    "license": "AGPL-3",
    "website": "https://github.com/AwesomeFoodCoops/odoo-production",
    "depends": [
        "pos_payment_credit",
    ],
    "assets": {
        "point_of_sale._assets_pos": [
            "pos_payment_credit_ticket/static/src/ticket_screen/ticket_screen.xml",
            "pos_payment_credit_ticket/static/src/order_receipt/order_receipt.xml",
            "pos_payment_credit_ticket/static/src/order_receipt/pos_order.esm.js",
        ],
    },
    "installable": True,
}
