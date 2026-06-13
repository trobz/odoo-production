import ast
from datetime import datetime

from odoo import Command
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

from .common import CoopProduceTest


class TestCoopProduce(CoopProduceTest):
    def test_coop_produce01(self):
        """
        Test the Coop Produce should take the quantities based on default
        packaging of the product and an advanced form view to plan orders
        of the week to send the supplier per day.
        """
        stock_inventory1 = self.StockInventory.create(
            {
                "name": "Inventory of V&F",
                "date": datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                "location_ids": [Command.set([self.StockLocation.id])],
                "categ_ids": [Command.set([self.CategoryCoop.id])],
            }
        )

        # Add products using "Add" button of Product categories
        stock_inventory1.action_add_category_supplier()

        # Stock Quants
        self.assertTrue(
            stock_inventory1.stock_quant_ids,
            "Stock Quants should be created after adding products"
            " using the add button of product categories.",
        )
        self.assertEqual(stock_inventory1.product_selection, "category")

        # Reset
        stock_inventory1.action_state_to_draft()

        # No Stock Quants after Reset
        self.assertFalse(
            stock_inventory1.stock_quant_ids,
            "Stock Quants should be deleted after reset the inventory.",
        )

        stock_inventory = self.StockInventory.create(
            {
                "name": "Inventory of V&F",
                "date": datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                "categ_ids": [Command.set([self.CategoryCoop.id])],
                "supplier_ids": [Command.set([self.SupplierCoop.id])],
                "location_ids": [Command.set([self.StockLocation.id])],
            }
        )
        # Add products using "Add" button of Supplliers
        stock_inventory.action_add_category_supplier()

        # Check Inventory lines adter added using suppliers' add button
        self.assertTrue(
            stock_inventory.stock_quant_ids,
            "Stock Quants should be created after adding products"
            " using the add button of suppliers.",
        )
        self.assertEqual(stock_inventory.product_selection, "category")
        self.assertEqual(
            len(stock_inventory.stock_quant_ids),
            1,
        )
        # Check quantity
        quant = stock_inventory.stock_quant_ids[0]
        self.assertEqual(
            quant.product_id,
            self.VariantCoop,
            "The product of the stock quant should be the product variant of "
            "the Coop Product.",
        )
        self.assertEqual(
            quant.default_packaging,
            self.VariantCoop.default_packaging,
            "The location of the stock quant should be the stock location.",
        )
        quant.qty_stock = 8.0
        self.assertEqual(
            quant.packaging_qty,
            3.0,
            "The packaging quantity should be the stock quantity divided by "
            "the default packaging.",
        )
        self.assertEqual(
            quant.qty_loss,
            5.0,
            "The quantity loss should be the difference between the packaging "
            "quantity and the stock quantity.",
        )

        # Validate F&V Inventory
        stock_inventory.action_state_to_done()

        # Check Week Date should not set by default
        self.assertFalse(
            stock_inventory.week_date,
            "F&V inventory should not have week date" " set when a new record.",
        )

        stock_inventory_wizard = self.StockInventoryWizard.create(
            {"week_date": datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT)}
        )

        ctx = {"active_id": stock_inventory.id}
        stock_inventory_wizard.with_context(**ctx).action_ok()

        # I check that F&V Inventory is in the "Done" state
        self.assertEqual(stock_inventory.state, "done")

        # Week Planification
        week_planification_id = stock_inventory.action_generate_planification()

        # Check week planification record created
        self.assertTrue(
            week_planification_id,
            "Week planification should be created after generating "
            "planification from inventory.",
        )

        order_week_planning = self.OrderWeekPlanning.browse(
            week_planification_id.get("res_id")
        )
        order_week_planning_lines = order_week_planning.line_ids
        order_week_planning_lines.write(
            {
                "monday_qty": 10.0,
            }
        )
        # Monday: Create Purchase Order

        ctx = {"day_number": 1}
        order_week_planning.with_context(**ctx).create_purchase_orders()

        purchase_orders_action = order_week_planning.action_view_orders()
        purchase_orders_domain = purchase_orders_action.get("domain", [])
        self.assertTrue(
            purchase_orders_domain,
            "Purchase orders domain should be returned by action view orders.",
        )

        if isinstance(purchase_orders_domain, str):
            purchase_orders = ast.literal_eval(purchase_orders_domain)[0][2]
        else:
            purchase_orders = purchase_orders_domain[0][2]

        # Check purchase orders
        self.assertTrue(
            purchase_orders,
            "Purchase orders should be created after creating "
            "purchase order for the day.",
        )
