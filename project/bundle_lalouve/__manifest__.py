# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Bundle: Lalouve',
    'version': '18.0.1.0.0',
    'author': 'Trobz',
    'license': 'AGPL-3',
    'category': 'Bundle',
    'website': 'http://www.trobz.com',
    'depends': [
        # oca/account-invoicing
        "partner_account_move_line",

        # oca/bank-statement-import
        "account_statement_import_caisse_epargne",

        # oca/edi-framework
        "edi_purchase_diapar_oca",

        # oca/pos
        "pos_payment_change_account",
        "pos_payment_credit_amount",
        "pos_product_multi_barcode",

        # oca/stock-logistics-workflow
        "scrap_reason_mandatory",

        # oca/stock-logistics-barcode
        "barcodes_generator_product",
        "barcodes_generator_partner",

        # oca/web
        "web_responsive",
    ],
    'installable': True,
}
