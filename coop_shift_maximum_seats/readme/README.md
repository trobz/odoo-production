# Shift: Maximum Available Seats

This module adds a company-level policy to control how the maximum available
seats are managed for Shifts and Shift Templates.

Two modes are available:

- **Manual**: The maximum seats per ticket are set manually by the user.
- **Auto**: The maximum seats per ticket are calculated automatically based
  on the shift's total **Maximum Attendees Number**, distributing the
  remaining capacity proportionally as registrations change.

## Features

- **Company-level policy**: Configure the mode once in company settings; all
  new Shifts and Shift Templates inherit it automatically.
- **Auto mode**: When a registration is created, updated, or deleted, the
  `seats_max` of each ticket is recalculated in real time so the total never
  exceeds the shift's `seats_max`.
- **Read-only enforcement**: In Auto mode, the *Seats Availability* field and
  the per-ticket *Maximum Seats* column are locked in the UI to prevent
  manual overrides.
- **Exchange policy guard**: Auto mode is incompatible with the
  *Participations put into exchange plus available standard seats plus
  available FTOP seats* exchange policy. A validation warning is shown if the
  user tries to combine the two.

## Configuration

1. Go to **Settings > Shifts** (or the Coop Membership configuration form).
2. Under **Maximum available ABCD/FTOP seats**, choose:
   - *Add Maximum available ABCD/FTOP seats manually* — default, manual control.
   - *Calculate Maximum available ABCD/FTOP seats automatically based on
     Maximum Attendees Number* — automatic calculation.
3. Save. Existing open Shifts and Shift Templates are updated immediately.

## Usage

### Manual mode

Set the **Maximum Seats** value on each ticket line directly on the Shift or
Shift Template form. The field remains editable.

### Auto mode

Set the **Maximum Attendees** field on the Shift or Shift Template. The
module distributes available capacity across ticket lines automatically:

```
ticket.seats_max = shift.seats_max - total_reserved + ticket.seats_reserved
```

The per-ticket **Maximum Seats** field and the **Seats Availability** field
become read-only. Values are updated whenever a registration is added,
changed, or removed.

## Authors

- Trobz
- La Louve
