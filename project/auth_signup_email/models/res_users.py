# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models

class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model
    def create(self, values):
        # overridden to prevent sending invited email to user for sign up
        if self.env.user.company_id.prevent_signup_email:
            self = self.with_context(no_reset_password=True)
        return super(ResUsers, self).create(values)
