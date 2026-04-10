To configure the module:

1. Go to Accounting > Configuration > Journals.
2. Open the bank journal that receives card settlements.
3. In the Journal Entries tab, configure Automatic POS Reconciliation:
   * CB Childs: select the POS journals whose sessions create bank payments on
     those journals.
   * CB Lines Domain: domain used to detect candidate bank statement lines.
   * CB Delta Days and CB Rounding: matching tolerance by date and amount.
4. If needed, enable CB Contactless Matching and configure:
   * Contactless Lines Domain
   * Contactless Delta Days
5. In Automatic Charges Reconciliation, configure:
   * Bank Expense Name/Ref/Note Pattern (regex)
   * Bank Expense Account

Recommendations:

* Keep parent bank journal liquidity accounts different from the outstanding
   account used by the matched POS bank payments.
* Start with strict domains and small rounding values, then relax only if
  needed.