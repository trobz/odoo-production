1.  Enable the *Pricelists* feature (*Point of Sale > Configuration >
    Settings > Pricing*) and add the pricelists you want to use to the
    *Available Pricelists* of your Point of Sale configuration. A
    pricelist is only offered in the front-end if it belongs to that
    list.
2.  On the customer form, set each partner's *Sale Pricelist*
    (`property_product_pricelist`).
3.  Open a Point of Sale session and start an order.
4.  Set a customer with the *Customer* button. Odoo already applies that
    customer's pricelist to the order automatically.
5.  Open the *More* actions of the order and click the *Pricelist*
    button.

The selection popup now only offers the pricelist assigned to the
current customer. When the customer has no pricelist, when that pricelist
is not part of the Point of Sale *Available Pricelists*, or when no
customer is set, the Point of Sale default pricelist is offered instead.
