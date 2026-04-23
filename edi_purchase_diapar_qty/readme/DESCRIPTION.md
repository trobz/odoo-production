This module customizes the EDI Purchase functionality to handle quantity calculations and pricing based on package quantities and base prices.

The module provides the following customizations:

* Extends purchase order consolidation to support package-based quantity calculations when the price policy is set to "package"
* Overrides price field selection in supplier price lists to use "base_price" instead of standard price
* Overrides price field selection in product supplier info to use "base_price" instead of standard price

This module is part of the EDI Purchase Diapar suite and requires the following dependencies:
* edi_purchase_diapar_oca
* purchase_package_qty
* coop_purchase
