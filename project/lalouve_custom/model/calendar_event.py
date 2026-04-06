from datetime import timedelta

from odoo import _, api, fields, models


class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    privacy = fields.Selection(default='confidential')
    send_invitation = fields.Boolean(string="Invite by email")
    prevent_change = fields.Boolean(string="Prevent change", default=True)
    description = fields.Html('Description', states={'done': [('readonly', True)]})

    @api.model
    def default_get(self, fields_list):
        vals = super().default_get(fields_list)
        context = self._context
        if context.get('default_allday') and vals.get('start'):
            default_duration = 1
            date_begin = vals.get('start')
            diff_hour = (
                fields.Datetime.now() + timedelta(hours=1)
            ).hour - date_begin.hour
            if diff_hour > 0:
                date_begin = date_begin + timedelta(hours=diff_hour)

            date_begin = date_begin.strftime('%Y-%m-%d %H:00:00')
            date_begin = fields.Datetime.from_string(date_begin)
            date_end = date_begin + timedelta(hours=default_duration)

            vals.update(
                {
                    'allday': False,
                    'start': date_begin,
                    'stop': date_end,
                    'duration': default_duration,
                }
            )
        return vals

    @api.multi
    def create_attendees(self):
        res = {}
        for rec in self:
            if rec.send_invitation:
                res2 = super(CalendarEvent, rec).create_attendees()
                res.update(res2)
            else:
                res2 = super(
                    CalendarEvent, rec.with_context(detaching=True)
                ).create_attendees()
                res.update(res2)
        return res

    @api.model
    def _number_to_letters(self, num):
        """
        Convert a number into a letters (3 -> 'C')
        """
        if not 1 <= num <= 18278:
            return ''
        letters = []
        while num > 0:
            num, remainder = divmod(num, 26)
            # check for exact division and borrow if needed
            if remainder == 0:
                remainder = 26
                num -= 1
            letters.append(chr(remainder + 64))
        result = ''.join(reversed(letters))
        return result

    @api.model
    def compute_week_name(self, dates):
        week_names = {}
        if not dates:
            return week_names
        get_param = self.env['ir.config_parameter'].sudo().get_param
        week_date = get_param('coop_shift.week_a_date')
        n_weeks_cycle = int(get_param('coop_shift.number_of_weeks_per_cycle'))

        for _date in dates:
            sql = """
                SELECT
                    (   1 +
                        MOD(
                            DIV(
                                ABS('{date_1}'::date - '{date_2}'::date)::integer,
                                7
                            ),
                            {weeks_cycle}
                        )
                    )::integer AS week_number
            """.format(
                date_1=_date, date_2=week_date, weeks_cycle=n_weeks_cycle
            )
            self.env.cr.execute(sql)
            res = self.env.cr.fetchone()
            week_name = self._number_to_letters(res[0])
            week_names.update({_date: week_name})
        return week_names

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        """
        Hide the privacy calendar

        """
        records = super().search_read(
            domain=domain, fields=fields, offset=offset, limit=limit, order=order
        )
        res = []
        for rec in records:
            if not rec.get('display_name') and rec.get('name') == _('Busy'):
                continue
            res.append(rec)
        return res
