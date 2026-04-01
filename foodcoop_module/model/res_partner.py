from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    signup_token = fields.Char(
        groups="base.group_erp_manager,foodcoop_module.functional_admin"
    )
    signup_type = fields.Char(
        groups="base.group_erp_manager,foodcoop_module.functional_admin"
    )
    signup_expiration = fields.Datetime(
        groups="base.group_erp_manager,foodcoop_module.functional_admin"
    )
