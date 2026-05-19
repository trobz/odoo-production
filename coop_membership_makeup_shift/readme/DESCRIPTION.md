# Description

The **Makeup Shift for Standard Member** module allows standard cooperative members
who missed a shift to self-register for a make-up shift directly from the memberspace
website portal.

## Key Features

- **Self-service make-up registration**: Members can browse and register for available
  shifts from the website without staff intervention
- **Eligibility enforcement**: Only members with a negative ABCD counter
  (`final_standard_point < 0`) in `alert`, `suspended`, or `delay` state can register
- **Real-time feedback**: Seat count updates immediately after registration; error modal
  shown if the member is ineligible or no seats remain
- **Company-level toggle**: Administrators can enable or disable the make-up shift
  feature per company via the Settings page
- **Makeup flag on registration**: Every registration created through this flow has
  `is_makeup = True`, allowing downstream logic to distinguish make-up from regular
  registrations
- **Exchange integration**: `_is_replacing_makeup_shift()` lets the exchange system
  detect when a replacing registration is covering a make-up shift

## Cooperative States Eligible for Make-up

| State | Description |
|-------|-------------|
| `alert` | Member missed a shift; within the grace period |
| `suspended` | Grace period expired; member is suspended |
| `delay` | Member has been granted a delay extension |

## Dependencies

| Module | Purpose |
|--------|---------|
| `coop_memberspace` | Provides the memberspace portal, `programmer_modal`, `modal_error` templates, and `shift_makeup` company field |
