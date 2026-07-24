This module adds a configuration option to prevent Odoo from automatically sending signup invitation emails when creating new users.

By default, Odoo sends an email notification ("Settings: New User Invite") to newly created users with their login credentials. This module allows you to disable this behavior at the company level, which is useful when:

- Creating users programmatically via API or scripts
- Bulk importing users where you want to send custom welcome emails
- Managing user credentials through an external system
- Testing or development environments where email notifications are not desired

The setting is enabled by default to prevent accidental email sending during user creation.
