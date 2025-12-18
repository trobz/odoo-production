from dateutil.relativedelta import relativedelta

from odoo import fields, models

from odoo.addons.queue_job.job import identity_exact


class AccountFrFec(models.TransientModel):
    _inherit = "l10n_fr.fec.export.wizard"

    def write(self, vals):
        if self._context.get("extension", "") == "txt" and vals.get("filename"):
            vals["filename"] = vals["filename"][:-3] + "txt"
        return super().write(vals)

    def export_fec_txt(self):
        self.ensure_one()
        return self.with_context(extension="txt").create_fec_report_action()

    def export_fec_csv_background(self):
        self.ensure_one()
        return self.generate_fec_file_in_background()

    def export_fec_txt_background(self):
        self.ensure_one()
        return self.generate_fec_file_in_background("txt")

    def create_attachment(self, date_from, date_to, extension):
        self.ensure_one()
        self.date_from = date_from
        self.date_to = date_to
        results = self.with_context(extension=extension).generate_fec()
        attachment = self.env["ir.attachment"].create(
            {
                "name": results.get("file_name"),
                "store_fname": self.filename,
                "db_datas": results.get("file_content"),
            }
        )
        email_template = self.env.ref(
            "l10n_fr_fec_background.send_fec_file_mail_template"
        )
        email_template.send_mail(
            self.id,
            force_send=True,
            email_values={"attachment_ids": [(4, attachment.id)]},
        )
        return True

    def generate_fec_file_in_background(self, extension="csv"):
        self.ensure_one()
        # Prepare periods
        date_from = fields.Date.from_string(self.date_from)
        date_to = fields.Date.from_string(self.date_to)
        periods = self.prepare_periods(date_from, date_to)

        # Call job
        for period_from, period_to in periods:
            self.write_fec_lines_session_job(period_from, period_to, extension)
        return True

    def prepare_periods(self, date_from, date_to):
        periods = []
        current_start = date_from

        while current_start <= date_to:
            current_end = current_start + relativedelta(day=31)
            if current_end > date_to:
                current_end = date_to

            periods.append((current_start, current_end))
            current_start = current_end + relativedelta(days=1)

        return periods

    def write_fec_lines_session_job(self, date_from, date_to, extension):
        """Job to write FEC lines per period"""
        self.with_delay(
            identity_key=identity_exact,
            description="Create FEC attachment",
        ).create_attachment(date_from, date_to, extension)
