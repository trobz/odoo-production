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
        result = super()._load_pos_data(data)
        # Credit payment is confirmed with the current cashier's own PIN.
        pin = self.env.user.pos_security_pin or False
        result["data"][0]["_pin"] = (
            hashlib.sha1(pin.encode("utf-8")).hexdigest() if pin else False
        )
        return result
