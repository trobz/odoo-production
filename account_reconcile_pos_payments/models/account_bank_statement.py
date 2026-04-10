# Copyright (C) 2017-Today: La Louve (<http://www.lalouve.net/>)
# Copyright (C) 2019-Today Druidoo (<info@druidoo.io>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
#          Julien Weste
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from datetime import timedelta

from odoo import _, api, fields, models
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
        This will try to find the payment for each line,
        and reconcile it with it.

        Returns not_reconciled_lines
        """
        self.ensure_one()
        reconciled_lines = self.env["account.bank.statement.line"]
        for line in lines:
            payment = self._find_pos_payment(date=line.date, amount=line.amount)
            # Ignore not matching
            if not payment:
                continue
            elif len(payment) > 1:
                _logger.debug(
                    'Multiple possible payments for "%s" line. Ignoring..',
                    line.payment_ref,
                )
                continue
            # Reconcile lines
            self._pos_reconcile_payment_with_lines(lines=line, payment=payment)
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
                # Try to find payment
                payment = self._find_pos_payment(
                    date=line.date, amount=(line.amount + alt_line.amount)
                )
                # Ignore not matching
                if not payment:
                    continue
                elif len(payment) > 1:
                    _logger.debug(
                        'Multiple possible payments for "%s" and "%s" line. '
                        "Ignoring...",
                        line.payment_ref,
                        alt_line.payment_ref,
                    )
                    continue
                # Reconcile lines
                self._pos_reconcile_payment_with_lines(
                    lines=(line | alt_line), payment=payment
                )
                reconciled_lines |= line
                reconciled_alt_lines |= alt_line
                break  # line has already reconciled, break the loop then.
        # Return tuple
        return (
            lines - reconciled_lines,
            alt_lines - reconciled_alt_lines,
        )

    def _find_pos_payment(self, date, amount):
        """
        Finds a POS payment by amount, using
        the setup on the journal
        """
        self.ensure_one()
        rounding = self.journal_id.cb_rounding
        target_amount = abs(amount)
        # Delta days is used only to get past statement, but not future ones
        max_date = date
        min_date = date - timedelta(days=self.journal_id.cb_delta_days)
        # Find matching payments
        pos_payment_ids = self.env["account.payment"].search(
            [
                ("journal_id", "in", self.journal_id.cb_child_ids.ids),
                ("date", "<=", max_date),
                ("date", ">=", min_date),
                ("amount", ">=", round(target_amount - rounding, 2)),
                ("amount", "<=", round(target_amount + rounding, 2)),
                ("state", "in", ["in_process", "paid"]),
                ("move_id", "!=", False),
            ]
        )
        _logger.info(
            "Searching POS Payments ("
            "min_date=%s, max_date=%s, amount=%s, rounding=%s, child_ids=%s"
            "): %s",
            min_date,
            max_date,
            target_amount,
            rounding,
            self.journal_id.cb_child_ids,
            pos_payment_ids,
        )
        ignored_pos_payment_ids = self.env["account.payment"]
        for payment in pos_payment_ids:
            if not payment.outstanding_account_id:
                ignored_pos_payment_ids |= payment
                continue
            liquidity_lines, _counterpart_lines, _writeoff_lines = (
                payment._seek_for_lines()
            )
            outstanding_move_lines = liquidity_lines.filtered(
                lambda move_line, p=payment: (
                    move_line.account_id == p.outstanding_account_id
                    and not move_line.reconciled
                )
            )
            if not outstanding_move_lines:
                _logger.debug(
                    "POS payment %s has no open outstanding lines.",
                    payment.display_name,
                )
                ignored_pos_payment_ids |= payment
        pos_payment_ids -= ignored_pos_payment_ids
        return pos_payment_ids

    @api.model
    def _pos_reconcile_payment_with_lines(self, lines, payment):
        self.ensure_one()
        payment_account_id = payment.outstanding_account_id.id
        if not payment_account_id:
            _logger.warning(
                "Skipping POS reconciliation for payment %s: no outstanding account.",
                payment,
            )
            return
        payment_liquidity_lines, _counterpart_lines, _writeoff_lines = (
            payment._seek_for_lines()
        )
        lines_to_reconcile = payment_liquidity_lines.filtered(
            lambda move_line: (
                move_line.account_id.id == payment_account_id
                and not move_line.reconciled
            )
        )
        for line in lines:
            line_liquidity_account_id = line.journal_id.default_account_id.id
            if payment_account_id == line_liquidity_account_id:
                _logger.warning(
                    "Skipping POS reconciliation for statement line %s: "
                    "target account %s equals liquidity account.",
                    line,
                    payment_account_id,
                )
                continue
            reconcile_label = f"{payment.journal_id.name} {payment.date} {payment.name}"
            # Find the suspense line and replace it with the POS payment account.
            _liquidity_line, suspense_line, _other_lines = line._seek_for_lines()
            if not suspense_line:
                _logger.warning(
                    "Statement line %s has no suspense line, skipping.", line
                )
                continue
            _logger.info(
                "Creating reconciliation for statement line %s with POS account %s",
                line,
                payment_account_id,
            )
            line.write(
                {
                    "checked": True,
                }
            )
            suspense_line.with_context(skip_account_move_synchronization=True).write(
                {
                    "account_id": payment_account_id,
                    "name": reconcile_label,
                }
            )
            lines_to_reconcile |= suspense_line.filtered(
                lambda move_line: not move_line.reconciled
            )
        if lines_to_reconcile:
            lines_to_reconcile.reconcile()
