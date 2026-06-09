This module provides custom enhancements to the Point of Sale for a
cooperative grocery context. It extends the standard `point_of_sale`,
`pos_sale`, `coop_point_of_sale`, `purchase_compute_order`, and
`pos_order_return` modules with the following features:

**Access Control for POS Control Buttons**

A new security group *PoS Access Control Buttons Group* gates the
pricelist, refund, fiscal-position, and quotation buttons in the POS
interface. Users who do not belong to the group see those buttons
disabled. Group membership is resolved at session load time and pushed
to the frontend so no extra round-trip is needed.

**Exact-match Search in POS**

The default POS search returns any record whose fields *contain* the
search string. This module overrides that behaviour so that when a term
matches a record *exactly*, only the exact match is returned, giving
cashiers a deterministic result when scanning barcodes or typing
cooperative numbers.

- **Products** – matched exactly against `display_name`, `barcode`, or
  `default_code`.
- **Partners** – matched exactly against `name`, `barcode`, `phone`,
  `mobile`, `email`, `vat`, or `contact_address`.

**Robust POS Order Return / Refund**

The standard return flow raises a `UserError` when no active session is
attached to the original order's session. This module catches that error
and locates the current user's open session automatically, then creates
the refund order in that session. Both the standard `_refund` path and
the partial-refund wizard (`action_partial_refund`) are handled.

**Partner List UI (French labels)**

The partner selection screen is trimmed for the cooperative workflow:

- The *Address* and *Email* columns are removed to reduce visual noise.
- Column headers are relabelled in French: *Nom*, *N° Coop*, *Statut*.

**Purchase Compute Order – Discount Field Label**

The *Discount* field on the computed purchase order form is relabelled
to *Discount (%)* to make the unit explicit for purchasing staff.
