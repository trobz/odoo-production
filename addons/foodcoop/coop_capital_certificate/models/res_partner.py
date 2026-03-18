# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Julien Weste (julien.weste@akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import Command, api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.depends("capital_certificate_ids")
    def _compute_capital_certificate_count(self):
        for partner in self:
            partner.capital_certificate_count = len(partner.capital_certificate_ids)

    capital_certificate_ids = fields.One2many(
        comodel_name="capital.certificate", inverse_name="partner_id"
    )
    capital_certificate_count = fields.Integer(
        compute="_compute_capital_certificate_count"
    )

    def generate_certificate(self, year=False, send_mail=False):
        if not year:
            return False

        aml_obj = self.env["account.move.line"]
        cc_obj = self.env["capital.certificate"]
        mail_template = self.env.ref(
            "coop_capital_certificate.capital_certificate_mail_template"
        )
        min_date = f"{year}-01-01"
        max_date = f"{year + 1}-01-01"

        cfc_obj = self.env["capital.fundraising.category"]
        account_list = tuple([c.capital_account_id.id for c in cfc_obj.search([])])
        for partner in self:
            lines = []
            aml_ids = aml_obj.search(
                [
                    ("partner_id", "=", partner.id),
                    ("date", ">=", min_date),
                    ("date", "<", max_date),
                    ("account_id", "in", account_list),
                    ("credit", ">", 0),
                ],
                order="account_id",
            )
            for aml in aml_ids:
                price = aml.product_id.list_price
                qty = aml.credit / price if price else 0
                lines.append(
                    Command.create(
                        {
                            "account_move_line_id": aml.id,
                            "date": aml.move_id.invoice_date,
                            "qty": qty,
                            "product": aml.product_id.name,
                            "price": price,
                            "payment_date": aml.date,
                        }
                    )
                )
            cc = cc_obj.create(
                {
                    "partner_id": partner.id,
                    "year": year,
                    "template_id": mail_template.id,
                    "line_ids": lines,
                }
            )
            cc.create_certificate(send_mail)
