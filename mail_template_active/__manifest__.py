{
    "name": "Mail template active",
    "version": "12.0.1.0.0",
    "category": "Custom",
    "description": """Add new field 'active' to mail.template model to allow
    deactivating mail templates without deleting them.""",
    "summary": "Add active field to mail templates",
    "license": "AGPL-3",
    "author": "Trobz",
    "website": "https://github.com/AwesomeFoodCoops/odoo-production",
    "depends": [
        "mail",
    ],
    "data": [
        "views/mail_template_views.xml",
    ],
    "test": [],
}
