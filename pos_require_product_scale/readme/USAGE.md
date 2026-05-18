**Enable the check for a shop**

1. Go to *Point of Sale > Configuration > Point of Sale*.
2. Open the shop you want to configure.
3. Enable **Require Product To Be Scaled**.
4. Save.

**Mark a product as requiring a scale**

1. Go to *Point of Sale > Products > Products*.
2. Open the product form and go to the **Point of Sale** tab.
3. Enable **To Weigh With Scale**.
4. Save.

**Cashier flow**

1. Add a *To Weigh With Scale* product to the order.
2. Leave the quantity as a whole number (the default after a single click).
3. Click **Payment**.
4. A warning dialog lists the products with a round weight and asks for
   confirmation.

   * Click **Ok** to proceed to payment.
   * Click **Cancel** to go back and correct the quantity (e.g. enter the
     actual weight read from the scale such as 1.340 kg).

No dialog appears when:

* the setting is disabled on the shop,
* the product does not have *To Weigh With Scale* enabled, or
* the quantity is already a decimal number.
