from odoo import api, models


class ShiftTemplateRegistrationLine(models.Model):
    _inherit = "shift.template.registration.line"

    @api.model
    def create(self, vals):
        lines = super().create(vals)
        regs = lines.mapped("registration_id")
        for reg in regs:
            reg.update_leaders(reg.partner_id)
        return lines

    @api.multi
    def write(self, vals):
        res = super().write(vals)
        regs = self.mapped("registration_id")
        for reg in regs:
            if reg.is_current_participant:
                reg.update_leaders(reg.partner_id)
            else:
                reg.update_leaders(reg.partner_id, action="del")
        return res

    @api.multi
    def unlink(self):
        regs = self.mapped("registration_id")
        res = super().unlink()
        for reg in regs:
            if not reg.is_current_participant:
                reg.update_leaders(reg.partner_id, action="del")
        return res
