# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.fr/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from openerp import api, fields, models, _
from openerp.exceptions import UserError
from datetime import datetime, timedelta


class ShiftChangeTeam(models.Model):
    _name = "shift.change.team"
    _inherit = ['mail.thread']

    partner_id = fields.Many2one('res.partner', string="Member", required=True)
    current_shift_template_id = fields.Many2one(
        'shift.template',
        compute="compute_current_shift_template",
        string="Current Team")
    next_current_shift_date = fields.Date(
        compute="compute_current_shift_template",
        string='Date of next shift current team',
        store=True)
    new_shift_template_id = fields.Many2one(
        'shift.template', string="New Team", required=True)
    is_ftop_new_shift = fields.Boolean(
        compute="compute_mess_change_team",
        string="Is new shift FTOP ?",
        store=True,
        default=False)
    first_next_shift_date = fields.Date(
        string="The date of first shift in new team",
    )
    second_next_shift_date = fields.Date(
        string="The date of second shift in new team",
    )
    full_seats_mess = fields.Html(
        compute="compute_full_seats_massagess",
        string="Full Seats Messagess",
        store=True
    )
    is_full_seats_mess = fields.Boolean(
        compute="compute_full_seats_massagess",
        string="Show full seats warning",
        store=True)
    new_next_shift_date = fields.Date(
        string="Start date of shift new team",
        required=True)
    mess_change_team = fields.Html(
        string='Message Change Team',
        compute='compute_mess_change_team',
        store=True)
    is_mess_change_team = fields.Boolean(
        compute="compute_mess_change_team",
        string="Show changing team messages",
        default=False,
        store=True)
    partner_unsubscribed = fields.Selection([
        ('subscribed', 'Subscribed'), ('unsubscribed', 'Unsubscribed')],
        compute="compute_current_shift_template",
        string="Member State",
        default='subscribed',
    )
    is_catch_up = fields.Boolean(
        string="Is Catch Up",
        default=False,
    )
    state = fields.Selection(
        [('draft', 'Draft'), ('closed', 'Closed')],
        string="Status",
    )
    mass_change_team_ids = fields.Many2many('mass.change.team',
                                            string="Mass change teams")

    @api.multi
    @api.constrains('current_shift_template_id', 'new_shift_template_id')
    def change_team_constraints(self):
        for record in self:
            if record.current_shift_template_id ==\
                    record.new_shift_template_id:
                raise UserError(
                    _('The new team should be different the current team'))

    @api.multi
    def button_close(self):
        for record in self:
            if record.is_mess_change_team or record.is_full_seats_mess:
                raise UserError(_(
                    'There are some processes that were not done, please do it!'))
            else:
                record.set_in_new_team()
                if record.new_shift_template_id.shift_type_id.is_ftop:
                    mail_template_ftop = self.env.ref(
                        'coop_membership.change_team_ftop_email')
                    if mail_template_ftop:
                        mail_template_ftop.attachment_ids = [
                            (6, 0, [self.env.ref(
                                'coop_membership.volant_sheet_attachment').id,
                                self.env.ref(
                                'coop_membership.volant_calendar_attachment').id])]
                        mail_template_ftop.send_mail(record.id)
                else:
                    mail_template_abcd = self.env.ref(
                        'coop_membership.change_team_abcd_email')
                    if mail_template_abcd:
                        mail_template_abcd.send_mail(record.id)
                        if record.is_catch_up:
                            point_counter_env = self.env['shift.counter.event']
                            point_counter_env.sudo().with_context({'automatic': True})\
                                .create({
                                    'name': _('Add 1 point for changing team'),
                                    'type': 'standard',
                                    'partner_id': record.partner_id.id,
                                    'point_qty': 1,
                                })

                record.state = 'closed'
        return True

    @api.multi
    def set_in_new_team(self):
        '''
            This method set partner on new team and the date of shifts 
        '''
        self.ensure_one()
        current_registration = self.partner_id.tmpl_reg_line_ids.filtered(
            lambda r: r.is_current)
        future_registrations = self.partner_id.tmpl_reg_line_ids.filtered(
            lambda r: r.is_future)
        if current_registration:
            current_registration.date_end = fields.Date.to_string(
                fields.Date.from_string(
                    self.new_next_shift_date) - timedelta(days=1))
        if future_registrations:
            for registration in future_registrations:
                registration.shift_template_id = self.new_shift_template_id
        else:
            if self.new_shift_template_id.shift_type_id.is_ftop:
                shift_type = 'ftop'
            else:
                shift_type = 'standard'
            shift_ticket =\
                self.new_shift_template_id.shift_ticket_ids.filtered(
                    lambda t: t.shift_type == shift_type)
            self.env['shift.template.registration.line'].create({
                'shift_template_id': self.new_shift_template_id.id,
                'partner_id': self.partner_id.id,
                'shift_ticket_id': shift_ticket[0].id,
                'date_begin': self.new_next_shift_date,
            })

        # Set days of two next shifts
        date_next_shifts = self.partner_id.registration_ids.filtered(
            lambda r: r.date_begin >=
            fields.Date.context_today(self)).mapped('date_begin')

        self.set_date_future_shifts(date_next_shifts)

        return True

    @api.multi
    def set_date_future_shifts(self, date_next_shifts):
        self.ensure_one()
        range_dates, list_dates = self.compute_range_day()
        if len(date_next_shifts) >= 2:
            self.first_next_shift_date = date_next_shifts[0]
            self.second_next_shift_date = date_next_shifts[1]
        elif len(date_next_shifts) == 1:
            self.first_next_shift_date = date_next_shifts[0]
            if list_dates:
                self.second_next_shift_date = fields.Date.to_string(list_dates[0])
        else:
            if list_dates:
                self.first_next_shift_date = fields.Date.to_string(list_dates[0])
                self.second_next_shift_date = fields.Date.to_string(list_dates[1])

    @api.multi
    @api.depends('new_shift_template_id')
    def compute_full_seats_massagess(self):
        for record in self:
            shift_tmp = record.new_shift_template_id
            if shift_tmp:
                available_standard_seat = 0
                for ticket in shift_tmp.shift_ticket_ids:
                    if ticket.shift_type == 'standard':
                        available_standard_seat += ticket.seats_available
                if available_standard_seat <= 0:
                    record.full_seats_mess = (_(
                        "There is no more seat in this " +
                        " team, would you like to continue?"))
                    record.is_full_seats_mess = True

    @api.multi
    def btn_full_seats_process(self):
        for record in self:
            record.is_full_seats_mess = False
        return {
            "type": "ir.actions.do_nothing",
        }

    @api.multi
    def convert_state_partner(self):
        self.ensure_one()
        state = self.partner_id.cooperative_state
        if state == 'unsubscribed':
            return (_('Unsubscribed'))
        elif state == 'exempted':
            return (_('Exempted'))
        elif state == 'vacation':
            return (_('Vacation'))
        elif state == 'up_to_date':
            return (_('Up to date'))
        elif state == 'alert':
            return (_('Alert'))
        elif state == 'suspended':
            return (_('Suspended'))
        elif state == 'delay':
            return (_('Delay'))
        elif state == 'blocked':
            return (_('Blocked'))
        elif state == 'unpayed':
            return (_('Unpayed'))
        elif state == 'not_concerned':
            return (_('Not Concerned'))
        else:
            return ''

    @api.multi
    def button_save_new(self):
        self.ensure_one()
        partner_ids = self._context.get('partner_ids', [])
        self.button_close()
        changed_team_ids = self._context.get('changed_team_ids', [])
        if not changed_team_ids:
            changed_team_ids = []
        changed_team_ids.append(self.id)
        if partner_ids:
            partner_id = partner_ids[0]
            partner_ids.remove(partner_ids[0])
            return {
                'name': _('Change Teams'),
                'type': 'ir.actions.act_window',
                'res_model': 'shift.change.team',
                'view_type': 'form',
                'target': 'new',
                'view_mode': 'form',
                'context': {'default_partner_id': partner_id,
                            'partner_ids': partner_ids,
                            'changed_team_ids': changed_team_ids},
            }
        elif changed_team_ids:
            return{
                'name': _('Change Teams'),
                'type': 'ir.actions.act_window',
                'res_model': 'shift.change.team',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'domain': [('id', 'in', changed_team_ids)],
                'context': {'not_show_button_next_member': True}
            }
        else:
            return

    @api.multi
    def button_save_close(self):
        self.ensure_one()
        self.button_close()
        changed_team_ids = self._context.get('changed_team_ids', [])
        if not changed_team_ids:
            changed_team_ids = []
        changed_team_ids.append(self.id)
        if changed_team_ids:
            return{
                'name': _('Change Teams'),
                'type': 'ir.actions.act_window',
                'res_model': 'shift.change.team',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'domain': [('id', 'in', changed_team_ids)],
                'context': {'not_show_button_next_member': True}
            }
        else:
            return

    @api.multi
    def button_next_member(self):
        self.ensure_one()
        partner_ids = self._context.get('partner_ids', [])
        # self.button_close()
        changed_team_ids = self._context.get('changed_team_ids', [])
        if not changed_team_ids:
            changed_team_ids = []
        changed_team_ids.append(self.id)
        if partner_ids:
            partner_id = partner_ids[0]
            partner_ids.remove(partner_ids[0])
            return {
                'name': _('Change Teams'),
                'type': 'ir.actions.act_window',
                'res_model': 'shift.change.team',
                'view_type': 'form',
                'target': 'new',
                'view_mode': 'form',
                'context': {'default_partner_id': partner_id,
                            'partner_ids': partner_ids,
                            'changed_team_ids': changed_team_ids, },
            }
        elif changed_team_ids:
            return{
                'name': _('Change Teams'),
                'type': 'ir.actions.act_window',
                'res_model': 'shift.change.team',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'domain': [('id', 'in', changed_team_ids)],
                'context': {'not_show_button_next_member': True}
            }
        else:
            return

    @api.multi
    def convert_format_datatime(self, date_change):
        for record in self:
            date = date_change.split('-')[2] + '/' +\
                date_change.split('-')[1] + '/' + date_change.split('-')[0]
            return unicode(date, "utf-8")

    @api.multi
    @api.depends('partner_id')
    def compute_current_shift_template(self):
        for record in self:
            if record.partner_id:
                # compute unsubscribed
                if record.partner_id.is_unsubscribed:
                    record.partner_unsubscribed = 'unsubscribed'
                    if record.is_catch_up:
                        record.is_catch_up = False

                # compute next shift date
                reg = record.partner_id.tmpl_reg_ids.filtered(
                    lambda r: r.is_current)
                if reg:
                    record.current_shift_template_id = reg[0].shift_template_id
                    next_shifts =\
                        record.current_shift_template_id.shift_ids.filtered(
                            lambda s: s.date_begin >
                            fields.Date.context_today(self))
                    record.next_current_shift_date = next_shifts and\
                        next_shifts[0].date_begin or False

    @api.multi
    def compute_range_day(self):
        self.ensure_one()
        next_shift_mounth = (fields.Datetime.from_string(
            self.new_next_shift_date) +
            timedelta(days=90)).strftime('%Y-%m-%d')
        rec_new_template_dates =\
            self.new_shift_template_id.get_recurrent_dates(
                self.new_next_shift_date, next_shift_mounth)
        if rec_new_template_dates:
            range_dates = rec_new_template_dates[0] -\
                fields.Datetime.from_string(
                    self.next_current_shift_date)
            return range_dates.days, rec_new_template_dates
        else:
            return False

    @api.multi
    @api.depends('next_current_shift_date', 'new_shift_template_id',
                 'new_next_shift_date')
    def compute_mess_change_team(self):
        for record in self:
            if record.next_current_shift_date and record.new_shift_template_id\
                    and record.new_next_shift_date:
                range_dates, list_dates = record.compute_range_day()
                if not record.current_shift_template_id.shift_type_id.is_ftop\
                        and not record.new_shift_template_id.shift_type_id.is_ftop:
                    if range_dates and range_dates > 42:
                        record.mess_change_team = (_(
                            "Il y a un écart de plus de 6 " +
                            "semaines entre le dernier service dans " +
                            "l’ancienne équipe et le premier avec la nouvelle." +
                            " Souhaitez-vous continuer ?"))
                        record.is_mess_change_team = True
                elif record.new_shift_template_id.shift_type_id.is_ftop:
                    record.is_ftop_new_shift = True
                    if range_dates and range_dates <= 15:
                        record.mess_change_team = (_(
                            "La date de démarrage est inférieure à 15 jours " +
                            " avant le jour de décompte volant qui suit. " +
                            "Souhaitez-vous continuer ?"
                        ))
                        record.is_mess_change_team = True

    @api.multi
    def btn_change_team_process(self):
        for record in self:
            record.is_mess_change_team = False
        return {
            "type": "ir.actions.do_nothing",
        }
