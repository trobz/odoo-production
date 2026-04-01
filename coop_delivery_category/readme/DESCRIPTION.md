This module adds delivery category functionality to the purchase system for cooperative management.

## Purpose

Allow grouping of products by delivery category to facilitate purchase order computation and management.

## Functionality

- Creates a new model "delivery.category" for categorizing products
- Adds many2many field to product.template for delivery categories
- Adds many2many field to computed.purchase.order for filtering
- Extends get_psi_domain method to filter products by delivery category

## Dependencies

- `purchase`: Base purchase module
- `purchase_compute_order`: Computed purchase order module

## License

AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
