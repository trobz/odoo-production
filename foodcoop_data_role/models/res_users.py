from odoo import api, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.multi
    def check_access_buttons(self, res_model):
        """
        Check group current user to hide buttons
        """
        res = super(ResUsers, self).check_access_buttons(res_model)
        # F#T59241 - Add "Print Badge" function to "Member Manager" role
        if res == 'saisie_group_partner' and self.has_group(
                'foodcoop_data_role.group_Member_Manager'):
            res = False
        return res
