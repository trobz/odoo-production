This module extends `website_sale_checkout_skip_payment` to enable the
*Skip Payment* option by default for all partners.

When installed, the field `skip_website_checkout_payment` on `res.partner` is
set to `True` by default, so new partners will automatically bypass the
payment step during the website checkout process without requiring manual
configuration.
