# Copyright (C) 2016-Today: La Louve (<http://www.cooplalouve.fr/>)
# @author: La Louve
# Copyright (C) 2020-Today: Druidoo (<https://www.druidoo.io>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html
{
    "name": "Coop Purchase",
    "version": "18.0.1.0.0",
    "category": "Purchase",
    "summary": "Coop Purchase",
    "author": "La Louve",
    "website": "https://github.com/AwesomeFoodCoops/odoo-production",
    "depends": [
        "base",
        "account",
        "product",
        "purchase",
        "purchase_compute_order",
        "purchase_package_qty",
        "stock",
        "coop_product_coefficient",
    ],
    "license": "AGPL-3",
    "data": [
        "security/res_group.xml",
        "security/ir.model.access.csv",
        "data/ir_actions_server.xml",
        "data/ir_exports_purchase_order_line.xml",
        "report/purchase_order_templates.xml",
        "report/purchase_quotation_templates.xml",
        "wizard/supplier_info_update.xml",
        "views/purchase_view.xml",
        "views/res_config_settings_view.xml",
        "views/account_move_views.xml",
        "views/product_supplierinfo_view.xml",
        "views/stock_picking_view.xml",
        "views/stock_quant_views.xml",
        "views/res_partner_view.xml",
        "views/purchase_compute_order_views.xml",
    ],
    "installable": True,
}
