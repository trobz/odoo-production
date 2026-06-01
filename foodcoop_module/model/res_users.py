from odoo import api, fields, models
from odoo.exceptions import AccessError


class ResUsers(models.Model):
    _inherit = "res.users"

    role_line_ids = fields.One2many(
        groups="base.group_erp_manager,foodcoop_module.functional_admin",
    )

    role_ids = fields.One2many(
        groups="base.group_erp_manager,foodcoop_module.functional_admin",
    )


class ResUsersRoleLine(models.Model):
    _inherit = "res.users.role.line"

    def _check_role_privilege(self, role):
        """Block non-sysadmin from assigning roles that grant functional_admin."""
        if self.env.user.has_group("base.group_system"):
            return
        restricted = self.env.ref(
            "foodcoop_module.functional_admin", raise_if_not_found=False
        )
        if not restricted:
            return
        if restricted in (role.group_id | role.implied_ids):
            raise AccessError(
                self.env._(
                    "You are not allowed to assign roles that grant "
                    "Foodcoop Administration privileges. "
                    "Please contact a system administrator."
                )
            )

    @api.model_create_multi
    def create(self, vals_list):
        role_ids = {vals["role_id"] for vals in vals_list if vals.get("role_id")}
        for role in self.env["res.users.role"].browse(role_ids):
            self._check_role_privilege(role)
        return super().create(vals_list)

    def write(self, vals):
        if "role_id" in vals:
            role = self.env["res.users.role"].browse(vals["role_id"])
            self._check_role_privilege(role)
        return super().write(vals)
