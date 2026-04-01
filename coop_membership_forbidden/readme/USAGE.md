This module adds the ability to mark partners as "forbidden members" in the cooperative membership system.

## Features

- Mark a partner as a forbidden member
- When a partner is marked as forbidden, their working state is automatically set to "blocked"
- A custom error message is displayed for forbidden members when they try to enter the store
- Only users with the "Manage forbidden member" group can modify the forbidden status

## Configuration

1. Go to Settings > Users & Companies > Groups
2. Assign the "Manage forbidden member" group to users who should be able to manage forbidden members
3. On partner form, the "Forbidden member" checkbox is visible but read-only by default
4. Users with the "Manage forbidden member" group can edit the "Forbidden member" checkbox
