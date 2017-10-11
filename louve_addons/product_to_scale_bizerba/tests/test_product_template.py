# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: La Louve (<http://www.lalouve.net/>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import os

from openerp.tests.common import SavepointCase
from openerp import tools, modules
from PIL import Image
import base64
import cStringIO


class TestBaseProductToScale(SavepointCase):

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
        log_text += ['0', '0', '0', '0', '0', '0', '0']

        product_text = "#".join(log_text)
        external_text = "\n".join([txt.replace("\n", '')
                                   for txt in log_external_text])
        if isinstance(product_text, str):
            product_text = unicode(product_text, 'iso-8859-1')
        if isinstance(external_text, str):
            product_text = unicode(external_text, 'iso-8859-1')
        return product_text, external_text

    def make_all_logs_as_send(self):
        '''
        @Function : this function used for making all created log is sent
        In scope Unittest, we don't need to test send file via FTP.
        '''
        logs = self.psl_obj.search([
            ('sent', '=', False),
            ('product_id', 'in', [self.prd_tmp_A.product_variant_ids[0].id,
                                  self.prd_tmp_B.product_variant_ids[0].id])])
        return logs.write({'sent': True})

    def prepare_scale_system_lines(self):
        # create product lines
        lines = [{'x2many_range': u'0', 'code': u'ABNR',
                  'name': u'N\xb0 de Rayon', 'sequence': 10,
                  'related_field_id': self.imd_obj.get_object_reference(
                     'product_to_scale_bizerba',
                     'field_product_scale_group_external_identity')[1],
                  'multiline_length': 0,
                  'field_id': self.imd_obj.get_object_reference(
                     'product_to_scale_bizerba',
                     'field_product_product_scale_group_id')[1],
                  'delimiter': u'#',
                  'type': u'many2one', 'numeric_round': 1.0,
                  'numeric_coefficient': 1.0, },
                 {'x2many_range': u'0', 'code': u'PLNR',
                  'name': u"N\xb0 d'Article", 'sequence': 11,
                  'multiline_length': 0,
                  'field_id': self.imd_obj.get_object_reference(
                    u'barcodes_generate',
                    'field_product_product_barcode_base')[1],
                  'delimiter': u'#',
                  'type': 'numeric', 'numeric_round': 1.0,
                  'numeric_coefficient': 1.0, },
                 {'x2many_range': u'0', 'code': u'ABEZ',
                  'name': u'Libell\xe9 Article', 'sequence': 12,
                  'multiline_length': 0,
                  'field_id': self.imd_obj.get_object_reference(
                     'product', 'field_product_product_name')[1],
                  'delimiter': u'#',
                  'type': 'text', 'numeric_round': 1.0,
                  'numeric_coefficient': 1.0, },
                 {'x2many_range': u'0', 'code': 'WGNR', 'constant_value': '1',
                  'name': u'N\xb0 Famille', 'sequence': 13,
                  'multiline_length': 0, 'delimiter': u'#',
                  'type': 'constant', 'numeric_round': 1.0,
                  'numeric_coefficient': 1.0, },
                 {'x2many_range': u'0', 'code': u'PREI',
                  'name': u'Prix Unitaire (x100)', 'sequence': 14,
                  'multiline_length': 0,
                  'field_id': self.imd_obj.get_object_reference(
                     u'product', 'field_product_product_list_price')[1],
                  'delimiter': u'#', 'type': 'numeric', 'numeric_round': 1.0,
                  'numeric_coefficient': 100.0, },
                 {'x2many_range': u'0', 'code': u'HAL1',
                  'name': u' Nombre de Jours Date 1', 'sequence': 15,
                  'multiline_length': 0,
                  'field_id': self.imd_obj.get_object_reference(
                     u'coop_default_pricetag',
                     'field_product_template_expiration_date_days')[1],
                  'delimiter': u'#', 'type': 'numeric', 'numeric_round': 1.0,
                  'numeric_coefficient': 1.0, },
                 {'x2many_range': u'0', 'code': u'HAL2', 'constant_value': '0',
                  'name': u' Nombre de Jours Date 2 (INUTILISE) ',
                  'sequence': 16, 'multiline_length': 0,
                  'delimiter': u'#', 'type': 'constant', 'numeric_round': 1.0,
                  'numeric_coefficient': 1.0, },
                 {'x2many_range': u'0', 'code': u'EAN1', 'name': u'Code EAN',
                  'sequence': 17, 'multiline_length': 0,
                  'field_id': self.imd_obj.get_object_reference(
                     u'product', 'field_product_product_barcode')[1],
                  'delimiter': u'#', 'type': 'text', 'numeric_round': 1.0,
                  'numeric_coefficient': 1.0, },
                 {'x2many_range': u'0', 'code': u'AART',
                  'name': u"Type Article ('P' / 'F')", 'sequence': 18,
                  'related_field_id': self.imd_obj.get_object_reference(
                     'product_to_scale_bizerba',
                     'field_product_uom_scale_type')[1],
                  'multiline_length': 0,
                  'field_id': self.imd_obj.get_object_reference(
                     u'product', 'field_product_product_uom_id')[1],
                  'delimiter': u'#', 'type': u'many2one', 'numeric_round': 1.0,
                  'numeric_coefficient': 1.0, },
                 {'x2many_range': u'0', 'code': u'TARA',
                  'name': u'Tare Article', 'sequence': 19,
                  'multiline_length': 0,
                  'field_id': self.imd_obj.get_object_reference(
                     u'product_to_scale_bizerba',
                     'field_product_product_scale_tare_weight')[1],
                  'delimiter': u'#', 'type': 'numeric', 'numeric_round': 1.0,
                  'numeric_coefficient': 1000.0, },
                 {'x2many_range': u'0', 'code': u'FIXG', 'name': u'Poids Fixe',
                  'sequence': 20, 'multiline_length': 0,
                  'field_id': self.imd_obj.get_object_reference(
                     u'coop_default_pricetag',
                     'field_product_template_weight_net')[1],
                  'delimiter': u'#', 'type': 'numeric', 'numeric_round': 1.0,
                  'numeric_coefficient': 1000.0, },
                 {'x2many_range': u'0', 'code': u'LOG1', 'constant_value': '0',
                  'name': u'Logo N\xb01', 'sequence': 21,
                  'multiline_length': 0,
                  'delimiter': u'#', 'type': 'constant', 'numeric_round': 1.0,
                  'numeric_coefficient': 1.0, },
                 {'x2many_range': u'0', 'code': u'LOG2', 'constant_value': '0',
                  'name': u' Logo N\xb02 (INUTILISE)',
                  'sequence': 22, 'multiline_length': 0, 'delimiter': u'#',
                  'type': 'constant', 'numeric_round': 1.0,
                  'numeric_coefficient': 1.0, },
                 {'x2many_range': u'0', 'code': u'LOG3', 'constant_value': '0',
                  'name': u'Logo N\xb03 (INUTILISE)', 'sequence': 23,
                  'multiline_length': 0, 'delimiter': u'#', 'type': 'constant',
                  'numeric_round': 1.0, 'numeric_coefficient': 1.0, },
                 {'x2many_range': u'0', 'code': u'ZUT1',
                  'name': u'Bloc Texte Ingr\xe9dients n\xb01', 'sequence': 24,
                  'multiline_length': 0,
                  'field_id': self.imd_obj.get_object_reference(
                     u'purchase_compute_order',
                     'field_product_product_ingredients')[1],
                  'delimiter': u'#', 'type': 'external_text',
                  'numeric_round': 1.0, 'numeric_coefficient': 1.0, },
                 {'x2many_range': u'0', 'code': u'ZUT2', 'constant_value': '0',
                  'name': u'Bloc Texte Ingr\xe9dients n\xb02 (INUTILISE)',
                  'sequence': 25, 'multiline_length': 0, 'delimiter': u'#',
                  'type': 'constant', 'numeric_round': 1.0,
                  'numeric_coefficient': 1.0, },
                 {'x2many_range': u'0', 'code': u'ZUT3', 'constant_value': '0',
                  'name': u'Bloc Texte Ingr\xe9dients n\xb03 (INUTILISE)',
                  'sequence': 26, 'multiline_length': 0, 'delimiter': u'#',
                  'type': 'constant', 'numeric_round': 1.0,
                  'numeric_coefficient': 1.0, },
                 {'x2many_range': u'0', 'code': u'ZUT4', 'constant_value': '0',
                  'name': u'Bloc Texte Ingr\xe9dients n\xb04 (INUTILISE)',
                  'sequence': 27, 'multiline_length': 0, 'delimiter': u'#',
                  'type': 'constant', 'numeric_round': 1.0,
                  'numeric_coefficient': 1.0, },
                 {'x2many_range': u'0', 'code': u'TX01',
                  'constant_value': u'Emballé le',
                  'name': u'Texte pour Zone de Texte N\xb01', 'sequence': 28,
                  'multiline_length': 0, 'delimiter': u'#',
                  'type': 'external_constant', 'numeric_round': 1.0,
                  'numeric_coefficient': 1.0, },
                 {'x2many_range': u'0', 'code': u'TX02',
                  'constant_value': u'De préférence avant',
                  'name': u'Texte pour Zone de Texte N\xb02', 'sequence': 29,
                  'multiline_length': 0, 'delimiter': u'#',
                  'type': 'external_constant', 'numeric_round': 1.0,
                  'numeric_coefficient': 1.0, },
                 {'x2many_range': u'0', 'code': u'TX03',
                  'name': u'Texte pour Zone de Texte N\xb03',
                  'sequence': 30, 'multiline_length': 0,
                  'field_id': self.imd_obj.get_object_reference(
                    u'coop_default_pricetag',
                    'field_product_template_extra_note_bizerba_pricetag_1')[1],
                  'delimiter': u'#', 'type': 'external_text',
                  'numeric_round': 1.0, 'numeric_coefficient': 1.0, },
                 {'x2many_range': u'0', 'code': u'TX04',
                  'name': u'Texte pour Zone de Texte N\xb04',
                  'sequence': 31, 'multiline_length': 0,
                  'field_id': self.imd_obj.get_object_reference(
                   u'coop_default_pricetag',
                   'field_product_template_extra_note_bizerba_pricetag_2')[1],
                  'delimiter': u'#', 'type': 'external_text',
                  'numeric_round': 1.0, 'numeric_coefficient': 1.0, },
                 {'x2many_range': u'0', 'code': u'TX05',
                  'constant_value': u'A vendre avant',
                  'name': u'Texte pour Zone de Texte N\xb05', 'sequence': 32,
                  'multiline_length': 0, 'delimiter': u'#',
                  'type': 'external_constant', 'numeric_round': 1.0,
                  'numeric_coefficient': 1.0, },
                 {'x2many_range': u'0', 'code': u'TX06',
                  'constant_value': u'Prix Unitaire',
                  'name': u'Texte pour Zone de Texte N\xb06', 'sequence': 33,
                  'multiline_length': 0, 'delimiter': u'#',
                  'type': 'external_constant', 'numeric_round': 1.0,
                  'numeric_coefficient': 1.0, },
                 {'x2many_range': u'0', 'code': u'TX07',
                  'constant_value': u'Poids Net',
                  'name': u'Texte pour Zone de Texte N\xb07', 'sequence': 34,
                  'multiline_length': 0, 'delimiter': u'#',
                  'type': 'external_constant', 'numeric_round': 1.0,
                  'numeric_coefficient': 1.0, },
                 {'x2many_range': '0', 'code': 'TX08',
                  'constant_value': 'Prix',
                  'name': u'Texte pour Zone de Texte N\xb08', 'sequence': 35,
                  'multiline_length': 0, 'delimiter': u'#',
                  'type': 'external_constant', 'numeric_round': 1.0,
                  'numeric_coefficient': 1.0, },
                 {'x2many_range': u'0', 'code': u'TX09', 'constant_value': '0',
                  'name': u'Texte pour Zone de Texte N\xb09 (INUTILISE)',
                  'sequence': 36, 'multiline_length': 0, 'delimiter': u'#',
                  'type': 'constant', 'numeric_round': 1.0,
                  'numeric_coefficient': 1.0, },
                 {'x2many_range': u'0', 'code': u'TX10', 'constant_value': '0',
                  'name': u'Texte pour Zone de Texte N\xb010 (INUTILISE)',
                  'sequence': 37, 'multiline_length': 0, 'delimiter': u'#',
                  'type': 'constant', 'numeric_round': 1.0,
                  'numeric_coefficient': 1.0},
                 {'x2many_range': u'0', 'code': u'MDAT', 'constant_value': '0',
                  'name': u'Image Article n\xb01 (INUTILISE)', 'sequence': 38,
                  'multiline_length': 0, 'delimiter': u'#', 'type': 'constant',
                  'numeric_round': 1.0, 'numeric_coefficient': 1.0, },
                 {'x2many_range': u'0', 'code': 'MDAT2', 'constant_value': '0',
                  'name': u'Image Article n\xb02 (INUTILISE)', 'sequence': 39,
                  'multiline_length': 0, 'delimiter': u'#', 'type': 'constant',
                  'numeric_round': 1.0, 'numeric_coefficient': 1.0, },
                 {'x2many_range': u'0', 'code': 'MDAT3', 'constant_value': '0',
                  'name': u'Image Article n\xb03 (INUTILISE)', 'sequence': 40,
                  'multiline_length': 0, 'delimiter': u'#', 'type': 'constant',
                  'numeric_round': 1.0, 'numeric_coefficient': 1.0, },
                 {'x2many_range': u'0', 'code': 'MDAT4', 'constant_value': '0',
                  'name': u'Image Article n\xb04 (INUTILISE)', 'sequence': 41,
                  'multiline_length': 0, 'delimiter': u'#', 'type': 'constant',
                  'numeric_round': 1.0, 'numeric_coefficient': 1.0, },
                 {'x2many_range': u'0', 'code': 'TXTA', 'constant_value': '0',
                  'name': 'Table Textes Nutrition (INUTILISE)', 'sequence': 42,
                  'multiline_length': 0, 'delimiter': u'', 'type': 'constant',
                  'numeric_round': 1.0, 'numeric_coefficient': 1.0}]
        self.scale_system_line_ids = []
        for line in lines:
            line.update({'scale_system_id': self.scale_system_id.id})
            line_id = self.psspl_obj.create(line)
            self.scale_system_line_ids.append(line_id.id)

    def set_scale_group_for_product(self):
        self.prd_tmp_A.product_variant_ids.write({'scale_group_id':
                                                  self.scale_group_1.id})
        self.prd_tmp_B.product_variant_ids.write({'scale_group_id':
                                                  self.scale_group_2.id})

    def setUp(self):
        super(TestBaseProductToScale, self).setUp()
        # Get Registries
        self.imd_obj = self.env['ir.model.data']
        self.ru_obj = self.env['res.users']
        self.prd_tmpl_obj = self.env['product.template']
        self.prd_prd_obj = self.env['product.product']
        self.pss_obj = self.env['product.scale.system']
        self.psg_obj = self.env['product.scale.group']
        self.psl_obj = self.env['product.scale.log']
        self.psspl_obj = self.env['product.scale.system.product.line']
        self.prd_uom_obj = self.env['product.uom']
        self.prd_categ_obj = self.env['product.category']
        self.pos_categ_obj = self.env['pos.category']

        # create product category
        self.cate_id = self.prd_categ_obj.create({
            'name': 'Vegerables',
            'type': 'normal',
            'property_cost_method': 'standard',
            'property_valuation': 'manual_periodic'})
        self.pos_cate_id = self.env['pos.category'].create({
            'name': 'Vegerables'})

        # create scale systems
        self.scale_system_id = self.pss_obj.create({
            'name': 'Scale Bizerba System',
            'encoding': 'iso-8859-1',
            'external_text_file_pattern': 'TEXT_MAG_0000_%Y%m%d_%H%M%S.CSV',
            'product_text_file_pattern': 'ARTI_MAG_0000_%Y%m%d_%H%M%S.CSV',
            'csv_relative_path': '/',
            'product_image_relative_path': '/IMAGE_IMPORT/'})

        # create scale groups
        self.scale_group_1 = self.psg_obj.create({
            'name': 'Group A',
            'external_identity': '001',
            'id': 10000,
            'scale_system_id': self.scale_system_id.id})
        self.scale_group_2 = self.psg_obj.create({
            'name': 'Group B',
            'external_identity': '002',
            'id': 20000,
            'scale_system_id': self.scale_system_id.id})
        self.prepare_scale_system_lines()
        # create products
        base_path = modules.get_module_path('product_to_scale_bizerba')
        img_path = os.path.join(base_path,
                                "static", "description",
                                "Abricot N4 vrac.jpg")
        jpgfile = Image.open(img_path)
        buffer = cStringIO.StringIO()
        jpgfile.save(buffer, format="JPEG")
        self.prd_tmp_A = self.prd_tmpl_obj.create(
            {'name': 'Celery',
             'barcode': 'PRD00000000A',
             'default_code': 'PRDA',
             'description': "Product A for test scale log.",
             'description_sale': "Product A for test scale log.",
             'list_price': 1.05,
             'standard_price': 0.5,
             'categ_id': self.cate_id.id,
             'pos_categ_id': self.pos_cate_id.id,
             'to_weight': True,
             'image': base64.b64encode(buffer.getvalue()),
             'uom_po_id': self.env.ref('product.product_uom_kgm').id,
             'uom_id': self.env.ref('product.product_uom_kgm').id})
        self.prd_tmp_A.product_variant_ids.write({
             'barcode_base': '8888',
             'expiration_date_days': 5,
             'scale_tare_weight': 0.03,
             'weight_net': 0.97,
             'ingredients': "Ingredients",
             'extra_note_bizerba_pricetag_1': "extra_note_bizerba_pricetag_1",
             'extra_note_bizerba_pricetag_2': "extra_note_bizerba_pricetag_2"})
        self.prd_tmp_B = self.prd_tmpl_obj.create(
            {'name': 'Abricot N4 vrac',
             'barcode': 'PRD00000000B',
             'default_code': 'PRDB',
             'description': "Product A for test scale log.",
             'description_sale': "Product A for test scale log.",
             'list_price': 1.85,
             'standard_price': 0.75,
             'categ_id': self.cate_id.id,
             'pos_categ_id': self.pos_cate_id.id,
             'image': base64.b64encode(buffer.getvalue()),
             'to_weight': True,
             'uom_po_id': self.env.ref('product.product_uom_kgm').id,
             'uom_id': self.env.ref('product.product_uom_kgm').id,
             })
        self.prd_tmp_B.product_variant_ids.write({
           'barcode_base': '9999',
           'expiration_date_days': 7,
           'scale_tare_weight': 0.03,
           'weight_net': 0.97,
           'ingredients': "Ingredients",
           'extra_note_bizerba_pricetag_1': "extra_note_bizerba_pricetag_1",
           'extra_note_bizerba_pricetag_2': "extra_note_bizerba_pricetag_2"})

        self.set_scale_group_for_product()

    @classmethod
    def setUpClass(cls):
        super(TestBaseProductToScale, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        super(TestBaseProductToScale, cls).tearDownClass()

    def assert_result_for_test(self, mode):
        scale_log_A = self.psl_obj.search([
           ('sent', '=', False),
           ('product_id', '=', self.prd_tmp_A.product_variant_ids[0].id),
           ('action', '=', mode)])
        scale_log_B = self.psl_obj.search([
           ('sent', '=', False),
           ('product_id', '=', self.prd_tmp_B.product_variant_ids[0].id),
           ('action', '=', mode)])
        if not scale_log_A or not scale_log_B:
            assert False
        else:
            for log in scale_log_A:
                product_text, external_text = self.generate_product_text(
                      self.prd_tmp_A.product_variant_ids[0],
                      self.scale_group_1, mode)
                self.assertEqual(log.product_text.strip(),
                                 product_text)
                self.assertEqual(log.external_text_display.strip(),
                                 external_text)
            for log in scale_log_B:
                product_text, external_text = self.generate_product_text(
                      self.prd_tmp_B.product_variant_ids[0],
                      self.scale_group_2, mode)
                self.assertEqual(log.product_text.strip(),
                                 product_text)
                self.assertEqual(log.external_text_display.strip(),
                                 external_text)

    def test_normal_cases(self):
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

    def test_abnormal_cases(self):
        self.make_all_logs_as_send()

        # update product
        self.prd_tmp_A.write({'name': u"Cidre brut Vergers Bio d’Ohain",
                              'ingredients': u"""
Mousse fine effervescence apporte une fraicheur agréable, Aspect limpide, couleur dorée-orangée, Puissant, complexe et varié, Arômes fruités, floraux, long en bouche
Pays d'origine : France
taux d'alcool : 5,50%
"""})
        self.prd_tmp_B.write({'name': u"Abricot N°4 vrac", 'ingredients': u"""
SOURCE DE LA FIBRE ALIMENTAIRE: Nos abricots séchés organiques sont parfaits pour tous les régimes car ils sont riches en fibres.
BOOST OF IRON: La teneur en fer d'abricots secs est donc bonne pour tous, en particulier les végétaliens."""})

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
