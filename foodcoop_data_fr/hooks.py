# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html


def post_init_hook(env):
    code = "511900"
    account = env["account.account"].search([("code", "=", code)], limit=1)
    if not account:
        main_company = env.ref("base.main_company")
        account = env["account.account"].create(
            {
                "name": "Crédit emis POS (remboursement)",
                "account_type": "liability_current",
                "company_ids": [(6, 0, [main_company.id])],
                "code": code,
                "reconcile": False,
            }
        )
    return True
