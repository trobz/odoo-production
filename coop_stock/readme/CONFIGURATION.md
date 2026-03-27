# Configuration

## Product Category Type

The module adds a **Type** field to product categories with two options:

| Value  | Description |
|--------|-------------|
| View   | Structural/parent category used for grouping only; not assigned to products directly |
| Normal | Leaf category that can be assigned to products |

To configure category types:

1. Navigate to **Inventory > Configuration > Product Categories**.
2. Open a category.
3. Set the **Type** field to `View` for parent/grouping categories or `Normal`
   for categories assigned directly to products.
4. Use `View` categories to build a hierarchy (e.g., `Food > Fresh > Dairy`)
   while only `Normal` categories are selectable on product forms.

## queue_job — Required for Async POS Picking Validation

The `queue_job` module is a required dependency and must be installed and
operational for asynchronous POS picking validation to function correctly.

Ensure the following before using POS features:

- The `queue_job` module is installed (listed under **Apps**).
- At least one Odoo worker process is running in addition to the main HTTP
  worker, so that queued jobs are processed. In production, this typically
  means starting Odoo with `--workers=N` (where N >= 2) and ensuring the
  job runner is active.
- Refer to the [OCA queue_job documentation](https://github.com/OCA/queue)
  for detailed worker and channel configuration.

If `queue_job` workers are not running, POS picking validation jobs will
accumulate in the queue without being processed.

## purchase_package_qty — Required for Package Quantity Sync

The `purchase_package_qty` module is a required dependency that provides the
package quantity field on purchase order lines and stock move lines.

The **Copy Expected Qtys** button on the picking form synchronizes package
quantities in addition to done quantities. Without `purchase_package_qty`
installed, this package sync step will have no effect, but the module will
otherwise function normally.

No additional configuration is needed for `purchase_package_qty` beyond its
installation.

## Other Features

No additional configuration is required for the following features. They are
active as soon as the module is installed:

- Vendor product code display on stock move lines
- Inactive product barcode search
- Product active/inactive status synchronization
- Inventory date preservation on adjustments
