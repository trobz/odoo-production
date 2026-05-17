from odoo.tests.common import TransactionCase


class TestStockInventoryBarcodeQtyUpdate(TransactionCase):
    def setUp(self):
        super().setUp()
        self.Wizard = self.env["stock.inventory.barcode"]
        self.StockQuant = self.env["stock.quant"]

        self.location = self.env["stock.location"].create(
            {"name": "Test Location", "usage": "internal"}
        )
        self.product = self.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "consu",
                "is_storable": True,
                "barcode": "BARCODE001",
                "default_code": "REF001",
            }
        )
        self.product2 = self.env["product.product"].create(
            {
                "name": "Test Product 2",
                "type": "consu",
                "is_storable": True,
                "barcode": "BARCODE002",
            }
        )
        self.product_lot = self.env["product.product"].create(
            {
                "name": "Lot Tracked Product",
                "type": "consu",
                "is_storable": True,
                "barcode": "LOTPROD001",
                "tracking": "lot",
            }
        )
        self.lot = self.env["stock.lot"].create(
            {
                "name": "LOT001",
                "product_id": self.product_lot.id,
                "company_id": self.env.company.id,
            }
        )
        self.inventory = self.env["stock.inventory"].create(
            {
                "name": "Test Inventory",
                "location_ids": [(4, self.location.id)],
                "product_selection": "all",
            }
        )
        self.inventory.action_state_to_in_progress()

    def _make_wizard(self, **kwargs):
        defaults = {
            "location_id": self.location.id,
            "scan_barcode_mode": "add",
            "use_latest_qty": True,
        }
        defaults.update(kwargs)
        ctx = {"active_model": "stock.inventory", "active_id": self.inventory.id}
        wiz_model = self.Wizard.with_context(**ctx)
        if "product_id" in defaults:
            return wiz_model.create(defaults)
        # No product yet — mirrors the browser state where the form is open but
        # no product has been scanned and the record doesn't exist in the DB yet.
        # product_id is required=True (NOT NULL) so we can't INSERT without it.
        all_defaults = wiz_model.default_get(list(wiz_model.fields_get()))
        all_defaults.update(defaults)
        return wiz_model.new(all_defaults)

    def _create_linked_quant(self, product, inventory_qty, lot=None):
        """Create a quant linked to the test inventory via both current_inventory_id
        and the stock_inventory_ids M2M so that update_wiz_screen can find it."""
        quant = self.StockQuant.sudo().create(
            {
                "product_id": product.id,
                "location_id": self.location.id,
                "quantity": inventory_qty,
            }
        )
        vals = {
            "current_inventory_id": self.inventory.id,
            "inventory_quantity": inventory_qty,
            "inventory_quantity_set": True,
            # Link via M2M so inventory_id.stock_quant_ids includes this quant
            "stock_inventory_ids": [(4, self.inventory.id)],
        }
        if lot:
            vals["lot_id"] = lot.id
        quant.write(vals)
        return quant

    # ------------------------------------------------------------------
    # product_code_change — barcode lookup
    # ------------------------------------------------------------------

    def test_scan_finds_product_by_barcode(self):
        wiz = self._make_wizard()
        wiz.product_code = "BARCODE001"
        wiz.product_code_change()
        self.assertEqual(wiz.product_id, self.product)
        self.assertFalse(wiz.product_code)

    def test_scan_finds_product_by_default_code(self):
        wiz = self._make_wizard()
        wiz.product_code = "REF001"
        wiz.product_code_change()
        self.assertEqual(wiz.product_id, self.product)
        self.assertFalse(wiz.product_code)

    def test_scan_finds_lot_for_lot_tracked_product(self):
        wiz = self._make_wizard(product_id=self.product_lot.id)
        wiz.product_code = "LOT001"
        wiz.product_code_change()
        self.assertEqual(wiz.lot_id, self.lot)
        self.assertFalse(wiz.product_code)

    # ------------------------------------------------------------------
    # product_id_change — new_change_qty accumulation (foodcoop12 logic)
    # ------------------------------------------------------------------

    def test_first_scan_use_latest_qty_true_seeds_from_existing(self):
        # Quant only needs current_inventory_id for _get_current_inventory_qty;
        # no M2M link required here since we are testing product_id_change, not save.
        quant = self.StockQuant.sudo().create(
            {
                "product_id": self.product.id,
                "location_id": self.location.id,
                "quantity": 10.0,
            }
        )
        quant.write(
            {
                "current_inventory_id": self.inventory.id,
                "inventory_quantity": 5.0,
                "inventory_quantity_set": True,
            }
        )
        wiz = self._make_wizard(product_id=self.product.id, use_latest_qty=True)
        wiz.product_id_change()
        # First scan: new_change_qty = existing_qty(5) + 1 = 6
        self.assertEqual(wiz.new_change_qty, 6.0)
        self.assertEqual(wiz.prev_product_id, self.product)

    def test_first_scan_use_latest_qty_false_starts_from_zero(self):
        quant = self.StockQuant.sudo().create(
            {
                "product_id": self.product.id,
                "location_id": self.location.id,
                "quantity": 10.0,
            }
        )
        quant.write(
            {
                "current_inventory_id": self.inventory.id,
                "inventory_quantity": 5.0,
                "inventory_quantity_set": True,
            }
        )
        wiz = self._make_wizard(product_id=self.product.id, use_latest_qty=False)
        wiz.product_id_change()
        # use_latest_qty=False: start from 0 → new_change_qty = 1
        self.assertEqual(wiz.new_change_qty, 1.0)

    def test_same_product_rescan_increments_new_change_qty(self):
        wiz = self._make_wizard(
            product_id=self.product.id,
            prev_product_id=self.product.id,
            new_change_qty=3.0,
        )
        wiz.product_id_change()
        self.assertEqual(wiz.new_change_qty, 4.0)

    def test_product_change_resets_counter(self):
        wiz = self._make_wizard(
            product_id=self.product2.id,
            prev_product_id=self.product.id,
            new_change_qty=5.0,
            use_latest_qty=False,
        )
        wiz.product_id_change()
        self.assertEqual(wiz.new_change_qty, 1.0)
        self.assertEqual(wiz.prev_product_id, self.product2)

    def test_product_code_change_increments_for_same_product(self):
        wiz = self._make_wizard(
            product_id=self.product.id,
            prev_product_id=self.product.id,
            new_change_qty=2.0,
        )
        wiz.product_code = "BARCODE001"
        wiz.product_code_change()
        # Same product re-scan in add mode: new_change_qty += 1
        self.assertEqual(wiz.new_change_qty, 3.0)
        self.assertFalse(wiz.product_code)

    # ------------------------------------------------------------------
    # save() — add mode: SET absolute quantity (foodcoop12 behaviour)
    # ------------------------------------------------------------------

    def test_save_add_sets_absolute_qty_not_additive(self):
        # Even with 5 existing inventory qty, save must SET to new_change_qty (3),
        # NOT add (3+5=8).  Set quant_id directly to bypass update_wiz_screen so
        # that the test is isolated to save() behaviour.
        quant = self._create_linked_quant(self.product, inventory_qty=5.0)
        wiz = self._make_wizard(product_id=self.product.id, new_change_qty=3.0)
        wiz.quant_id = quant
        wiz.save()
        quant.invalidate_recordset()
        self.assertEqual(quant.inventory_quantity, 3.0)

    def test_save_add_creates_quant_when_none_exists(self):
        # No pre-existing quant: save() → update_wiz_screen creates one → writes qty.
        wiz = self._make_wizard(product_id=self.product.id, new_change_qty=4.0)
        wiz.save()
        quant = self.StockQuant.search(
            [
                ("product_id", "=", self.product.id),
                ("location_id", "=", self.location.id),
                ("current_inventory_id", "=", self.inventory.id),
            ]
        )
        self.assertTrue(quant)
        self.assertEqual(quant.inventory_quantity, 4.0)

    # ------------------------------------------------------------------
    # save() — change mode
    # ------------------------------------------------------------------

    def test_save_change_mode_sets_change_qty_directly(self):
        # Set quant_id directly so update_wiz_screen is skipped; then set
        # change_qty to the desired value and verify the write.
        quant = self._create_linked_quant(self.product, inventory_qty=5.0)
        wiz = self._make_wizard(product_id=self.product.id, scan_barcode_mode="change")
        wiz.quant_id = quant
        wiz.change_qty = 15.0
        wiz.save()
        quant.invalidate_recordset()
        self.assertEqual(quant.inventory_quantity, 15.0)

    # ------------------------------------------------------------------
    # scan_barcode_mode / use_latest_qty propagated via default_get
    # ------------------------------------------------------------------

    def test_default_get_propagates_change_mode(self):
        self.inventory.write({"scan_barcode_mode": "change"})
        wiz = self.Wizard.with_context(
            active_model="stock.inventory",
            active_id=self.inventory.id,
        ).create({"location_id": self.location.id, "product_id": self.product.id})
        self.assertFalse(wiz.zero_count)
        self.assertEqual(wiz.scan_barcode_mode, "change")

    def test_default_get_propagates_use_latest_qty_false(self):
        self.inventory.write({"use_latest_qty": False})
        wiz = self.Wizard.with_context(
            active_model="stock.inventory",
            active_id=self.inventory.id,
        ).create({"location_id": self.location.id, "product_id": self.product.id})
        self.assertFalse(wiz.use_latest_qty)

    # ------------------------------------------------------------------
    # Full end-to-end: scan → product_id_change → save → DB check
    # ------------------------------------------------------------------

    def test_full_flow_single_scan_no_prior_qty(self):
        wiz = self._make_wizard(use_latest_qty=False)
        wiz.product_code = "BARCODE001"
        wiz.product_code_change()
        wiz.product_id_change()  # new_change_qty = 1, prev_product_id = product
        # save() calls update_wiz_screen (quant_id not set), creates quant, writes 1
        wiz.save()
        quant = self.StockQuant.search(
            [
                ("product_id", "=", self.product.id),
                ("location_id", "=", self.location.id),
                ("current_inventory_id", "=", self.inventory.id),
            ]
        )
        self.assertEqual(len(quant), 1)
        self.assertEqual(quant.inventory_quantity, 1.0)

    def test_full_flow_accumulation_3_scans(self):
        wiz = self._make_wizard(use_latest_qty=False)
        # First scan: product found via barcode, product_id_change sets new_change_qty=1
        wiz.product_code = "BARCODE001"
        wiz.product_code_change()
        wiz.product_id_change()
        self.assertEqual(wiz.new_change_qty, 1.0)
        # Two more re-scans of same product: product_code_change increments
        for _ in range(2):
            wiz.product_code = "BARCODE001"
            wiz.product_code_change()
        self.assertEqual(wiz.new_change_qty, 3.0)
        wiz.save()
        quant = self.StockQuant.search(
            [
                ("product_id", "=", self.product.id),
                ("location_id", "=", self.location.id),
                ("current_inventory_id", "=", self.inventory.id),
            ]
        )
        self.assertEqual(quant.inventory_quantity, 3.0)

    def test_full_flow_use_latest_qty_adds_to_existing(self):
        # Existing inventory qty = 5; after 2 scans new_change_qty should be 5+2=7.
        quant = self._create_linked_quant(self.product, inventory_qty=5.0)
        wiz = self._make_wizard(product_id=self.product.id, use_latest_qty=True)
        wiz.product_id_change()  # new_change_qty = 5+1 = 6
        wiz.product_code = "BARCODE001"
        wiz.product_code_change()  # same product re-scan: new_change_qty = 7
        self.assertEqual(wiz.new_change_qty, 7.0)
        wiz.quant_id = quant
        wiz.save()
        quant.invalidate_recordset()
        self.assertEqual(quant.inventory_quantity, 7.0)

    def test_full_flow_lot_tracked(self):
        wiz = self._make_wizard()
        wiz.product_code = "LOTPROD001"
        wiz.product_code_change()
        wiz.product_id_change()  # new_change_qty = 1
        wiz.product_code = "LOT001"
        wiz.product_code_change()  # sets lot_id
        wiz.update_wiz_screen({})
        wiz.save()
        quant = self.StockQuant.search(
            [
                ("product_id", "=", self.product_lot.id),
                ("lot_id", "=", self.lot.id),
                ("location_id", "=", self.location.id),
                ("current_inventory_id", "=", self.inventory.id),
            ]
        )
        self.assertTrue(quant)
        self.assertEqual(quant.inventory_quantity, 1.0)
