This module provides French-specific data configuration for the Foodcoop system.

## Features

- Creates a credit account for POS payments
- Configures credit journal with default debit account
- Customizes partner view to show credit page only for relevant partners

## Configuration

1. Install the module
2. The module will automatically create a credit account with code "511900" if it doesn't exist
3. The credit journal from `pos_payment_credit` module will be configured with the default debit account

## Requirements

- This module depends on:
  - `coop_membership`
  - `pos_payment_credit`
