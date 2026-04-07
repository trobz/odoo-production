# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tools.sql import column_exists, create_column


def pre_init_hook(env):
    """Do not compute the sale_order_template_id field on existing SOs."""
    if not column_exists(env.cr, "shift_extension", "is_new"):
        create_column(env.cr, "shift_extension", "is_new", "BOOLEAN")
