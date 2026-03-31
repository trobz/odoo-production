# Copyright (C) 2017-Today: La Louve (<http://www.lalouve.net/>)
# Copyright (C) 2019-Today Druidoo (<info@druidoo.io>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
#          Julien Weste
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from datetime import timedelta

from odoo import Command, _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)


class AccountBankStatement(models.Model):
    _inherit = "account.bank.statement"

    can_reconcile_expense = fields.Boolean(
        help="Technical field", compute="_compute_can_reconcile_expense"
    )

    can_reconcile_pos = fields.Boolean(
        help="Technical field", compute="_compute_can_reconcile_pos"
    )

    def _compute_can_reconcile_expense(self):
        for rec in self:
            rec.can_reconcile_expense = bool(rec.journal_id.bank_expense_account_id)

    def _compute_can_reconcile_pos(self):
        for rec in self:
            rec.can_reconcile_pos = bool(rec.journal_id.cb_child_ids)

    def button_reconcile_bank_expense(self):
        """Tries to automatically reconcile bank expenses"""
        self.ensure_one()
        count = self.line_ids._reconcile_bank_expense()
        if count == 0:
            raise UserError(_("No line is matched to Bank Expense Pattern"))

    def button_reconcile_pos(self):
        self.ensure_one()
        self._reconcile_pos()

    def _reconcile_pos(self):
        """
        It will try to match the account moves of every CB journal
        with a single statement line in our bank account.

        If contactless matching is enabled, it will also try 2-lines
        combinations.

        If there's a match, it will create the corresponding account.moves
        and reconcile everything.
        """
        for rec in self:
            if not rec.journal_id.cb_child_ids:
                raise UserError(
                    _("The journal %s has no CB Child Journals.")
                    % rec.journal_id.display_name
                )

            if not rec.journal_id.cb_lines_domain:
                raise UserError(
                    _("The journal %s has no CB Lines Domain.")
                    % rec.journal_id.display_name
                )

            if (
                rec.journal_id.cb_contactless_matching
                and not rec.journal_id.cb_contactless_lines_domain
            ):
                raise UserError(
                    _("The journal %s has no CB Contactless Lines Domain.")
                    % rec.journal_id.display_name
                )

            # Lines that match the standard pattern (unreconciled only)
            domain = [
                ("statement_id", "=", rec.id),
                ("is_reconciled", "=", False),
            ]
            domain += safe_eval(rec.journal_id.cb_lines_domain)
            lines = rec.line_ids.search(domain)
            # Process regular 1-line matching first
            not_reconciled_lines = rec._pos_reconcile_lines(lines)

            # Manage contact-less matching
            if rec.journal_id.cb_contactless_matching:
                domain = [
                    ("statement_id", "=", rec.id),
                    ("is_reconciled", "=", False),
                ]
                domain += safe_eval(rec.journal_id.cb_contactless_lines_domain)
                alt_lines = rec.line_ids.search(domain)
                # Process alt lines 1-line matching first
                not_reconciled_alt_lines = rec._pos_reconcile_lines(alt_lines)

                # Process combinations
                if not_reconciled_lines and not_reconciled_alt_lines:
                    rec._pos_reconcile_lines_combined(
                        not_reconciled_lines, not_reconciled_alt_lines
                    )

    def _pos_reconcile_lines(self, lines):
        """
        This will try to find the statement for each line,
        and reconcile it with it.

        Returns not_reconciled_lines
        """
        self.ensure_one()
        reconciled_lines = self.env["account.bank.statement.line"]
        for line in lines:
            statement = self._find_pos_statement(date=line.date, amount=line.amount)
            # Ignore not matching
            if not statement:
                continue
            elif len(statement) > 1:
                _logger.debug(
                    'Multiple possible statements for "%s" line. Ignoring..',
                    line.payment_ref,
                )
                continue
            # Reconcile lines
            self._pos_reconcile_statement_with_lines(lines=line, statement=statement)
            reconciled_lines |= line
        return lines - reconciled_lines

    def _pos_reconcile_lines_combined(self, lines, alt_lines):
        """
        This will try to find the statatement using a combination
        of lines (1+1 matching)

        Returns a tuple with:
            (not_reconciled_lines, not_reconciled_alt_lines)
        """
        self.ensure_one()
        delta_days = self.journal_id.cb_contactless_delta_days
        reconciled_lines = self.env["account.bank.statement.line"]
        reconciled_alt_lines = self.env["account.bank.statement.line"]
        for line in lines:
            for alt_line in alt_lines:
                # if line is already reconciled, skip it
                if alt_line in reconciled_alt_lines:
                    continue
                # Ignore lines that do not comply cb_contactless_delta_days
                date_limit_min = line.date - timedelta(days=delta_days)
                date_limit_max = line.date + timedelta(days=delta_days)
                if alt_line.date > date_limit_max or alt_line.date < date_limit_min:
                    continue
                # Try to find statement
                statement = self._find_pos_statement(
                    date=line.date, amount=(line.amount + alt_line.amount)
                )
                # Ignore not matching
                if not statement:
                    continue
                elif len(statement) > 1:
                    _logger.debug(
                        'Multiple possible statements for "%s" and "%s" line. '
                        "Ignoring...",
                        line.payment_ref,
                        alt_line.payment_ref,
                    )
                    continue
                # Reconcile lines
                self._pos_reconcile_statement_with_lines(
                    lines=(line | alt_line), statement=statement
                )
                reconciled_lines |= line
                reconciled_alt_lines |= alt_line
                break  # line has already reconciled, break the loop then.
        # Return tuple
        return (
            lines - reconciled_lines,
            alt_lines - reconciled_alt_lines,
        )

    def _find_pos_statement(self, date, amount):
        """
        Finds a pos statement by amount, using
        the setup on the journal
        """
        self.ensure_one()
        rounding = self.journal_id.cb_rounding
        # Delta days is used only to get past statement, but not future ones
        max_date = date
        min_date = date - timedelta(days=self.journal_id.cb_delta_days)
        # Find matching statements
        pos_statement_ids = self.env["account.bank.statement"].search(
            [
                ("journal_id", "in", self.journal_id.cb_child_ids.ids),
                ("date", "<=", max_date),
                ("date", ">=", min_date),
                ("balance_end_real", ">=", round(amount - rounding, 2)),
                ("balance_end_real", "<=", round(amount + rounding, 2)),
                ("line_ids", "!=", False),
            ]
        )
        _logger.debug(
            "Searching POS Statements ("
            "min_date=%s, max_date=%s, amount=%s, rounding=%s, child_ids=%s"
            "): %s",
            min_date,
            max_date,
            amount,
            rounding,
            self.journal_id.cb_child_ids,
            pos_statement_ids,
        )
        # Filter statements that are already reconciled
        # In Odoo 18, account.bank.statement no longer has move_line_ids;
        # we collect the move lines from each statement line's move.
        ignored_pos_statement_ids = self.env["account.bank.statement"]
        account_id = self.journal_id.default_account_id.id
        for st in pos_statement_ids:
            pos_move_lines = st.line_ids.move_id.line_ids
            reconciled_move_lines = pos_move_lines.filtered(
                lambda ml: ml.reconciled and ml.account_id.id == account_id
            )
            if reconciled_move_lines:
                _logger.debug(
                    "There are debits on the journal and they are reconciled."
                )
                ignored_pos_statement_ids |= st
        pos_statement_ids -= ignored_pos_statement_ids
        # Return found statements
        return pos_statement_ids

    @api.model
    def _pos_reconcile_statement_with_lines(self, lines, statement):
        self.ensure_one()
        # In Odoo 18, both debit and credit use the same default_account_id.
        st_account_id = statement.journal_id.default_account_id.id
        lines_to_reconcile_ids = []
        for line in lines:
            line_liquidity_account_id = line.journal_id.default_account_id.id
            if st_account_id == line_liquidity_account_id:
                _logger.warning(
                    "Skipping POS reconciliation for statement line %s: "
                    "target account %s equals liquidity account.",
                    line,
                    st_account_id,
                )
                continue
            reconcile_label = (
                f"{statement.journal_id.name} {statement.date} {statement.name}"
            )
            # Find the suspense line and replace it with the POS journal account
            _liquidity_line, suspense_line, _other_lines = line._seek_for_lines()
            if not suspense_line:
                _logger.warning(
                    "Statement line %s has no suspense line, skipping.", line
                )
                continue
            _logger.info(
                "Creating reconciliation for statement line %s with POS account %s",
                line,
                st_account_id,
            )
            line.write(
                {
                    "checked": True,
                    "line_ids": [
                        Command.update(
                            suspense_line.id,
                            {
                                "account_id": st_account_id,
                                "name": reconcile_label,
                            },
                        )
                    ],
                }
            )
            # Collect the newly created counterpart line for reconciliation
            _liq, _susp, new_other_lines = line._seek_for_lines()
            for move_line in new_other_lines:
                if (
                    move_line.account_id.id == st_account_id
                    and move_line.id not in lines_to_reconcile_ids
                ):
                    lines_to_reconcile_ids.append(move_line.id)
        # Collect the POS statement move lines on the same account
        for pos_st_line in statement.line_ids:
            for move_line in pos_st_line.move_id.line_ids:
                if (
                    move_line.account_id.id == st_account_id
                    and move_line.id not in lines_to_reconcile_ids
                    and not move_line.reconciled
                ):
                    lines_to_reconcile_ids.append(move_line.id)
        # Process reconciliation
        move_lines = self.env["account.move.line"].browse(lines_to_reconcile_ids)
        move_lines.reconcile()
