# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Bundle: Lalouve',
    'version': '18.0.1.0.0',
    'author': 'Trobz',
    'license': 'AGPL-3',
    'category': 'Bundle',
    'website': 'http://www.trobz.com',
    'depends': [
        # oca/stock-logistics-workflow
        "scrap_reason_mandatory",

        # oca/stock-logistics-barcode
        "barcodes_generator_product",
        "barcodes_generator_partner",
    ],
    'installable': True,
}
