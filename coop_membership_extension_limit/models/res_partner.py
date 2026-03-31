# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class ResPartner(models.Model):
    _inherit = "res.partner"

    def _compute_cooperative_state(self):
        res = super()._compute_cooperative_state()
        self._update_extension_by_cooperative_state()
        return res

    def _update_extension_by_cooperative_state(self):
        partners = self.filtered(
            lambda partner: partner.cooperative_state == "up_to_date"
        )
        if not partners:
            return
        extensions = self.env["shift.extension"].search(
            [("partner_id", "in", partners.ids), ("is_new", "=", True)]
        )
        if extensions:
            extensions.write({"is_new": False})
