# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.fr/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from openerp import models, fields, api


class PosConfigSettings(models.Model):
    _inherit = 'pos.config.settings'

    account_journal_ids = fields.Many2many(
        'account.journal',
        'rel_pos_config_journal',
        'rel_account_journal_pos',
        string="Cheques Journals",
        help="Please indicate here the cheques journals for which you " +
        "would like to display a message when used in POS")

    payable_to = fields.Char(string="Payable to")
