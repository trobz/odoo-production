from odoo import fields, models


class MailTemplate(models.Model):
    _inherit = "mail.template"

    active = fields.Boolean(default=True)
