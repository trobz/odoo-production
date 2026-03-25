from odoo import fields, models


class ResPartnerAlert(models.Model):
    _name = "res.partner.alert"
    _description = "Res Partner Alert"
    _rec_name = "expected_member_id"

    expected_member_id = fields.Many2one(
        comodel_name="res.partner",
        required=True,
    )
    partner_ids = fields.Many2many(
        comodel_name="res.partner",
        required=True,
        string="Employee To Alert",
    )
    state = fields.Selection(
        selection=[("open", "Open"), ("close", "Closed")],
        default="open",
    )

    def button_close(self):
        self.write({"state": "close"})
