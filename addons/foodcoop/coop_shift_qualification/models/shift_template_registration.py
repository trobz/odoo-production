from odoo import api, models
from odoo.exceptions import ValidationError


class ShiftTemplateRegistration(models.Model):
    _inherit = "shift.template.registration"

    def update_leaders(self, partners, action="add"):
        if not partners:
            return
        for reg in self:
            tmpl = reg.shift_template_id
            shifts = tmpl.shift_ids.filtered(lambda s: s.state != "done")
            if action == "add":
                to_add = partners
                if reg.is_current_participant:
                    leaders = to_add.filtered("is_qual_leader")
                    for partner in leaders:
                        warn_msg = partner._get_leader_ftop_warning(tmpl)
                        if warn_msg:
                            raise ValidationError(warn_msg)
                    to_add = leaders
                else:
                    to_add = self.env["res.partner"]

                if to_add:
                    tmpl.user_ids |= to_add
                    for shift in shifts:
                        shift.user_ids |= to_add

            elif action == "del":
                tmpl.user_ids -= partners
                for shift in shifts:
                    shift.user_ids -= partners

    @api.model_create_multi
    def create(self, vals_list):
        regs = super().create(vals_list)
        for reg in regs:
            reg.update_leaders(reg.partner_id)
        return regs

    def write(self, vals):
        res = True
        if vals.get("partner_id") or vals.get("shift_template_id"):
            for reg in self:
                reg.update_leaders(reg.partner_id, action="del")
                res = super(ShiftTemplateRegistration, reg).write(vals)
                reg.update_leaders(reg.partner_id)
        else:
            res = super().write(vals)
        return res

    def unlink(self):
        res = True
        for reg in self:
            reg.update_leaders(reg.partner_id, action="del")
            res = super(ShiftTemplateRegistration, reg).unlink()
        return res
