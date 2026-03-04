# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class CapitalFundraisingCategory(models.Model):
    _inherit = "capital.fundraising.category"

    # Column Section
    is_default = fields.Boolean()

    minimum_share_qty = fields.Integer()

    line_ids = fields.One2many()

    is_worker_capital_category = fields.Boolean()
