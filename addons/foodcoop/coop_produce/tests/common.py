from odoo.tests import common


class CoopProduceTest(common.TransactionCase):
    """Base class - Test the Coop Produce."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Useful models
        cls.StockInventory = cls.env["stock.inventory"]
        cls.OrderWeekPlanning = cls.env["order.week.planning"]
        cls.StockInventoryWizard = cls.env["stock.inventory.wizard"]
        cls.OrderWeekPlanning = cls.env["order.week.planning"]

        cls.SupplierCoop = cls.env["res.partner"].create(
            {
                "name": "Coop Supplier",
                "supplier_rank": 1,
            }
        )
        cls.CategoryCoop = cls.env["product.category"].create(
            {
                "name": "Coop Category",
            }
        )
        cls.ProductCoop = cls.env["product.template"].create(
            {
                "name": "Coop Product",
                "list_price": 14.0,
                "standard_price": 8.0,
                "type": "consu",
                "default_code": "COOP_PRODUCT",
                "categ_id": cls.CategoryCoop.id,
                "is_storable": True,
            }
        )
        cls.SupplierInfo = cls.env["product.supplierinfo"].create(
            {
                "partner_id": cls.SupplierCoop.id,
                "price": 8,
                "product_tmpl_id": cls.ProductCoop.id,
                "product_id": cls.ProductCoop.product_variant_id.id,
            }
        )
        cls.ProductCoop.product_variant_id.default_packaging = 2
        cls.StockLocation = cls.env.ref("stock.stock_location_stock")
