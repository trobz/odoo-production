This module controls access to POS control buttons using a security group.

A new security group *PoS Access Control Buttons Group* gates the
pricelist, refund, fiscal-position, and quotation buttons in the POS
interface. Users who do not belong to the group see those buttons
disabled. Group membership is resolved at session load time and pushed
to the frontend so no extra round-trip is needed.
