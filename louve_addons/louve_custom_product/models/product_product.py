# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from openerp import fields, models, api, _
from openerp.exceptions import Warning
import openerp.addons.decimal_precision as dp


class ProductProduct(models.Model):
    _inherit = 'product.product'

    scale_logo_code = fields.Char(
        related="product_tmpl_id.scale_logo_code",
        string="Scale Logo Code",
        readonly=True,
        store=True)
    volume = fields.Float(digits=dp.get_precision('Volume'))
    multi_barcode_ids = fields.One2many(
        'product.multi.barcode', 'product_id',
        string='Product Multiple Barcodes')

    @api.model
    def search(self, args, offset=0, limit=0, order=None, count=False):
        new_args = self.get_domain_multi_barcode_for_product(args)
        return super(ProductProduct, self).search(
            new_args, offset, limit, order, count=count)

    @api.model
    def get_domain_multi_barcode_for_product(self, args):
        """
            Get Multi Barcode for product if when search product with "barcode"
        """
        new_args = []
        for arg in args:
            if arg[0] == 'barcode':
                new_args += [
                    '|', ('multi_barcode_ids.barcode', arg[1], arg[2]), arg]
            else:
                new_args += [arg]
        return new_args

    @api.multi
    def unlink(self):
        raise Warning(_(
            'You cannot delete product, please archive it instead'))
        return super(ProductProduct, self).unlink()

    @api.multi
    def write(self, vals):
        if 'available_in_pos' in vals and not vals['available_in_pos']:
            self.check_pos_session_running()
        return super(ProductProduct, self).write(vals)

    @api.multi
    def check_pos_session_running(self):
        pos_sessions = self.env['pos.session'].search(
            [('state', 'in', ['opening_control', 'opened'])])
        if pos_sessions:
            raise Warning(_(
                'You cannot unticking Available in the Point of Sale '
                'When POS Session are running with ids %s') % pos_sessions.ids)
        return True
