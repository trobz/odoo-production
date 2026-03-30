import datetime

from odoo import Command, api, fields, models


class StockInventory(models.Model):
    _inherit = "stock.inventory"

    exhausted = fields.Boolean(default=True)
    week_number = fields.Integer(
        compute="_compute_week_number",
        store=True,
        help="Number Of Inventory Week",
    )
    week_date = fields.Date(
        string="Began Order Scheduling On.",
        help="Week planning start date",
    )
    hide_initialisation = fields.Boolean(
        help="Hide Initialisation Area",
    )
    categ_ids = fields.Many2many(
        "product.category",
        "stock_inventory_product_categ",
        "inventory_id",
        "categ_id",
        string="Product categories",
    )
    supplier_ids = fields.Many2many(
        "res.partner",
        "stock_inventory_res_partner",
        "inventory_id",
        "supplier_id",
        domain="[('supplier_rank', '>', 1), ('is_company', '=', True)]",
        help="Specify product category to focus in your inventory.",
    )
    weekly_inventory = fields.Boolean(
        string="Is A Weekly Inventory",
        help="Technical field to distinct odoo inventory with weekkly inventory",
    )

    @api.depends("date")
    def _compute_week_number(self):
        for inventory in self:
            if not inventory.date:
                inventory.week_number = 0
            else:
                week_number = datetime.datetime.strptime(
                    str(inventory.date), "%Y-%m-%d %H:%M:%S"
                ).strftime("%W")
                inventory.week_number = week_number

    @api.model
    def _get_planning_line_from_stock_quants(self, stock_quant_lines):
        line_vals = []
        for quant in stock_quant_lines:
            supplier_info = (
                quant.product_id.seller_ids and quant.product_id.seller_ids[0] or False
            )
            val = {
                "product_id": quant.product_id.id,
                "supplier_id": supplier_info and supplier_info.partner_id.id or False,
                # set to this value because this value is used on purchase order
                "price_unit": supplier_info and supplier_info.base_price or 0.0,
                # set to this value because this value is used on purchase order
                "price_policy": supplier_info and supplier_info.price_policy or "uom",
                "default_packaging": quant.product_id.default_packaging,
                "supplier_packaging": supplier_info and supplier_info.package_qty or 0,
                # it should be this. To be vaildated by coop :
                # line.packaging_qty *
                # line.product_id.default_packaging/(supplier_info.package_qty
                # or 1),
                "start_inv": quant.qty_stock,
            }
            line_vals.append(val)
        return line_vals

    def action_generate_planification(self):
        """Generate the Planification"""
        self.ensure_one()
        line_vals = self._get_planning_line_from_stock_quants(self.stock_quant_ids)
        week_planning_obj = self.env["order.week.planning"]

        week_planning_value = {
            "date": self.week_date,
            "line_ids": [Command.create(x) for x in line_vals],
            "hide_initialisation": True,
        }
        new_id = week_planning_obj.create(week_planning_value)
        return {
            "type": "ir.actions.act_window",
            "res_model": "order.week.planning",
            "res_id": new_id.id,
            "view_mode": "form",
            "target": "current",
        }

    def action_state_to_done(self):
        check_date_begin = self._context.get("check_date_begin", False)
        for stock_inventory in self:
            if not stock_inventory.week_date and check_date_begin:
                return {
                    "type": "ir.actions.act_window",
                    "res_model": "stock.inventory.wizard",
                    "res_id": False,
                    "view_mode": "form",
                    "target": "new",
                }
        return super().action_state_to_done()

    def _get_product_ids(self):
        product_obj = self.env["product.product"]
        supplierinfo_obj = self.env["product.supplierinfo"]

        product_ids = []
        # Look for already existing product
        already_added_product_ids = self.stock_quant_ids.mapped("product_id")
        if self.categ_ids:
            # Look for products belong to selectec categories
            product_ids = product_obj.search(
                [
                    ("categ_id", "in", self.categ_ids.ids),
                    ("product_tmpl_id.is_storable", "=", True),
                ]
            ).ids

        if self.supplier_ids:
            # Look for products belong to selectecd categories
            supplierinfo_ids = supplierinfo_obj.search(
                [("partner_id", "in", self.supplier_ids.ids)]
            )
            product_tmpl_ids = supplierinfo_ids.mapped("product_tmpl_id")
            product_ids += product_obj.search(
                [
                    ("product_tmpl_id", "in", product_tmpl_ids.ids),
                    ("product_tmpl_id.is_storable", "=", True),
                ]
            ).ids

        # treate only new poducts to add and no modification to existing
        # products
        product_ids = list(set(product_ids) ^ set(already_added_product_ids.ids))
        return product_ids

    def action_add_category_supplier(self):
        self.ensure_one()
        location_ids = self.location_ids.ids
        search_filter = [
            (
                "location_id",
                "child_of" if not self.exclude_sublocation else "in",
                location_ids,
            ),
            ("to_do", "=", True),
        ]
        product_ids = self._get_product_ids()
        if product_ids:
            search_filter.append(("product_id", "in", product_ids))
        quants = self.env["stock.quant"].search(search_filter)
        found_product_ids = quants.mapped("product_id").ids
        unfound_product_ids = list(set(product_ids) - set(found_product_ids))
        for product in self.env["product.product"].browse(unfound_product_ids):
            quants |= self.env["stock.quant"].create(
                {
                    "product_id": product.id,
                    "product_uom_id": product.uom_id.id,
                    "inventory_quantity": 0.0,
                    "location_id": location_ids[0],
                }
            )
        self.write(
            {
                "state": "in_progress",
                "stock_quant_ids": [Command.set(quants.ids)],
            }
        )
        quants.write(
            {
                "to_do": True,
                "user_id": self.responsible_id,
                "inventory_date": self.date,
                "current_inventory_id": self.id,
            }
        )
        return True

    def init_with_theorical_qty(self):
        for inventory in self:
            for quant in inventory.stock_quant_ids:
                quant.write(
                    {
                        "inventory_quantity": (
                            quant.packaging_qty * quant.default_packaging
                        ),
                        "qty_stock": quant.packaging_qty,
                    }
                )


class StockQuant(models.Model):
    _inherit = "stock.quant"

    default_packaging = fields.Float(
        compute="_compute_quanties",
        store=True,
    )
    packaging_qty = fields.Float(
        string="Theorical Packaging Qty",
        compute="_compute_quanties",
        store=True,
        digits="Product Unit of Measure",
    )
    qty_loss = fields.Float(
        compute="_compute_qty_loss",
        string="Quantity Lost",
        digits="Product Unit of Measure",
        help="Quantity Theoric Of Reference - Stock Quantity",
    )
    qty_stock = fields.Float(
        string="Stock Quantity",
        digits="Product Unit of Measure",
        help="Stock Quantity",
    )

    @api.depends("product_id", "qty_stock")
    def _compute_quanties(self):
        for quant in self:
            product = quant.product_id
            default_packaging = product.default_packaging

            if not default_packaging:
                quant.default_packaging = 0.0
                quant.packaging_qty = 0.0
            else:
                quant.default_packaging = default_packaging
                quant.packaging_qty = product.qty_available / default_packaging

    @api.depends("packaging_qty", "qty_stock")
    def _compute_qty_loss(self):
        for quant in self:
            quant.qty_loss = (quant.qty_stock - quant.packaging_qty) or 0.00

    @api.onchange("qty_stock")
    def onchange_qty_stock(self):
        if not self.default_packaging:
            return self._show_warning_no_default_packaging()

        self.inventory_quantity = self.qty_stock * self.default_packaging

    def _show_warning_no_default_packaging(self):
        self.ensure_one()
        return {
            "warning": {
                "title": self.env._("Warning: wrong default packaging"),
                "message": self.env._(
                    "The default packaging is not defined on the product"
                ),
            }
        }

    @api.onchange("product_id")
    def onchange_product_id(self):
        self.qty_loss = -self.packaging_qty
        self.inventory_quantity = 0.0
        if self.product_id and not self.product_id.default_packaging:
            return self._show_warning_no_default_packaging()
