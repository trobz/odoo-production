# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Show Attendees on Memberspace",
    "version": "18.0.1.0.0",
    "category": "Tools",
    "summary": """""",
    "author": "Trobz, La Louve",
    "website": "https://github.com/AwesomeFoodCoops/odoo-production",
    "license": "AGPL-3",
    "depends": [
        "coop_memberspace",
    ],
    "data": [
        "views/my_work.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "coop_memberspace_attendee/static/src/scss/coop_memberspace_attendee.scss",
            "coop_memberspace_attendee/static/src/js/programmer_un_extra.esm.js",
            "coop_memberspace_attendee/static/src/js/programmer_une_vacation.esm.js",
        ],
    },
}
