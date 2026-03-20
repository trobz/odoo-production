from odoo import api, fields, models


class AccountPayment(models.Model):
    _inherit = "account.payment"

    state = fields.Selection(
        selection_add=[("cancelled", "Cancelled")],
        ondelete={"cancelled": "cascade"},
    )
    partner_code = fields.Integer(related="partner_id.barcode_base", store=True)
    operation_type = fields.Selection(
        [
            ("sepa_debit", "SEPA Direct Debit"),
            ("sepa_credit", "SEPA Direct Credit"),
            ("check", "Check"),
            ("credit_card", "Credit card"),
            ("lcr", "LCR"),
            ("other", "Other"),
        ],
    )
    text_check_code = fields.Text(string="Check Code")
    text_lcr_code = fields.Text(string="LCR Code")

    @api.onchange("operation_type")
    def onchange_operation_type(self):
        invoice = self.invoice_ids and self.invoice_ids[0]
        memo = ""
        if invoice:
            memo = invoice.ref or invoice.name
        if self.operation_type != "check":
            self.text_check_code = ""
        if self.operation_type != "lcr":
            self.text_lcr_code = ""
        if self.operation_type == "sepa_debit":
            self.memo = memo + "-" + self.env._("SEPA Direct Debit")
        if self.operation_type == "sepa_credit":
            self.memo = memo + "-" + self.env._("SEPA Direct Credit")
        if self.operation_type == "credit_card":
            self.memo = memo + "-" + self.env._("Credit Card ")
        if self.operation_type == "other":
            self.memo = memo

    @api.onchange("text_check_code", "text_lcr_code")
    def onchange_memo_based_on_operation_type(self):
        invoice = self.invoice_ids and self.invoice_ids[0]
        memo = ""
        if invoice:
            memo = invoice.ref or invoice.name
        if self.text_check_code:
            check_nb = self.env._("Check nb ")
            self.memo = f"{memo}-{check_nb}{self.text_check_code}"
        if self.text_lcr_code:
            lcr_nb = self.env._("LCR nb ")
            self.memo = f"{memo}-{lcr_nb}{self.text_lcr_code}"
