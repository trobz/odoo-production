# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
# @author Julien WESTE
# @author Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import date, datetime, timedelta

from odoo import api, fields, models

from .report_wallchart_common import rounding_limit

WEEK_DAYS = {
    "mo": "Monday",
    "tu": "Tuesday",
    "we": "Wednesday",
    "th": "Thursday",
    "fr": "Friday",
    "sa": "Saturday",
    "su": "Sunday",
}

weekday_list = [
    "mo",
    "tu",
    "we",
    "th",
    "fr",
    "sa",
    "su",
]


class ReportWallchartTemplate(models.AbstractModel):
    _name = "report.coop_shift.report_wallchart_template"
    _inherit = "report.coop_shift.report_wallchart_common"
    _description = "Wallchart report for shift templates"

    @api.model
    def _get_ticket_partners(self, ticket):
        partners = []
        future_seats = 0
        for reg in ticket.registration_ids:
            ok = False
            dates = ""
            for line in reg.line_ids:
                if (
                    line.date_end
                    and fields.Date.from_string(line.date_end) <= date.today()
                ) or line.state != "open":
                    continue
                ok = True
                if (
                    line.date_begin
                    and fields.Date.from_string(line.date_begin) > date.today()
                ):
                    date_begin = datetime.strftime(
                        fields.Date.from_string(line.date_begin) - timedelta(days=1),
                        "%x",
                    )
                    dates = f"+ until {date_begin} " + dates
                    future_seats += 1
                if line.date_end:
                    date_end = datetime.strftime(
                        fields.Date.from_string(line.date_end) + timedelta(days=1), "%x"
                    )
                    dates = f"+ from {date_end} " + dates
                    future_seats -= 1
            dates = dates and (" (" + dates[2:-1] + ")")
            if ok:
                partners.append({"partner_id": reg.partner_id, "dates": dates})
        return partners, future_seats

    @api.model
    def _get_tickets(
        self, template, product_name="coop_shift.product_product_shift_standard"
    ):
        product_name = "coop_shift.product_product_shift_standard"
        return super()._get_tickets(template, product_name)

    @api.model
    def _get_template_info(self, template):
        tickets = self._get_tickets(template)
        partners = []
        seats_max = 0
        future_seats = 0
        for ticket in tickets:
            p, f = self._get_ticket_partners(ticket)
            partners += p
            future_seats += f
            seats_max += ticket.seats_max
        return partners, seats_max, future_seats

    @api.model
    def _get_templates(self, data):
        final_result = []
        n_weeks_cycle = self._get_number_weeks_per_cycle()
        number_to_letters = self.env["shift.template"]._number_to_letters
        for week_day in data.keys():
            if week_day == "id" or not data.get(week_day, False):
                continue
            if week_day not in weekday_list:
                continue

            result = []
            templates = self.env["shift.template"].search([(week_day, "=", True)])
            time_slots = sorted(
                {(template.start_time, template.end_time) for template in templates},
                key=lambda slot: slot[0],
            )
            for t in time_slots:
                res = {}
                res["start_time"] = self.format_float_time(t[0])
                res["end_time"] = self.format_float_time(t[1])
                base_search = [
                    ("start_time", ">=", t[0] - rounding_limit),
                    ("start_time", "<=", t[0] + rounding_limit),
                    ("end_time", ">=", t[1] - rounding_limit),
                    ("end_time", "<=", t[1] + rounding_limit),
                    ("week_list", "=", week_day.upper()),
                ]
                for week in range(1, n_weeks_cycle + 1):
                    template = self.env["shift.template"].search(
                        base_search + [("week_number", "=", week)]
                    )
                    if not template:
                        res["partners" + number_to_letters(week)] = []
                        res["free_seats" + number_to_letters(week)] = 0
                        continue
                    template = template[0]
                    partners, seats_max, future_seats = self._get_template_info(
                        template
                    )
                    res["partners" + number_to_letters(week)] = partners
                    res["free_seats" + number_to_letters(week)] = max(
                        0, seats_max - len(partners)
                    )

                contain_data_in_period = any(
                    len(res.get("partners" + number_to_letters(week), [])) > 0
                    for week in range(1, n_weeks_cycle + 1)
                )
                if contain_data_in_period:
                    result.append(res)
            if result:
                weeks = [
                    (n, self.env["shift.template"]._number_to_letters(n))
                    for n in range(1, self._get_number_weeks_per_cycle() + 1)
                ]
                final_result.append(
                    {
                        "day": self.env._(WEEK_DAYS[week_day]),
                        "weeks": weeks,
                        "next_dates": self._get_next_dates(
                            weekday_list.index(week_day)
                        ),
                        "times": result,
                    }
                )
        return final_result

    @api.model
    def _get_next_dates(self, weekday):
        result = {}
        today = date.today()
        n_weeks_cycle = self._get_number_weeks_per_cycle()
        next_date = today + timedelta(days=(weekday - today.weekday()) % 7)
        week_number = self._get_week_number(next_date)
        for i in range(1, n_weeks_cycle + 1):
            delta = (i - week_number[0]) % n_weeks_cycle
            key = "week" + self.env["shift.template"]._number_to_letters(i)
            week_dates = [
                datetime.strftime(
                    next_date + timedelta(weeks=delta + (n_weeks_cycle * week_offset)),
                    "%d/%m",
                )
                for week_offset in range(7)
            ]
            result[key] = f"({', '.join(week_dates)}, ...)"
        return result

    @api.model
    def _get_report_values(self, docids, data=None):
        model_name = self.env.context.get("active_model")
        docs = {}
        docs["Wallcharts"] = self._get_templates(data["form"])
        return {
            "doc_ids": self.ids,
            "partner_id": self.env.user.partner_id,
            "doc_model": model_name,
            "data": data["form"],
            "docs": docs,
            "date": date,
        }
