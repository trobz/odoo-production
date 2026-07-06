{
    "name": "Website Coop Custom",
    "version": "18.0.1.0.0",
    "category": "Website",
    "summary": "Customise the website header layout for food-coop sites",
    "author": "Trobz",
    "website": "http://www.trobz.com",
    "license": "LGPL-3",
    "depends": [
        "website",
    ],
    "data": [
        "views/website_templates.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "website_coop_custom/static/src/scss/website_coop_custom.scss",
        ],
    },
    "installable": True,
}
