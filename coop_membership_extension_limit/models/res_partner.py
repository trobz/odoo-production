# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    def _compute_cooperative_state(self):
        super()._compute_cooperative_state()
        self._update_extension_by_cooperative_state()

    def _update_extension_by_cooperative_state(self):
        records = self.filtered(lambda r: r.cooperative_state == "up_to_date")
        if not records:
            return
        extensions = self.env["shift.extension"].search([
            ("partner_id", "in", records.ids),
            ("is_new", "=", True)
        ])
        if extensions:
            extensions.write({"is_new": False})
