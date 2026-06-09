After installation, grant the *PoS Access Control Buttons Group* to the
users who are allowed to change the pricelist, issue refunds, switch
fiscal positions, or open quotations from the POS interface.

1.  Go to **Settings → Users & Companies → Users**.
2.  Open the target user's form.
3.  In the **Other** section (or via **Technical → Security → Groups**
    if developer mode is active), add the group
    `coop_pos_custom / PoS Access Control Buttons Group`.

Users without this group will see the pricelist, refund,
fiscal-position, and quotation buttons present on the screen but
rendered as disabled.
