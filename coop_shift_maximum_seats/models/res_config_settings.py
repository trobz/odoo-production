# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    shift_max_available_seats = fields.Selection(
        selection=[
            ("manual", "Add Maximum available ABCD/FTOP seats manually"),
            (
                "auto",
                "Calculate Maximum available ABCD/FTOP seats automatically based on Maximum Attendees Number",
            ),
        ],
        string="Maximum available ABCD/FTOP seats",
        related="company_id.shift_max_available_seats",
        readonly=False,
    )

    @api.onchange("shift_max_available_seats")
    def onchange_shift_max_available_seats(self):
        if (
            self.shift_max_available_seats == "auto"
            and self.shift_exchange_policy == "registraion_standard_ftop"
        ):
            self.shift_max_available_seats = "manual"
            return {
                "warning": {
                    "titile": _("Validation Error"),
                    "message": _(
                        "This option is not available when `Shift replacement list contains` is `Participations put into exchange plus available standard seats plus available ftop seats`"
                    ),
                }
            }

    @api.onchange("shift_exchange_policy")
    def onchange_shift_exchange_policy(self):
        if (
            self.shift_max_available_seats == "auto"
            and self.shift_exchange_policy == "registraion_standard_ftop"
        ):
            self.shift_exchange_policy = "registraion"
            return {
                "warning": {
                    "titile": _("Validation Error"),
                    "message": _(
                        "This option is not available when `Maximum available ABCD/FTOP seats` is `Auto`"
                    ),
                }
            }
