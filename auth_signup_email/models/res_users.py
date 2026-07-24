# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class ResUsers(models.Model):
    _inherit = "res.users"

    def _action_reset_password(self, signup_type="reset"):
        """
        Skip sending invite email on user creation
        when prevent_signup_email is enabled.
        """
        if signup_type == "signup" and self.env.context.get("create_user"):
            self = self.filtered(lambda u: not u.company_id.prevent_signup_email)
            if not self:
                return
        return super()._action_reset_password(signup_type=signup_type)
