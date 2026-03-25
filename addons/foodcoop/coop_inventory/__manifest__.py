# Copyright (C) 2017 - Today: La Louve
# @author: Julien WESTE
# Copyright (C) 2020-Today: Druidoo (<https://www.druidoo.io>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Coop - Inventory",
    "version": "18.0.1.0.1",
    "category": "stock",
    "author": "La Louve",
    "website": "https://github.com/AwesomeFoodCoops/odoo-production",
    "license": "AGPL-3",
    "depends": [
        "purchase_stock",
        "purchase_package_qty",
        "stock_inventory",
    ],
    "data": [
        "data/report_paperformat.xml",
        "report/report_stockinventory.xml",
        "view/view_stock_inventory.xml",
        "view/view_stock_picking.xml",
    ],
}
