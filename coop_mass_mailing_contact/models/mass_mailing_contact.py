from odoo import fields, models


class MassMailingContact(models.Model):
    _inherit = "mail.mass_mailing.contact"

    is_member_contact = fields.Boolean(default=False)
