# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, SUPERUSER_ID


def post_init_hook(cr, registry):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        credit_journal = env.ref('pos_payment_credit.credit_journal', False)
        code = '511900'
        account = env['account.account'].search(
            [('code', '=', code)], limit=1)
        if not account:
            account = env['account.account'].create({
                'name': 'Crédit emis POS (remboursement)',
                'user_type_id': env.ref('account.data_account_type_liquidity').id,
                'company_id': env.ref('base.main_company').id,
                'code': code,
                'reconcile': False
            })
        if credit_journal and account:
            credit_journal.write({
                'default_credit_account_id': account.id,
                'default_debit_account_id': account.id,
            })