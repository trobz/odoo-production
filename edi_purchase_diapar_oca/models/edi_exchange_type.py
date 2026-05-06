from datetime import datetime

from pytz import timezone, utc

from odoo import fields, models

DEFAULT_DATE_FMT = "%Y%m%d"
DEFAULT_TIME_FMT = "%H%M%S"


class EDIExchangeType(models.Model):
    _inherit = "edi.exchange.type"

    field_mapping_ids = fields.One2many(
        comodel_name="edi.field.mapping",
        inverse_name="exchange_type_id",
        string="Field Mappings",
    )
    header_code = fields.Char()
    lines_code = fields.Char()
    delivery_sign = fields.Char()

    def _make_exchange_filename_time(self):
        self.ensure_one()
        pattern_settings = self.advanced_settings.get("filename_pattern", {})
        force_tz = pattern_settings.get("force_tz", self.env.user.tz)
        time_pattern = pattern_settings.get("time_pattern", DEFAULT_TIME_FMT)
        tz = timezone(force_tz) if force_tz else None
        now = datetime.now(utc).astimezone(tz)
        return self.env["ir.http"]._slugify(now.strftime(time_pattern))

    def _make_exchange_filename(self, exchange_record):
        res = super()._make_exchange_filename(exchange_record)
        return res.format(time=self._make_exchange_filename_time())
