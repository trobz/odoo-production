Some Foodcoop websites use the e-commerce module in a **pre-order** mode, where
payment is not handled online but physically in the store. In that context, the
payment term on website orders should differ from the default partner term.

This module allows administrators to configure a **default payment term per
website**. When a sale order is created through the website, the term is
resolved in the following priority order:

1. Partner's own payment term (if set on the contact)
2. Website's default payment term (configured by this module)
3. Odoo's built-in fallback (`account_payment_term_immediate` or first company term)
