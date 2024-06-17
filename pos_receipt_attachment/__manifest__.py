# Copyright (C) Nguyen Minh Chien (chien@trobz.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


{
    "name": "Point of Sale - Attach Receipt to Backend",
    "summary": "Send receipt to backend as an attachment",
    "version": "12.0.1.0.1",
    "category": "Sales/Point Of Sale",
    "website": "https://trobz.com",
    "author": "Trobz",
    "license": "AGPL-3",
    "depends": ["point_of_sale", "pos_ticket_send_by_mail"],
    "data": [
        "data/ir_cron.xml",
        "views/templates.xml",
        "views/report_paperformat.xml",
        "views/report_receipt.xml",
    ],
    "qweb": [],
    "installable": True,
}
