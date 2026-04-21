# Copyright (C) Nguyen Minh Chien (chien@trobz.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo import api, models
from odoo.exceptions import AccessError, UserError

_logger = logging.getLogger(__name__)


class OutofStockError(AccessError):
    """Out of stock exception"""

    def __init__(self, msg):
        super().__init__(msg)


class PosOrder(models.Model):
    _inherit = "pos.order"

    @api.model
    def _get_scrap_vals(self, order, line, default_vals):
        vals = {}
        session = self.env["pos.session"].browse(order.get("pos_session_id"))
        location = session.config_id.picking_type_id.default_location_src_id
        if len(line) == 3:
            product = self.env["product.product"].browse(line[2].get("product_id"))
            vals = {
                "product_id": product.id,
                "scrap_qty": line[2].get("qty"),
                "product_uom_id": product.uom_id.id,
                "origin": self.env._("POS Session: ") + session.display_name,
            }
            if location:
                vals["location_id"] = location.id
            vals.update(default_vals)
        return vals

    @api.model
    def create_scrap_from_ui(self, order, default_vals=None):
        scrap_ids = []
        msg = {}
        if default_vals is None:
            default_vals = {}
        session = self.env["pos.session"].browse(order.get("pos_session_id"))
        scrap_order_option = session.config_id.scrap_order_option
        lines = order.get("lines")
        Scrap = self.env["stock.scrap"]
        try:
            with self.env.cr.savepoint():
                if scrap_order_option == "no":
                    raise AccessError(self.env._("Scrap order is disabled."))
                vals = []
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
                                raise OutofStockError(
                                    self.env._(
                                        "The product {} has no enough stock."
                                    ).format(scrap.product_id.display_name)
                                )
                    scrap_ids = scraps.ids
                msg = {
                    "title": self.env._("Successful!"),
                    "body": self.env._(
                        "The product(s) has been sent to scrap location"
                    ),
                }
        except OutofStockError as e:
            scrap_ids = []
            msg = {"title": self.env._("No Enough Stock!"), "body": e.args[0]}
        except AccessError:
            scrap_ids = []
            msg = {
                "title": self.env._("Access Error!"),
                "body": self.env._("You have no right to make the scrap order."),
            }
        except UserError as err:
            scrap_ids = []
            _logger.error("====================================")
            _logger.error(str(err))
            msg = {
                "title": self.env._("User Error!"),
                "body": self.env._(
                    "Stock data is incorrect. Please contact the administrator."
                ),
            }
        except Exception as err:
            scrap_ids = []
            _logger.error("====================================")
            _logger.error(str(err))
            msg = {
                "title": self.env._("Error!"),
                "body": self.env._("Data is incorrect."),
            }
        return {"scrap_ids": scrap_ids, "msg": msg}
