This module extends Odoo 18's built-in group-based visibility mechanism so
that website pages and menu items are hidden from users who do not belong to
the required security groups.

- **Website pages**: when a page's visibility is set to *Restricted Group*
  and one or more groups are specified, the page's ``is_visible`` flag is set
  to ``False`` for users outside those groups. This prevents the page from
  appearing in menus and other visibility-aware listings.
- **Website menus**: menu items with *Visible Groups* configured are hidden
  from users who do not belong to at least one of the specified groups.

Access to the ``/shop`` routes for logged-in users only is handled natively
by Odoo 18's ``ecommerce_access`` setting on the website (Website →
Configuration → Settings → *Who can buy*).
