This module requires a manager to be logged in when validating a Point of
Sale order that includes a credit payment line.

When a cashier attempts to validate an order with credit payments, the system
checks the current cashier's role. If the cashier is not a manager, validation
is blocked and a message prompts the user to have a manager log in first.
