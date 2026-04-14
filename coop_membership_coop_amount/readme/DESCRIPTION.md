This module extends the cooperative membership functionality by adding a field to display the cooperative amount (coop_amount) for members.

## Features

1. **Coop Amount Display**: Shows the total cooperative amount for each partner based on fundraising journal items.

2. **Fundraising Invoices**: Displays a list of fundraising invoices associated with the partner.

3. **Fundraising Journal Items**: Shows the journal items related to capital fundraising for the partner.

4. **Total Subscribed Amount**: Computes and displays the total subscribed amount from fundraising invoices.

## Technical Details

- Inherits from `res.partner` model
- Adds computed fields for coop_amount, fundraising_invoice_ids, and fundraising_journal_item_ids
- Uses account move and account move line models
- Depends on `coop_membership`, `capital_subscription`, and `coop_account` modules
