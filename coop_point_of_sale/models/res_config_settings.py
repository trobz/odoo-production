# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models
from odoo.tools.sql import SQL


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    account_journal_ids = fields.Many2many(
        related="pos_config_id.account_journal_ids",
        readonly=False,
    )
    payable_to = fields.Char(related="pos_config_id.payable_to", readonly=False)
    qty_zero_remove_line = fields.Boolean(
        related="pos_config_id.qty_zero_remove_line",
        readonly=False,
    )
    enable_popup_verify_payment = fields.Boolean(
        related="pos_config_id.enable_popup_verify_payment",
        readonly=False,
    )

    def action_recompute_shift_weeks(self):
        res = super().action_recompute_shift_weeks()
        # Update pos_session
        self._recompute_week_number(
            "pos_session", "start_at", "week_number", "week_name"
        )
        # Compute cycle
        self.env.cr.execute(
            SQL(
                """
            UPDATE pos_session
            SET cycle = CONCAT(week_name, week_day)
            """
            )
        )
        # Update pos_order
        self._recompute_week_number(
            "pos_order", "date_order", "week_number", "week_name"
        )
        self.env.cr.execute(
            SQL(
                """
            UPDATE pos_order
            SET cycle = CONCAT(week_name, week_day)
            """
            )
        )
        # Update pos_order_line
        self.env.cr.execute(
            SQL(
                """
            UPDATE pos_order_line pol
            SET
                week_number = po.week_number,
                week_name = po.week_name,
                cycle = po.cycle
            FROM pos_order po
            WHERE pol.order_id = po.id
            """
            )
        )
        return res
