# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from odoo import api, fields, models


class StockScrap(models.Model):
    _inherit = "stock.scrap"

    @api.model
    def get_list_for_ui(self):
        result = []
        records = self.sudo().search(
            [
                "|",
                ("origin", "like", self.env._("POS Session: ")),
                ("origin", "like", "POS Session: "),
            ],
            order="id DESC",
            limit=50,
        )
        for scrap in records:
            # Format quantity with unit of measure
            quantity_str = f"{scrap.scrap_qty} {scrap.product_uom_id.name}"

            # Get state label from selection field
            state_label = dict(self._fields["state"].selection).get(
                scrap.state, scrap.state
            )

            result.append(
                {
                    "name": scrap.name,
                    "product_display_name": scrap.product_id.display_name,
                    "qty_str": quantity_str,
                    "state_label": state_label,
                    "origin": scrap.origin.replace("POS Session: ", "").replace(
                        self.env._("POS Session: "), ""
                    ),
                    "date": scrap.create_date
                    and fields.Datetime.to_string(scrap.create_date)
                    or "",
                }
            )
        return result
