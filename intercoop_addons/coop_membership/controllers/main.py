# -*- coding: utf-8 -*-

import openerp
from openerp import http
from openerp.http import request
from openerp.addons.website.models.website import slug
from openerp.addons.web.controllers import main
import logging
import werkzeug
from datetime import datetime

_logger = logging.getLogger(__name__)


class WebsiteRegisterMeeting(http.Controller):

    @http.route(['/discovery'], type='http',
                auth="none", website=True)
    def discovery_web_client(self, s_action=None, **kw):
        main.ensure_db()
        if not request.session.uid:
            return werkzeug.utils.redirect('/discovery/login', 303)
        if kw.get('redirect'):
            return werkzeug.utils.redirect(kw.get('redirect'), 303)

        request.uid = request.session.uid
        return werkzeug.utils.redirect('/web/membership/discovery-meeting-form', 303)

    @http.route('/discovery/login', type='http', auth="none")
    def discovery_web_login(self, redirect=None, **kw):
        main.ensure_db()
        request.params['login_success'] = False
        if request.httprequest.method == 'GET' and redirect and request.session.uid:
            return http.redirect_with_hash(redirect)

        if not request.uid:
            request.uid = openerp.SUPERUSER_ID

        values = request.params.copy()
        try:
            values['databases'] = http.db_list()
        except openerp.exceptions.AccessDenied:
            values['databases'] = None

        if request.httprequest.method == 'POST':
            old_uid = request.uid
            uid = request.session.authenticate(request.session.db, request.params['login'], request.params['password'])
            if uid is not False:
                request.params['login_success'] = True
                if not redirect:
                    redirect = '/web/membership/discovery-meeting-form'
                return http.redirect_with_hash(redirect)
            request.uid = old_uid
            values['error'] = _("Wrong login/password")
        return request.render('coop_membership.login', values)         

    @http.route(['/web/membership/discovery-meeting-form'], type='http',
                auth="none", website=True)
    def get_discover_meeting(self):

        # Get event available
        event_obj = request.registry['event.event']
        event_ids = event_obj.search(request.cr, request.uid, [
            ('is_discovery_meeting', '=', True),
            ('state', '=', 'confirm')
        ])
        events = event_obj.browse(request.cr, request.uid, event_ids,
                                  context=request.context)
        value = {
            'events': events,
        }
        return request.render("coop_membership.register_form", value)

    @http.route(['/web/membership/register/submit'], type='http',
                auth="public", methods=['POST'], csrf=False, website=True)
    def subscribe_discovery_meeting(self, **post):
        value = {}

        # Get data from form
        name = post.get('name', False)
        email = post.get('email', False)
        first_name = post.get('first_name', False)
        sex = post.get('sex', False)
        mobile = post.get('mobile', False)
        phone = post.get('phone', False)
        street1 = post.get('street1', False)
        street2 = post.get('street2', False)
        city = post.get('city', False)
        zipcode = post.get('zipcode', False)
        social_registration = post.get('social_registration', False)
        event_id = post.get('select_event', False)
        dob = post.get('dob', False)
        already_cooperator = post.get('cooperator')

        # conver dob to correct format in database
        try:
            dob = datetime.strptime(
                dob, "%m/%d/%Y").date().strftime('%Y-%m-%d')
        except:
            _logger.warn(
                'Convert birthdate from %s on discovery meeting form failed', dob)


        # Check email exist in database
        partner_obj = request.registry['res.partner']
        partner_id = partner_obj.search(request.cr, request.uid, [
            ('email', '=', email),
        ])

        event_obj = request.registry['event.event']
        event = event_obj.browse(request.cr, request.uid, int(event_id),
                                 context=request.context)

        is_event_valid = True

        # Check invalid and available seat event
        if event and event.is_discovery_meeting and event.state\
                == 'confirm':
            if event.seats_availability == 'limited' and event.seats_max\
                    and event.seats_available < 1:
                is_event_valid = False
        else:
            is_event_valid = False

        if partner_id:
            return request.render(
                "coop_membership.register_submit_form_err_email", value)
        elif not is_event_valid:
            return request.render(
                "coop_membership.register_submit_form_err_event", value)
        else:

            # create event registration
            val = {
                'event_id': event.id,
                'name': name + '' + first_name,
                'email': email,
                'already_cooperator': already_cooperator,
            }
            attendee_id = self.create_event_registration(val)

            partner_val = {
                'name': name + ' ' + first_name,
                'sex': sex,
                'email': email,
                'street': street1,
                'street2': street2,
                'city': city,
                'zip': zipcode,
                'phone': phone,
                'mobile': mobile,
                'birthdate': dob,
            }
            # Create contact partner
            new_partner_id = self.create_contact_partner(partner_val)

            if new_partner_id:

                partner = partner_obj.browse(request.cr, request.uid,
                                             new_partner_id,
                                             context=request.context)

                request.registry['event.registration'].write(
                    request.cr, request.uid, attendee_id,
                    {'partner_id': new_partner_id},
                    context=request.context)


                if social_registration == 'yes':
                    partner.set_underclass_population()

                # Create attachment file
                # contract = partner.attach_report_in_mail()

                # Send email
                template_email = request.env.ref(
                    'coop_membership.register_confirm_email')
                if template_email:
                    # template_email.sudo().attachment_ids = [
                    #     (6, 0, (contract.ids))]
                    template_email.sudo().send_mail(attendee_id)

            return request.render(
                "coop_membership.register_submit_form_success", value)

    def create_event_registration(self, val):
        event_reg_obj = request.registry['event.registration']
        event_registration = event_reg_obj.create(
            request.cr, request.uid, val, context=request.context)
        return event_registration

    def create_contact_partner(self, partner_val):
        partner_obj = request.registry['res.partner']
        partner_id = partner_obj.create(
            request.cr, request.uid, partner_val, context=request.context)
        return partner_id
