# -*- coding: utf-8 -*-
from openerp import models, fields, api


class BankReconciliationSummaryWizard(models.TransientModel):
    _name = 'bank.reconciliation.summary.wizard'
    _description = 'Bank Reconciliation Summary Wizard'

    journal_id = fields.Many2one(
        'account.journal', "Journal",
        domain=[('type', '=', 'bank')], required=True)
    analysis_date = fields.Date('Analysis Date', required=True)

    @api.multi
    def get_data(self):
        self.ensure_one()
        data = {}
        journal_id = self.journal_id or False
        analysis_date = self.analysis_date
        move_lines = self.env['account.move.line'].search([
            ('date', '<=', analysis_date),
            ('reconciled', '=', False),
            ('credit', '!=', 0.00),
            ('debit', '=', 0.00)])
        bank_statement_lines = self.env['account.bank.statement.line'].search([
            ('date', '<=', analysis_date),
            ('journal_id', '!=', journal_id.id),
            ('journal_entry_ids', '=', False)])
        if move_lines:
            data.update({'move_line_ids': move_lines.ids})
        if move_lines:
            data.update({'bank_statement_line_ids': bank_statement_lines.ids})
        return data

    @api.multi
    def print_report(self, data):
        data = self.get_data()
        report_name = 'bank_reconciliation_summary_xlsx'
        return self.env['report'].get_action(self, report_name, data=data)
