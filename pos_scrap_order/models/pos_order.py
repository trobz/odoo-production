# Copyright (C) Nguyen Minh Chien (chien@trobz.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, api, _
from odoo.exceptions import AccessError
import logging

_logger = logging.getLogger(__name__)

class OutofStockError(AccessError):
    """ Out of stock exception """
    def __init__(self, msg):
        super().__init__(msg)

class PosOrder(models.Model):
    _inherit = "pos.order"

    @api.model
    def _get_scrap_vals(self, order, line, default_vals):
        vals = {}
        session = self.env["pos.session"].browse(order.get("pos_session_id"))
        location = session.config_id.stock_location_id
        if len(line) == 3:
            product = self.env["product.product"].browse(line[2].get("product_id"))
            vals = {
                "product_id": product.id,
                "scrap_qty": line[2].get("qty"),
                "location_id": location.id,
                "product_uom_id": product.uom_id.id,
                "origin": _("POS Session: ") + session.display_name
            }
            vals.update(default_vals)
        return vals

    @api.model
    def create_scrap_from_ui(self, order, default_vals={}):
        scrap_ids = []
        msg = {}
        vals = []
        session = self.env["pos.session"].browse(order.get("pos_session_id"))
        scrap_order_option = session.config_id.scrap_order_option
        lines = order.get("lines")
        Scrap = self.env["stock.scrap"]
        try:
            if scrap_order_option == "no":
                raise AccessError("")
            for line in lines:
                if len(line) == 3:
                    vals.append(self._get_scrap_vals(order, line, default_vals))
            if len(vals) == len(lines):
                scraps = Scrap.create(vals)
                if scrap_order_option == "force":
                    scraps.do_scrap()
                else:
                    for scrap in scraps:
                        res = scrap.action_validate()
                        if scrap_order_option == "onhand" and res is not True:
                            raise OutofStockError(_("The product {} has no enough stock.").format(
                                scrap.product_id.display_name))
                scrap_ids = scraps.ids
            msg = {
                "title": _("Successful!"),
                "body": _("The product(s) has been sent to scrap location")
            }
        except OutofStockError as e:
            self.env.cr.rollback()
            msg = {
                "title": _("No Enough Stock!"),
                "body": e.args[0]
            }
        except AccessError as e:
            msg = {
                "title": _("Access Error!"),
                "body": _("You have no right to make the scrap order.")
            }
        except Exception as err:
            _logger.error("====================================")
            _logger.error(str(err))
            msg = {
                "title": _("Error!"),
                "body": _("Data is incorrect.")
            }
        return {"scrap_ids": scrap_ids, "msg": msg}
