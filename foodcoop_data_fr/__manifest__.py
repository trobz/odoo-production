# -*- coding: utf-8 -*-
{
    'name': 'Data for Foodcoop in France',
    'version': '12.0.1.0.1',
    'category': 'Trobz Standard Modules',
    'description': """
    """,
    'author': 'Trobz',
    'website': 'http://www.trobz.com',
    'depends': [
        'coop_membership',
        'pos_payment_credit',

    ],
    'test': [],
    'data': [
        'views/view_res_partner.xml',
    ],
    'post_init_hook': 'post_init_hook',
}
