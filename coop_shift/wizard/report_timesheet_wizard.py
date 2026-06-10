# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
# @author Julien WESTE
# @author Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import timedelta

from odoo import api, fields, models


class ReportTimesheet(models.TransientModel):
    _name = "report.timesheet"
    _description = "Report Timesheet"

    def _get_selected_shifts(self):
        shift_ids = self.env.context.get("active_ids", False)
        if shift_ids:
            return shift_ids

    date_report = fields.Date(string="Report Date", default=fields.Date.context_today)
    date_report_prior = fields.Date(
        string="Previous Date",
        compute="_compute_date_report_prior",
    )
    shift_ids = fields.Many2many(
        "shift.shift",
        "shift_timeshift_rel",
        "timesheet_id",
        "shift_id",
        string="Shifts",
        default=_get_selected_shifts,
    )

    @api.depends("date_report")
    def _compute_date_report_prior(self):
        for rec in self:
            if rec.date_report:
                # Subtract 1 day using Python's standard timedelta
                rec.date_report_prior = rec.date_report - timedelta(days=1)
            else:
                rec.date_report_prior = False

    def check_report(self):
        self.ensure_one()
        data = {}
        data["ids"] = self.env.context.get("active_ids", [])
        data["model"] = self.env.context.get("active_model", "ir.ui.menu")
        data["form"] = self.read(["date_report", "shift_ids"])[0]
        data["form"]["used_context"] = dict(lang=self.env.context.get("lang", "en_US"))
        return self.env.ref("coop_shift.timesheet_label").report_action(self, data)
