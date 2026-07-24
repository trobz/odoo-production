**Before starting**

An inventory session must be in the *In Progress* state. Go to
*Inventory → Physical Inventory*, create or open a session, and click
**Begin Adjustments** to move it to *In Progress*.

---

**Opening the barcode interface**

1. Open an *In Progress* inventory session.
2. Set **Scan Mode** (*Add Qty* or *Change Qty*) and, if using *Add Qty*,
   toggle **Use Latest Qty** as needed.
3. Click **Start Barcode Interface**.

---

**Scanning products — Add Qty mode**

1. Point the scanner at a product barcode or internal reference.
   The *Scan Barcode* field is focused automatically.
2. The product is identified and the counter starts at 1.
3. Scan the same product again to increment the counter (+1 per scan).
4. For lot-tracked products, scan the product barcode first, then the
   lot barcode. Scanning the lot does **not** increment the counter.
5. Click **Update** to record the quantity. If **Auto Save** is enabled,
   switching to a different product saves automatically.

With **Use Latest Qty** on, the counter starts from the quantity already
recorded in the session, so three scans of a product with an existing count
of 5 will record 8. With **Use Latest Qty** off, the base is always 0, so
three scans always record 3.

---

**Scanning products — Change Qty mode**

1. Scan a product barcode.
2. The quantity field is pre-filled with the value already recorded for
   that product/lot in the session.
3. Edit the quantity directly and click **Update**.

---

**Applying the inventory**

The barcode wizard only updates the counted quantities on the inventory
session. To post the actual stock adjustment:

1. Close the barcode wizard.
2. From the inventory session, click the **Inventory Adjustment** button
   to open the quants view.
3. Apply quantities from there using the standard inventory adjustment flow.
