This module overrides the default POS search behaviour so that when a
search term matches a record *exactly*, only that exact match is
returned. This gives cashiers a deterministic result when scanning
barcodes or typing cooperative numbers.

- **Products** – matched exactly against `display_name`, `barcode`, or
  `default_code`.
- **Partners** – matched exactly against `name`, `barcode`, `phone`,
  `mobile`, `email`, `vat`, or `contact_address`.

Partial searches continue to work as usual when no exact match is found.
