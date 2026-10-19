import hashlib

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ResUsers(models.Model):
    _inherit = "res.users"

    pos_security_pin = fields.Char(
        string="POS Security PIN",
        help="Numeric PIN to authorize credit payment validation in the Point of Sale.",
        copy=False,
    )

    @api.constrains("pos_security_pin")
    def _check_pos_security_pin(self):
        for user in self:
            if user.pos_security_pin and not user.pos_security_pin.isdigit():
                raise ValidationError(
                    self.env._("POS Security PIN must contain only digits.")
                )

    def _load_pos_data(self, data):
        result = super()._load_pos_data(data)
        # Keep current user PIN for compatibility with existing POS flows.
        pin = self.env.user.pos_security_pin or False
        result["data"][0]["_pin"] = (
            hashlib.sha1(pin.encode("utf-8")).hexdigest() if pin else False
        )

        # Provide manager credentials metadata used by frontend manager validation.
        managers = (
            self.sudo()
            .search(
                [
                    (
                        "groups_id",
                        "in",
                        self.env.ref("point_of_sale.group_pos_manager").id,
                    ),
                    ("active", "=", True),
                    ("pos_security_pin", "!=", False),
                ]
            )
            .read(["id", "name", "login", "pos_security_pin"], load=False)
        )

        result["data"][0]["_manager_auth_users"] = [
            {
                "id": manager["id"],
                "name": manager["name"],
                "login": manager["login"],
                "_pin": hashlib.sha1(
                    manager["pos_security_pin"].encode("utf-8")
                ).hexdigest(),
            }
            for manager in managers
            if manager.get("pos_security_pin")
        ]
        return result
