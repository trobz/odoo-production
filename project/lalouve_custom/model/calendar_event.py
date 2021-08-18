# -*- coding: utf-8 -*-

from datetime import timedelta
from odoo import api, fields, models


class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    privacy = fields.Selection(default='confidential')

    @api.model
    def default_get(self, fields_list):
        vals = super(CalendarEvent, self).default_get(fields_list)
        context = self._context
        if context.get('default_allday') and vals.get('start'):
            default_duration = 1
            date_begin = vals.get('start')
            diff_hour = (fields.Datetime.now() + timedelta(hours=1)
                ).hour - date_begin.hour
            if diff_hour > 0:
                date_begin = date_begin + timedelta(hours=diff_hour)
            
            date_begin = date_begin.strftime('%Y-%m-%d %H:00:00')
            date_begin = fields.Datetime.from_string(date_begin)
            date_end = date_begin + timedelta(hours=default_duration)

            vals.update({
                'allday': False,
                'start': date_begin,
                'stop': date_end,
                'duration': default_duration
            })
        return vals
