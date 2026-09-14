This is a glue module between `pos_event` and `pos_user_restriction`.

`pos_event` lets cashiers sell event tickets from the Point of Sale. When
an order that contains event tickets is validated, the corresponding
`event.registration` records (and their answers) are created on the
backend on behalf of the cashier.

`pos_event` grants the required access rights to
`point_of_sale.group_pos_user` only. Users restricted through
`pos_user_restriction` belong to
`group_assigned_points_of_sale_user` instead, which does **not** inherit
those rights. As a result, such users get an `AccessError` and cannot
validate an order that contains event tickets.

This module grants `group_assigned_points_of_sale_user` the minimal set
of access rights it needs to persist event registrations from the Point
of Sale, without giving it back-office rights to create or edit events.

It installs automatically whenever both `pos_event` and
`pos_user_restriction` are installed.
