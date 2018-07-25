# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.fr/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from openerp import api, fields, models, _
from openerp.exceptions import ValidationError


class ShiftHoliday(models.Model):
    _name = "shift.holiday"
    _order = 'date_begin desc'

    HOLIDAY_STATE_SELECTION = [
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
        ('cancel', 'Canceled'),
    ]

    name = fields.Char(string="Name", required=True)
    holiday_type = fields.Selection(
        [('long_period', 'Long Period'), ('single_day', 'Single Day')],
        required=True,
        string=" Holiday Type")
    long_period_shift_ids = fields.One2many(
        'shift.shift', 'long_holiday_id', sring="Shifts")
    single_day_shift_ids = fields.One2many(
        'shift.shift', 'single_holiday_id', string='Shifts')
    date_end = fields.Date(string="Date End", required=True)
    date_begin = fields.Date(string="Date Begin", required=True)
    state = fields.Selection(
        selection=HOLIDAY_STATE_SELECTION, default='draft')
    make_up_type = fields.Selection(
        [('1_make_up', '1 Make Up'), ('0_make_up', '0 Make Up')],
        string="Make Up")

    @api.multi
    @api.constrains('date_begin', 'date_end')
    def check_over_lap(self):
        for record in self:
            if record.date_begin > record.date_end:
                raise ValidationError(
                    _('Date End should be greater than Date Begin.'))
            elif record.holiday_type == 'single_day' and\
                    record.date_end != record.date_begin:
                raise ValidationError(
                    _('Date End should be equal Date Begin in Single Day.'))
            else:
                holidays = self.search([
                    ('date_begin', '<=', record.date_end),
                    ('date_end', '>=', record.date_begin),
                    ('id', '!=', record.id),
                    ('holiday_type', '=', record.holiday_type)
                ])
                if holidays:
                    raise ValidationError(
                        _('There is a holiday already exist in this period'))

    @api.multi
    @api.onchange('holiday_type')
    def onchange_holiday_type(self):
        self.ensure_one()
        if self.holiday_type != 'long_period':
            self.make_up_type = False

    @api.multi
    def button_confirm(self):
        for record in self:
            shifts = self.env['shift.shift'].search([
                ('date_begin', '>=', record.date_begin),
                ('date_end', '<=', record.date_end),
                ('state', 'not in', ['draft', 'cancel']),
            ])
            # Get shifts base on holiday type ensure that shift weren't on any holiday

            if record.holiday_type == 'long_period':
                shifts = shifts.filtered(lambda s: not s.long_holiday_id)
                record.long_period_shift_ids = [[6, 0, shifts.ids]]
            else:
                shifts = shifts.filtered(lambda s: not s.single_holiday_id)
                record.single_day_shift_ids = [[6, 0, shifts.ids]]
        record.state = 'confirmed'
        return True

    @api.multi
    def button_done(self):
        for record in self:
            if record.holiday_type == 'long_period':
                record.attribute_point_qty_long_period()
            else:
                unmarked_shifts = []
                for shift in record.single_day_shift_ids:
                    if not shift.state_in_holiday:
                        unmarked_shifts.append(shift.name)
                if unmarked_shifts:
                    list_name = '\n- '.join(unmarked_shifts)
                    mess = _('''Here are shifts that weren't marked open or closed
                                - %s\n
                                Please mark all of shift''') % list_name
                    raise ValidationError(mess)
                else:
                    record.attribute_point_qty_single_day()
            record.state = 'done'
        return True

    @api.multi
    def attribute_point_qty_long_period(self):
        '''
            This method attribute the point qty for attendee on long holiday
            With Rule:
            Plus 2 in holiday type 0 make up with shift type standard and 
            attendees was absent
            Plus 1 in holiday type 1 make up for (shift type standard and
            attendees were exscued) or (shift type volant and attendees were 
            absent or excused)

        '''
        self.ensure_one()
        point_counter_env = self.env['shift.counter.event']

        # Approve for shift that weren't marked any another single holiday
        shifts = self.long_period_shift_ids.filtered(
            lambda s: not s.single_holiday_id or s.single_holiday_id.state != 'done')

        shifts.write({
            'is_on_holiday': True
        })

        attendees = shifts.mapped('registration_ids').filtered(
            lambda a: a.state == 'absent' or a.state == 'excused')
        if self.make_up_type == '0_make_up':
            for attendee in attendees:
                count_vals = {}
                if attendee.shift_type == 'standard' and\
                        attendee.state == 'absent':
                    count_vals = {
                        'point_qty': 2
                    }
                else:
                    count_vals = {
                        'point_qty': 1
                    }
                if count_vals:
                    count_vals.update({
                        'shift_id': attendee.shift_id.id,
                        'type': attendee.shift_type,
                        'partner_id': attendee.partner_id.id,
                        'name': _('Balance qty for long period holiday'),
                        'holiday_id': self.id,
                    })
                    point_counter_env.sudo().with_context(
                        automatic=True).create(count_vals)
        else:
            for attendee in attendees.filtered(
                    lambda a: a.shift_type == 'standard' and a.state == 'absent'):
                count_vals = {
                    'shift_id': attendee.shift_id.id,
                    'type': attendee.shift_type,
                    'partner_id': attendee.partner_id.id,
                    'name': _('Balance qty for long period holiday'),
                    'holiday_id': self.id,
                    'point_qty': 1
                }
                point_counter_env.sudo().with_context(
                    automatic=True).create(count_vals)

    @api.multi
    def attribute_point_qty_single_day(self):
        '''
            This method attribute the point qty for attendees are on single
            holiday
            With Rule:
            Plus 2 in shift was closed with shift type standard and 
            attendees was absent
            Plus 1 in shift was open for (shift type standard and attendees were 
            exscued) or (shift type volant and attendees were absent or excused)
        '''

        self.ensure_one()
        point_counter_env = self.env['shift.counter.event']

        email_closed_template = self.env.ref(
            'coop_membership.anounce_close_on_holiday_email')
        email_open_template = self.env.ref(
            'coop_membership.anounce_open_on_holiday_email')

        # Reset for overlap (single holiday is preferable than long period)
        another_holiday = self.single_day_shift_ids.filtered(
            lambda s: s.long_holiday_id and
            s.long_holiday_id.state == 'done').mapped('long_holiday_id')

        if another_holiday:
            another_holiday.reset_point_qty()

        self.single_day_shift_ids.write({'is_on_holiday': True})

        closed_shifts = self.single_day_shift_ids.filtered(
            lambda s: s.state_in_holiday == 'closed')
        open_shifts = self.single_day_shift_ids.filtered(
            lambda s: s.state_in_holiday == 'open')

        # Set maximum available FTOP seats = 0
        ftop_tickets = closed_shifts.mapped('shift_ticket_ids').filtered(
            lambda t: t.shift_type == 'ftop')
        ftop_tickets.write({'seats_max': 0})

        # Balance qty for attendee which are on closed shift
        for attendee in closed_shifts.mapped('registration_ids').filtered(
                lambda a: a.state == 'absent' or a.state == 'excused'):
            count_vals = {}
            if attendee.state == 'absent' and attendee.shift_type == 'standard':
                count_vals = {
                    'point_qty': 2
                }
            else:
                count_vals = {
                    'point_qty': 1
                }
            if count_vals:
                count_vals.update({
                    'shift_id': attendee.shift_id.id,
                    'type': attendee.shift_type,
                    'partner_id': attendee.partner_id.id,
                    'name': _('Balance qty for single holiday'),
                    'holiday_id': self.id,
                })
                point_counter_env.sudo().with_context(
                    automatic=True).create(count_vals)

                # Send email anounce
                if email_closed_template:
                    email_closed_template.send_mail(attendee.id)

        for attendee in open_shifts.mapped('registration_ids').filtered(
                lambda a: a.state == 'absent' and a.shift_type == 'standard'):
            count_vals = {
                'shift_id': attendee.shift_id.id,
                'type': attendee.shift_type,
                'partner_id': attendee.partner_id.id,
                'point_qty': 1,
                'name': _('Balance qty for single holiday'),
                'holiday_id': self.id,
            }
            point_counter_env.sudo().with_context(
                automatic=True).create(count_vals)

            # Send email anounce
            if email_open_template:
                email_open_template.send_mail(attendee.id)

    @api.multi
    def reset_point_qty(self):
        for holiday in self:
            events = self.env['shift.counter.event'].search([
                ('holiday_id', '=', holiday.id)])
            for event in events:
                last_qty = event.point_qty
                last_notes = event.notes or ''
                event.point_qty = 0
                event.notes = '%s %s %s' % (
                    last_notes,
                    '\n Point qty was updated by overlap.',
                    '(Last qty is %s)' % (last_qty))
        return True

    @api.multi
    def button_cancel(self):
        for record in self:
            events = record.env['shift.counter.event'].search([
                ('holiday_id', '=', record.id)])

            # Set qty all to 0 for counter event were linked current holiday
            for event in events:
                last_qty = event.point_qty
                last_notes = event.notes or ''
                event.point_qty = 0
                event.notes = '%s %s %s' % (
                    last_notes,
                    '\n Point qty was updated by cancelling holiday.',
                    '(Last qty is %s)' % (last_qty))
            record.state = 'cancel'
        return True

    @api.multi
    def button_draft(self):
        for record in self:
            if record.holiday_type == 'long_period':
                for shift in record.long_period_shift_ids:
                    shift.in_single_day = False
                    shift.state_in_holiday = False
                record.long_period_shift_ids = False
            else:
                for shift in record.single_day_shift_ids:
                    shift.in_single_day = False
                    shift.state_in_holiday = False
                record.single_day_shift_ids = False
            record.state = 'draft'
        return True
