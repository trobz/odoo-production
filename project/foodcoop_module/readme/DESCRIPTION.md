This module is the installer for the Foodcoop system.

## Purpose

Provides the foundation for managing a food cooperative by setting up user groups, access rights, and menus necessary for administration.

## Functionality

- Creates the "Foodcoop Administration" group with specific permissions
- Grants full access to res.users model for administrators
- Provides read-only access to user roles
- Adds custom administration menu
- Customizes user form view with access restrictions

## Dependencies

- `auth_signup`: For user signup functionality
- `base_user_role`: For role-based access control

## License

AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
