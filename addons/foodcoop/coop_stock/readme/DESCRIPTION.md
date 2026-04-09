# Description

The `coop_stock` module extends Odoo's core stock management with custom features
tailored for food cooperative operations. It addresses the specific needs of food
cooperatives around inventory accuracy, vendor traceability, product lifecycle
management, and point-of-sale integration.

This module builds on top of Odoo's `stock` and `stock_account` apps, adding
cooperative-specific workflows such as backdated inventory adjustments, vendor
product code visibility on pickings, and asynchronous POS picking validation for
high-volume environments.

The inventory valuation report is enhanced to support category-level filtering,
consumable product handling, and date-aware historical valuation with Excel export,
giving cooperative managers the financial visibility they need for accurate stock
accounting.

## Main Features

- **Vendor Product Code on Pickings** — Displays vendor-specific product codes on
  stock move lines based on the picking's partner, improving traceability during
  reception and preparation.
- **Copy Expected Quantities** — One-click button on the picking form to synchronize
  expected quantities (`product_uom_qty`) with actual quantities (`quantity`) and
  package quantities, reducing manual data entry.
- **Inventory Date Preservation** — Preserves inventory dates through move creation
  and supports backdating via the `inventory_datetime` context key or the quant's
  `inventory_date` field.
- **Inactive Product Barcode Search** — Barcode-based product searches include
  inactive products so that archived items can still be identified during receiving
  or inventory operations.
- **Product Active/Inactive Sync** — Automatically manages the product template's
  active status based on variant status, preventing orphaned active templates with
  all-inactive variants.
- **Async POS Picking Validation** — Handles invalid POS pickings (zero-quantity
  moves) asynchronously via `queue_job`, processing up to 100 orders per job to
  avoid timeouts during high-volume close-of-day operations.
- **Product Category Type** — Adds a View/Normal type field to product categories
  for hierarchical organization aligned with cooperative product structures.
- **Enhanced Inventory Valuation Report** — Extended with product category names,
  consumable filtering, date-aware historical valuation, and Excel export.
