from odoo import fields, models


class MailMessage(models.Model):
    _inherit = "mail.message"

    task_description = fields.Html(
        compute="_compute_task_description", string="Description"
    )

    def _compute_task_description(self):
        for msg in self:
            if not msg.sudo().tracking_value_ids:
                msg.task_description = msg.body
                continue
            tracking_values = msg.sudo().tracking_value_ids._tracking_value_format()
            description = self.env._("CHANGES: <ul>")
            for vals in tracking_values:
                old_value = vals.get("oldValue", {}).get("value", "")
                new_value = vals.get("newValue", {}).get("value", "")
                description += "<li>{changed_field}: {old}{new}</li>".format(
                    changed_field=vals.get("changedField"),
                    old=str(old_value) + " => " if old_value else "",
                    new=new_value,
                )
            description += "</ul>"
            msg.task_description = description
