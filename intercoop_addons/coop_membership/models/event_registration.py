# -*- coding: utf-8 -*-

from openerp import models, fields, api


class event_registration(models.Model):
    _inherit = 'event.registration'

    is_discovery_meeting_event = fields.Boolean(
        'Discovery Meeting Event',
        related='event_id.is_discovery_meeting')

    @api.multi
    def convert_event_date_begin(self):
        for record in self:
            date = record.event_id.date_begin[0:10].split('-')[2] + '/' +\
                record.event_id.date_begin[0:10].split('-')[1] + '/' +\
                record.event_id.date_begin[0:10].split('-')[0]
            return unicode(date, "utf-8")

    @api.multi
    def get_address_meeting(self):
        for record in self:
            street = record.event_id.address_id and\
                record.event_id.address_id.street or False
            zip_code = record.event_id.address_id and\
                record.event_id.address_id.zip or False
            city = record.event_id.address_id and\
                record.event_id.address_id.city or False
            address = '%s %s %s' % (str(street), str(zip_code), str(city))
            return address

    @api.multi
    def get_email_contact_meeting(self):
        email_contact_meeting =\
            self.env['ir.config_parameter'].sudo().get_param(
                'email_meeting_contact')
        return email_contact_meeting or False

    @api.model
    def create(self, vals):
        res = super(event_registration, self).create(vals)
        template_email = self.env.ref(
            'coop_membership.registration_confirm_meeting_email')
        if res.is_discovery_meeting_event and template_email:
            template_email.send_mail(res.id)
        return res
