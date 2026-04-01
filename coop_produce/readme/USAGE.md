# Usage

## Product setup

- Open a product form.
- Set the product packaging so the computed `default_packaging` is filled from the first packaging quantity.
- Link vendor information when you want to use supplier-based inventory initialization.

## Inventory workflow

- Open an inventory adjustment using the Coop Produce form.
- Set the inventory date and one or more stock locations.
- Optionally enable `Exclude sublocation` if only the selected locations must be considered.
- Use `Product categories` and/or `Suppliers` in the initialization area.
- Click `Add` to load matching products into the inventory.

What the add action does:

- It builds the product list from the selected categories and suppliers.
- It creates missing stock quants when a matching product has no quant yet in the selected location scope.
- It moves the inventory to `In Progress` and prepares the selected products for counting.

## Counting and validation

- Review the generated inventory lines.
- `Default Packaging` shows the packaging quantity coming from the product.
- Enter `Stock Quantity` in packaging units.
- Use `Init Qties` if you want to initialize the counted quantity from the theoretical quantity.
- Click `Validate` to finish the inventory.

If the inventory is validated with the `check_date_begin` context and no `Week planning start date` is set, the module opens the dedicated wizard first.

## Week planning

- Once the inventory is done, set `Week planning start date` if needed.
- Click `Generate Week Planification`.
- The module creates an `order.week.planning` record initialized from the inventory lines.
- Complete daily quantities on the planning and generate purchase orders from the planning flow.
