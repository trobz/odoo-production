To configure the signup email behavior:

1. Go to **Settings > General Settings**
2. Scroll to the **Users** section
3. Find the **Prevent Signup Email** option (visible only for Technical Features users)
4. Check the box to prevent sending invitation emails when creating new users
5. Uncheck the box to allow Odoo to send standard signup invitation emails
6. Click **Save**

**Note**: This setting is enabled by default. When enabled, new users will not receive the automatic "Settings: New User Invite" email during user creation.

**Technical Details**: The setting applies at the company level, so multi-company installations can have different configurations per company. The email prevention only affects signup-type password reset actions triggered during user creation (when the context includes `create_user`).
