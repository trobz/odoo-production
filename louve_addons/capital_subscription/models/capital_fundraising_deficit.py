# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from openerp import api, fields, models, _
from openerp.exceptions import ValidationError


class CapitalFundraisingDeficit(models.Model):
    _name = 'capital.fundraising.deficit'

    start_date = fields.Date("Start Date", required=True)
    end_date = fields.Date("End Date")
    amount_by_share = fields.Float("Amount By Share", required=True)
    fund_cate_id = fields.Many2one(
                    comodel_name="capital.fundraising.category",
                    string="Fundraising Category")

    @api.multi
    @api.constrains('start_date', 'end_date')
    def _check_overlap_dates(self):
        """
        @Function to check if date ranges in all deficit shares is overlap
        """
        if self.fund_cate_id.id:
            deficit_shares = self.env['capital.fundraising.deficit'].search([
                ('fund_cate_id', '=', self.fund_cate_id.id)])

            for deficit in deficit_shares:
                for deficit2 in deficit_shares:
                    if deficit2.id == deficit.id:
                        continue

                    is_overlap = False
                    # Constraint dates
                    if deficit2.start_date and deficit2.end_date:
                        if deficit2.start_date > deficit2.end_date:
                            raise ValidationError(
                                _("Stop Date should be greater than "
                                  "Start Date."))

                    if not deficit.end_date:
                        if not deficit2.end_date or deficit2.end_date >= \
                                deficit.start_date:
                            is_overlap = True
                    else:
                        if (not deficit2.end_date and
                            deficit2.start_date <= deficit.end_date) or \
                            (deficit2.end_date and deficit2.end_date >=
                             deficit.start_date and deficit2.start_date <=
                             deficit.end_date):
                                is_overlap = True

                    if is_overlap:
                        raise ValidationError(_(
                            "You cannot have two Capital Fundraising "
                            "Deficit configuration lines that overlap"))
