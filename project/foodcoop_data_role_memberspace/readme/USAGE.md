This module configures the Member role for the Foodcoop memberspace system.

## Features

- Automatically creates "Member" user group and role
- Restricts access rights for members through dedicated groups
- Assigns new memberspace users to the Member role automatically
- Provides a demo member user for testing

## Configuration

1. Install the module
2. The "Member" role and groups will be automatically created
3. New users created through memberspace will be automatically assigned the Member role
4. The role includes implied groups:
   - Restrict rights for Member
   - Memberspace group from coop_memberspace

## Demo Data

- A demo member user is created with login: `member@example.com`
- This user is assigned the Member role automatically

## Requirements

- This module depends on:
  - `foodcoop_data_role`
  - `coop_memberspace`
