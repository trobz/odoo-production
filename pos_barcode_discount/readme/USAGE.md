This module enables discount application by product categories in POS using barcode scanning.

## Features

- Scan discount barcodes (pattern: 22{NN}........) to apply discounts
- Configure which product categories are eligible for discounts
- Automatic validation of discount applicability based on product category
- Confirmation dialog when applying discounts to restricted categories
- Error notification for products not eligible for discount

## Configuration

1. Install the module
2. Go to Point of Sale > Configuration > Settings
3. Enable "Discount By Categories" option for your POS configuration
4. Select the product categories that are eligible for discounts
5. If no categories are selected, discounts apply to all products

## Usage

1. In POS interface, scan a discount barcode (starting with 22)
2. If discount by category is enabled and categories are configured:
   - If product belongs to allowed category: confirmation dialog appears
   - If product doesn't belong to allowed category: error message is shown
3. If discount by category is disabled or no categories configured: normal discount behavior

## Requirements

- This module depends on:
  - `point_of_sale`
