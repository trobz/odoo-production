from odoo.tests.common import tagged

from odoo.addons.edi_purchase_diapar_oca.tests.test_edi_purchase_diapar_oca import (
    TestEdiPurchaseDiaparOCA,
)


@tagged("post_install", "-at_install")
class TestEdiPurchaseDiaparQty(TestEdiPurchaseDiaparOCA):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_6 = cls.env.ref("product.product_product_6")
        cls.supplier_info_6 = cls.env["product.supplierinfo"].create(
            {
                "product_tmpl_id": cls.product_6.product_tmpl_id.id,
                "partner_id": cls.edi_supplier.id,
                "product_code": "334455",
                "min_qty": 1,
                "base_price": 10,
            }
        )

    def _generate_fake_input_ch_content_product_6(self):
        product_code = self.supplier_info_6.product_code
        product_name = "BISCOTTE 6CEREALE.300HEUD"
        price_ht = "000015500"
        apply_date = "20060305"
        return (
            f"07{product_code}00015{product_name}{price_ht}"
            + f"0000214100024000033924604808270011013700000030000{apply_date}0001403"
        )

    def test_edi_input_process_ch_with_base_price(self):
        order = self._create_purchase_order(self.edi_supplier, self.product_6)
        order.button_confirm()
        exchange_record_ch = self.env["edi.exchange.record"].create(
            {
                "backend_id": self.backend.id,
                "type_id": self.exchange_type_ch.id,
                "model": "purchase.order",
                "res_id": order.id,
            }
        )
        fake_content = self._generate_fake_input_ch_content_product_6().strip()
        exchange_record_ch._set_file_content(fake_content)
        exchange_record_ch.write({"edi_exchange_state": "input_received"})
        exchange_record_ch.backend_id.exchange_process(exchange_record_ch)
        self.assertEqual(
            exchange_record_ch.edi_exchange_state,
            "input_processed",
            "The EDI exchange record should be processed successfully.",
        )

        supplier_price_list = self.env["supplier.price.list"].search(
            [
                ("supplier_id", "=", self.edi_supplier.id),
                ("product_tmpl_id", "=", self.product_6.product_tmpl_id.id),
            ]
        )
        self.assertTrue(
            supplier_price_list, "A supplier price list record should be created."
        )
        self.assertEqual(
            supplier_price_list.price,
            1.55,
            "The price in the supplier price list should be updated to the new price.",
        )
        supllier_info = self.env["product.supplierinfo"].search(
            [
                ("partner_id", "=", self.edi_supplier.id),
                ("product_code", "=", self.supplier_info_6.product_code),
            ]
        )
        self.assertTrue(supllier_info, "The supplier info record should exist.")
        self.assertEqual(
            supllier_info.base_price,
            1.55,
            "The base price in the supplier info should be updated to the new price.",
        )
