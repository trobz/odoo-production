# Copyright (C) 2012-Today GRAP (http://www.grap.coop)
# Copyright (C) 2020-Today: Druidoo (<https://www.druidoo.io>)
# @author Julien WESTE
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Coop Default Price Tag",
    "version": "18.0.1.1.0",
    "category": "Custom",
    "author": "GRAP, Akretion - Julien WESTE, Druidoo, La Louve",
    "website": "https://github.com/AwesomeFoodCoops/odoo-production",
    "license": "AGPL-3",
    "depends": [
        "product",
        "product_print_category",
        "base",
        "purchase_package_qty",
    ],
    "data": [
        "security/res_groups.xml",
        "security/ir.model.access.csv",
        "data/decimal_precision_data.xml",
        "data/ir_actions_report.xml",
        "data/report_paperformat.xml",
        "data/pricetag_model.xml",
        "data/product_label.xml",
        "report/coop_custom_product_report.xml",
        "report/report_pricetag.xml",
        "report/report_pricetag_vegetables.xml",
        "data/product_print_category.xml",
        "views/view_pricetag_model.xml",
        "views/view_product_print_category.xml",
        "views/view_product_label.xml",
        "views/view_product_product.xml",
        "views/view_product_template.xml",
    ],
    "demo": ["demo/product_print_category.xml"],
    "assets": {
        "web.report_assets_common": [
            "coop_default_pricetag/static/src/scss/*.scss",
        ],
    },
}
