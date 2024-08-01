# Copyright (C) Nguyen Minh Chien (chien@trobz.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64
from odoo import fields, models, api
import logging

_logger = logging.getLogger(__name__)


class PosOrder(models.Model):
    _inherit = "pos.order"

    image_receipt = fields.Binary(
        attachment=True
    )

    @api.model
    def cron_update_image_receipt(self, limit=None):
        args = [
            ("res_field", "=", "image_receipt"),
            ("res_model", "=", "pos.order"),
            ("res_id", "=", False),
        ]
        attachments = self.env["ir.attachment"].search(args, limit=limit)
        for attachment in attachments:
            order = self.search([
                ("pos_reference", "=", attachment.datas_fname),
            ], limit=1)
            if order:
                attachment.res_id = order.id

    @api.model
    def _prepare_attachment(self, name, data):
        vals = {
            "datas_fname": name,
            "name": "image_receipt",
            "res_field": "image_receipt",
            "res_model": "pos.order",
            "datas": data
        }
        return vals

    @api.model
    def add_image_receipt(self, name, data):
        if not name or not data:
            return False
        order = self.env["pos.order"].search([("pos_reference", "=", name)], limit=1)
        if order:
            order.write({"image_receipt": data})
            return True
        else:
            # Store as an attachment
            Attachment = self.env["ir.attachment"]
            exist = Attachment.search([
                ("datas_fname", "=", name),
                ("res_field", "=", "image_receipt"),
                ("res_model", "=", "pos.order")
            ], limit=1)
            if not exist:
                vals = self._prepare_attachment(name, data)
                Attachment.create(vals)
        return False

    @api.model
    def add_image_receipt_patch(self, receipts):
        for receipt in receipts:
            self.add_image_receipt(receipt["id"], receipt["data"])
        return True

    @api.model
    def _order_fields(self, ui_order):
        vals = super()._order_fields(ui_order)
        if ui_order.get("image_receipt"):
            vals["image_receipt"] = ui_order['image_receipt']
        return vals

    @api.model
    def _send_order_cron(self):
        """
        Only send the ticket which order's linked to a receipt attachment
        """
        _logger.info("------------------------------------------------------")
        _logger.info("Start to send ticket")
        orders = self.search([
            ('email_status', '=', 'to_send'),
            ('image_receipt', '!=', False)
        ])
        orders.send_receipt_by_body_from_ui()

    def send_receipt_by_body_from_ui(self):
        mail_template = self.env.ref(
            "pos_ticket_send_by_mail.email_send_pos_receipt", False)
        if not mail_template:
            return
        receipt_report = self.env.ref("pos_receipt_attachment.action_report_pos_receipt")
        report_service = receipt_report.report_name
        for order in self:
            report_name = mail_template._render_template(
                mail_template.report_name, mail_template.model, order.id)
            if not report_name:
                report_name = 'report.' + report_service
            receipt_pdf, format = receipt_report.render_qweb_pdf([order.id])
            receipt_raw = base64.b64encode(receipt_pdf)
            email_values = {"attachments": [(report_name, receipt_raw)]}
            mail_template.send_mail(order.id, email_values=email_values, force_send=True)
            order.email_status = 'sent'
            # Make sure we commit the change to not send ticket twice
            self.env.cr.commit()
