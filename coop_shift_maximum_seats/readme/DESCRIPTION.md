This module adds a company-level policy to control how the maximum available
seats are managed for Shifts and Shift Templates.

Two modes are available:

- **Manual**: The maximum seats per ticket are set manually by the user.
- **Auto**: The maximum seats per ticket are calculated automatically based
  on the shift's total **Maximum Attendees Number**, distributing the
  remaining capacity proportionally as registrations change.
