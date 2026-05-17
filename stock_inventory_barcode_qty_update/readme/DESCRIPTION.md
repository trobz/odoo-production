Extends the barcode inventory wizard (`stock_inventory_barcode`) to support
two counting modes and ties scans directly to a named inventory session
(`stock_inventory`).

Key additions:

- **Add Qty mode**: each barcode scan increments a per-product counter
  (`new_change_qty`). Scanning the same product again keeps incrementing the
  counter; switching to a different product resets it to 1.
- **Change Qty mode**: the quantity field is pre-filled with the value already
  recorded for that product/lot in the session, ready for manual correction.
- **Use Latest Qty** option (Add Qty mode only): when enabled, the counter
  starts from the quantity already recorded in the session instead of zero,
  so successive scans add on top of previously counted quantities.
- Scans are always linked to the active inventory session via
  `current_inventory_id` on `stock.quant`, keeping adjustments isolated from
  concurrent sessions on other locations.
- The barcode input field and scan settings remain visible after each update,
  so operators can scan continuously without extra clicks.
