# Copyright (C) 2012-Today GRAP (http://www.grap.coop)
# Copyright (C) 2020-Today: Druidoo (<https://www.druidoo.io>)
# @author Julien WESTE
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProductLabel(models.Model):
    _name = "product.label"
    _description = "Pricetag Label"

    code = fields.Char(required=True)
    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(string="Company", comodel_name="res.company")
    website = fields.Char()
    note = fields.Text()
    image = fields.Image(
        max_width=1024,
        max_height=1024,
        help=" used as image for the label, limited to 1024x1024px.",
    )
    scale_logo_code = fields.Char()
