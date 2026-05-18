When a cashier clicks the **Payment** button in the Point of Sale, this module
checks whether any order line contains a product marked as *To Weigh With
Scale* (``to_weight = True``) with a whole-number quantity (1, 2, 3 kg…).

If such lines are found, a confirmation dialog is shown listing the products
concerned and asking the cashier to verify that the weight has been properly
measured on the scale before proceeding.

* If the cashier confirms, the payment flow continues normally.
* If the cashier cancels, they are returned to the order screen to correct
  the quantity.

The check is controlled by a per-shop toggle so it can be enabled only for
shops that have a connected scale.
