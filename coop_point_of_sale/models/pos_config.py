# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import Command, api, fields, models


class PosConfig(models.Model):
    _inherit = "pos.config"

    account_journal_ids = fields.Many2many(
        "account.journal",
        "rel_pos_config_journal",
        "rel_account_journal_pos",
        string="Check Journals",
        help="Please indicate here the cheques journals for which you "
        + "would like to display a message when used in POS",
    )
    payable_to = fields.Char()
    qty_zero_remove_line = fields.Boolean(
        string="Remove Zero Qty Line",
        default=True,
    )
    enable_popup_verify_payment = fields.Boolean(
        string="Allow execution of script popup_verify_payment",
        default=True,
    )

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        journals = self.env.user.company_id.journal_config_ids
        payable_to = self.env.user.company_id.payable_to
        res.update(
            {
                "account_journal_ids": [Command.set(journals.ids)],
                "payable_to": payable_to,
            }
        )
        return res

    def execute(self):
        for record in self:
            self.env.user.company_id.journal_config_ids = [
                Command.set(record.account_journal_ids.ids)
            ]
            self.env.user.company_id.payable_to = record.payable_to
        return super().execute()
