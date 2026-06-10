{
    "name": "Coop - Web",
    "version": "18.0.1.0.0",
    "category": "Custom",
    "summary": "Global UI customizations for all foodcoop instances",
    "author": "Trobz, La Louve",
    "website": "https://github.com/AwesomeFoodCoops/odoo-production",
    "license": "AGPL-3",
    "depends": [
        "web",
    ],
    "assets": {
        "web.assets_backend": [
            "coop_web/static/src/scss/list_view.scss",
        ],
    },
    "installable": True,
}
