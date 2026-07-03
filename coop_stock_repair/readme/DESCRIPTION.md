This module restricts access to the repair count field and button added
by the *Repairs* module on the stock picking form.

The `repair` module adds a repair count field/button on the stock picking
form without any group restriction. Because Odoo evaluates the field even
when it stays hidden, users without Inventory access (e.g. POS cashiers)
hit an Access Error when opening a picking form, instead of simply not
seeing the button.

Not every coop installs the `repair` module, so this adjustment lives in
its own module instead of adding a hard dependency on `repair` in
`coop_stock`.
