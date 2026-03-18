# Usage (Functional test guide)

This guide is intended for functional consultants (FC) and testers.

## Pre-conditions

- Module `coop_shift_qualification` is installed.
- Module dependency `coop_membership` is installed.
- You have access rights to edit:

  - Partners (members)
  - Shift templates and registrations
  - Partner qualifications

- There is at least:

  - 1 shift template with some non-done shifts
  - 1 member (partner)
  - 1 qualification marked as leader (`is_leader = True`)

## Main screens

- **Partner Qualifications**

  - Model: `res.partner.qualification`
  - Menu: depends on deployment, typically under membership/coop configuration.

- **Partner form**

  - Field: `Qualifications` (Many2many)

- **Shift template**

  - Leaders: `shift.template.user_ids`

## Test scenarios

### Scenario A: Set partner as qualified leader (manual)

1. Open a partner.
2. Add at least one qualification where `is_leader = True`.

Expected:

- Partner field `is_qual_leader` becomes True.
- If the partner is currently participating in shift templates (current registration lines), then the partner is added as leader on:

  - shift template `user_ids`
  - all non-done shifts `user_ids`

If it fails:

- You may get an error message from `res.partner._get_leader_ftop_warning()` (for example related to ABCD/FTOP constraints).

### Scenario B: Remove leader qualification

1. Open the same partner.
2. Remove all leader qualifications (so no qualification with `is_leader = True` remains).

Expected:

- Partner `is_qual_leader` becomes False.
- Partner is removed from leaders on all non-done shifts of templates where they were leader.
- Partner `template_ids` becomes empty (leaders removed).

### Scenario C: Add a participant to a shift template registration line

1. Open a shift template.
2. Add a registration line so that the partner becomes a **current participant**.

Expected:

- The system calls `registration.update_leaders(partner)`.
- If the partner is qualified leader, they are added to:

  - `shift.template.user_ids`
  - all non-done `shift.user_ids`

### Scenario D: Remove participant (or set non-current)

1. Edit registration line so the partner is no longer a current participant, or delete the line.

Expected:

- The system removes the partner from template leaders and shift leaders accordingly.

### Scenario E: Qualification leader limit configuration

1. Go to Settings.
2. Set **Number of Leader** to `1`.
3. Try to mark 2 different qualification records as `is_leader = True`.

Expected:

- System blocks the second one with a validation error.

## Where to look when debugging

- Partner: `qualification_ids`, `is_qual_leader`, `template_ids`
- Shift template: `user_ids`
- Shifts: `user_ids` (excluding state `done`)
- Logs/errors: validation error messages when violating leader assignment constraints.
