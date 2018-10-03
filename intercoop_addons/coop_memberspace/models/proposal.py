# -*- coding: utf-8 -*-

from openerp import models, api, fields, _
from openerp.exceptions import ValidationError
import random
from datetime import datetime, timedelta
from openerp.tools.safe_eval import safe_eval

def random_token():
    # the token has an entropy of about 120 bits (6 bits/char * 20 chars)
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    return ''.join(random.SystemRandom().choice(chars) for i in xrange(20))


class Proposal(models.Model):
    _name = "proposal"
    _description ="Proposal exchange the shift"

    src_registration_id = fields.Many2one(
        'shift.registration', 'Source Registration', required=True)
    des_registration_id = fields.Many2one(
        'shift.registration', 'Destination Registration', required=True)
    state = fields.Selection([
        ('in_progress', 'In Progress'), # The proposal waiting confirm.
        ('cancel', 'Cancelled'), # The proposal canceled.
        ('refuse', 'Refused'), # The proposal was refused.
        ('accept', 'Accepted') # The proposal was accepted.
    ], string="Status", default="in_progress")
    token = fields.Char(string='Token', copy=False)
    token_valid = fields.Boolean('Token Valid', compute='_compute_token_valid')
    token_expiration = fields.Datetime('Token Expiration', copy=False)
    send_email_request_confirm = fields.Boolean(
        'Email sent to request confirm.')
    send_email_confirm_accept_done = fields.Boolean(
        'Email sent to confirm accept done.')
    send_email_refuse = fields.Boolean('Email sent to inform refused')
    send_email_accept = fields.Boolean('Email sent to inform accepted')

    @api.multi
    def _compute_token_valid(self):
        dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        for proposal in self:
            proposal.token_valid = bool(proposal.token) and \
                (not proposal.token_expiration or
                 dt <= proposal.token_expiration)

    @api.one
    @api.constrains('src_registration_id', 'des_registration_id')
    def _check_amount(self):
        # This constraint check if exists any proposal have
        # src_registration_id = self.des_registration_id and
        # des_registration_id = self.src_registration_id,
        # the system will raise an error.
        proposal = self.search([
            ('src_registration_id', '=', self.des_registration_id.id),
            ('des_registration_id', '=', self.src_registration_id.id),
            ('state', 'not in', ['cancel', 'refuse'])
        ], limit=1)
        if proposal:
            raise ValidationError(
                _('''You already have a proposal from this shift.
                    Please check and accept it.'''))

    @api.model
    def create(self, vals):
        src_registration_id = vals.get('src_registration_id', False)
        src = self.env['shift.registration'].browse(src_registration_id)
        if not src or src.exchange_state != 'in_progress':
            raise ValidationError(
                _('The source shift registration not ready on the market.'))
        try:
            IrConfig  = self.env['ir.config_parameter']
            token_expiration = safe_eval(IrConfig.sudo().get_param(
                'proposal_token_expiration')) or False
            if token_expiration and token_expiration < 1:
                token_expiration = False
        except:
            token_expiration = False
        if token_expiration:
            token_expiration = datetime.now() + timedelta(
                hours=token_expiration)
            vals.update({'token_expiration': token_expiration})
        vals.update({'token': random_token()}) # Init token
        res = super(Proposal, self).create(vals)
        res.send_email_request_confirm_proposal()
        return res

    @api.multi
    def send_email_request_confirm_proposal(self):
        mail_tmpl = self.env.ref('coop_memberspace.request_confirm_proposal')
        if mail_tmpl:
            for record in self:
                mail_tmpl.send_mail(record.id)
                record.send_email_request_confirm = True

    @api.multi
    def accept_proposal(self):
        confirm_exchange_done_mail_tmpl = self.env.ref(
            'coop_memberspace.confirm_exchange_done')
        proposal_accepted_mail_tmpl = self.env.ref(
            'coop_memberspace.proposal_accepted')
        for record in self:
            # Replace shift for member B
            new_src_reg_id = record.src_registration_id.copy({
                'partner_id': record.des_registration_id.partner_id.id,
                'replaced_reg_id': record.src_registration_id.id,
                'exchange_replaced_reg_id': record.des_registration_id.id,
                'tmpl_reg_line_id': False,
                'template_created': False,
                'state': 'replacing',
                'exchange_state': 'replacing'})
            # Replace shift for member A
            new_des_reg_id = record.des_registration_id.copy({
                'partner_id': record.src_registration_id.partner_id.id,
                'replaced_reg_id': record.des_registration_id.id,
                'exchange_replaced_reg_id': record.src_registration_id.id,
                'tmpl_reg_line_id': False,
                'template_created': False,
                'state': 'replacing',
                'exchange_state': 'replacing'})

            record.src_registration_id.write({
               'state': "replaced",
               'exchange_state': "replaced",
               'replacing_reg_id': new_src_reg_id.id,
               'exchange_replacing_reg_id': new_des_reg_id.id
            })
            
            record.des_registration_id.write({
               'state': "replaced",
               'exchange_state': "replaced",
               'replacing_reg_id': new_des_reg_id.id,
               'exchange_replacing_reg_id': new_src_reg_id.id
            })
            # Send email to member A to inform exchange done.
            if confirm_exchange_done_mail_tmpl:
                confirm_exchange_done_mail_tmpl.send_mail(record.id)
                record.send_email_confirm_accept_done = True
            if proposal_accepted_mail_tmpl:
                proposal_accepted_mail_tmpl.send_mail(record.id)
                record.send_email_accept = True
        self.write({'state': 'accept'})

    @api.multi
    def refuse_proposal(self):
        proposal_cancelled_mail_tmpl = self.env.ref(
            'coop_memberspace.proposal_cancelled')
        self.write({'state': 'refuse'})
        if proposal_cancelled_mail_tmpl:
            for record in self:
                # Send email to member B to inform exchange was refused.
                proposal_cancelled_mail_tmpl.send_mail(record.id)
                record.send_email_refuse = True
