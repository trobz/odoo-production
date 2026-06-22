This module customizes the behavior of the `pos_payment_credit` module in the
Point of Sale interface for La Louve food cooperative.

It hides the "Payment request pending" and "Send" button that normally appear
when a credit payment line is added, as well as the status messages
("Payment Successful", "Payment successful. Remaining credit: ...") shown after
processing. This simplifies the cashier experience by removing unnecessary
intermediate steps.

When `auto_apply_credit_amount` is enabled on the payment method, the credit
payment is automatically processed when the payment screen opens, so the
cashier only needs to click Validate to complete the order.
