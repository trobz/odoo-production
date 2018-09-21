# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.fr/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from openerp import models, fields


class PosConfigSettings(models.Model):
    _inherit = 'pos.config.settings'

    receipt_options = fields.Selection(
        [
            (1, 'Do not send receipt via email'),
            (2, 'Email receipt and print it'),
            (3, 'Email receipt and print it unless configured on user that he only receives electronically')
        ], string="Receipt"
    )
