
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Account Financial Reports Custom',
    'version': '12.0.1.0.0',
    'category': 'Reporting',
    'summary': 'OCA Financial Reports',
    'author': 'Camptocamp SA,'
              'initOS GmbH,'
              'redCOR AG,'
              'Eficent,'
              'Odoo Community Association (OCA)',
              'Trobz'
    "website": "https://trobz.com",
    'depends': [
        'account_financial_report'
    ],
    'data': [
        'report/templates/general_ledger.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'AGPL-3',
}
