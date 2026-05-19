from datetime import datetime, timedelta

from odoo import http
from odoo.http import request

from odoo.addons.website.controllers.main import Website as WebsiteController


class Website(WebsiteController):
    @http.route("/standard/programmer_makeup", type="http", auth="user", website=True)
    def page_programmer_makeup(self, **kwargs):
        user = request.env.user
        partner = user.partner_id
        tmpl = partner.tmpl_reg_line_ids.filtered(lambda r: r.is_current)
        shift_env = request.env["shift.shift"]
        shifts_available = shift_env
        if tmpl:
            shifts_available = shift_env.sudo().search(
                [
                    ("shift_template_id.is_technical", "=", False),
                    (
                        "shift_template_id",
                        "not in",
                        tmpl.mapped("shift_template_id.id"),
                    ),
                    (
                        "date_begin",
                        ">=",
                        (datetime.now() + timedelta(days=1)).strftime(
                            "%Y-%m-%d 00:00:00"
                        ),
                    ),
                    "|",
                    ("registration_ids", "=", False),
                    ("registration_ids.partner_id", "not in", partner.ids),
                    ("shift_template_id.shift_type_id.is_ftop", "=", False),
                    ("state", "!=", "cancel"),
                ],
                order="date_begin",
            )
            shifts_available = shifts_available.filtered(
                lambda t: t.seats_availability == "unlimited"
                or t.seats_reserved < t.seats_max
            )
        eligible = partner.check_makeup_shift()
        return request.render(
            "coop_membership_makeup_shift.counter",
            {
                "shifts_available": shifts_available,
                "user": user,
                "eligible": eligible,
                "partner_state": partner._fields["cooperative_state"].convert_to_export(
                    partner.cooperative_state, partner
                ),
            },
        )
