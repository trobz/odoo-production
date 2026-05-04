# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Website Category Publish",
    "version": "18.0.1.0.0",
    "author": "Trobz, La Louve",
    "license": "AGPL-3",
    "category": "Website",
    "website": "https://github.com/AwesomeFoodCoops/odoo-production",
    "summary": "Allow user to publish/unpublish product by its category",
    "depends": [
        "website_sale",
    ],
    "data": [
        "views/product_public_category_views.xml",
        "views/website_sale_templates.xml",
    ],
    "application": False,
    "installable": True,
}
