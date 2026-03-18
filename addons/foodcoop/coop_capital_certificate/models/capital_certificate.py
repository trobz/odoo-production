# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Julien Weste (julien.weste@akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class CapitalCertificate(models.Model):
    _name = "capital.certificate"
    _description = "Capital Certificates"

    partner_id = fields.Many2one(
        "res.partner",
        required=True,
        ondelete="cascade",
    )
    year = fields.Integer(required=True)
    template_id = fields.Many2one(
        "mail.template",
        string="Email to Send",
        required=True,
        ondelete="restrict",
        help="""This field contains the template of the"""
        """ mail that will be automatically sent""",
    )
    line_ids = fields.One2many(
        string="Certificate Lines",
        comodel_name="capital.certificate.line",
        inverse_name="certificate_id",
    )

    @api.constrains("partner_id", "year")
    def _unique_partner_year(self):
        for certificate in self:
            if (
                certificate.search_count(
                    [
                        ("partner_id", "=", certificate.partner_id.id),
                        ("year", "=", certificate.year),
                    ]
                )
                > 1
            ):
                raise ValidationError(
                    self.env._(
                        "Partner %s already has a certificate for year %s!",
                        certificate.partner_id.name,
                        certificate.year,
                    )
                ) from None

    def create_certificate(self, send_mail=False):
        self.ensure_one()
        if send_mail:
            self.template_id.send_mail(res_id=self.id)


class CapitalCertificateLine(models.Model):
    _name = "capital.certificate.line"
    _description = "Capital Certificate Lines"

    account_move_line_id = fields.Many2one(comodel_name="account.move.line")
    certificate_id = fields.Many2one(comodel_name="capital.certificate")
    date = fields.Date("Invoice Date")
    payment_date = fields.Date()
    qty = fields.Integer("Quantity")
    product = fields.Char("Category")
    price = fields.Float("Unit Price")
