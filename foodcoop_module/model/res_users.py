from odoo import fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    role_line_ids = fields.One2many(
        groups="base.group_erp_manager,foodcoop_module.functional_admin",
    )

    role_ids = fields.One2many(
        groups="base.group_erp_manager,foodcoop_module.functional_admin",
    )
