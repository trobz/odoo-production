from datetime import date

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import SQL


class AccountExport(models.Model):
    _name = "account.export"
    _description = "Account Export"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(
        "Export filename",
        size=32,
        required=True,
        default=lambda self: self._get_default_name(),
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("exported", "Exported"),
        ],
        default="draft",
    )
    last_export_date = fields.Datetime(readonly=True)
    filter_move_lines = fields.Selection(
        [
            ("all", "Export all move lines"),
            ("non_exported", "Export only non exported move lines"),
        ],
        "Move lines to export",
        default="non_exported",
    )
    date_from = fields.Date("From date")
    date_to = fields.Date("To date")
    invoice_ids = fields.Many2many(
        "account.move",
        string="Invoices",
        domain="[('company_id', '=', company_id)]",
    )
    journal_ids = fields.Many2many(
        "account.journal",
        string="Journals",
        domain="[('company_id', '=', company_id)]",
    )
    partner_ids = fields.Many2many("res.partner", string="Partner")
    config_id = fields.Many2one(
        "account.export.config",
        "Export Configuration",
        default=lambda self: self._get_default_config(),
        required=True,
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        help="Company related to this export",
        index=True,
        required=True,
        default=lambda self: self.env.company,
    )

    @api.constrains("company_id", "journal_ids", "invoice_ids")
    def _check_multi_company(self):
        for rec in self.filtered("company_id"):
            journal_company_ids = rec.journal_ids.mapped("company_id")
            invoice_company_ids = rec.invoice_ids.mapped("company_id")
            if journal_company_ids and journal_company_ids != rec.company_id:
                raise ValidationError(
                    self.env._(
                        "The company in the journals do not match the company "
                        "in this Export configuration. \n\n"
                        "Company on Journal: %s\n"
                        "Company on Export: %s",
                        journal_company_ids,
                        rec.company_id,
                    )
                )
            if invoice_company_ids and invoice_company_ids != rec.company_id:
                raise ValidationError(
                    self.env._(
                        "The company in the invoices do not match the company "
                        "in this Export configuration. \n\n"
                        "Company on Invoices: %s\n"
                        "Company on Export: %s",
                        invoice_company_ids,
                        rec.company_id,
                    )
                )

    @api.model
    def _get_default_name(self):
        return f"export{date.today().strftime('%y%m%d')}"

    @api.model
    def _get_default_config(self):
        config = self.env["account.export.config"].search(
            [("is_default", "=", True)], limit=1
        )
        if not config:
            config = self.env["account.export.config"].search([], limit=1)
        return config.id

    def action_create_report(self):
        self.ensure_one()
        report_action = self.env.ref("account_export.report_xls").report_action(
            self.ids
        )
        self.last_export_date = fields.Datetime.now()
        return report_action

    def get_account_move_line_data(self):
        self.ensure_one()
        aml_groupedby_journal, move_ids = self.get_account_move_line_group_by_journal()
        output = []
        for line in aml_groupedby_journal:
            journal_id = line["journal_id"]
            move_line_ids = line["move_line_ids"]
            groupings = self.get_journal_groupings(journal_id)
            line_data = self.get_report_line_data(groupings, move_line_ids)
            output += line_data
        self.env["account.move"].browse(move_ids).write({"exported": True})
        return output

    @api.model
    def get_report_line_data(self, groupings, move_line_ids):
        res = []
        if groupings:
            sql_query = SQL(
                """
                SELECT
                    %(groupings)s,
                    array_agg(aml.id) as move_line_ids
                FROM account_move_line aml
                WHERE aml.id IN %(move_line_ids)s
                GROUP BY %(groupings)s
                """,
                groupings=", ".join(groupings),
                move_line_ids=tuple(move_line_ids),
            )
            self.env.cr.execute(sql_query)
            grouped_move_lines = self.env.cr.dictfetchall()
            for g_mv_line in grouped_move_lines:
                if not g_mv_line["move_line_ids"]:
                    continue
                report_line = self.get_report_line_detail_data(
                    g_mv_line["move_line_ids"], groupings
                )
                res.append(report_line)
        else:
            for acc_move_line in move_line_ids:
                report_line = self.get_report_line_detail_data(
                    [acc_move_line], groupings=False
                )
                res.append(report_line)
        return res

    @api.model
    def get_report_line_detail_data(self, move_line_ids, groupings=False):
        vals = self._get_report_line_detail_data(move_line_ids, groupings)
        return self.config_id.field_ids.get_column_values(vals)

    @api.model
    def _get_report_line_detail_data(self, move_line_ids, groupings=False):
        if not groupings:
            move_line_ids = move_line_ids[:1]
        sql_query = SQL(
            """
            SELECT
                aml.id,
                aj.id AS account_journal_id,
                CASE
                    WHEN aml.journal_id IS NULL THEN NULL
                    ELSE aj.export_code
                END AS export_code,
                aj.code AS journal_code,
                aml.partner_id AS partner_id,
                rp.name AS partner_name,
                aml.date,
                am.name AS move_number,
                CASE
                    WHEN aml.partner_id IS NOT NULL
                        AND (aa.code_store::json ->> %(company_id)s) IS NOT NULL
                        AND LEFT((aa.code_store::json ->> %(company_id)s), 3) = '401'
                        AND rp.property_account_payable_software IS NOT NULL
                        THEN rp.property_account_payable_software
                    WHEN aml.partner_id IS NOT NULL
                        AND (aa.code_store::json ->> %(company_id)s) IS NOT NULL
                        AND LEFT((aa.code_store::json ->> %(company_id)s), 3) = '411'
                        AND rp.property_account_receivable_software IS NOT NULL
                        THEN rp.property_account_receivable_software
                    ELSE COALESCE((aa.code_store::json ->> %(company_id)s), '')
                END AS export_account_code,
                (aa.code_store::json ->> %(company_id)s) AS account_code,
                aa.name AS account_name,
                CASE
                    WHEN aj.type = 'sale' THEN aml.ref
                    WHEN aj.type = 'purchase' THEN COALESCE(rp.name, '')
                    ELSE COALESCE(aml.ref, rp.name, '')
                END AS account_move_name,
                aml.debit,
                aml.credit,
                COALESCE(aml.name, '') AS move_line_name,
                COALESCE(rp.ref, '') AS partner_ref,
                COALESCE((pt.name->>'en_US'), '') AS product_name,
                COALESCE(pp.default_code, '') AS product_code
            FROM account_move_line aml
            LEFT JOIN account_journal aj ON aml.journal_id = aj.id
            LEFT JOIN account_move am ON aml.move_id = am.id
            LEFT JOIN res_partner rp ON aml.partner_id = rp.id
            LEFT JOIN account_account aa ON aml.account_id = aa.id
            LEFT JOIN product_product pp ON aml.product_id = pp.id
            LEFT JOIN product_template pt ON pp.product_tmpl_id = pt.id
            WHERE aml.id IN %(move_line_ids)s
            """,
            company_id=str(self.company_id.id),
            move_line_ids=tuple(move_line_ids),
        )
        self._cr.execute(sql_query)
        move_line_data = self._cr.dictfetchall()
        res_data = dict(move_line_data[0])
        if groupings:
            group_keys = [k for k in res_data.keys() if k not in ["credit", "debit"]]
            res_data["debit"] = 0.0
            res_data["credit"] = 0.0
            for line in move_line_data:
                for key in group_keys:
                    if (
                        res_data[key]
                        and res_data[key] != "GROUPED"
                        and res_data[key] != line[key]
                    ):
                        res_data[key] = "GROUPED"
                res_data["debit"] += line["debit"]
                res_data["credit"] += line["credit"]
        if not res_data.get("export_code") and res_data.get("journal_code"):
            res_data["export_code"] = res_data["journal_code"]
        if res_data.get("export_code") == "NO-JOURNAL-CODE":
            res_data["export_code"] = None
        res_data["move_line_date"] = res_data["date"] and str(res_data["date"])
        return res_data

    def get_account_move_line_group_by_journal(self):
        where_clause = SQL(
            """
            WHERE
                am.state <> %s
                %s %s %s %s %s %s
            """,
            "draft",
            SQL("AND am.exported IS NOT TRUE")
            if self.filter_move_lines == "non_exported"
            else SQL(""),
            SQL("AND aml.date >= %s", self.date_from) if self.date_from else SQL(""),
            SQL("AND aml.date <= %s", self.date_to) if self.date_to else SQL(""),
            SQL("AND aml.move_id IN %s", tuple(self.invoice_ids.ids))
            if self.invoice_ids
            else SQL(""),
            SQL("AND aml.journal_id IN %s", tuple(self.journal_ids.ids))
            if self.journal_ids
            else SQL(""),
            SQL("AND aml.partner_id IN %s", tuple(self.partner_ids.ids))
            if self.partner_ids
            else SQL(""),
        )
        aml_grouped_journal_query = SQL(
            """
            SELECT
                aml.journal_id AS journal_id,
                array_agg(aml.id) AS move_line_ids
            FROM account_move_line aml
            LEFT JOIN account_move am ON aml.move_id = am.id
            %s
            GROUP BY aml.journal_id
            """,
            where_clause,
        )
        self._cr.execute(aml_grouped_journal_query)
        move_line_grouped_journal = self._cr.dictfetchall()
        aml_moves_query = SQL(
            """
            SELECT array_agg(DISTINCT am.id) as account_moves
            FROM
                account_move_line aml
                INNER JOIN account_move am ON aml.move_id = am.id
            %s
            """,
            where_clause,
        )
        self._cr.execute(aml_moves_query)
        account_moves = self._cr.dictfetchall()[0]["account_moves"]
        return move_line_grouped_journal, account_moves

    @api.model
    def get_journal_groupings(self, journal_id):
        grouping_fields = self.env["account.journal"].browse(journal_id).group_fields
        return ["aml." + g_field.name for g_field in grouping_fields]
