from odoo import api, models


class ReportPosHashIntegrity(models.AbstractModel):
    _inherit = "report.l10n_fr_pos_cert.report_pos_hash_integrity"

    @api.model
    def _get_report_values(self, docids, data=None):
        # When the queue-based check already computed the result, render from it
        # instead of re-running the full (synchronous) integrity check.
        precomputed = (data or {}).get("pos_hash_integrity_result")
        if precomputed:
            return {
                "doc_ids": docids,
                "doc_model": self.env["res.company"],
                "data": precomputed,
                "docs": self.env["res.company"].browse(self.env.company.id),
            }
        return super()._get_report_values(docids, data=data)
