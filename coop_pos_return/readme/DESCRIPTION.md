The standard POS return flow raises a `UserError` when no active session
is attached to the original order's session. This module catches that
error and locates the current user's open session automatically, then
creates the refund order in that session. Both the standard `_refund`
path and the partial-refund wizard (`action_partial_refund`) are
handled.
