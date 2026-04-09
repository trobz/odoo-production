## Copy Expected Quantities on a Picking

1. Navigate to **Inventory > Operations > Transfers**.
2. Open any transfer in the `Ready` or `In Progress` state.
3. In the **Detailed Operations** tab, click the **Copy Expected Qtys** button.
4. The system copies the `Demand` quantity into the `Done` quantity and the
   package quantity for each move line, removing the need to enter quantities
   manually when receiving a full shipment.

## Barcode Search for Inactive Products

When scanning a barcode during a receipt, inventory adjustment, or POS session,
the system automatically includes archived (inactive) products in the search
results if the search is barcode-based. This ensures that products archived in
error or temporarily deactivated can still be located and processed.

Note: Name-based product searches continue to respect the active filter and will
not return inactive products.

## Backdating an Inventory Adjustment

Two methods are available for preserving or overriding the inventory date when
validating an inventory adjustment:

**Method 1 — Using the `inventory_date` field on the quant:**

1. Navigate to **Inventory > Operations > Physical Inventory**.
2. Locate the quant (stock line) you want to adjust.
3. Set the **Inventory Date** field to the desired historical date.
4. Validate the adjustment. The system uses this date when creating the
   corresponding stock move, preserving the backdated timestamp.

**Method 2 — Using the `inventory_datetime` context key (developer/technical):**

Pass `inventory_datetime` in the calling context when triggering the inventory
move programmatically. The module's override of `_get_inventory_move_values()`
reads this key and sets the move date accordingly. This is typically used by
automated scripts or integrations that need to import historical inventory.

## Inventory Valuation Report with Category Filter

1. Navigate to **Inventory > Reporting > Inventory Valuation**.
2. Use the **Product Category** filter to restrict the report to a specific
   category or category hierarchy.
3. The report automatically excludes consumable products from valuation totals
   (consumables are shown for reference but not included in stock value).
4. To view historical valuation, select a past date in the date field. The report
   applies date-aware context to return inventory values as of that date.
5. Click **Export to Excel** to download the report in `.xlsx` format for
   offline analysis or reporting to cooperative management.

## POS Picking Validation (Managers)

When a point-of-sale session is closed, the system may encounter POS orders with
zero-quantity moves (e.g., from cancelled or voided items). These invalid pickings
are handled automatically:

1. The `pos.order` model detects zero-quantity moves after session close.
2. Validation is queued as an asynchronous job via `queue_job`, processing up to
   100 orders per job to avoid request timeouts.
3. Managers can monitor job progress under **Technical > Queue Jobs** (if the
   `queue_job` app is visible in the menu) or via the job queue dashboard.
4. Failed jobs will appear in the queue with an error state and can be retried
   individually.

No manual intervention is required under normal circumstances. If jobs remain
in a failed state, review the job's exception details for root cause information.
