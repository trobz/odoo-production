{
    'name': 'Lalouve Custom',
    'version': '18.0.1.0.0',
    'category': 'Custom',
    'author': 'Trobz',
    'website': 'http://www.trobz.com',
    'license': 'LGPL-3',
    'depends': [
        'coop_project',
        'coop_point_of_sale',
        'lalouve_custom_timesheet'
    ],
    'data': [
        'security/res_groups.xml',
        'view/calendar_view.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'lalouve_custom/static/src/**/*',
        ],
    },
    'installable': True,
}
