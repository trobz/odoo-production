{
    'name': 'Lalouve Custom: Member Timesheet',
    'version': '18.0.1.0.0',
    'category': 'Custom',
    'summary': 'Lalouve Custom Timesheet Report',
    'author': 'Trobz',
    'website': 'https://github.com/AwesomeFoodCoops/odoo-production',
    'license': 'LGPL-3',
    'depends': [
        'coop_shift'
    ],
    'data': [
        'report/report_timesheet.xml',
    ],
    'assets': {
        'web.report_assets_common': [
            'lalouve_custom_timesheet/static/src/css/report_timesheet.css',
        ],
    },
    'installable': True,
}
