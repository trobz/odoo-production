# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Julien Weste (julien.weste@akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import Command, api, fields, models
from odoo.tools.sql import SQL


class CapitalCertificateWizard(models.TransientModel):
    _name = "capital.certificate.wizard"
    _description = "Capital Fiscal Certificate Report"

    @api.model
    def _get_default_year(self):
        current_date = fields.Date.from_string(fields.Date.today())
        return current_date.year - 1

    def _get_partner_selection(self):
        return [
            ("list", "List of partners"),
            ("all", "All partners"),
        ]

    year = fields.Integer(default=_get_default_year)
    send_mail = fields.Boolean(
        default=True,
        help="""If the box is checked, an email """
        """ will be automatically sent to partners who subscribed capital."""
        """If it isn't checked, the pdf files will be created but not sent """
        """by email.""",
    )
    partner_selection = fields.Selection(
        _get_partner_selection,
    )
    partner_ids = fields.Many2many(
        "res.partner",
        "res_partner_capital_certificate_rel",
        "capital_certificate_id",
        "partner_id",
    )

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        partner_list = self.env.context.get("active_ids", False)
        if partner_list:
            res["partner_ids"] = Command.set(partner_list)
            res["partner_selection"] = "list"
        else:
            res["partner_selection"] = "all"
        return res

    def generate_certificates(self):
        self.ensure_one()
        cfc_obj = self.env["capital.fundraising.category"]
        account_clause = SQL()
        accounts = cfc_obj.search([]).mapped("capital_account_id")
        if accounts:
            account_clause = SQL("AND aml.account_id IN %s", tuple(accounts.ids))
        year = self.read(["year"])[0]["year"]
        partner_clause = SQL()
        if self.partner_selection == "list":
            partner_list = self.partner_ids.ids
            partner_clause = SQL("AND rp.id IN %s", tuple(partner_list))

        query = SQL(
            """
            SELECT
                rp.id
            FROM
                res_partner as rp, account_move_line as aml,
                product_product as pp, product_template as pt
            WHERE
                rp.id = aml.partner_id AND aml.product_id = pp.id AND
                pp.product_tmpl_id = pt.id AND
                pt.is_capital_fundraising is true AND
                EXTRACT(YEAR FROM aml.date) = %s
                %s
                %s
            GROUP BY rp.id
            """,
            str(year),
            account_clause,
            partner_clause,
        )
        self.env.cr.execute(query)
        partner_ids = self.env.cr.fetchall()
        partner_ids = [p[0] for p in partner_ids]
        partners = self.env["res.partner"].browse(partner_ids)
        partners.generate_certificate(year, self.send_mail)
