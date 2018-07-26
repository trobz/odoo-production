# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.fr/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from openerp import api, fields, models, _
from openerp.exceptions import UserError
from datetime import datetime, timedelta


class ShiftChangeTeam(models.Model):
    _name = "shift.change.team"

    partner_id = fields.Many2one('res.partner', string="Member", required=True)
    current_shift_template_id = fields.Many2one(
        'shift.template', string="Current Team", required=True)
    next_current_shift_date = fields.Date(
        compute="compute_next_current_shift_date",
        string='Date of next shift current team',
        store=True)
    new_shift_template_id = fields.Many2one(
        'shift.template', string="New Team", required=True)
    new_next_shift_date = fields.Date(
        compute="compute_new_next_shift_date",
        string="Start date of shift new team",
        store=True)
    mess_standard_to_ftop = fields.Html(
        string='Message Change From ABCD to Another',
        compute='compute_mess_standard_to_ftop',
        store=True)

    @api.multi
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        self.ensure_one()
        if self.partner_id:
            reg = self.partner_id.tmpl_reg_ids.filtered(
                lambda r: r.is_current)
            if reg:
                self.current_shift_template_id = reg[0].shift_template_id
            else:
                reg = self.partner_id.tmpl_reg_ids.filtered(
                    lambda r: r.is_future)
                if reg:
                    self.current_shift_template_id =\
                        reg[0].shift_template_id

    @api.multi
    @api.depends('current_shift_template_id')
    def compute_next_current_shift_date(self):
        for record in self:
            if record.current_shift_template_id:
                next_shifts =\
                    record.current_shift_template_id.shift_ids.filtered(
                        lambda s: s.date_begin >
                        fields.Date.context_today(self))
                record.next_current_shift_date = next_shifts and\
                    next_shifts[0].date_begin or False

    @api.multi
    @api.depends('next_current_shift_date')
    def compute_new_next_shift_date(self):
        for record in self:
            if record.next_current_shift_date:
                current_shift_date = fields.Date.from_string(
                    record.next_current_shift_date)
                record.new_next_shift_date = fields.Date.to_string(
                    current_shift_date + timedelta(days=1))

    @api.multi
    @api.depends('new_next_shift_date')
    def compute_mess_standard_to_ftop(self):
        for record in self:
            next_shift_mounth = (fields.Datetime.from_string(
                fields.Date.context_today(self)) +
                timedelta(days=30)).strftime('%Y-%m-%d')
            rec_new_template_dates =\
                record.new_shift_template_id.get_recurrent_dates(
                    record.new_next_shift_date, next_shift_mounth)
            print '\n\n==>>', rec_new_template_dates
            record.mess_standard_to_ftop = (_(
                "Il y a un écart de plus de 6 " +
                "semaines entre le dernier service dans l’ancienne équipe et" +
                " le premier avec la nouvelle. Souhaitez-vous continuer ?"))
