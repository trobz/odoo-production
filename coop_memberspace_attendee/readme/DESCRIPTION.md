Extends the memberspace shift registration pages to display the number of
expected attendees (reserved seats) for each shift, and allows members to
view the full list of registered attendees.

Two tables are extended:

- **Programmer un extra**: the static list of available extra shifts gains an
  "Expected attendees" column showing the reserved seat count and a link to
  open the attendee list modal.
- **FTOP programmer modal** (`mywork_ftop`): the dynamic shift list inside the
  FTOP programmer dialog gains the same column, populated via the existing
  `ftop_get_shift` RPC call which is extended to include `seats_reserved` per
  shift.

The attendee list modal fetches member names on demand via
`shift.shift.get_expected_attendee()` and renders them inline without a full
page reload.

This module is designed to be inherited by site-specific modules that may
override the column label or appearance (e.g. `custom_sqq_vdm`).
