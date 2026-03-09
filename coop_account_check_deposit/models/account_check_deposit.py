from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    check_holder_name = fields.Char()

    @api.onchange("partner_id")
    def onchange_partner_id(self):
        change_check_holder_name = self._context.get("change_check_holder_name", False)
        if self.partner_id and not self.check_holder_name:
            if change_check_holder_name or self.check_deposit_id:
                self.check_holder_name = self.partner_id.display_name

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        res.with_context(create_mode=True).update_check_holder_name()
        return res

    def write(self, vals):
        res = super().write(vals)
        if not self._context.get("create_mode"):
            self.update_check_holder_name()
        return res

    def update_check_holder_name(self):
        """
        Update check holder name for item was generate from deposit
        """
        for record in self:
            if (
                record.check_deposit_id
                and record.partner_id
                and not record.check_holder_name
            ):
                record.check_holder_name = record.partner_id.display_name
            elif not record.check_deposit_id and record.check_holder_name:
                record.check_holder_name = ""
