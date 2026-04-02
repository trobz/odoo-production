from odoo import fields
from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestPurchase(TransactionCase):
    def setUp(self):
        super().setUp()
        self.PurchaseOrder = self.env["purchase.order"]
        self.AccountMove = self.env["account.move"]
        self.AccountAccount = self.env["account.account"]
        self.Journal = self.env["account.journal"]
        self.SupplierInfoUpdate = self.env["supplier.info.update"]
        self.supplier_id = self.env.ref("base.res_partner_3")
        self.product_1 = self.env.ref("product.product_product_8")
        self.product_1.purchase_method = "purchase"
        self.purchase_journal = self.Journal.search(
            [("type", "=", "purchase")], limit=1
        )
        self.cash_journal = self.Journal.search([("type", "=", "cash")], limit=1)

        self.po_vals = {
            "partner_id": self.supplier_id.id,
            "order_line": [
                (
                    0,
                    0,
                    {
                        "name": self.product_1.name,
                        "product_id": self.product_1.id,
                        "product_qty": 5.0,
                        "product_uom": self.product_1.uom_po_id.id,
                        "price_unit": 500.0,
                        "date_planned": fields.Date.today(),
                    },
                )
            ],
        }
        self.po = self.PurchaseOrder.create(self.po_vals)

        self.supplier_id.show_discount = True

        self.supplierinfo_1 = self.env["product.supplierinfo"].create(
            {
                "partner_id": self.supplier_id.id,
                "product_tmpl_id": self.product_1.product_tmpl_id.id,
                "min_qty": 0.0,
                "price_policy": self.po.order_line[0].price_policy,
                "base_price": 100.0,
                "discount": 0.0,
            }
        )

        self.company_partner_bank = self.env["res.partner.bank"].create(
            {
                "partner_id": self.env.user.company_id.partner_id.id,
                "acc_number": "1234567890",
            }
        )

    def _create_move_from_po(self, move_type, partner_bank_id=None):
        move_new = self.AccountMove.new(
            {
                "purchase_id": self.po.id,
                "move_type": move_type,
                "company_id": self.env.user.company_id.id,
                "partner_bank_id": partner_bank_id.id if partner_bank_id else False,
            }
        )
        move_new._onchange_purchase_auto_complete()
        move_new._onchange_partner_id()
        inv_vals = move_new._convert_to_write(move_new._cache)

        if not inv_vals.get("invoice_date"):
            inv_vals["invoice_date"] = fields.Date.today()
        if not inv_vals.get("date"):
            inv_vals["date"] = fields.Date.today()

        for o2m_field in ("invoice_line_ids", "line_ids"):
            commands = inv_vals.get(o2m_field)
            if not commands:
                continue
            inv_vals[o2m_field] = [
                command for command in commands if command and command[0] not in (5, 6)
            ]
        return self.AccountMove.create(inv_vals)

    def test_001_check_po_line(self):
        self.po.order_line.update_po_price_to_vendor_price()
        vendor_price_line = self.product_1.seller_ids.filtered(
            lambda vp_line: vp_line.partner_id.id == self.supplier_id.id
        )
        if vendor_price_line:
            self.assertEqual(
                vendor_price_line[0].base_price,
                self.po.order_line[0].price_unit,
                f"Supplier's Base price has to be {self.po.order_line[0].price_unit}",
            )

    def test_002_check_invoice(self):
        self.po.button_confirm()
        picking = self.po.picking_ids
        picking.move_line_ids.write({"quantity": 5.0})
        picking.button_validate()

        # Vendor Bill 1
        self.invoice1 = self._create_move_from_po("in_invoice")
        self.assertEqual(
            self.invoice1.invoice_line_ids[0].quantity,
            5.0,
            "Product Quantity has to be 5.0!",
        )
        self.invoice1.invoice_line_ids[0].quantity = 3.0
        self.invoice1.action_post()

        # Vendor Bill 2
        self.invoice2 = self._create_move_from_po("in_invoice")
        self.assertEqual(
            self.invoice2.invoice_line_ids[0].quantity,
            2.0,
            "Product Quantity has to be 2.0!",
        )

        # Vendor Refund Bill 3
        self.invoice3 = self.invoice1._reverse_moves(
            default_values_list=[
                {
                    "invoice_date": fields.Date.today(),
                    "date": fields.Date.today(),
                    "partner_bank_id": self.company_partner_bank.id,
                }
            ]
        )
        self.assertEqual(
            self.invoice3.invoice_line_ids[0].quantity,
            3.0,
            "Refund Product's Quantity has to be 3.0!",
        )

    def test_003_block_invoice_until_reception_confirmed(self):
        self.po.button_confirm()
        with self.assertRaises(UserError):
            self._create_move_from_po("in_invoice")

    def test_004_supplier_info_update_wizard_updates_vendor_price(self):
        ctx = {
            "active_model": "purchase.order",
            "active_id": self.po.id,
        }
        defaults = self.SupplierInfoUpdate.with_context(**ctx).default_get(
            ["line_ids", "partner_id", "show_discount"]
        )
        wizard = self.SupplierInfoUpdate.with_context(**ctx).create(defaults)

        self.assertEqual(wizard.partner_id, self.supplier_id)
        self.assertTrue(wizard.line_ids, "Wizard should have at least one line")

        line = wizard.line_ids.filtered(
            lambda line: line.seller_id == self.supplierinfo_1
        )[:1]
        self.assertTrue(line, "Wizard should include a line linked to supplierinfo")
        line.price_unit = 250.0
        line.discount = 10.0

        wizard.update_prices()
        self.supplierinfo_1.invalidate_recordset(["base_price", "discount"])
        self.assertEqual(self.supplierinfo_1.base_price, 250.0)
        self.assertEqual(self.supplierinfo_1.discount, 10.0)

    def test_005_supplierinfo_create_maps_price_to_base_price(self):
        supplierinfo = self.env["product.supplierinfo"].create(
            {
                "partner_id": self.supplier_id.id,
                "product_tmpl_id": self.product_1.product_tmpl_id.id,
                "min_qty": 0.0,
                "price_policy": self.po.order_line[0].price_policy,
                "price": 42.0,
            }
        )
        self.assertEqual(supplierinfo.base_price, 42.0)

    def test_006_supplierinfo_write_maps_price_to_base_price(self):
        self.supplierinfo_1.write({"price": 55.0})
        self.supplierinfo_1.invalidate_recordset(["base_price"])
        self.assertEqual(self.supplierinfo_1.base_price, 55.0)

    def test_007_supplierinfo_compute_prices_with_taxes(self):
        Tax = self.env["account.tax"]
        company = self.env.company
        company_ctx = {"allowed_company_ids": [company.id]}
        included_tax = Tax.with_context(allowed_company_ids=[company.id]).create(
            {
                "name": "Included 10%",
                "amount": 10.0,
                "amount_type": "percent",
                "type_tax_use": "sale",
                "price_include_override": "tax_included",
                "company_id": company.id,
            }
        )
        excluded_tax = Tax.with_context(allowed_company_ids=[company.id]).create(
            {
                "name": "Excluded 20%",
                "amount": 20.0,
                "amount_type": "percent",
                "type_tax_use": "sale",
                "price_include_override": "tax_excluded",
                "company_id": company.id,
            }
        )

        product_tmpl = (
            self.env["product.template"]
            .with_context(**company_ctx)
            .with_company(company)
            .create(
                {
                    "name": "Test Product Taxes",
                    "company_id": company.id,
                    "list_price": 110.0,
                    "taxes_id": [(6, 0, (included_tax + excluded_tax).ids)],
                }
            )
        )
        product_tmpl = product_tmpl.with_context(**company_ctx).with_company(company)
        self.assertEqual(
            product_tmpl.with_company(company).taxes_id,
            included_tax + excluded_tax,
        )
        supplierinfo = self.env["product.supplierinfo"].create(
            {
                "partner_id": self.supplier_id.id,
                "product_tmpl_id": product_tmpl.id,
                "min_qty": 0.0,
                "price_policy": self.po.order_line[0].price_policy,
                "base_price": 1.0,
            }
        )
        supplierinfo = supplierinfo.with_context(**company_ctx).with_company(company)
        supplierinfo.product_tmpl_id.invalidate_recordset(["taxes_id", "list_price"])
        self.assertEqual(
            supplierinfo.product_tmpl_id.taxes_id,
            included_tax + excluded_tax,
        )
        supplierinfo.invalidate_recordset(
            ["price_taxes_excluded", "price_taxes_included"]
        )
        supplierinfo._compute_get_prices()

        self.assertAlmostEqual(supplierinfo.price_taxes_excluded, 100.0, places=2)
        self.assertAlmostEqual(supplierinfo.price_taxes_included, 132.0, places=2)

    def test_008_invoice_line_onchange_product_sets_vendor_values(self):
        self.po.button_confirm()
        picking = self.po.picking_ids
        picking.move_line_ids.write({"quantity": 5.0})
        picking.button_validate()

        invoice = self._create_move_from_po("in_invoice")
        line = invoice.invoice_line_ids[0]

        line.discount = 0.0
        line.base_price = 0.0
        line.price_unit = 0.0

        line._onchange_product_id()
        self.assertEqual(line.discount, self.supplierinfo_1.discount)
        self.assertEqual(line.base_price, self.supplierinfo_1.base_price)

    def test_009_invoice_creation_allowed_if_pickings_cancelled(self):
        self.po.button_confirm()
        self.po.picking_ids.write({"state": "cancel"})
        invoice = self._create_move_from_po("in_invoice")
        self.assertEqual(invoice.move_type, "in_invoice")
