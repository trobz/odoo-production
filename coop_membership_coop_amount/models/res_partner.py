
from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    coop_amount = fields.Float(compute="_compute_coop_amount")

    def _compute_coop_amount(self):
        JournalItem = self.env["account.move.line"]
        categories = self.env["capital.fundraising.category"].sudo().search([])
        capital_accounts = categories.mapped("capital_account_id")
        domain = [
            ("move_id.state", "=", "posted"),
            ("account_id", "in", capital_accounts.ids),
            ("partner_id", "in", self.ids)
        ]
        datas = JournalItem.read_group(
            domain, ["other_balance"], ["partner_id"]
        )
        self.update({"coop_amount": 0})
        for data in datas:
            partner = self.filtered(lambda p: p.id == data["partner_id"][0])
            partner.coop_amount = data.get("other_balance")
