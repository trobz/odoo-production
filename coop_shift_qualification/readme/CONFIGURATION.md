# Configuration

## System parameter

- `coop_shift_qualification.nb_of_leader`

  - Type: integer
  - Default: `1`
  - Meaning: maximum number of qualification records (`res.partner.qualification`) that can be marked as leader (`is_leader = True`).

## Settings UI

In Settings (`res.config.settings`), the module adds:

- **Number of Leader** (`nb_of_leader`)

This field is stored as config parameter `coop_shift_qualification.nb_of_leader`.

## Data loaded

- `data/res_partner_qualification.xml`

This file defines the default qualification records used by the coop.

## Important functional constraints

- Qualification `name` is limited to 5 characters.
- When setting a qualification as leader (`is_leader = True`), the total number of leader qualifications cannot exceed `coop_shift_qualification.nb_of_leader`.
