This module requires the cashier to confirm a security PIN when validating a
Point of Sale order that includes a credit payment line.

When a cashier attempts to validate an order with credit payments, the system
checks the current cashier's role. Managers (and admins) are trusted and can
validate directly. Any other cashier must enter their own security PIN to
confirm the credit payment; validation is blocked until the correct PIN is
entered.
