# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.fr/>)
# Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from odoo import api, fields, models
from odoo.exceptions import ValidationError

WEEK_DAY_MAP = {
    0: "Mon",
    1: "Tue",
    2: "Wes",
    3: "Thu",
    4: "Fri",
    5: "Sat",
    6: "Sun",
}


class PosSession(models.Model):
    _inherit = "pos.session"

    week_number = fields.Integer(
        compute="_compute_week_number",
        store=True,
    )
    week_name = fields.Char(
        compute="_compute_week_number",
        string="Week",
        store=True,
    )
    week_day = fields.Char(
        string="Day",
        compute="_compute_week_number",
        store=True,
    )
    cycle = fields.Char(
        compute="_compute_week_number",
        store=True,
    )
    search_year = fields.Char(
        string="Year (Search)",
        compute="_compute_date_search",
        store=True,
        index=True,
    )
    search_month = fields.Char(
        string="Month (Search)",
        compute="_compute_date_search",
        store=True,
        index=True,
    )
    search_day = fields.Char(
        string="Day (Search)",
        compute="_compute_date_search",
        store=True,
        index=True,
    )
    order_count = fields.Integer(compute="_compute_orders", store=True)
    amount_untaxed = fields.Monetary(compute="_compute_orders", store=True)
    amount_total = fields.Monetary(compute="_compute_orders", store=True)

    @api.depends("order_ids.amount_total", "order_ids.amount_tax")
    def _compute_orders(self):
        session_data = self.env["pos.order"].read_group(
            [("state", "!=", "cancel"), ("session_id", "in", self.ids)],
            fields=["amount_total", "amount_tax"],
            groupby=["session_id"],
        )
        result = dict(
            (
                data["session_id"][0],
                {
                    "order_count": data["session_id_count"],
                    "amount_tax": data["amount_tax"],
                    "amount_total": data["amount_total"],
                },
            )
            for data in session_data
        )
        for session in self:
            vals = result.get(session.id, {})
            session.order_count = vals.get("order_count", 0)
            session.amount_total = vals.get("amount_total", 0.0)
            session.amount_untaxed = session.amount_total - vals.get("amount_tax", 0.0)

    @api.depends("start_at")
    def _compute_week_number(self):
        number_to_letters = self.env["shift.template"]._number_to_letters
        # Compute week numbers
        data = self.env["shift.template"]._get_week_number_multi(
            records=self, field_name="start_at"
        )
        for rec in self:
            if not rec.start_at:
                rec.update(
                    {
                        "week_number": False,
                        "week_name": False,
                        "week_day": False,
                        "cycle": False,
                    }
                )
            else:
                # Get week number
                week_number = data.get(rec.id)
                week_name = number_to_letters(week_number)
                # Compute week day
                week_day = self.env._(
                    WEEK_DAY_MAP.get(fields.Date.from_string(rec.start_at).weekday())
                )
                rec.update(
                    {
                        "week_number": week_number,
                        "week_name": week_name,
                        "week_day": week_day,
                        "cycle": f"{week_name}{week_day}",
                    }
                )

    @api.depends("start_at")
    def _compute_date_search(self):
        """Merge from date_search_extended module from version 9
        remove date_search_extended module from version 12"""
        for rec in self:
            if rec.start_at:
                rec.search_year = rec.start_at.strftime("%Y")
                rec.search_month = rec.start_at.strftime("%Y-%m")
                rec.search_day = rec.start_at.strftime("%Y-%m-%d")
            else:
                rec.search_year = False
                rec.search_month = False
                rec.search_day = False

    @api.constrains("user_id", "state")
    def _check_unicity(self):
        """Prevent an user from having more than one active POS session."""
        for session in self:
            if session.rescue:
                continue
            duplicate_count = self.search_count(
                [
                    ("state", "not in", ("closed", "closing_control")),
                    ("user_id", "=", session.user_id.id),
                    ("rescue", "=", False),
                    ("id", "!=", session.id),
                ]
            )
            if duplicate_count:
                raise ValidationError(
                    self.env._(
                        "You cannot create two active sessions with the same responsible."
                    )
                )

    def _recompute_week_fields_async(self):
        NUM_RECORDS_PER_JOB = 1000
        chunked = [
            self[i : i + NUM_RECORDS_PER_JOB]
            for i in range(0, len(self), NUM_RECORDS_PER_JOB)
        ]
        for chunk in chunked:
            chunk.with_delay()._job_recompute_week_fields_async()
        return True

    def _job_recompute_week_fields_async(self):
        self._compute_week_number()
