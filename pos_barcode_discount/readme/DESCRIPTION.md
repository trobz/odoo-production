This module extends Odoo Point of Sale to apply discounts by product categories using barcode scanning.

## Purpose

Enables POS users to apply discounts to specific product categories by scanning discount barcodes, with configurable category restrictions.

## Functionality

- Adds barcode rule for discounted product categories (EAN13 pattern: 22{NN}........)
- Configures POS to apply discounts based on product categories
- Adds settings to enable/disable discount by category feature
- Allows selecting specific product categories for discount application
- Displays confirmation dialog when applying discounts to configured categories
- Shows error message when discount doesn't apply to a product category
- Computes all child categories for discount application

## Dependencies

- `point_of_sale`: Odoo Point of Sale module

## License

AGPL-3.0 (http://www.gnu.org/licenses/agpl.html)
