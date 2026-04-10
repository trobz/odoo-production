##############################################################################
#
#    Purchase - Package Quantity Module for Odoo
#    Copyright (C) 2016-Today Akretion (https://www.akretion.com)
#    @author Julien WESTE
#    @author Sylvain LE GAL (https://twitter.com/legalsylvain)
#    Copyright (C) 2020-Today: Druidoo (<https://www.druidoo.io>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    product_default_code = fields.Char(
        string="Internal Reference", related="product_id.default_code", store=True
    )

    def _get_vendor_packaging(self):
        """Return vendor packaging from seller_ids matching the picking partner."""
        partner = self.picking_id.partner_id
        if not self.product_id or not partner:
            return False
        seller = self.product_id.seller_ids.filtered(lambda s: s.partner_id == partner)
        return seller[0].product_packaging_id if seller else False

    @api.onchange("picking_id")
    def _onchange_suggest_packaging_from_vendor(self):
        vendor_packaging = self._get_vendor_packaging()
        if vendor_packaging:
            self.product_packaging_id = vendor_packaging

    @api.onchange("product_id", "product_qty", "product_uom")
    def _onchange_suggest_packaging(self):
        vendor_packaging = self._get_vendor_packaging()
        if vendor_packaging:
            self.product_packaging_id = vendor_packaging
            return
        return super()._onchange_suggest_packaging()

    def unlink(self):
        for move in self:
            if move.state not in ("draft", "cancel"):
                if move.product_uom_qty == 0:
                    move.state = "cancel"
        return super().unlink()

    vendor_product_code = fields.Char(compute="_compute_move_product_code")

    @api.depends("product_id", "picking_id.partner_id")
    def _compute_move_product_code(self):
        for pack in self:
            vendor_product_code = ""
            sellers = pack.product_id.seller_ids
            for seller in sellers:
                if seller.partner_id == pack.picking_id.partner_id:
                    vendor_product_code = seller.product_code
            pack.vendor_product_code = vendor_product_code
