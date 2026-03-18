from odoo import api, fields, models
from odoo.exceptions import UserError


class AccountMoveReversal(models.TransientModel):
    _inherit = "account.move.reversal"

    refund_quantity_origin = fields.Integer()
    refund_quantity = fields.Integer(
        string="Quantity Of Shares To Refund",
        required=False,
    )
    is_capital_fundraising = fields.Boolean(
        string="Is Capital Fundraising",
        related="move_ids.is_capital_fundraising",
    )

    @api.depends("move_ids", "move_ids.fundraising_category_id")
    def _compute_journal_id(self):
        res = super()._compute_journal_id()
        records = self.filtered(
            lambda r: r.is_capital_fundraising and r.move_type == "out_invoice"
        )
        journals = records._get_refund_journals()
        if journals:
            for record in records:
                record.journal_id = journals[0]
        return res

    @api.depends("move_ids", "move_ids.fundraising_category_id")
    def _compute_available_journal_ids(self):
        res = super()._compute_available_journal_ids()
        records = self.filtered(
            lambda r: r.is_capital_fundraising and r.move_type == "out_invoice"
        )
        journals = records._get_refund_journals()
        if journals:
            for record in records:
                record.available_journal_ids = journals
        return res

    def _get_refund_journals(self):
        records = self
        journals = self.env["account.journal"]
        for record in records:
            journals = record.move_ids.mapped(
                "fundraising_category_id.journal_refund_ids"
            )
        return journals

    @api.constrains("refund_quantity")
    def _check_refund_quantity_is_positive(self):
        if self.is_capital_fundraising and self.refund_quantity <= 0:
            raise UserError(
                self.env._("Error! The refund quantity must be greater than 0.")
            )
        return True

    def reverse_moves(self, is_modify=False):
        res = super().reverse_moves(is_modify=is_modify)
        new_invoices = self.new_move_ids.filtered(
            lambda move: move.move_type == "out_refund"
            and move.fundraising_category_id
            and move.state == "draft"
        )
        if not new_invoices:
            return res

        if not is_modify:
            # Case 1: Reverse (is_modify=False)
            #  - Update the qty of shares to refund on the reversed invoice (refund).
            #  - Update the account of the invoice lines to use the one defined on
            #    the fundraising category (Final Capital Account).
            for invoice in new_invoices:
                refund_account = invoice.fundraising_category_id.refund_account_id
                if refund_account:
                    term_lines = invoice.line_ids.filtered(
                        lambda line: line.display_type == "payment_term"
                    )
                    term_lines.update({"account_id": refund_account.id})
                if invoice.fundraising_category_id.capital_account_id:
                    invoice.invoice_line_ids.update(
                        {
                            "account_id": (
                                invoice.fundraising_category_id.capital_account_id.id
                            )
                        }
                    )
                if self.refund_quantity > 0:
                    invoice.apply_refund_deficit_share(self.refund_quantity)
        else:
            # Case 2: Reverse and Create Invoice
            # - Update the qty of shares on the created invoice: old qty - refund qty.
            if self.refund_quantity > 0:
                new_qty = self.refund_quantity_origin - self.refund_quantity
                if new_qty > 0:
                    for invoice in new_invoices:
                        invoice.invoice_line_ids.update(
                            {
                                "quantity": new_qty,
                            }
                        )
                else:
                    # If the new quantity is 0 or negative,
                    # we cancel the created invoice and its lines
                    new_invoices.button_cancel()
                    new_invoices.invoice_line_ids.unlink()
                    new_invoices.unlink()
        return res
