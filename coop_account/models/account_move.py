from odoo import Command, api, fields, models
from odoo.exceptions import UserError, ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

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

    def unmatch_bankstatement(self):
        for record in self:
            record.line_ids.write({"statement_line_id": False})

    def unmatch_bankstatement_wizard(self):
        active_ids = self._context.get("active_ids", [])
        active_model = self._context.get("active_model", [])
        view_id = self.env.ref("coop_account.view_unmatch_bank_statement_wizard_form")
        mess_confirm = self.env._(
            "Are you sure you want to unmatch %s transactions?",
            len(active_ids),
        )
        wizard = self.env["unmatch.bank.statement.wizard"].create(
            {"mess_confirm": mess_confirm}
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

    def check_bank_statement_journal(self):
        for move in self:
            for line in move.line_ids:
                if (
                    line.statement_id
                    and not line.statement_id.journal_id.bank_account_id
                    and line.account_id.reconciled_account
                ):
                    raise UserError(
                        self.env._(
                            "You cannot reconcile that account move with "
                            "a bank statement line that is not related to "
                            "bank journal."
                        )
                    )

    def write(self, vals):
        res = super().write(vals)
        self.check_bank_statement_journal()
        return res

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

    def merge_move_lines(self):
        for move in self:
            if move.state != "draft":
                # Not merge invoice line when invoice != draft
                raise ValidationError(self.env._("You can only merge draft invoice!"))
            # Only merge invoice line when invoice at state draft
            to_delete_ids = []
            itered_ids = []
            for inv_line in move.invoice_line_ids:
                itered_ids.append(inv_line.id)
                line_to_merge = self.env["account.move.line"].search(
                    [
                        ("move_id", "=", move.id),
                        ("discount", "=", inv_line.discount),
                        ("price_unit", "=", inv_line.price_unit),
                        ("product_id", "=", inv_line.product_id.id),
                        ("account_id", "=", inv_line.account_id.id),
                        ("id", "not in", itered_ids),
                    ],
                    limit=1,
                )
                if line_to_merge:
                    to_delete_ids.append(inv_line.id)
                    line_to_merge.write(
                        {
                            "quantity": line_to_merge.quantity + inv_line.quantity,
                            "ref": (line_to_merge.ref or "") + (inv_line.ref or ""),
                        }
                    )
            move.write(
                {
                    "invoice_line_ids": [
                        Command.unlink(id_delete) for id_delete in to_delete_ids
                    ]
                }
            )
