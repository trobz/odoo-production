from odoo import api, fields, models


class ShiftTemplate(models.Model):
    _inherit = "shift.template"

    memberspace_alias_ids = fields.One2many(
        "memberspace.alias", "shift_id", "Memberspace Alias"
    )

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        # generate automatically an alias
        for rec in records:
            rec.create_email_alias()
        return records

    def create_email_alias(self):
        self.ensure_one()
        template_name = self.name.replace(" ", "").replace(":", "").split("-")
        if len(template_name) < 2:
            return False
        prefix = f"{template_name[-2][:3]}{template_name[-1]}"

        # 1. for the coordinators of the team
        leader_alias_prefix = f"coordos.{prefix}"
        self.env["memberspace.alias"].create(
            {
                "name": leader_alias_prefix,
                "shift_id": self.id,
                "alias_name": leader_alias_prefix,
                "type": "coordinator",
            }
        )
        # 2. for the members of the team (include coordinators))
        team_alias_prefix = f"service.{prefix}"
        self.env["memberspace.alias"].create(
            {
                "name": team_alias_prefix,
                "shift_id": self.id,
                "alias_name": team_alias_prefix,
                "type": "team",
            }
        )
