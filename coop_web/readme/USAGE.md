# Usage (Functional test guide)

This guide is intended for functional consultants (FC) and testers.

## Pre-conditions

- Module `web` is installed (standard Odoo backend).
- Module `coop_web` is installed.
- Any list view with long column headers is accessible (e.g. the **Achats**
  tab on a product form).

---

## Feature 1: Column header text wrapping in list views

### What to verify

Long column header labels must be fully visible — they should wrap onto
multiple lines instead of being truncated with `…`.

### Steps

1. Go to **Inventory > Products > Products** (or any module with a list
   view).
2. Open a product and navigate to the **Achats** tab.
3. Inspect the column headers: *Conditionnement*, *Nb. Colis MIN*,
   *Conditionnement indicatif hors taxes*, *Prix de vente TTC*, etc.
4. Confirm that all header labels are **fully readable** — no text is cut
   off with an ellipsis.
5. Resize the browser window to a narrower width and confirm the headers
   **wrap to multiple lines** rather than overflowing their cells.

---

## Feature 2: Text cell wrapping for char and many2one fields

### What to verify

Long values in character or many2one columns must wrap instead of being
clipped in read-only rows.

### Steps

1. Open any list view that contains a many2one or text column with long
   values (e.g. **Purchase > Products > Vendors** list).
2. Confirm that long product or partner names **wrap onto the next line**
   instead of being cut off.
3. Click a row to select it — the selected row uses Odoo's default edit
   behaviour and is not affected by this customization.
