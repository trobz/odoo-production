import hashlib

from odoo import api, fields, models


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
                raise models.ValidationError(
                    self.env._("POS Security PIN must contain only digits.")
                )

    def _load_pos_data(self, data):
        config_data = data["pos.config"]["data"][0]
        config_id = config_data["id"]
        group_manager_id = config_data["group_pos_manager_id"]

        field_list = self._load_pos_data_fields(config_id)

        # Current user
        user = self.search_read(
            [("id", "=", self.env.uid)],
            field_list + ["groups_id", "pos_security_pin"],
            load=False,
        )
        user[0]["role"] = (
            "manager" if group_manager_id in user[0]["groups_id"] else "cashier"
        )
        pin = user[0].pop("pos_security_pin") or False
        user[0]["_pin"] = (
            hashlib.sha1(pin.encode("utf-8")).hexdigest() if pin else False
        )
        del user[0]["groups_id"]

        # All other users who have a PIN set (any role can confirm)
        other_users = self.sudo().search_read(
            [
                ("id", "!=", self.env.uid),
                ("pos_security_pin", "!=", False),
                ("pos_security_pin", "!=", ""),
            ],
            ["id", "name", "partner_id", "pos_security_pin", "groups_id"],
            load=False,
        )
        for u in other_users:
            pin = u.pop("pos_security_pin") or False
            u["_pin"] = hashlib.sha1(pin.encode("utf-8")).hexdigest() if pin else False
            u["role"] = (
                "manager" if group_manager_id in u.get("groups_id", []) else "cashier"
            )
            u.pop("groups_id", None)

        return {
            "data": user + other_users,
            "fields": field_list,
        }
