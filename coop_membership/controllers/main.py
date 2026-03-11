import logging
from datetime import datetime

import requests

from odoo import fields, http
from odoo.http import request

_logger = logging.getLogger(__name__)


class WebsiteRegisterMeeting(http.Controller):
    @http.route(["/discovery"], type="http", auth="public", website=True)
    def get_discover_meeting(self, **post):
        REGISTER_USER_ID = int(
            request.env["ir.config_parameter"].sudo().get_param("register_user_id")
        )
        captcha_site_key = (
            request.env["ir.config_parameter"].sudo().get_param("captcha_site_key")
        )
        user = request.env["res.users"].browse(REGISTER_USER_ID)
        company = user.company_id

        # Get event available
        event_obj = request.env["event.event"].with_user(user)
        events = event_obj.search(
            [
                ("is_discovery_meeting", "=", True),
                ("stage_id", "in", company.discovery_meeting_event_stage_ids.ids),
                ("date_begin", ">=", fields.Datetime.to_string(datetime.now())),
            ]
        )
        available_events = events.filtered(
            lambda e: not (e.seats_limited and e.seats_available < 1)
        )
        datas = available_events._get_event_data_for_register_form()

        value = {
            "datas": datas,
            "captcha_site_key": captcha_site_key,
            "description": company.discovery_meeting_description or "",
            "notice": company.discovery_meeting_notice or "",
        }
        value = self._prepare_register_form_vals(value)
        return request.render("coop_membership.register_form", value)

    @http.route(
        ["/discovery/reregister"],
        type="http",
        auth="public",
        methods=["POST", "GET"],
        csrf=False,
        website=True,
    )
    def get_discover_meeting_again(self, **post):
        REGISTER_USER_ID = int(
            request.env["ir.config_parameter"].sudo().get_param("register_user_id")
        )
        captcha_site_key = (
            request.env["ir.config_parameter"].sudo().get_param("captcha_site_key")
        )
        user = request.env["res.users"].browse(REGISTER_USER_ID)
        # Get event available
        event_obj = request.env["event.event"].with_user(user)
        events = event_obj.search(
            [
                ("is_discovery_meeting", "=", True),
                (
                    "stage_id",
                    "in",
                    user.company_id.discovery_meeting_event_stage_ids.ids,
                ),
                ("date_begin", ">=", fields.Datetime.to_string(datetime.now())),
            ]
        )
        available_events = events.filtered(
            lambda e: not (e.seats_limited and e.seats_available < 1)
        )
        datas = available_events._get_event_data_for_register_form()

        name = post.get("name", False)
        email = post.get("email", False)
        first_name = post.get("first_name", False)
        gender = post.get("gender", "male")
        mobile = post.get("mobile", False)
        phone = post.get("phone", False)
        street1 = post.get("street1", False)
        street2 = post.get("street2", False)
        city = post.get("city", False)
        zipcode = post.get("zipcode", False)
        social_registration = post.get("social_registration", False)
        dob = post.get("dob", False)

        value = {
            "name": name,
            "email": email,
            "first_name": first_name,
            "gender": gender,
            "mobile": mobile,
            "phone": phone,
            "street1": street1,
            "street2": street2,
            "city": city,
            "social_registration": social_registration,
            "zipcode": zipcode,
            "dob": dob,
            "datas": datas,
            "captcha_site_key": captcha_site_key,
        }
        value = self._prepare_register_form_vals(value)
        return request.render("coop_membership.register_again_form", value)

    @http.route(
        ["/web/membership/register/submit"],
        type="http",
        auth="public",
        methods=["POST"],
        csrf=False,
        website=True,
    )
    def subscribe_discovery_meeting(self, **post):
        captcha_secret_key = (
            request.env["ir.config_parameter"].sudo().get_param("captcha_secret_key")
        )
        capcha_response = post.get("g-recaptcha-response")
        verify_url = "https://www.google.com/recaptcha/api/siteverify"
        payload = {"secret": captcha_secret_key, "response": capcha_response}
        capcha_res = requests.post(verify_url, data=payload, timeout=10).json()

        if not capcha_res["success"]:
            return request.render("coop_membership.discovery_back")

        REGISTER_USER_ID = int(
            request.env["ir.config_parameter"].sudo().get_param("register_user_id")
        )
        user = request.env["res.users"].browse(REGISTER_USER_ID)
        user_company = user.company_id
        # Get data from form
        name = post.get("name", False)
        email = post.get("email", False)
        first_name = post.get("first_name", False)
        gender = post.get("gender", False)
        mobile = post.get("mobile", False)
        phone = post.get("phone", False)
        street1 = post.get("street1", False)
        street2 = post.get("street2", False)
        city = post.get("city", False)
        zipcode = post.get("zipcode", False)
        social_registration = post.get("social_registration", False)
        event_id = post.get("select_event", False)
        dob = post.get("dob", False)

        # convert dob to correct format in database
        try:
            dob_date = datetime.strptime(dob, "%Y-%m-%d").date()
            if dob_date < datetime.strptime("1900-01-01", "%Y-%m-%d").date():
                dob = False
            else:
                dob = dob_date.strftime("%Y-%m-%d")
        except BaseException:
            _logger.warning(
                """Convert birthdate from %s on
                discovery meeting form failed
                """,
                dob,
            )

        # Check email exist in database
        partner_obj = request.env["res.partner"].with_user(user)
        partner_id = partner_obj.search([("email", "=", email)])

        event_obj = request.env["event.event"].with_user(user)
        event = event_obj.browse(int(event_id))
        is_event_valid = True

        # Check invalid and available seat event
        if (
            event
            and event.is_discovery_meeting
            and event.stage_id in user_company.discovery_meeting_event_stage_ids
        ):
            if event.seats_limited and event.seats_max and event.seats_available < 1:
                is_event_valid = False
        else:
            is_event_valid = False

        if partner_id:
            company = partner_id[0].company_id or request.env.user.company_id
            company_email = company.email_meeting_contact or company.email
            email_contact = {
                "email_contact": company_email or "",
                "company_name": company.company_name or company.name,
            }
            return request.render(
                "coop_membership.register_submit_form_err_email", email_contact
            )
        elif not is_event_valid:
            value_registered = {
                "name": name,
                "email": email,
                "first_name": first_name,
                "gender": gender,
                "mobile": mobile,
                "phone": phone,
                "street1": street1,
                "street2": street2,
                "city": city,
                "social_registration": social_registration,
                "zipcode": zipcode,
                "dob": dob
                and datetime.strptime(dob, "%Y-%m-%d").date().strftime("%d/%m/%Y"),
            }
            return request.render(
                "coop_membership.register_submit_form_err_event", value_registered
            )
        else:
            # create event registration
            val = {
                "event_id": event.id,
                "name": name + ", " + first_name,
                "email": email,
            }
            attendee = self.create_event_registration(val, user)

            partner_val = {
                "name": name + ", " + first_name,
                "gender": gender,
                "email": email,
                "street": street1,
                "street2": street2,
                "city": city,
                "zip": zipcode,
                "phone": phone,
                "mobile": mobile,
                "birthdate_date": dob or False,
            }
            partner_val = self._prepare_partner_val(partner_val, **post)
            # Create contact partner
            partner = self.create_contact_partner(partner_val, user)
            website = "/discovery"

            if partner:
                attendee.partner_id = partner.id

                if partner.company_id.website:
                    website = partner.company_id.website

                if social_registration == "yes":
                    partner.set_underclass_population()

                # Create attachment file
                # contract = partner.attach_report_in_mail()

                # Send email
                template_email = request.env.ref(
                    "coop_membership.register_confirm_email"
                )
                if template_email:
                    # template_email.sudo().attachment_ids = [
                    #     (6, 0, (contract.ids))]
                    template_email.sudo().send_mail(attendee.id)

            value = {"website": website}

            return request.render("coop_membership.register_submit_form_success", value)

    def create_event_registration(self, val, user):
        event_reg_obj = request.env["event.registration"].with_user(user)
        event_registration = event_reg_obj.create(val)
        event_registration.action_confirm()
        return event_registration

    def create_contact_partner(self, partner_val, user):
        partner_obj = request.env["res.partner"].with_user(user)
        partner_id = partner_obj.create(partner_val)
        return partner_id

    def _prepare_partner_val(self, partner_val, **post):
        # Create hook for other modules to implement
        return partner_val

    def _prepare_register_form_vals(self, vals):
        # Create hook for other modules to implement
        return vals
