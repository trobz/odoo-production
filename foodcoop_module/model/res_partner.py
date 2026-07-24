from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    signup_type = fields.Char(
        groups="base.group_erp_manager,foodcoop_module.functional_admin"
    )
