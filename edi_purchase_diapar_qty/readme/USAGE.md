This module is automatically installed and configured when installing the edi_purchase_diapar_oca module with its dependencies.

**Package Quantity Calculation:**

When processing purchase orders with a "package" price policy:
1. The module returns the `product_qty_package` instead of the standard quantity during consolidation
2. This ensures accurate quantity handling for products sold in packages

**Base Price Configuration:**

For supplier price lists and product supplier info:
1. The module configures the price field to use "base_price" 
2. This allows using alternative price fields for EDI purchase processing
