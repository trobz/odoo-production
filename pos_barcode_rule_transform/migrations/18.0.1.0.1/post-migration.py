def migrate(cr, version):
    # Odoo 18 changed two settings vs Odoo 12, causing weight barcodes with 3
    # decimal places (e.g. 0.496 kg) to be rounded to 0.500 in POS.
    #
    # In POS set_quantity:
    #   rounding = Math.max(unit.rounding, Math.pow(10, -decimals))
    #
    # Odoo 12: decimal_precision=3, kg rounding=0.001 → max(0.001,0.001)=0.001 ✓
    # Odoo 18: decimal_precision=2, kg rounding=0.010 → max(0.010,0.010)=0.010 ✗

    # Fix 1: restore "Product Unit of Measure" decimal precision to 3 digits
    cr.execute("""
        UPDATE decimal_precision
        SET digits = 3
        WHERE name = 'Product Unit of Measure'
          AND digits != 3
    """)

    # Fix 2: restore kg rounding to 0.001
    cr.execute("""
        UPDATE uom_uom
        SET rounding = 0.001
        WHERE id = (
            SELECT res_id
            FROM ir_model_data
            WHERE module = 'uom'
              AND name = 'product_uom_kgm'
        )
          AND rounding != 0.001
    """)
