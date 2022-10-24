# -*- coding: utf-8 -*-
{
    'name': 'Project Foodcoop Installer',
    'version': '12.0.1.0.0',
    'category': 'Trobz Standard Modules',
    'description': """
This module will install all module dependencies of a foodcoop.
    """,
    'author': 'Trobz',
    'website': 'http://www.trobz.com',
    'depends': [
        'auth_signup',
        'base_user_role',
    ],
    'data': [
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        'menu/admin_menu.xml',
        'views/res_users_views.xml',
    ],
    'test': [],
    'installable': True,
    'active': False,
    'application': True,
}
