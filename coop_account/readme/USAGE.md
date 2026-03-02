## Account Moves

### Search by Date
Account moves include computed search fields:
- **Year (Search)**: Filter by year (e.g., "2024")
- **Month (Search)**: Filter by year-month (e.g., "2024-06")
- **Day (Search)**: Filter by exact date (e.g., "2024-06-15")

### Merge Invoice Lines
For draft invoices, you can merge duplicate invoice lines with the same product, price, discount, and account:
1. Open a draft invoice
2. Click **Merge Move Lines** to combine matching lines

### Unmatch Bank Statement
To remove bank statement matching from transactions:
1. Select account move lines
2. Click **Unmatch Bank Statement** to open the wizard
3. Confirm to unlink statement references

## Payments

### Operation Types
When creating payments, select an operation type:
- **SEPA Direct Debit**: For incoming SEPA debits
- **SEPA Direct Credit**: For outgoing SEPA credits
- **Check**: With optional check code
- **Credit Card**: For card payments
- **LCR**: For Letter of Credit Remittance
- **Other**: For other payment methods

The memo field auto-populates based on the operation type and associated invoice.

## Bank Statement Reconciliation

### Reconcile Move Lines
Use the reconciliation wizard to reconcile selected move lines:
1. Select move lines from account move
2. Choose the target account
3. Confirm reconciliation

### Bank Statement Validation
The system prevents reconciling account moves with bank statement lines that are not linked to a bank journal, ensuring proper accounting practices.
