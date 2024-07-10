# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Payment Credit > for Member',
    'version': '12.0.1.0.0',
    'category': 'Member',
    'author': 'Trobz',
    'license': 'AGPL-3',
    'depends': [
        'pos_payment_credit',
        'coop_membership'
    ],
    'data': [
        "views/res_partner_view.xml",
    ],
    "qweb": [],
    'installable': True,
}
