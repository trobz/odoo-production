Bridge module automatically installed when both ``coop_sale`` and
``sale_timesheet`` are present.

It keeps the ``sale_timesheet`` dependency out of ``coop_sale`` so that
foodcoop instances running ``coop_sale`` without ``sale_timesheet`` are not
forced to install the latter.

Currently it:

* Hides the "Invoicing Policy", "Tracking", product tooltip and
  "Re-Invoicing Threshold" fields on the product form for *service*
  products, by inheriting the ``sale_timesheet`` product form view.
