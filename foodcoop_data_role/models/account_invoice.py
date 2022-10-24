# Copyright 2019 Coop IT Easy SCRLfs
# @author Pierrick Brun <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
            toolbar=False, submenu=False):
        res = super(AccountInvoice, self).fields_view_get(
            view_id, view_type, toolbar, submenu)
        if self.user_has_groups(
                "foodcoop_data_role.group_member_accountant_restrict") and \
            res.get("toolbar", {}).get("action"):
            del res["toolbar"]["action"]
        return res
