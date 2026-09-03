By default, the Point of Sale pricelist button lets the cashier pick any
pricelist made available on the Point of Sale configuration.

This module restricts that list: the pricelist selection popup only
shows the pricelist assigned to the current customer (the partner's
*Sale Pricelist* / `property_product_pricelist`). When the customer has
no pricelist assigned - or when no customer is set on the order - the
popup falls back to the Point of Sale default pricelist.

This prevents cashiers from accidentally applying a pricelist that does
not belong to the customer.
