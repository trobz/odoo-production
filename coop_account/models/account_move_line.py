import json

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.sql import SQL


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    other_balance = fields.Monetary(compute="_compute_other_balance", store=True)
    search_year = fields.Char(
        string="Year (Search)",
        compute="_compute_date_search",
        store=True,
        index=True,
    )
    search_month = fields.Char(
        string="Month (Search)",
        compute="_compute_date_search",
        store=True,
        index=True,
    )
    search_day = fields.Char(
        string="Day (Search)",
        compute="_compute_date_search",
        store=True,
        index=True,
    )

    @api.depends("credit", "debit")
    def _compute_other_balance(self):
        for record in self:
            record.other_balance = record.credit - record.debit

    @api.depends("date")
    def _compute_date_search(self):
        """Merge from date_search_extended module from version 9
        remove date_search_extended module from version 12"""
        for rec in self:
            if rec.date:
                rec.search_year = rec.date.strftime("%Y")
                rec.search_month = rec.date.strftime("%Y-%m")
                rec.search_day = rec.date.strftime("%Y-%m-%d")
            else:
                rec.search_year = False
                rec.search_month = False
                rec.search_day = False

    def _create_writeoff(self, vals):
        move_lines = super()._create_writeoff(vals)
        partner = self.mapped("partner_id")
        for line in move_lines:
            line.partner_id = (
                partner.id
                if len(partner) == 1 and not any(not line.partner_id for line in self)
                else False
            )
        return move_lines

    def unmatch_bankstatement_wizard(self):
        active_ids = self._context.get("active_ids", [])
        active_model = self._context.get("active_model", [])
        view_id = self.env.ref("coop_account.view_unmatch_bank_statement_wizard_form")
        mess_confirm = self.env._(
            "Are you sure you want to unmatch %s transactions?",
            len(active_ids),
        )
        wizard = self.env["unmatch.bank.statement.wizard"].create(
            {
                "mess_confirm": mess_confirm,
            }
        )
        return {
            "name": self.env._("Unmatch Bank Statement"),
            "type": "ir.actions.act_window",
            "view_id": view_id.id,
            "view_mode": "form",
            "res_id": wizard.id,
            "res_model": "unmatch.bank.statement.wizard",
            "target": "new",
            "context": {"active_ids": active_ids, "active_model": active_model},
        }

    @api.model
    def export_wrong_reconciliation_ml(self):
        wrong_reconciliation_ml_data = self.get_wrong_reconciliation_ml_data()
        return json.dumps(
            {
                "context": self.env.context,
                "domain": [],
                "fields": wrong_reconciliation_ml_data["fields"],
                "groupby": [],
                "ids": wrong_reconciliation_ml_data["ids"],
                "import_compat": False,
                "model": self._name,
            }
        )

    @api.model
    def get_wrong_reconciliation_ml_read_fields(self):
        return [
            "name",
            "journal_id",
            "ref",
            "date",
            "partner_id",
            "company_id",
            "check_holder_name",
            "account_id",
            "move_id",
            "debit",
            "credit",
            "quantity",
            "statement_line_id",
            "statement_id",
            "payment_id",
            "check_deposit_id",
        ]

    @api.model
    def get_wrong_reconciliation_ml_data(self):
        read_fields = self.get_wrong_reconciliation_ml_read_fields()
        model_fields = self._fields
        export_fields = [
            {"name": field.name, "label": field.string, "type": field.type}
            for field in model_fields.values()
            if field.name in read_fields
        ]
        wrong_move_lines = self.get_wrong_reconciliation_ml()
        if not wrong_move_lines:
            raise UserError(self.env._("Everything is ok. There's nothing to export."))
        return {
            "fields": export_fields,
            "ids": wrong_move_lines.ids,
        }

    @api.model
    def get_wrong_reconciliation_ml(self):
        wrong_move_lines = self
        selected_journals = self.env["account.journal"].search(
            [("export_wrong_reconciliation", "=", True)]
        )
        if not selected_journals:
            raise UserError(
                self.env._(
                    "Before using this feature, please select a few journals "
                    "to analyze.\nGo to 'Accounting > Configuration > Journals' "
                    "and enable the 'Export Wrong Reconciliation' checkbox."
                )
            )
        self.env.cr.execute(
            SQL(
                """
            SELECT statement_line_id
            FROM account_move_line
            WHERE statement_line_id IS NOT NULL AND journal_id IN %s
            GROUP BY statement_line_id
            HAVING COUNT(statement_line_id) > 1
            """,
                tuple(selected_journals.ids),
            )
        )
        stmt_line_ids = [id_tuple[0] for id_tuple in self.env.cr.fetchall()]
        bank_stmt_lines = self.env["account.bank.statement.line"].browse(stmt_line_ids)
        for stml in bank_stmt_lines:
            move_line_ids = stml.move_id.line_ids
            move_ids = move_line_ids.mapped("move_id")
            if len(move_ids) == 1 and len(move_line_ids) == 2:
                continue
            stml_date = stml.date
            for aml in move_line_ids.filtered(lambda ml: not ml.statement_id):
                aml_date = aml.date
                if (aml_date.year, aml_date.month) > (stml_date.year, stml_date.month):
                    wrong_move_lines |= aml
        return wrong_move_lines
