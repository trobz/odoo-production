# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class GeneralLedgerReportWizardCustom(models.TransientModel):
    _inherit = "general.ledger.report.wizard"

    def _get_atr_from_dict(self, obj_id, data, key):
        values = data.get(obj_id) or data.get(str(obj_id))
        if not values:
            return ""
        return values.get(key, "")
