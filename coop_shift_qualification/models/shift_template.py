from odoo import Command, api, models
from odoo.exceptions import ValidationError


class ShiftTemplate(models.Model):
    _inherit = "shift.template"

    def update_qualification(self, partners, action="add", raise_error=True):
        if not partners:
            return
        lead_quals = self.env["res.partner.qualification"].search(
            [("is_leader", "=", True)]
        )
        if not lead_quals:
            return
        for tmpl in self:
            if tmpl.is_ftop:
                continue
            regs = tmpl.current_registration_ids
            reg_partner_ids = set(regs.mapped("partner_id").ids)

            if action == "add":
                candidates = partners.filtered(
                    lambda p, reg_partner_ids=reg_partner_ids: p.id in reg_partner_ids
                )
                candidates = candidates.filtered(lambda p: not p.is_qual_leader)

                if candidates:
                    invalid = self.env["res.partner"]
                    for partner in candidates:
                        warn_msg = partner._get_leader_ftop_warning(tmpl)
                        if warn_msg:
                            if raise_error:
                                raise ValidationError(warn_msg)
                            invalid |= partner

                    candidates -= invalid

                if candidates:
                    candidates.write(
                        {"qualification_ids": [Command.link(lead_quals[0].id)]}
                    )

            elif action == "del":
                to_del = self.env["res.partner"]
                for partner in partners:
                    curr_tmpls = partner.template_ids - self
                    if not curr_tmpls:
                        to_del |= partner
                if to_del:
                    to_del.write(
                        {
                            "qualification_ids": [
                                Command.unlink(qid) for qid in lead_quals.ids
                            ]
                        }
                    )

    @api.model_create_multi
    def create(self, vals_list):
        tmpls = super().create(vals_list)
        for tmpl in tmpls:
            tmpl.update_qualification(tmpl.mapped("user_ids"))
        return tmpls

    def write(self, vals):
        res = True
        if vals.get("user_ids") or vals.get("shift_type_id"):
            for tmpl in self:
                curr_partners = tmpl.mapped("user_ids")
                res = super(ShiftTemplate, tmpl).write(vals)
                new_partners = tmpl.mapped("user_ids")
                to_add = new_partners - curr_partners
                to_del = curr_partners - new_partners
                tmpl.update_qualification(to_del, action="del")
                tmpl.update_qualification(to_add)
        else:
            res = super().write(vals)
        return res

    def unlink(self):
        res = True
        for tmpl in self:
            tmpl.update_qualification(tmpl.mapped("user_ids"), action="del")
            res = super(ShiftTemplate, tmpl).unlink()
        return res
