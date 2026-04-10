To reconcile bank expenses automatically:

1. Open a bank statement containing expense lines.
2. Click Auto Reconcile Expenses.
3. The module matches unreconciled lines using the configured regex patterns
   and posts counterparts on the Bank Expense Account.

To reconcile POS payments automatically:

1. Open a bank statement containing card settlement lines.
2. Click Auto Reconcile POS Payments.
3. The module tries:
   * single-line matching against POS bank payments created on child journals;
   * optional contactless combined matching (line + line).
4. For each successful match, the bank statement suspense line is switched to
   the payment outstanding account and reconciled with the payment move line.

If no line is matched, review domains, rounding, and date delta parameters on
the journal.