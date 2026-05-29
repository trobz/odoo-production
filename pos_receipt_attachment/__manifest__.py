# Copyright (C) Nguyen Minh Chien (chien@trobz.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


{
    "name": "Point of Sale - Attach Receipt to Backend",
    "summary": "Send receipt to backend as an attachment",
    "version": "18.0.1.0.1",
    "category": "Sales/Point Of Sale",
    "website": "https://github.com/AwesomeFoodCoops/odoo-production",
    "author": "Trobz, La Louve",
    "license": "AGPL-3",
    "depends": ["point_of_sale", "pos_ticket_send_by_mail"],
    "data": [
        "data/ir_cron.xml",
        "views/report_paperformat.xml",
        "views/report_receipt.xml",
    ],
    "assets": {
        "point_of_sale._assets_pos": [
            "pos_receipt_attachment/static/src/js/pos_store.esm.js",
            "pos_receipt_attachment/static/src/js/receipt_screen.esm.js",
            "pos_receipt_attachment/static/src/xml/receipt_header.xml",
        ],
        "web.report_assets_common": [
            "pos_receipt_attachment/static/src/css/print.scss",
        ],
    },
    "installable": True,
}
