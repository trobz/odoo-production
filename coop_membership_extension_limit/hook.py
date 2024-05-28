# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

def pre_init(cr):
    cr.execute("""ALTER TABLE shift_extension
            ADD COLUMN IF NOT EXISTS is_new BOOLEAN""")
    return True
