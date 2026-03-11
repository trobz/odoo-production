# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# @author: Julien Weste
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    fundraising_partner_type_ids = fields.Many2many(
        comodel_name="capital.fundraising.partner.type",
        string="Fundraising Partner Type",
    )

    amount_subscription = fields.Float(
        string="Total Subscribed Amount", compute="_compute_amount_subscription"
    )

    # Compute section
    def _compute_amount_subscription(self):
        inv_obj = self.env["account.move"].sudo()
        for partner in self:
            invoices = inv_obj.search(
                [
                    ("move_type", "in", ["out_invoice", "out_refund"]),
                    ("partner_id", "=", partner.id),
                    ("is_capital_fundraising", "=", True),
                    ("state", "=", "posted"),
                ]
            )
            partner.amount_subscription = sum(invoices.mapped("amount_total_signed"))
