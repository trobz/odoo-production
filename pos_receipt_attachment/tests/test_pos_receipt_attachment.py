import base64
from unittest.mock import MagicMock, patch

from odoo.tests import common


class TestAddImageReceipt(common.TransactionCase):
    """Tests for PosOrder.add_image_receipt"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.PosOrder = cls.env["pos.order"]
        cls.Attachment = cls.env["ir.attachment"]
        cls.dummy_data = base64.b64encode(b"fake_image_data").decode()

    def _orphan_attachment_count(self, uuid):
        return self.Attachment.search_count(
            [
                ("name", "=", uuid),
                ("res_field", "=", "image_receipt"),
                ("res_model", "=", "pos.order"),
                ("res_id", "=", False),
            ]
        )

    def test_returns_false_when_name_is_none(self):
        self.assertFalse(self.PosOrder.add_image_receipt(None, self.dummy_data))

    def test_returns_false_when_data_is_none(self):
        self.assertFalse(self.PosOrder.add_image_receipt("some-uuid", None))

    def test_returns_false_when_both_none(self):
        self.assertFalse(self.PosOrder.add_image_receipt(None, None))

    def test_returns_false_when_empty_strings(self):
        self.assertFalse(self.PosOrder.add_image_receipt("", ""))

    def test_creates_orphan_attachment_when_no_matching_order(self):
        uuid = "test-add-uuid-001"
        self.assertEqual(self._orphan_attachment_count(uuid), 0)

        result = self.PosOrder.add_image_receipt(uuid, self.dummy_data)

        self.assertFalse(result)
        self.assertEqual(self._orphan_attachment_count(uuid), 1)

    def test_does_not_create_duplicate_orphan_attachment(self):
        uuid = "test-add-uuid-002"

        self.PosOrder.add_image_receipt(uuid, self.dummy_data)
        self.PosOrder.add_image_receipt(uuid, self.dummy_data)

        self.assertEqual(self._orphan_attachment_count(uuid), 1)

    def test_orphan_attachment_has_correct_fields(self):
        uuid = "test-add-uuid-003"
        self.PosOrder.add_image_receipt(uuid, self.dummy_data)

        attachment = self.Attachment.search(
            [
                ("name", "=", uuid),
                ("res_field", "=", "image_receipt"),
                ("res_model", "=", "pos.order"),
            ],
            limit=1,
        )
        self.assertTrue(attachment)
        self.assertFalse(attachment.res_id)
        self.assertEqual(attachment.datas.decode(), self.dummy_data)

    def test_writes_to_existing_order_and_returns_true(self):
        uuid = "test-add-uuid-order-001"
        fake_order = MagicMock()
        fake_order.__bool__ = lambda self: True

        with patch.object(type(self.PosOrder), "search", return_value=fake_order):
            result = self.PosOrder.add_image_receipt(uuid, self.dummy_data)

        self.assertTrue(result)
        fake_order.write.assert_called_once_with({"image_receipt": self.dummy_data})

    def test_does_not_create_attachment_when_order_found(self):
        """When an existing order is found, no orphan attachment should be created."""
        uuid = "test-add-uuid-order-002"
        fake_order = MagicMock()
        fake_order.__bool__ = lambda self: True

        with patch.object(type(self.PosOrder), "search", return_value=fake_order):
            self.PosOrder.add_image_receipt(uuid, self.dummy_data)

        self.assertEqual(self._orphan_attachment_count(uuid), 0)


class TestCronUpdateImageReceipt(common.TransactionCase):
    """Tests for PosOrder.cron_update_image_receipt"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.PosOrder = cls.env["pos.order"]
        cls.Attachment = cls.env["ir.attachment"]
        cls.dummy_data = base64.b64encode(b"fake_image_data").decode()

    def _create_orphan_attachment(self, uuid):
        return self.Attachment.create(
            {
                "name": uuid,
                "res_field": "image_receipt",
                "res_model": "pos.order",
                "res_id": False,
                "datas": self.dummy_data,
            }
        )

    def test_returns_early_when_no_orphan_attachments(self):
        result = self.PosOrder.cron_update_image_receipt()
        self.assertIsNone(result)

    def test_does_nothing_when_no_matching_orders(self):
        uuid = "test-cron-uuid-001"
        attachment = self._create_orphan_attachment(uuid)

        # No pos.order with this uuid → res_id stays False
        self.PosOrder.cron_update_image_receipt()

        attachment.invalidate_recordset()
        self.assertFalse(attachment.res_id)

    def test_links_orphan_attachment_to_matching_order(self):
        uuid = "test-cron-uuid-002"
        attachment = self._create_orphan_attachment(uuid)

        class _FakeOrder:
            def __init__(self, uuid, oid):
                self.uuid = uuid
                self.id = oid

        with patch.object(
            type(self.PosOrder), "search", return_value=[_FakeOrder(uuid, 99)]
        ) as mock_search:
            self.PosOrder.cron_update_image_receipt()
            mock_search.assert_called_once()

        # Odoo 18 lazy writes: flush pending cache writes to DB before re-reading
        self.env.flush_all()
        attachment.invalidate_recordset()
        self.assertEqual(attachment.res_id, 99)

    def test_skips_attachment_when_uuid_not_in_orders(self):
        """Attachment whose uuid has no matching order must remain unlinked."""
        known_uuid = "test-cron-uuid-003"
        other_uuid = "test-cron-uuid-no-match"
        attachment_known = self._create_orphan_attachment(known_uuid)
        attachment_other = self._create_orphan_attachment(other_uuid)

        class _FakeOrder:
            def __init__(self, uuid, oid):
                self.uuid = uuid
                self.id = oid

        with patch.object(
            type(self.PosOrder), "search", return_value=[_FakeOrder(known_uuid, 55)]
        ) as mock_search:
            self.PosOrder.cron_update_image_receipt()
            mock_search.assert_called_once()

        self.env.flush_all()
        attachment_known.invalidate_recordset()
        attachment_other.invalidate_recordset()
        self.assertEqual(attachment_known.res_id, 55)
        self.assertFalse(attachment_other.res_id)

    def test_limit_parameter_passed_to_attachment_search(self):
        with patch.object(type(self.Attachment), "search") as mock_search:
            mock_search.return_value = self.Attachment.browse([])
            self.PosOrder.cron_update_image_receipt(limit=10)

        mock_search.assert_called_once()
        _, kwargs = mock_search.call_args
        self.assertEqual(kwargs.get("limit"), 10)


class TestSendOrderCron(common.TransactionCase):
    """Tests for PosOrder._send_order_cron"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.PosOrder = cls.env["pos.order"]

    def test_searches_orders_with_empty_id_list_when_no_attachments(self):
        with patch.object(
            type(self.env["ir.attachment"]), "search_read", return_value=[]
        ):
            with patch.object(type(self.PosOrder), "search") as mock_order_search:
                mock_order_search.return_value = self.PosOrder.browse([])
                self.PosOrder._send_order_cron()

        mock_order_search.assert_called_once()
        domain = mock_order_search.call_args[0][0]
        id_clause = next(c for c in domain if c[0] == "id")
        self.assertEqual(id_clause[2], [])

    def test_calls_send_receipt_for_matched_orders(self):
        fake_res_ids = [{"res_id": 10}, {"res_id": 20}]
        mock_orders = MagicMock()

        with patch.object(
            type(self.env["ir.attachment"]), "search_read", return_value=fake_res_ids
        ):
            with patch.object(type(self.PosOrder), "search", return_value=mock_orders):
                self.PosOrder._send_order_cron()

        mock_orders.send_receipt_by_body_from_ui.assert_called_once()

    def test_filters_orders_by_to_send_email_status(self):
        fake_res_ids = [{"res_id": 5}]

        with patch.object(
            type(self.env["ir.attachment"]), "search_read", return_value=fake_res_ids
        ):
            with patch.object(type(self.PosOrder), "search") as mock_order_search:
                mock_order_search.return_value = self.PosOrder.browse([])
                self.PosOrder._send_order_cron()

        domain = mock_order_search.call_args[0][0]
        status_clause = next(c for c in domain if c[0] == "email_status")
        self.assertEqual(status_clause, ("email_status", "=", "to_send"))


class TestSendReceiptByBodyFromUi(common.TransactionCase):
    """Tests for PosOrder.send_receipt_by_body_from_ui"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.PosOrder = cls.env["pos.order"]

    def test_returns_early_when_no_mail_template(self):
        with patch.object(self.env, "ref", return_value=False):
            # Should not raise
            self.PosOrder.send_receipt_by_body_from_ui()

    def test_does_nothing_on_empty_recordset(self):
        mock_template = MagicMock()
        with patch.object(self.env, "ref", return_value=mock_template):
            self.PosOrder.send_receipt_by_body_from_ui()

        mock_template.send_mail.assert_not_called()

    def test_sends_email_updates_status_and_commits(self):
        mock_template = MagicMock()
        fake_pdf = b"fake_pdf_content"

        class _FakeOrder:
            id = 1
            name = "POS/001"
            email_status = "to_send"

        fake_order = _FakeOrder()

        def pos_iter(self_model):
            return iter([fake_order])

        with patch.object(type(self.PosOrder), "__iter__", pos_iter), \
             patch.object(self.env, "ref", return_value=mock_template), \
             patch.object(
                 type(self.env["ir.actions.report"]),
                 "_render_qweb_pdf",
                 return_value=(fake_pdf, "application/pdf"),
             ), \
             patch.object(self.env.cr, "commit"):
            self.PosOrder.send_receipt_by_body_from_ui()

        mock_template.send_mail.assert_called_once()
        call_kwargs = mock_template.send_mail.call_args[1]
        attachments = call_kwargs["email_values"]["attachments"]
        self.assertEqual(len(attachments), 1)
        filename, content = attachments[0]
        self.assertIn("Receipt", filename)
        self.assertIn("POS/001", filename)
        self.assertEqual(content, base64.b64encode(fake_pdf))

    def test_continues_to_next_order_on_exception(self):
        mock_template = MagicMock()

        class _FakeOrder:
            def __init__(self, name, oid):
                self.name = name
                self.id = oid
                self.email_status = "to_send"

        fake_order_1 = _FakeOrder("POS/001", 1)
        fake_order_2 = _FakeOrder("POS/002", 2)

        call_count = {"n": 0}

        def failing_render(*args, **kwargs):
            call_count["n"] += 1
            if call_count["n"] == 1:
                raise RuntimeError("PDF generation failed")
            return (b"pdf", "application/pdf")

        def pos_iter(self_model):
            return iter([fake_order_1, fake_order_2])

        with patch.object(type(self.PosOrder), "__iter__", pos_iter), \
             patch.object(self.env, "ref", return_value=mock_template), \
             patch.object(
                 type(self.env["ir.actions.report"]),
                 "_render_qweb_pdf",
                 side_effect=failing_render,
             ), \
             patch.object(self.env.cr, "commit"):
            # Should not propagate the exception
            self.PosOrder.send_receipt_by_body_from_ui()

        # Second order still processed despite first failing
        self.assertEqual(mock_template.send_mail.call_count, 1)
