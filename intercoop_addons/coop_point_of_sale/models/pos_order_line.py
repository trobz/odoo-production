# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import models, api, fields, _
from datetime import datetime, timedelta
from openerp.addons.connector.queue.job import job
from openerp.addons.connector.session import ConnectorSession


class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    week_number = fields.Char(string='Week', compute="_compute_week_number",
                              store=True)
    week_day = fields.Char(
        string="Day", compute="_compute_week_day", store=True)
    cycle = fields.Char(string="Cycle", compute="_compute_cycle", store=True)

    @api.multi
    @api.depends('create_date')
    def _compute_week_number(self):
        for line in self:
            if not line.create_date:
                line.week_number = False
            else:
                weekA_date = fields.Date.from_string(
                    self.env.ref('coop_shift.config_parameter_weekA').value)
                create_date = fields.Date.from_string(line.create_date)
                week_number =\
                    1 + (((create_date - weekA_date).days // 7) % 4)
                if week_number == 1:
                    line.week_number = 'A'
                elif week_number == 2:
                    line.week_number = 'B'
                elif week_number == 3:
                    line.week_number = 'C'
                elif week_number == 4:
                    line.week_number = 'D'

    @api.multi
    @api.depends('create_date')
    def _compute_week_day(self):
        for line in self:
            if line.create_date:
                date_order_object = datetime.strptime(
                    line.create_date, '%Y-%m-%d %H:%M:%S')
                wd = date_order_object.weekday()
                if wd == 0:
                    line.week_day = _("Mon")
                elif wd == 1:
                    line.week_day = _("Tue")
                elif wd == 2:
                    line.week_day = _("Wes")
                elif wd == 3:
                    line.week_day = _("Thu")
                elif wd == 4:
                    line.week_day = _("Fri")
                elif wd == 5:
                    line.week_day = _("Sat")
                elif wd == 6:
                    line.week_day = _("Sun")

    @api.multi
    @api.depends('week_number', 'week_day')
    def _compute_cycle(self):
        for line in self:
            line.cycle = "%s%s" % (line.week_number, line.week_day)

    # Custom Section
    @api.multi
    def update_cycle_pos_order(self):

        line_ids = self.ids
        num_line_per_job = 500
        splited_line_list = \
            [line_ids[i: i + num_line_per_job]
             for i in range(0, len(line_ids), num_line_per_job)]
        # Prepare session for job
        session = ConnectorSession(self._cr, self._uid,
                                   {'lang': 'fr_FR'})
        # Create jobs
        for line_list in splited_line_list:
            update_cycle_pos_order_job.delay(
                session, 'pos.order.line', line_list)
        return True


@job
def update_cycle_pos_order_job(session, model_name, line_list):
    ''' Job for compute cycle '''
    orders = session.env[model_name].browse(line_list)
    orders._compute_week_number()
    orders._compute_week_day()
    orders._compute_cycle()

    @api.multi
    def compute_amount_line_all(self):
        """
        Util function that easily call _compute_amount_line_all from JSONRPC
        """
        self._compute_amount_line_all()
        return True
