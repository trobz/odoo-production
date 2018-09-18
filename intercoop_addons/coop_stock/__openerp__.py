# -*- coding: utf-8 -*-

{
    'name': 'Coop - Stock',
    'version': '9.0.2.0.0',
    'category': 'Custom',
    'summary': 'Custom settings for stock',
    'depends': [
        'stock', 'stock_account',
    ],
    'data': [
        'views/action.xml',
        'views/menu.xml',
        'views/stock_picking_view.xml',

        'report/report_stockinventory.xml',
    ],
    'installable': True,
}
