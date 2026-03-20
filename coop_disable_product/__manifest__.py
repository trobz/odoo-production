# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.fr/>)
# @author: La Louve
# Copyright (C) 2020-Today: Druidoo (<https://www.druidoo.io>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html


{
    "name": "Coop Limit Creation of Product",
    "version": "18.0.1.0.0",
    "category": "Product",
    "author": "La Louve, Druidoo",
    "website": "https://github.com/AwesomeFoodCoops/odoo-production",
    "license": "AGPL-3",
    "depends": ["purchase", "account", "stock", "sale_management"],
    "data": [
        "views/account_move_views.xml",
        "views/view_purchase_order.xml",
        "views/view_sale_order.xml",
        "views/view_stock_picking.xml",
        "views/view_stock_move.xml",
    ],
    "installable": True,
}
