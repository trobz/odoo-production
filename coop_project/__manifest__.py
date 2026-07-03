{
    "name": "Coop - Project",
    "version": "18.0.1.0.0",
    "category": "Custom",
    "author": "Trobz, La Louve",
    "website": "https://github.com/AwesomeFoodCoops/odoo-production",
    "license": "AGPL-3",
    "depends": [
        "calendar",
        "project",
    ],
    "data": [
        "data/project_data.xml",
        "data/mail_template.xml",
        "view/mail_message_view.xml",
        "view/project_view.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "coop_project/static/src/scss/style.scss",
            "coop_project/static/src/xml/kanban.xml",
            "coop_project/static/src/js/calendar_renderer.esm.js",
            "coop_project/static/src/js/kanban_project_renderer.esm.js",
        ],
    },
    "test": [],
    "installable": True,
}
