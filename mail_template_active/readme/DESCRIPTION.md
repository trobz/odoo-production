This module adds archive functionality to mail templates in Odoo, allowing you to deactivate email templates without deleting them permanently.

In standard Odoo, mail templates can only be deleted, which means losing the template configuration entirely. This module extends the mail template form view to include:

- An **active** field that enables archiving/unarchiving templates
- A visual **"Archived" ribbon** displayed on archived templates for easy identification

This is particularly useful when:

- You want to temporarily disable certain email templates without losing their configuration
- Managing seasonal or event-specific templates that are only needed at certain times
- Testing new templates while keeping old versions available for reference
- Maintaining a clean active template list while preserving historical templates

Archived templates are hidden from the default view but can be easily restored when needed by using the standard Odoo archive filter.
