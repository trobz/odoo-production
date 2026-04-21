Go to **Point of Sale → Configuration → Settings** and locate the **Scrap Order** section.

Set the **Scrap Order Option** field to one of the following values:

| Option | Behaviour |
|--------|-----------|
| **No Scrap Order** | Scrap buttons are hidden in POS. No scrap order can be created. |
| **Create and validate for products with stock only** *(default)* | Creates scrap orders and validates them only if the product has sufficient on-hand quantity. |
| **Always create, validate if has stock** | Always creates scrap orders; validates them only when stock is available. |
| **Always create, validate regardless of stock** | Always creates and validates scrap orders, even if on-hand quantity is zero or negative. |
