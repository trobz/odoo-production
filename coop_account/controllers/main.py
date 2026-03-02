from odoo import http


class CoopAccount(http.Controller):
    @http.route(
        "/coop_account/export_wrong_reconciliation_ml", type="json", auth="user"
    )
    def export_wrong_reconciliation_ml(self):
        return http.request.env["account.move.line"].export_wrong_reconciliation_ml()
