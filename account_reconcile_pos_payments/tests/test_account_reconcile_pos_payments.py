from odoo.tests.common import TransactionCase


class TestBankStatementReconciliation(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.bs_model = cls.env["account.bank.statement"]
        cls.bsl_model = cls.env["account.bank.statement.line"]
        cls.acc_model = cls.env["account.account"]
        cls.partner = cls.env["res.partner"].create({"name": "test"})

    def test_reconciliation_reconcile_bank_expense(self):
        st_line = self.create_statement_line(100)
        if not st_line:
            return
        st_line.statement_id.button_reconcile_bank_expense()
        self.assertTrue(
            st_line.is_reconciled,
            "The statement line should be reconciled after bank expense "
            "reconciliation.",
        )

    def create_statement_line(self, st_line_amount):
        bank_expense_account = self.acc_model.search(
            [("account_type", "=", "expense"), ("name", "=", "Bank Fees")],
            limit=1,
        )
        if not bank_expense_account:
            return None
        company = self.env.company
        journal = self.env["account.journal"].search(
            [("type", "=", "bank"), ("company_id", "=", company.id)], limit=1
        )
        journal.bank_expense_name_pattern = "expense_name"
        journal.bank_expense_ref_pattern = "expense_ref"
        journal.bank_expense_note_pattern = "expense_note"
        journal.bank_expense_account_id = bank_expense_account.id
        bank_stmt = self.bs_model.create(
            {
                "journal_id": journal.id,
            }
        )
        bank_stmt_line = self.bsl_model.create(
            {
                "payment_ref": "expense_name",
                "ref": "expense_ref",
                "narration": "expense_note",
                "statement_id": bank_stmt.id,
                "partner_id": self.partner.id,
                "amount": st_line_amount,
                "journal_id": journal.id,
                "date": "2024-01-01",
            }
        )
        bank_stmt.write({"can_reconcile_expense": True})
        return bank_stmt_line

    def test_reconciliation_reconcile_pos(self):
        st_line, payment = self.create_pos_statement_line(100)
        if not st_line or not payment:
            return
        st_line.statement_id.button_reconcile_pos()
        payment.invalidate_recordset(["is_matched", "reconciled_statement_line_ids"])
        self.assertTrue(
            st_line.is_reconciled,
            "The statement line should be reconciled after POS auto-reconciliation.",
        )
        self.assertTrue(
            payment.is_matched,
            "The POS payment should be matched after auto-reconciliation.",
        )

    def create_pos_statement_line(self, st_line_amount):
        company = self.env.company
        parent_journal = self.env["account.journal"].search(
            [("type", "=", "bank"), ("company_id", "=", company.id)], limit=1
        )
        outstanding_account = self.acc_model.search(
            [
                ("account_type", "=", "asset_current"),
                ("reconcile", "=", True),
                ("deprecated", "=", False),
                ("company_ids", "in", company.id),
            ],
            limit=1,
        )
        if not outstanding_account:
            outstanding_account = self.partner.property_account_receivable_id

        child_journal = self.env["account.journal"].search(
            [
                ("type", "=", "bank"),
                ("company_id", "=", company.id),
                ("id", "!=", parent_journal.id),
            ],
            limit=1,
        ) or self.env["account.journal"].create(
            {
                "name": "POS Child Journal",
                "code": "POSC",
                "type": "bank",
                "company_id": company.id,
                "default_account_id": outstanding_account.id,
            }
        )
        parent_journal.cb_child_ids = [(6, 0, [child_journal.id])]
        parent_journal.cb_lines_domain = "[('payment_ref', 'ilike', '%CB/CONT/01%')]"

        payment = self.env["account.payment"].create(
            {
                "journal_id": child_journal.id,
                "amount": st_line_amount,
                "payment_type": "inbound",
                "partner_type": "customer",
                "partner_id": self.partner.id,
                "destination_account_id": (
                    self.partner.property_account_receivable_id.id
                ),
                "force_outstanding_account_id": outstanding_account.id,
                "date": "2024-01-01",
            }
        )
        payment.action_post()

        bank_stmt = self.bs_model.create(
            {
                "journal_id": parent_journal.id,
                "balance_end_real": st_line_amount,
            }
        )
        bank_stmt_line = self.bsl_model.create(
            {
                "payment_ref": "CB/CONT/01",
                "statement_id": bank_stmt.id,
                "partner_id": self.partner.id,
                "amount": st_line_amount,
                "journal_id": parent_journal.id,
                "date": "2024-01-01",
            }
        )
        return bank_stmt_line, payment
