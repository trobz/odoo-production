# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Coop - Inventory Recurrent",
    "version": "18.0.1.1.0",
    "category": "stock",
    "author": "Trobz, La Louve",
    "website": "https://github.com/AwesomeFoodCoops/odoo-production",
    "license": "AGPL-3",
    "depends": [
        "coop_inventory",
    ],
    "data": [
        "security/ir.model.access.csv",
        "view/report_stockinventory_new.xml",
        "view/view_stock_inventory_category_group.xml",
        "wizards/view_stock_inventory_recurrent_wizard.xml",
        "wizards/view_stock_inventory_recurrent_report_wizard.xml",
    ],
}
