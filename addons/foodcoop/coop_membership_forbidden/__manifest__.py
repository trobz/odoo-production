# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Coop membership - forbidden member",
    "version": "18.0.1.0.0",
    "category": "Tools",
    "summary": "Mark partners as forbidden members in cooperative membership",
    "author": "Trobz, La Louve",
    "website": "https://github.com/AwesomeFoodCoops/odoo-production",
    "license": "AGPL-3",
    "depends": [
        "coop_membership",
        "coop_badge_reader",
    ],
    "data": [
        "security/res_groups.xml",
        "views/res_partner_view.xml",
    ],
}
