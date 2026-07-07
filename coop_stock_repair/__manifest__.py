# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.fr/>)
# Copyright (C) 2020-Today: Druidoo (<https://www.druidoo.io>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html


{
    "name": "Coop - Stock Repair",
    "version": "18.0.1.0.0",
    "category": "Custom",
    "summary": "Restrict repair button/field access on stock picking to stock users",
    "author": "La Louve, Druidoo",
    "website": "https://github.com/AwesomeFoodCoops/odoo-production",
    "license": "AGPL-3",
    "depends": [
        "stock",
        "repair",
    ],
    "data": [
        "views/stock_picking_view.xml",
    ],
    "installable": True,
}
