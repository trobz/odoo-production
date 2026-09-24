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
                "alias_name": self._find_unique_alias_name(leader_alias_prefix),
                "type": "coordinator",
            }
        )
        # 2. for the members of the team (include coordinators))
        team_alias_prefix = f"service.{prefix}"
        self.env["memberspace.alias"].create(
            {
                "name": team_alias_prefix,
                "shift_id": self.id,
                "alias_name": self._find_unique_alias_name(team_alias_prefix),
                "type": "team",
            }
        )

    def _find_unique_alias_name(self, name):
        """Find a unique alias name similar to ``name``, appending an integer
        suffix until an unused one is found.

        Reproduces the behaviour Odoo core had up to v12
        (``_clean_and_make_unique`` / ``_find_unique``), dropped in v18 where
        ``mail.alias.create`` now raises a UserError on collision instead of
        silently making the name unique.
        """
        mail_alias = self.env["mail.alias"]
        sanitized = mail_alias._sanitize_alias_name(name)
        alias_domain = self.env.company.alias_domain_id
        sequence = None
        while True:
            candidate = f"{sanitized}{sequence}" if sequence is not None else sanitized
            domain = [("alias_name", "=", candidate)]
            if alias_domain:
                domain += [("alias_domain_id", "=", alias_domain.id)]
            if not mail_alias.search(domain, limit=1):
                break
            sequence = (sequence + 1) if sequence else 2
        return candidate
