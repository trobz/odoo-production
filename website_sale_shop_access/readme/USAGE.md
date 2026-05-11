## Restricting Website Pages by Group

1. Go to **Website → Pages** and open the desired page via the technical
   Settings button (🐛), or navigate to **Technical → User Interface → Views**
   and open the corresponding view.
2. Set **Visibility** to *Restricted Group*.
3. In the **Access Rights** tab, add the security groups that should be able
   to see the page.
4. Save. The page will only be visible to users who belong to at least one of
   the selected groups. Users outside those groups will not see the page even
   if it is published.

Leaving the groups empty (while keeping *Restricted Group* visibility) is not
useful — use *Public* or *Connected* visibility instead.

## Restricting Menu Items by Group

1. Go to **Website → Configuration → Menus** and open the menu entry to
   restrict.
2. In the **Visible Groups** field, select one or more security groups.
3. Save. The menu item will only appear for users who belong to at least one
   of the selected groups.

## Shop Access (logged-in users only)

Restricting the ``/shop`` to logged-in users is handled by Odoo's built-in
setting: **Website → Configuration → Settings → Shop → Who can buy** →
select *Logged in users*.
