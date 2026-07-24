This module serves as an installer for the Foodcoop system.

## Features

- Creates "Foodcoop Administration" user group
- Provides access rights for user management
- Adds administration menu for managing users
- Customizes user views to restrict access rights

## Configuration

1. Install the module
2. The "Foodcoop Administration" group will be automatically created
3. Users with this group can access the Administration menu
4. The group has specific access rights to:
   - res.users model (full access)
   - res.users.role model (read only)
   - res.users.role_line model (full access)

## Requirements

- This module depends on:
  - `auth_signup`
  - `base_user_role`
