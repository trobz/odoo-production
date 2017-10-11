# -*- coding: utf-8 -*-
# Copyright (C) 2015-Today: Smile (<http://www.smile.fr>)
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import os

from openerp.tests.common import SavepointCase
from openerp.addons.product_to_scale_bizerba.tests.test_product_template\
    import TestBaseProductToScale
from openerp import tools, modules
from PIL import Image
import base64
import cStringIO


class TestLouveProductToScale(TestBaseProductToScale):

    def generate_product_text(self, product, scale_group, mode='create'):
        '''
        @Function: to generate the expectation product_text of scale log
        base on the scale system lines defination.
        '''
        log_text = []
        log_external_text = []
        external_prefix = "C"
        if mode == 'create' or mode == 'write':
            log_text.append("C")
        else:
            log_text.append("S")
        log_text.append(scale_group.external_identity)
        external_prefix += "#%s" % (scale_group.external_identity)
        log_text += [str(product.barcode_base), product.name, "1",
                     "%s" % (int(product.list_price * 100)),
                     str(product.expiration_date_days), "0",
                     product.barcode, "P",
                     "%s" % (int(product.scale_tare_weight * 1000)),
                     "%s" % (int(product.weight_net * 1000)),
                     product.scale_logo_code, "0", '0']
        ext_text = "".join([external_prefix, '#', "%s%s" % (
           str(product.id),
           str(self.scale_system_line_ids[len(log_text) - 1]).rjust(4, '0')),
                            '#', product.ingredients])
        log_external_text.append(ext_text)
        log_text.append("%s%s" % (
           str(product.id),
           str(self.scale_system_line_ids[len(log_text) - 1]).rjust(4, '0')))
        log_text += ['0', '0', '0']
        ext_text = "".join([external_prefix, '#',
                            str(self.scale_system_line_ids[len(log_text) - 1]),
                            '#', u"Emballé le"])
        log_external_text.append(ext_text)
        log_text.append(str(self.scale_system_line_ids[len(log_text) - 1]))
        ext_text = "".join([external_prefix, '#',
                            str(self.scale_system_line_ids[len(log_text) - 1]),
                            '#', u"De préférence avant"])
        log_external_text.append(ext_text)
        log_text.append(str(self.scale_system_line_ids[len(log_text) - 1]))
        ext_text = "".join([external_prefix, '#', "%s%s" % (
           str(product.id),
           str(self.scale_system_line_ids[len(log_text) - 1]).rjust(4, '0')),
                            '#', product.extra_note_bizerba_pricetag_1])
        log_external_text.append(ext_text)
        log_text.append("%s%s" % (
           str(product.id),
           str(self.scale_system_line_ids[len(log_text) - 1]).rjust(4, '0')))
        ext_text = "".join([external_prefix, '#', "%s%s" % (
           str(product.id),
           str(self.scale_system_line_ids[len(log_text) - 1]).rjust(4, '0')),
                            '#', product.extra_note_bizerba_pricetag_2])
        log_external_text.append(ext_text)
        log_text.append("%s%s" % (
           str(product.id),
           str(self.scale_system_line_ids[len(log_text) - 1]).rjust(4, '0')))
        ext_text = "".join([external_prefix, '#',
                            str(self.scale_system_line_ids[len(log_text) - 1]),
                            '#', u"A vendre avant"])
        log_external_text.append(ext_text)
        log_text.append(str(self.scale_system_line_ids[len(log_text) - 1]))
        ext_text = "".join([external_prefix, '#',
                            str(self.scale_system_line_ids[len(log_text) - 1]),
                            '#', u"Prix Unitaire"])
        log_external_text.append(ext_text)
        log_text.append(str(self.scale_system_line_ids[len(log_text) - 1]))
        ext_text = "".join([external_prefix, '#',
                            str(self.scale_system_line_ids[len(log_text) - 1]),
                            '#', u"Poids Net"])
        log_external_text.append(ext_text)
        log_text.append(str(self.scale_system_line_ids[len(log_text) - 1]))
        ext_text = "".join([external_prefix, '#',
                            str(self.scale_system_line_ids[len(log_text) - 1]),
                            '#', u"Prix"])
        log_text.append(str(self.scale_system_line_ids[len(log_text) - 1]))
        log_external_text.append(ext_text)
        log_text += ['0', '0', '0', '0', '0', '0', '0']

        product_text = "#".join(log_text)
        external_text = "\n".join([txt.replace("\n", '')
                                   for txt in log_external_text])
        if isinstance(product_text, str):
            product_text = unicode(product_text, 'iso-8859-1')
        if isinstance(external_text, str):
            product_text = unicode(external_text, 'iso-8859-1')
        return product_text, external_text

    def prepare_scale_system_lines(self):
        super(TestLouveProductToScale, self).prepare_scale_system_lines()

        # update scale logo code lines
        vals = {'x2many_range': u'0', 'code': u'LOG1', 'constant_value': '1',
                'name': u'Logo N\xb01', 'sequence': 21,
                'multiline_length': 0,
                'field_id': self.imd_obj.get_object_reference(
                   'louve_custom_product',
                   'field_product_product_scale_logo_code')[1],
                'delimiter': u'#', 'type': 'text', 'numeric_round': 1.0,
                'numeric_coefficient': 1.0, }
        for line in self.scale_system_id.product_line_ids:
            if line.code == vals['code']:
                line.write(vals)
                break

    def setUp(self):
        super(TestLouveProductToScale, self).setUp()

    @classmethod
    def setUpClass(cls):
        super(TestLouveProductToScale, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        super(TestLouveProductToScale, cls).tearDownClass()
