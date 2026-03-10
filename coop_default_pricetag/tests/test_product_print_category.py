# Copyright (C) 2012-Today GRAP (http://www.grap.coop)
# Copyright (C) 2020-Today: Druidoo (<https://www.druidoo.io>)
# @author Julien WESTE
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import Command
from odoo.tests.common import TransactionCase


class TestProductPrintCategory(TransactionCase):
    """Tests for 'Product Print Category' Module"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.wizard_obj = cls.env["product.print.wizard"]
        cls.pricetag = cls.env.ref("coop_default_pricetag.pricetag_model_default")
        cls.custom_report_obj = cls.env["report.product_print_category.report_pricetag"]
        cls.prod_categ = cls.env.ref("product.product_category_all")
        cls.prod_uom = cls.env.ref("uom.product_uom_categ_unit")
        cls.prod_name = cls.env.ref("product.field_product_product__name")
        cls.qweb_view = cls.env.ref("coop_default_pricetag.report_pricetag")
        cls.print_category = cls.env["product.print.category"].create(
            {
                "name": "Default Category",
                "pricetag_model_id": cls.pricetag.id,
                "field_ids": [Command.link(cls.prod_name.id)],
                "qweb_view_id": cls.qweb_view.id,
            }
        )
        cls.template_obj = cls.env["product.template"]
        cls.product_obj = cls.env["product.product"]
        cls.template0 = cls.template_obj.create(
            {
                "name": "template0",
                "categ_id": cls.prod_categ.id,
                "uom_id": cls.prod_uom.id,
                "uom_po_id": cls.prod_uom.id,
                "description_sale": "template0",
                "standard_price": 10.0,
                "list_price": 12.0,
                "type": "consu",
                "print_category_id": cls.print_category.id,
            }
        )
        # Use the auto-created variant; mark as already printed
        cls.product0 = cls.template0.product_variant_ids[0]
        cls.product0.write({"default_code": "tmp0", "to_print": False})
        cls.template1 = cls.template_obj.create(
            {
                "name": "template1",
                "categ_id": cls.prod_categ.id,
                "uom_id": cls.prod_uom.id,
                "uom_po_id": cls.prod_uom.id,
                "description_sale": "template1",
                "standard_price": 50.0,
                "list_price": 60.0,
                "type": "consu",
                "print_category_id": cls.print_category.id,
            }
        )
        # template2 provides the 3rd product; mark as already printed
        cls.template2 = cls.template_obj.create(
            {
                "name": "template2",
                "categ_id": cls.prod_categ.id,
                "uom_id": cls.prod_uom.id,
                "uom_po_id": cls.prod_uom.id,
                "description_sale": "template2",
                "standard_price": 20.0,
                "list_price": 25.0,
                "type": "consu",
                "print_category_id": cls.print_category.id,
            }
        )
        cls.template2.product_variant_ids[0].write({"to_print": False})

    # Test Section
    def test_01_test_wizard_obsolete(self):
        wizard = self.wizard_obj.with_context(
            active_model="product.print.category", active_ids=[self.print_category.id]
        ).create({})
        self.assertEqual(
            len(wizard.line_ids), 1, "Print obsolete product should propose 1 product"
        )

    def test_02_test_wizard_all(self):
        wizard = self.wizard_obj.with_context(
            active_model="product.print.category",
            active_ids=[self.print_category.id],
            all_products=True,
        ).create({})
        self.assertEqual(
            len(wizard.line_ids), 3, "Print all products should propose 3 products"
        )
        wizard.print_report()
        self.env["report.coop_default_pricetag.report_pricetag"]._get_report_values(
            docids=[wizard.id]
        )
        self.env[
            "report.coop_default_pricetag.report_pricetag_barcode"
        ]._get_report_values(docids=[wizard.id])
        self.env[
            "report.coop_default_pricetag.report_pricetag_simple_barcode"
        ]._get_report_values(docids=[wizard.id])
