import base64

from odoo import _, api, fields, models
from odoo.tools.misc import format_date

from odoo.addons.l10n_fr_pos_cert.models.res_company import ctx_tz
from odoo.addons.queue_job.delay import group

BATCH_SIZE = 5000


class PosInalterabilityCheck(models.Model):
    _name = "pos.inalterability.check"
    _description = "POS Inalterability Check"
    _order = "create_date desc"

    name = fields.Char(compute="_compute_name", store=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company
    )
    state = fields.Selection(
        [
            ("pending", "Pending"),
            ("enqueued", "Enqueued"),
            ("done", "Done"),
            ("failed", "Failed"),
        ],
        default="pending",
        readonly=True,
    )
    queue_job_id = fields.Many2one("queue.job", readonly=True, ondelete="set null")
    batch_ids = fields.One2many(
        "pos.inalterability.check.batch", "check_id", readonly=True
    )
    pdf_report = fields.Binary(readonly=True, attachment=True)
    pdf_filename = fields.Char(readonly=True)
    error_message = fields.Text(readonly=True)

    @api.depends("company_id", "create_date")
    def _compute_name(self):
        for rec in self:
            date_str = (
                rec.create_date.strftime("%Y-%m-%d")
                if rec.create_date
                else str(fields.Date.today())
            )
            rec.name = f"POS Inalterability Check - {rec.company_id.name} - {date_str}"

    def action_open_job(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "queue.job",
            "res_id": self.queue_job_id.id,
            "view_mode": "form",
            "target": "current",
        }

    def action_run_check(self):
        self.ensure_one()
        self.batch_ids.unlink()
        self.write(
            {
                "state": "enqueued",
                "error_message": False,
                "pdf_report": False,
                "pdf_filename": False,
            }
        )
        job = self.with_delay()._run_integrity_check()
        self.queue_job_id = job.db_record()

    def _pos_order_domain(self):
        return [
            ("state", "in", ["paid", "done", "invoiced"]),
            ("company_id", "=", self.company_id.id),
            ("l10n_fr_secure_sequence_number", "!=", 0),
        ]

    def _run_integrity_check(self):
        """Split the flagged POS orders into batches and verify each in its own
        queue job, then finalize (aggregate + render the PDF).

        Each order is only checked against the *stored* hash of the previous
        order, so the batches are independent and can run concurrently.
        """
        self.ensure_one()
        company = self.company_id
        if not company._is_accounting_unalterable():
            self.write(
                {
                    "state": "failed",
                    "error_message": _(
                        "Accounting is not unalterable for the company %s. This "
                        "mechanism is designed for companies where accounting is "
                        "unalterable.",
                        company.name,
                    ),
                }
            )
            return
        orders = self.env["pos.order"].search(
            self._pos_order_domain(), order="l10n_fr_secure_sequence_number ASC"
        )
        if not orders:
            self.write(
                {
                    "state": "failed",
                    "error_message": _(
                        "There isn't any order flagged for data inalterability yet "
                        "for the company %s. This mechanism only runs for point of "
                        "sale orders generated after the installation of the module "
                        "France - Certification CGI 286 I-3 bis. - POS",
                        company.name,
                    ),
                }
            )
            return
        order_ids = orders.ids
        delayables = []
        previous_hash = ""
        for i in range(0, len(order_ids), BATCH_SIZE):
            batch_ids = order_ids[i : i + BATCH_SIZE]
            delayables.append(self.delayable()._verify_batch(batch_ids, previous_hash))
            # Stored hash of the batch's last order = previous_hash of the next one.
            previous_hash = self.env["pos.order"].browse(batch_ids[-1]).l10n_fr_hash
        group(*delayables).on_done(self.delayable()._finalize_check()).delay()

    def _verify_batch(self, order_ids, previous_hash):
        """Verify a contiguous batch of orders against the stored hash chain and
        store the corrupted order names on a dedicated batch record (one row per
        job to avoid write conflicts between concurrent batches)."""
        self.ensure_one()
        orders = (
            self.env["pos.order"].with_context(prefetch_fields=False).browse(order_ids)
        )
        corrupted = []
        previous = previous_hash
        for order in orders:
            if order.l10n_fr_hash != order._compute_hash(previous_hash=previous):
                corrupted.append(order.name)
            previous = order.l10n_fr_hash
        self.env["pos.inalterability.check.batch"].create(
            {"check_id": self.id, "corrupted_orders": ", ".join(corrupted)}
        )

    def _build_order_info(self, order):
        entry_reference = _("(Receipt ref.: %s)")
        order_reference_string = (
            order.pos_reference and entry_reference % order.pos_reference or ""
        )
        return [
            ctx_tz(order, "date_order"),
            order.l10n_fr_hash,
            order.name,
            order_reference_string,
            ctx_tz(order, "write_date"),
        ]

    def _finalize_check(self):
        """Aggregate the batch results and render the PDF from the precomputed
        data (without re-running the full check)."""
        self.ensure_one()
        company = self.company_id
        corrupted = []
        for batch in self.batch_ids:
            if batch.corrupted_orders:
                corrupted += batch.corrupted_orders.split(", ")
        orders = self.env["pos.order"].search(
            self._pos_order_domain(), order="l10n_fr_secure_sequence_number ASC"
        )
        start_info = self._build_order_info(orders[0])
        end_info = self._build_order_info(orders[-1])
        report_dict = {
            "first_order_name": start_info[2],
            "first_order_hash": start_info[1],
            "first_order_date": start_info[0],
            "last_order_name": end_info[2],
            "last_order_hash": end_info[1],
            "last_order_date": end_info[0],
        }
        corrupted_str = ", ".join(corrupted)
        msg_alert = (
            _("Corrupted data on point of sale orders: %s", corrupted_str)
            if corrupted
            else "None"
        )
        data = {
            "result": report_dict,
            "msg_alert": msg_alert,
            "printing_date": format_date(
                self.env, fields.Date.to_string(fields.Date.today())
            ),
            "corrupted_orders": corrupted_str or "None",
        }
        pdf_content, _dummy = (
            self.env["ir.actions.report"]
            .with_company(company)
            ._render_qweb_pdf(
                "l10n_fr_pos_cert.report_pos_hash_integrity",
                res_ids=[company.id],
                data={"pos_hash_integrity_result": data},
            )
        )
        self.write(
            {
                "state": "done",
                "pdf_report": base64.b64encode(pdf_content),
                "pdf_filename": "Hash integrity result PDF.pdf",
            }
        )
        self.batch_ids.unlink()


class PosInalterabilityCheckBatch(models.Model):
    _name = "pos.inalterability.check.batch"
    _description = "POS Inalterability Check Batch"

    check_id = fields.Many2one(
        "pos.inalterability.check",
        required=True,
        ondelete="cascade",
        index=True,
    )
    corrupted_orders = fields.Text()
