# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: La Louve (<http://www.lalouve.net/>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import os

from test_product_template import TestBaseProductToScale


class TestProductToScaleWithImage(TestBaseProductToScale):

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
                     "0", "0", '0']
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
        log_text += ['0', '0']
        # add image name
        if product.image:
            log_text.append("%s.%s" % (str(product.id), 'jpeg'))
        else:
            log_text.append("")
        log_text += ['0', '0', '0', '0']

        product_text = "#".join(log_text)
        external_text = "\n".join([txt.replace("\n", '')
                                   for txt in log_external_text])
        if isinstance(product_text, str):
            product_text = unicode(product_text, 'iso-8859-1')
        if isinstance(external_text, str):
            product_text = unicode(external_text, 'iso-8859-1')
        return product_text, external_text

    def prepare_scale_system_lines(self):
        super(TestProductToScaleWithImage, self).prepare_scale_system_lines()

        # update scale image lines
        vals = {'x2many_range': u'0', 'code': 'MDAT', 'sequence': 38,
                'field_id': self.imd_obj.get_object_reference(
                   'product', 'field_product_product_image')[1],
                'delimiter': u'#', 'type': 'product_image',
                'constant_value': '', 'multiline_length': False,
                'suffix': '.jpeg', 'numeric_round': False,
                'numeric_coefficient': False}
        for line in self.scale_system_id.product_line_ids:
            if line.code == vals['code']:
                line.write(vals)
                break

    def setUp(self):
        super(TestProductToScaleWithImage, self).setUp()

    @classmethod
    def setUpClass(cls):
        super(TestProductToScaleWithImage, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        super(TestProductToScaleWithImage, cls).tearDownClass()

    def test_abnormal_cases(self):
        super(TestProductToScaleWithImage, self).test_abnormal_cases()
        self.make_all_logs_as_send()

        # remove image
        self.prd_tmp_A.write({'image': False})
        self.prd_tmp_A.product_variant_ids.write({'image': False})
        self.prd_tmp_B.write({'image': False})
        self.prd_tmp_B.product_variant_ids.write({'image': False})

        # create scale logs for creation
        self.scale_group_1.send_all_to_scale_create()
        self.scale_group_2.send_all_to_scale_create()
        self.assert_result_for_test('create')

        # create scale logs for creation
        self.scale_group_1.send_all_to_scale_write()
        self.scale_group_2.send_all_to_scale_write()
        self.assert_result_for_test('write')

        # create scale logs for creation
        self.scale_group_1.product_ids.send_scale_unlink()
        self.scale_group_2.product_ids.send_scale_unlink()
        self.assert_result_for_test('unlink')
