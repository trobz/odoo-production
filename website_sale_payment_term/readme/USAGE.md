## Configuration

1. Go to **Website → Configuration → Websites**.
2. Select the website you want to configure.
3. In the **Default Payment Term** field, choose the payment term to apply to
   orders placed through that website.
4. Save.

> The field is only visible to users with the **Billing** access right
> (`account.group_account_invoice`).

## Behavior

Once configured, the payment term is automatically applied when:

- A customer places an order through the website (checkout flow).
- A backend user changes the partner on an existing website order.

The partner's own payment term always takes priority. The website term is only
applied when the partner has no term configured.
