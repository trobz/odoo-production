{
    "name": "Coop Produce",
    "version": "18.0.1.0.0",
    "category": "Warehouse",
    "summary": "Coop Produce",
    "author": "La Louve, Druidoo",
    "website": "https://github.com/AwesomeFoodCoops/odoo-production",
    "license": "AGPL-3",
    "depends": [
        "base",
        "product",
        "stock",
        "purchase",
        "purchase_package_qty",
        "stock_inventory",
    ],
    "data": [
        # DATA
        "security/ir.model.access.csv",
        "data/decimal_precision.xml",
        # VIEWS
        "views/product_views.xml",
        "views/stock_views.xml",
        "views/week_order_planning_view.xml",
        "wizard/show_product_history_view.xml",
        "wizard/stock_inventory_wizard.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "coop_produce/static/src/css/style.css",
        ],
    },
}
