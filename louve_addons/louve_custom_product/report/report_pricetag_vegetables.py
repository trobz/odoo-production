# -*- coding: utf-8 -*-

from openerp import models


class ReportPricetagVegetables(models.AbstractModel):
    _name = 'report.louve_custom_product.report_pricetag_vegetables'
    _inherit = 'report.coop_default_pricetag.report_pricetag'
