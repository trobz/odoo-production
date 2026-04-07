This module extends the cooperative membership functionality by adding the ability to mark partners as "forbidden members".

## Purpose

This module allows administrators to mark certain partners as forbidden, which prevents them from entering the store and blocks their working state.

## Functionality

- Adds a boolean field `is_forbidden` on partners
- Automatically sets the working state to "blocked" for forbidden members
- Displays a custom error message for forbidden members
- Provides group-based access control for managing forbidden status

## Dependencies

- `coop_membership`: Base cooperative membership module
- `coop_badge_reader`: Badge reader integration

## License

AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
