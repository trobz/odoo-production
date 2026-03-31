from odoo import http
from odoo.exceptions import AccessError
from odoo.http import request
from odoo.service.common import exp_version
from odoo.tools import py_to_js_locale


class CoopBadgeReader(http.Controller):
    def _get_company(self):
        return request.env.company

    def _get_user(self):
        return request.env.user

    @http.route("/badge_reader", type="http", auth="user")
    def badge_reader(self, **kwargs):
        company = self._get_company()
        user = self._get_user()
        has_group = user.has_group("coop_badge_reader.group_time_clock")
        if not has_group:
            raise AccessError(
                request.env._(
                    "You do not have the required permissions "
                    "to access the badge reader."
                )
            )
        version_info = exp_version()
        return request.render(
            "coop_badge_reader.index",
            {
                "badge_reader_info": {
                    "uid": user.id,
                    "user_name": user.name,
                    "partner_id": user.partner_id.id,
                    "company_id": company.id,
                    "company_name": company.name,
                    "lang": py_to_js_locale(user.partner_id.lang),
                    "server_version_info": version_info.get("server_version_info"),
                }
            },
        )

    @http.route("/coop_badge_reader/static/www/index.html", type="http", auth="user")
    def badge_reader_static(self, **kwargs):
        return request.redirect("/badge_reader")
