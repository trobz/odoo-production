# Coop Shift Qualification

## Purpose
This module manages **shift leader qualification** for members and ensures that leader assignments on shift templates/shifts stay consistent with a partner's qualifications.

It adds:

- A new model `res.partner.qualification`.
- A Many2many on `res.partner` to assign qualifications.
- Synchronization logic between:

  - Partner qualifications (leader/non-leader)
  - Shift template leaders (`shift.template.user_ids`)
  - Shift leaders (`shift.user_ids` for shifts not in state `done`)

## Main business rules

- A partner becomes a **"qualified leader"** (`res.partner.is_qual_leader = True`) when they have at least one qualification where `is_leader = True`.
- When a partner is a qualified leader and is a **current participant** of a shift template registration, they can be automatically added as a leader on:

  - The related shift template (`shift.template.user_ids`)
  - All non-done shifts of that template (`shift.user_ids`)

- When a partner is removed from being leader (no leader qualification or removed from registration), the partner may be removed from:

  - `shift.template.user_ids`
  - all non-done `shift.user_ids`

- A partner cannot be assigned as leader in some cases. The validation message comes from `res.partner._get_leader_ftop_warning()`.

## Technical overview (for reviewers)

### Key models and methods

- `res.partner.qualification`

  - Constraint: qualification `name` length limited to 5.
  - Compute: `can_be_leader` computed from config parameter `coop_shift_qualification.nb_of_leader` and current number of leader qualifications.

- `res.partner`

  - Field: `qualification_ids` (Many2many) with inverse method `_inverse_update_shift_leader()`.
  - Compute: `is_qual_leader` + `qualifications` (stored).
  - Method: `_inverse_update_shift_leader()` updates shift leaders based on qualification.

- `shift.template`

  - Method: `update_qualification(partners, action="add"|"del", raise_error=True)`

    - Adds/removes leader qualification on partners based on their participation and template assignment.

- `shift.template.registration`

  - Method: `update_leaders(partners, action="add"|"del")`

    - Adds/removes partners in leaders of the template and non-done shifts.

- `shift.template.registration.line`

  - Overrides `create/write/unlink` to call `registration.update_leaders()`.

### Post init hook

- `post_init_hook()` calls `res.partner.qualification._update_partner_qualification()` to synchronize qualifications to existing templates after installation.

## Notes about performance changes (18.0)

The 18.0 implementation uses batching where possible to minimize repeated M2M updates:

- Batch updates for shift leader assignment/removal (`shifts.user_ids |= partner` / `shifts.user_ids -= partner`).
- Batch qualification add/remove using `write()` with M2M commands.

These changes are intended to keep the same behavior with fewer ORM operations.
