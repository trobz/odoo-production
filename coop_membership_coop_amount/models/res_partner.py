from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    fundraising_invoice_ids = fields.One2many(
        "account.move",
        "partner_id",
        domain=[
            ("move_type", "in", ("out_invoice", "out_refund")),
            ("is_capital_fundraising", "=", True),
            ("state", "in", ("draft", "posted")),
        ],
    )
    fundraising_journal_item_ids = fields.One2many(
        "account.move.line",
        "partner_id",
        domain=lambda self: self._get_fundraising_item_domain(),
    )

    amount_subscription = fields.Float()
    coop_amount = fields.Float(compute="_compute_coop_amount", store=True)

    def _get_fundraising_item_domain(self):
        categories = self.env["capital.fundraising.category"].sudo().search([])
        if not categories:
            return [("id", "=", False)]
        capital_accounts = categories.mapped("capital_account_id")
        return [
            ("move_id.state", "=", "posted"),
            ("account_id", "in", capital_accounts.ids),
        ]

    @api.depends(
        "fundraising_invoice_ids",
        "fundraising_invoice_ids.state",
        "fundraising_invoice_ids.invoice_line_ids",
    )
    def _compute_amount_subscription(self):
        return super()._compute_amount_subscription()

    @api.depends(
        "fundraising_journal_item_ids",
        "fundraising_journal_item_ids.move_id.state",
        "fundraising_journal_item_ids.account_id",
        "fundraising_journal_item_ids.partner_id",
    )
    def _compute_coop_amount(self):
        JournalItem = self.env["account.move.line"]
        domain = self._get_fundraising_item_domain()
        domain.append(("partner_id", "in", self.ids))
        datas = JournalItem.read_group(domain, ["other_balance"], ["partner_id"])
        self.update({"coop_amount": 0})
        for data in datas:
            partner = self.filtered(lambda p, data=data: p.id == data["partner_id"][0])
            partner.coop_amount = data.get("other_balance")
