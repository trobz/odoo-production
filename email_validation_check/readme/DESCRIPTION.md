This module provides email validation functionality for partners in the cooperative membership system.

## Purpose

Ensure that partner email addresses are valid by sending a confirmation email with a unique validation link.

## Functionality

- Generates a unique validation string for partners with email addresses
- Sends automatic validation emails when partners are created or email is changed
- Validates email through a web-based confirmation link
- Shows warning on partner form for unvalidated emails
- Allows partners to request new validation emails

## Dependencies

- `coop_membership`: Base cooperative membership module

## License

AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
