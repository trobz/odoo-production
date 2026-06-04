import odoo
from odoo import http
from odoo.http import request

UPDATE_PHONE = ["mobile", "phone"]

UPDATE_ADDRESS = ["street", "city", "zip"]


class Website(odoo.addons.website.controllers.main.Website):
    @http.route("/edit-phone", type="http", auth="user", website=True, methods=["POST"])
    def edit_phone(self, **kw):
        new_value = {}
        for field in list(x for x in UPDATE_PHONE if x in kw):
            new_value.update({field: kw.get(field, False)})
        request.env.user.partner_id.write(new_value)
        return request.redirect("/profile")

    @http.route(
        "/edit-address",
        type="http",
        auth="user",
        website=True,
        methods=["POST"],
    )
    def edit_address(self, **kw):
        new_value = {}
        for field in list(x for x in UPDATE_ADDRESS if x in kw):
            new_value.update({field: kw.get(field, False)})
        request.env.user.partner_id.write(new_value)
        return request.redirect("/profile")

    @http.route(
        "/edit-email-pos-receipt",
        type="http",
        auth="user",
        website=True,
        methods=["POST"],
    )
    def edit_email_pos_receipt(self, **kw):
        pos_email_receipt = (
            "email_pos_receipt"
            if kw.get("pos_email_receipt")
            else "no_email_pos_receipt"
        )
        request.env.user.partner_id.write({"pos_email_receipt": pos_email_receipt})
        return request.redirect("/profile")
