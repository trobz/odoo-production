# Copyright (C) Nguyen Minh Chien (chien@trobz.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class PosOrder(models.Model):
    _inherit = "pos.order"

    image_receipt = fields.Binary(attachment=True)

    def cron_update_image_receipt(self, limit=None):
        attachments = self.env["ir.attachment"].search(
            [
                ("res_field", "=", "image_receipt"),
                ("res_model", "=", "pos.order"),
                ("res_id", "in", [False, 0]),
            ],
            limit=limit,
        )
        if not attachments:
            return
        orders = self.search([("uuid", "in", attachments.mapped("name"))])
        uuid_to_id = {o.uuid: o.id for o in orders}
        for attachment in attachments:
            order_id = uuid_to_id.get(attachment.name)
            if order_id:
                attachment.res_id = order_id

    @api.model
    def add_image_receipt(self, name, data):
        if not name or not data:
            return False
        order = self.search([("uuid", "=", name)], limit=1)
        if order:
            order.write({"image_receipt": data})
            return True
        Attachment = self.env["ir.attachment"]
        if not Attachment.search(
            [
                ("name", "=", name),
                ("res_field", "=", "image_receipt"),
                ("res_model", "=", "pos.order"),
            ],
            limit=1,
        ):
            Attachment.create(
                {
                    "name": name,
                    "res_field": "image_receipt",
                    "res_model": "pos.order",
                    "datas": data,
                }
            )
        return False

    def _send_order_cron(self):
        """Only send tickets that have an image_receipt attachment.
        Binary(attachment=True) fields are not searchable via domain in Odoo 18,
        so we query ir.attachment directly.
        """
        order_ids = [
            r["res_id"]
            for r in self.env["ir.attachment"]
            .sudo()
            .search_read(
                [
                    ("res_model", "=", "pos.order"),
                    ("res_field", "=", "image_receipt"),
                    ("res_id", "!=", False),
                ],
                fields=["res_id"],
            )
        ]
        orders = self.search(
            [("email_status", "=", "to_send"), ("id", "in", order_ids)]
        )
        _logger.info("Sending receipts for %d orders", len(orders))
        orders.send_receipt_by_body_from_ui()

    def send_receipt_by_body_from_ui(self):
        mail_template = self.env.ref(
            "pos_ticket_send_by_mail.email_send_pos_receipt", False
        )
        if not mail_template:
            _logger.warning("No mail template found for sending ticket")
            return
        for order in self:
            try:
                receipt_pdf, _ = self.env["ir.actions.report"]._render_qweb_pdf(
                    "pos_receipt_attachment.action_report_pos_receipt", [order.id]
                )
                mail_template.send_mail(
                    order.id,
                    email_values={
                        "attachments": [
                            (
                                "Receipt - %s.pdf" % order.name,
                                base64.b64encode(receipt_pdf),
                            )
                        ]
                    },
                    force_send=True,
                )
                order.email_status = "sent"
                # Commit immediately to prevent duplicate sends on partial failure
                self.env.cr.commit()
            except Exception:
                _logger.exception(
                    "Failed to send receipt email for order %s", order.name
                )
