Install this module alongside `pos_payment_credit`.

**Manual credit payment:**

1. Select a customer with available credit.
2. On the payment screen, click the Credit payment method button.
3. A confirmation dialog appears — click **Ok** to confirm or **Cancel** to abort.
4. Click **Validate** to complete the order.

**Auto-apply credit (requires `auto_apply_credit_amount` on the payment method):**

1. Enable **Auto Apply Credit Amount** on the Credit payment method in POS
   configuration.
2. Open a POS session and create an order for a customer with available credit.
3. On the payment screen, the credit line is added and processed automatically.
4. Click **Validate** to complete the order — no extra steps needed.
