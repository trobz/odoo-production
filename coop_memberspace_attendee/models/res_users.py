
from odoo import api, models


class ResUsers(models.Model):
    _inherit = "res.users"

    @api.model
    def ftop_get_shift(self):
        shifts = super(ResUsers, self).ftop_get_shift()
        for rec in shifts:
            shift = self.env["shift.shift"].browse(rec["id"])
            rec["seats_reserved"] = shift.seats_reserved
        return shifts
