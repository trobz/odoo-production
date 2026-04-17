{
    "name": "Coop Memberspace Cancelation",
    "version": "18.0.1.0.0",
    "category": "Custom",
    "summary": "Standard member can cancel his shifts",
    "author": "La Louve, Trobz",
    "license": "AGPL-3",
    "website": "https://github.com/AwesomeFoodCoops/odoo-production",
    "depends": [
        "coop_memberspace",
    ],
    "data": [
        "views/website_view.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "coop_memberspace_cancelation/static/src/js/exchange_shift.esm.js",
        ],
    },
    "installable": True,
    "application": False,
}
