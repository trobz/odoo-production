# Usage

## Coefficient setup

- Go to `Sales` / `Configuration` / `Product Coefficients`.
- Create or update your coefficients.

## Product configuration

- Open a product (menu `Sales` / `Products` / `Products`).
- In the `Coefficients` page, select coefficients (1..9) as needed.
- Use the `Include in Cost` checkbox for the coefficients that must impact the product cost (`standard_price`).

## Understand the computed prices

- **Base Price**: derived from supplier information.
- **Theoretical Price**: computed sale price based on Base Price and configured coefficients.
- **Theoretical Cost**: computed cost based on Base Price and coefficients included in cost.

## Apply theoretical prices to products

**Single product**

On the product form:

- Use `Use Theoretical Price` to update the product `Sales Price`.
- Use `Use Theoretical Cost` to update the product `Cost`.

**Multiple products (wizard)**

From the product list view:

- Select products.
- Run the wizard `Use Theoretical Price`.

## Automatic updates (Settings)

The module adds settings under `Sales` settings (not in a dedicated app):

- `Update Base Price Automatically`
- `Update Theoretical Cost Automatically`
- `Update Theoretical Price Automatically`

These settings are stored in `ir.config_parameter` and are parsed as booleans.

## Nightly base price recomputation (Cron + queue.job)

A cron job exists to recompute base prices.

For performance, recomputation is split into **queue jobs**:

- Templates are split by batch (default: 100 templates per job).
- Each job recomputes the base price for its batch.

Prerequisites:

- `queue_job` must be installed and the job runner must be running.

## Troubleshooting

- If theoretical values are not updated after changing supplier info, run `Recompute Base price` on the product template.
- If cron is enabled but jobs are not executed, verify that the job runner is running and that `queue_job` is installed.
