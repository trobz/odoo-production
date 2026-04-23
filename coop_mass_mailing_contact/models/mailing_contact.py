from odoo import fields, models


class MailingContact(models.Model):
    _inherit = "mailing.contact"

    is_member_contact = fields.Boolean(default=False)
