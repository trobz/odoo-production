# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


def post_init_hook(env):
    env["res.partner.qualification"]._update_partner_qualification()
