from odoo import api, fields, models


class MailMessage(models.Model):
    _inherit = "mail.message"

    task_description = fields.Html(
        compute="_compute_task_description", string="Task Description"
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

    @api.model_create_multi
    def create(self, vals_list):
        messages = super().create(vals_list)
        mt_comment = self.env.ref("coop_project.mt_task_comment", raise_if_not_found=False)
        if not mt_comment:
            return messages
        for msg in messages:
            if msg.subtype_id != mt_comment or not msg.partner_ids:
                continue
            internal_partners = msg.partner_ids.filtered(
                lambda p: p.user_ids and not p.user_ids[:1].share
            )
            if not internal_partners:
                continue
            existing_pids = msg.sudo().notification_ids.mapped("res_partner_id").ids
            to_notify = internal_partners.filtered(lambda p: p.id not in existing_pids)
            if not to_notify:
                continue
            self.env["mail.notification"].sudo().create([
                {
                    "author_id": msg.author_id.id,
                    "mail_message_id": msg.id,
                    "notification_status": "sent",
                    "notification_type": "inbox",
                    "res_partner_id": partner.id,
                }
                for partner in to_notify
            ])
            users = to_notify.mapped("user_ids")
            followers = self.env["mail.followers"].sudo().search([
                ("res_model", "=", msg.model),
                ("res_id", "=", msg.res_id),
                ("partner_id", "in", users.partner_id.ids),
            ])
            for user in users:
                user._bus_send_store(
                    msg.with_user(user).with_context(allowed_company_ids=[]),
                    for_current_user=True,
                    add_followers=True,
                    followers=followers,
                    notification_type="mail.message/inbox",
                )
        return messages
