**Scanning barcodes / searching by cooperative number**

In the POS product screen, type or scan a barcode (or any exact
identifier). If exactly one product matches the full string, only that
product is shown. Partial searches continue to work as usual when no
exact match is found.

The same logic applies to the partner-selection screen: scan a member's
barcode or type their cooperative number, name, phone, email, or VAT
number. When a single exact match exists it is surfaced immediately.

**Returning / refunding an order**

Open the **Orders** list in the POS, select the order to return, and
click **Return**. If the order's original session is already closed, the
module automatically routes the refund into the current user's active
session instead of raising an error. A session must be open for the
refund to proceed.

For a partial return, click **Partial Refund**; the partial-return
wizard opens in the same way, using the current session when the
original session is closed.

**Controlling access to POS buttons**

Cashiers without the *PoS Access Control Buttons Group* will find the
pricelist, refund, fiscal-position, and quotation buttons disabled.
Supervisors or managers with the group can use these buttons normally.

**Computed purchase order**

The *Discount* column on the computed purchase order form is shown as
*Discount (%)* to clarify that the value is a percentage.
