This module provides French-specific data configuration for the Foodcoop system.

## Purpose

Extends the Foodcoop functionality with French-specific accounting and partner configurations.

## Functionality

- Creates a credit account (511900) for POS payments and refunds
- Configures the credit journal with default debit account
- Customizes partner view to show credit page only for members, former members, and interested people

## Dependencies

- `coop_membership`: Base cooperative membership module
- `pos_payment_credit`: POS payment credit module

## License

AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
