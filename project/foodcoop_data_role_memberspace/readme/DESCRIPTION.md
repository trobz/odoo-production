This module provides role configuration for Foodcoop Memberspace.

## Purpose

Defines the "Member" role and associated user groups for the Foodcoop memberspace system, enabling proper access rights for cooperative members.

## Functionality

- Creates a "Member" user group for memberspace access
- Creates a "Restrict rights for Member" group with hidden category
- Defines a "Member" role linked to the user groups
- Provides a demo member user account
- Automatically assigns new memberspace users to the Member role
- Extends res.partner to handle member role assignment

## Dependencies

- `foodcoop_data_role`: Base role configuration for Foodcoop
- `coop_memberspace`: Memberspace functionality module

## License

AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
