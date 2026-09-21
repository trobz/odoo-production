# Copyright (C) 2026-Today: La Louve (<http://www.lalouve.fr/>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html


{
    "name": "Coop Sale",
    "version": "18.0.1.0.0",
    "category": "Sales",
    "author": "La Louve, Trobz",
    "website": "https://github.com/AwesomeFoodCoops/odoo-production",
    "license": "AGPL-3",
    "depends": ["sale", "sale_timesheet", "product_print_category"],
    "data": [
        "views/sale_order_view.xml",
        "views/product_print_category_menu.xml",
        "views/product_template_views.xml",
    ],
    "installable": True,
}
