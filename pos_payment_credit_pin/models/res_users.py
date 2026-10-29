from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import consteq


class ResUsers(models.Model):
    _inherit = "res.users"

    pos_security_pin = fields.Char(
        string="POS Security PIN",
        help="Numeric PIN to authorize credit payment validation in the Point of Sale.",
        groups="point_of_sale.group_pos_manager",
        copy=False,
    )

    @api.constrains("pos_security_pin")
    def _check_pos_security_pin(self):
        for user in self:
            if user.pos_security_pin and not user.pos_security_pin.isdigit():
                raise ValidationError(
                    self.env._("POS Security PIN must contain only digits.")
                )

    @api.model
    def verify_pos_manager_pin(self, login, pin):
        """Verify a POS manager PIN server-side, returning only a boolean.

        The PIN is never sent to the client; comparison is constant-time.
        """
        if not login or not pin:
            return False
        manager = self.sudo().search(
            [
                ("login", "=", login),
                ("active", "=", True),
                (
                    "groups_id",
                    "in",
                    self.env.ref("point_of_sale.group_pos_manager").id,
                ),
                ("pos_security_pin", "!=", False),
            ],
            limit=1,
        )
        return bool(manager) and consteq(manager.pos_security_pin, pin)
