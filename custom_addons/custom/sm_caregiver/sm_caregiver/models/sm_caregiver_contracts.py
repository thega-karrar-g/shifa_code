from odoo import models, fields, api, _
import uuid
from datetime import timedelta, datetime, date
from odoo.exceptions import UserError, ValidationError
import json
import requests
import logging
_logger = logging.getLogger(__name__)


class SmCaregiverContracts(models.Model):
    _name = 'sm.caregiver.contracts'
    _description = 'Caregiver Contracts'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    STATE = [
        ('draft', 'Draft'),
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid'),
        ('evaluation', 'Evaluation'),
        ('renew', 'Renew'),
        ('assign_caregiver', 'Assign Caregiver'),
        ('active', 'Active'),
        ('holdreq', 'Hold Req.'),
        ('hold', 'Hold'),
        ('reactivation_request', 'Reactivation Request'),
        ('cancel', 'Canceled'),
        ('terminationreq', 'Termination Req.'),
        ('terminated', 'Terminated'),
        ('completed', 'Completed'),
    ]

    YES_NO = [
        ('yes', 'Yes'),
        ('no', 'No'),
    ]

    # calculate vat
    @api.depends('ssn', 'service_price', 'no_caregiver')
    def _calculate_vat(self):
        for rec in self:
            vat = 0
            if rec.ssn and rec.ssn[0] == '2':
                vat = (rec.service_price * int(rec.no_caregiver) - rec.discount_val) * 0.15
            
            add_service_vat = (rec.additional_service_id.lst_price * int(rec.no_caregiver) - rec.discount_val) * 0.15
            vat = vat + add_service_vat
            #vat += rec.additional_service_id.lst_price * 0.15
            rec.vat = vat

    @api.onchange('service_id', 'additional_service_id')
    def onchange_service(self):
        for rec in self:
            if rec.service_id:
                rec.service_price = rec.service_id.list_price
                rec.duration = rec.service_id.duration
            if rec.service_id and rec.additional_service_id:
                rec.service_price = rec.service_id.list_price + rec.additional_service_id.lst_price
                rec.duration = rec.service_id.duration

            if rec.additional_service_id:
                rec.product_price = rec.additional_service_id.lst_price

    # calculate bmi
    @api.depends('height', 'weight')
    def _compute_bmi(self):
        for r in self:
            if not r.height:
                return 0
            else:
                r.bmi = r.weight / (r.height * r.height) * 10000
                return r.bmi

    # calculate discount value
    @api.depends('discount', 'discount_id', 'service_price', 'no_caregiver')
    def _calculate_discount(self):
        for rec in self:
            if rec.discount_id:
                rec.discount_val = rec.service_id.list_price * (rec.discount_id.fixed_type / 100) * int(rec.no_caregiver)
            else:
                rec.discount_val = rec.service_id.list_price * (rec.discount / 100) * int(rec.no_caregiver)

    # calculate total amount of sleep request
    @api.depends('service_price', 'vat', 'discount_val', 'no_caregiver')
    def _cal_net_payment(self):
        for rec in self:
            rec.amount_payable = ((rec.service_price * int(rec.no_caregiver)) - rec.discount_val + rec.vat)

    # get discount percentage value from discount model
    @api.depends('discount_id')
    def _compute_discount_value(self):
        for rec in self:
            if rec.discount_id:
                rec.discount = rec.discount_id.fixed_type
            else:
                rec.discount = 0

    state = fields.Selection(STATE, string='State', readonly=False, default=lambda *a: 'draft',tracking=True)
    name = fields.Char('Reference', index=True, copy=False)

    # patient details
    patient_id = fields.Many2one('oeh.medical.patient', string='Second Party (Patient)', help="Second Party Name",
                                 required=False,
                                 readonly=False, tracking=True)
    nationality = fields.Selection([
        ('KSA', 'Saudi'),
        ('NON', 'Non-Saudi')
    ], related='patient_id.ksa_nationality', string="Second Party Nationality")
    house_location = fields.Char(string='House Location', readonly=True,
                                 states={'draft': [('readonly', False)]}, related="patient_requested_id.house_location")
    house_number = fields.Char(string='House Number', readonly=True,
                               states={'draft': [('readonly', False)]}, related="patient_requested_id.house_number")
    branch = fields.Selection([
        ('riyadh', 'Riyadh'),
        ('dammam', 'Dammam'),
        ('jeddah', 'Jeddah'),
    ], string="Branch", readonly=False, states={'draft': [('readonly', False)]},required=True,default='riyadh')
    ssn = fields.Char(string='ID Number', related='patient_requested_id.ssn')
    patient_ssn = fields.Char(string='Patient ID Number', related='patient_id.ssn')
    mobile = fields.Char(string='Mobile', related='patient_requested_id.mobile')

    # service details
    date = fields.Date(string="Date", required=True, readonly=True,
                       states={'draft': [('readonly', False)]}, tracking=True)
    service_id = fields.Many2one('sm.shifa.service', string='Service', required=True,
                                 domain=[('service_type', '=', 'Car')], readonly=True,
                                 states={'draft': [('readonly', False)],'renew': [('readonly', False)]}, tracking=True)
    additional_service_id = fields.Many2one('sm.shifa.service', string='Additional Service',
                                            domain=[('service_type', '=', 'Car')], readonly=True,
                                            states={'draft': [('readonly', False)]}, tracking=True)
    additional_service_id = fields.Many2one('product.product', string='Additional Service',
                                            domain=[('type', '=', 'service')], readonly=True,
                                            states={'draft': [('readonly', False)],'renew': [('readonly', False)]}, tracking=True)
    product_price = fields.Float()
    service_price = fields.Float(string="Service Price", related=False, store=True)
    duration = fields.Integer(string="Duration", related=False, store=True)
    no_caregiver = fields.Selection([('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')], required=True,
                                    string="Number of Caregiver",
                                    readonly=False,
                                    states={'terminated': [('readonly', True)], 'active': [('readonly', True)],
                                            'cancel': [('readonly', True)], 'hold': [('readonly', True)],
                                            'hodreq': [('readonly', True)],'paid': [('readonly', True)],'evaluation': [('readonly', True)]}, tracking=True)
    vat = fields.Float(string='VAT(+) 15%', compute=_calculate_vat)
    discount_id = fields.Many2one('sm.shifa.discounts', string='Discount Name',
                                  domain=[('state', '=', 'Active')], readonly=True,
                                  states={'draft': [('readonly', False)], 'unpaid': [('readonly', False)],'renew': [('readonly', False)]},
                                  tracking=True)
    discount = fields.Float(string='Discount %', compute=_compute_discount_value, store=True)
    discount_val = fields.Float(string='Discount', compute=_calculate_discount, store=True)
    amount_payable = fields.Float('Amount Payable', compute=_cal_net_payment)

    # other details
    pro_pending = fields.Boolean(string="Pro. Free Service", readonly=True,
                                 states={'draft': [('readonly', False)], 'unpaid': [('readonly', False)]})

    payment_made_through = fields.Selection([
        ('pending', 'Free Service'),
        ('mobile', 'Mobile App'),
        ('call_center', 'Call Center'),
    ], string="Pay. Made Thru.", required=False, readonly=True,
        states={'draft': [('readonly', False)], 'unpaid': [('readonly', False)],'renew': [('readonly', False)]})
    mobile_payment_state = fields.Char(string='Mobile payment state', readonly=True,
                                       states={'draft': [('readonly', False)], 'unpaid': [('readonly', False)]})
    deduction_amount = fields.Float(string="Ded. Amount", readonly=True,
                                    states={'draft': [('readonly', False)], 'unpaid': [('readonly', False)]},
                                    tracking=True)
    payment_reference = fields.Char(string='Payment Ref. #', readonly=True)
    payment_method_name = fields.Char(string="Payment Method Name", readonly=True)
    auto_renew = fields.Boolean(default=True)

    # questionnaire details
    is_patient_conscious = fields.Selection(YES_NO, readonly=False,
                                            states={'terminated': [('readonly', True)], 'active': [('readonly', True)],
                                                    'cancel': [('readonly', True)], 'hold': [('readonly', True)],
                                                    'holdreq': [('readonly', True)]})
    have_chronic_diseases = fields.Selection(YES_NO, readonly=False,
                                             states={'terminated': [('readonly', True)], 'active': [('readonly', True)],
                                                     'cancel': [('readonly', True)], 'hold': [('readonly', True)],
                                                     'holdreq': [('readonly', True)]})
    mention_diseases = fields.Char(readonly=False,
                                   states={'terminated': [('readonly', True)], 'active': [('readonly', True)],
                                           'cancel': [('readonly', True)], 'hold': [('readonly', True)],
                                           'holdreq': [('readonly', True)]})
    use_insulin_needles = fields.Selection(YES_NO, readonly=False,
                                           states={'terminated': [('readonly', True)], 'active': [('readonly', True)],
                                                   'cancel': [('readonly', True)], 'hold': [('readonly', True)],
                                                   'holdreq': [('readonly', True)]})
    can_move_or_seated = fields.Selection([
        ('move', 'Move'),
        ('seated', 'Seated'),
    ], readonly=False,
        states={'terminated': [('readonly', True)], 'active': [('readonly', True)], 'cancel': [('readonly', True)],
                'hold': [('readonly', True)], 'holdreq': [('readonly', True)]})
    eat_food_or_tube = fields.Selection([
        ('eat_food', 'Eat Food'),
        ('feeding_tube', 'Feeding tube'),
    ], readonly=False,
        states={'terminated': [('readonly', True)], 'active': [('readonly', True)], 'cancel': [('readonly', True)],
                'hold': [('readonly', True)], 'holdreq': [('readonly', True)]})

    tube_position = fields.Selection([
        ('nose', 'Nose'),
        ('abdomen', 'Abdomen'),
    ], readonly=False,
        states={'terminated': [('readonly', True)], 'active': [('readonly', True)], 'cancel': [('readonly', True)],
                'hold': [('readonly', True)], 'holdreq': [('readonly', True)]})

    is_laryngeal_cleft = fields.Selection(YES_NO, readonly=False,
                                          states={'terminated': [('readonly', True)], 'active': [('readonly', True)],
                                                  'cancel': [('readonly', True)], 'hold': [('readonly', True)],
                                                  'holdreq': [('readonly', True)]})
    use_oxygen_inhaled_medications = fields.Selection(YES_NO, readonly=False,
                                                      states={'terminated': [('readonly', True)],
                                                              'active': [('readonly', True)],
                                                              'cancel': [('readonly', True)],
                                                              'hold': [('readonly', True)],
                                                              'holdreq': [('readonly', True)]})
    have_any_catheter = fields.Selection(YES_NO, readonly=False,
                                         states={'terminated': [('readonly', True)], 'active': [('readonly', True)],
                                                 'cancel': [('readonly', True)], 'hold': [('readonly', True)],
                                                 'holdreq': [('readonly', True)]})
    wounds_diabetic_bed_sores = fields.Selection(YES_NO, readonly=False,
                                                 states={'terminated': [('readonly', True)],
                                                         'active': [('readonly', True)],
                                                         'cancel': [('readonly', True)], 'hold': [('readonly', True)],
                                                         'holdreq': [('readonly', True)]})
    wear_diapers = fields.Selection(YES_NO, readonly=False,
                                    states={'terminated': [('readonly', True)], 'active': [('readonly', True)],
                                            'cancel': [('readonly', True)], 'hold': [('readonly', True)],
                                            'holdreq': [('readonly', True)]})
    comment = fields.Char(String="Comment", readonly=False,
                          states={'terminated': [('readonly', True)], 'active': [('readonly', True)],
                                  'cancel': [('readonly', True)], 'hold': [('readonly', True)],
                                  'holdreq': [('readonly', True)]})

    # evaluation
    first_party = fields.Many2one('hr.employee', string='Old First Party', domain=[('active', '=', True)],
                                  readonly=False,
                                  states={'terminated': [('readonly', True)], 'active': [('readonly', True)],
                                          'cancel': [('readonly', True)]})
    first_party_user = fields.Many2one('res.users', string='First Party', domain=[('active', '=', True)],
                                       readonly=False,
                                       states={'terminated': [('readonly', True)], 'active': [('readonly', True)],
                                               'cancel': [('readonly', True)]}, default=lambda self: self.env.user)
    second_party = fields.Char(string='Second Party', readonly=False,
                               states={'terminated': [('readonly', True)], 'active': [('readonly', True)],
                                       'cancel': [('readonly', True)]})
    second_party_id = fields.Char(string='Second Party ID', readonly=False, related="patient_id.ssn",
                                  states={'terminated': [('readonly', True)], 'active': [('readonly', True)],
                                          'cancel': [('readonly', True)]})
    second_party_mobile = fields.Char(string='Second Party Mobile', readonly=False, related="patient_id.mobile",
                                      states={'terminated': [('readonly', True)], 'active': [('readonly', True)],
                                              'cancel': [('readonly', True)]})
    patient_name = fields.Char(string='Patient Name', readonly=False,
                               states={'terminated': [('readonly', True)], 'active': [('readonly', True)],
                                       'cancel': [('readonly', True)]})

    patient_requested_id = fields.Many2one('oeh.medical.patient', string='Requested By',
                                           states={'terminated': [('readonly', True)], 'active': [('readonly', True)],
                                                   'cancel': [('readonly', True)]})
    starting_date = fields.Date(string='Starting Date', readonly=False,
                                states={'terminated': [('readonly', True)], 'active': [('readonly', False)],
                                        'cancel': [('readonly', True)]},tracking=True)
    ending_date = fields.Date(string='Ending Date', readonly=False,
                              states={'terminated': [('readonly', True)], 'active': [('readonly', False)],
                                      'cancel': [('readonly', True)]},tracking=True)
    jitsi_link = fields.Text()  # mobile jitsi link
    invitation_text_jitsi = fields.Html(string='Invitation Link', readonly=True)

    # caregiver details
    caregiver = fields.Many2one('oeh.medical.physician', string='First Caregiver', readonly=False,
                                states={'terminated': [('readonly', True)], 'active': [('readonly', False)],
                                        'cancel': [('readonly', True)], 'hold': [('readonly', True)],
                                        'holdreq': [('readonly', True)]}, domain=[('role_type', '=', 'C')],tracking=True)
    caregiver_second = fields.Many2one('oeh.medical.physician', string='Second Caregiver', readonly=False,
                                       states={'terminated': [('readonly', True)], 'active': [('readonly', True)],
                                               'cancel': [('readonly', True)], 'hold': [('readonly', True)],
                                               'holdreq': [('readonly', True)]}, domain=[('role_type', '=', 'C')])
    caregiver_third = fields.Many2one('oeh.medical.physician', string='Third Caregiver', readonly=False,
                                      states={'terminated': [('readonly', True)], 'active': [('readonly', True)],
                                              'cancel': [('readonly', True)], 'hold': [('readonly', True)],
                                              'holdreq': [('readonly', True)]}, domain=[('role_type', '=', 'C')])

    # accounting and payment request
    payment_date = fields.Date(string='OLD Reminder Date', compute="_generate_date", store=True)
    reminder_date = fields.Date('Reminder Date', compute="_compute_reminder_date", store=True)
    date_payment = fields.Date(string='Payment Date')
    request_payment_ids = fields.One2many('sm.shifa.requested.payments', 'caregiver_contract_id',
                                          string='Payment Request#', copy=False,
                                          readonly=True)
    move_ids = fields.One2many('account.move', 'caregiver_contract_id', string='account move', ondelete='restrict',
                               readonly=True, copy=False)

    attachment_ids = fields.Many2many('ir.attachment', string="Upload Signed Contract", readonly=False,
                                      states={'terminated': [('readonly', True)], 'active': [('readonly', True)],
                                              'cancel': [('readonly', True)], 'hold': [('readonly', True)],
                                              'holdreq': [('readonly', True)]})
    caregiver_id = fields.Many2one('sm.caregiver', string="caregiver")
    request_payment_id = fields.Many2one('sm.shifa.requested.payments', string='Payment Request#', copy=False, readonly=True)
    treatment_id = fields.Many2one('sm.treatments', string='Treatment#', copy=False, readonly=True)

    hold = fields.Boolean()
    hold_reason = fields.Char()
    hold_date = fields.Date()
    reactivation = fields.Boolean()
    reactivation_reason = fields.Char()
    reactivation_date = fields.Date()
    termination_date = fields.Date()
    termination_reason = fields.Char()
    cancellation_reason = fields.Char()
    remaining_days = fields.Integer('Number of refunded days', compute="_compute_remaining_days", store=True)
    hold_reason_ids = fields.One2many('sm.hold.reason', 'caregiver_contract_id')
    reactivation_reason_ids = fields.One2many('sm.reactivation.reason', 'caregiver_contract_id')
    reactivation_reason_count = fields.Integer(compute="_compute_reactivation_reason_count")
    evaluation_date = fields.Date()
    call_center_census_id = fields.Many2one('sm.shifa.call.center.census', ondelete='cascade')
    cancellation_ids = fields.One2many('sm.shifa.cancellation.refund', 'caregiver_contract_id')
    cancellation_count = fields.Integer(compute="_compute_cancellation_count")
    refund_req = fields.Many2one('sm.shifa.cancellation.refund', string='Refund Request')
    active = fields.Boolean(default=True)
    caregiver_contract_count = fields.Integer(compute="_compute_caregiver_count")

    def _compute_caregiver_count(self):
        for rec in self:
            rec.caregiver_contract_count = len(rec.patient_id.caregiver_contract_ids)

    def _compute_cancellation_count(self):
        for rec in self:
            rec.cancellation_count = len(rec.cancellation_ids)

    def _compute_reactivation_reason_count(self):
        for rec in self:
            rec.reactivation_reason_count = len(rec.reactivation_reason_ids)

    @api.depends('termination_date', 'ending_date', 'hold_reason_ids.remaining_days')
    def _compute_remaining_days(self):
        for rec in self:
            rec.remaining_days = False
            if rec.hold_reason_ids:
                rec.remaining_days = rec.hold_reason_ids[-1].remaining_days
            elif rec.termination_date and rec.ending_date:
                rec.remaining_days = (rec.ending_date - rec.termination_date).days

    # create payment request
    def create_payment_request(self, date):
        pay_values = {
            # 'patient': self.patient_id.id,
            'patient': self.patient_requested_id.id,
            'type': 'caregiver',
            'details': "Caregiver" + self.name,
            'date': date or datetime.now().date(),
            'payment_method': 'point_of_sale',
            'state': 'Send',
            'payment_amount': self.amount_payable,
            'caregiver_contract_id': self.id,
        }
        pay_req = self.env['sm.shifa.requested.payments'].create(pay_values)
        pay_req.set_to_send()

    def create_cancel_request(self):
        pay_values = {
            # 'patient': self.patient_id.id,
            'patient': self.patient_id.id,
            'state': 'Processed',
            'type': 'caregiver',
            'reason': self.termination_reason if self.termination_reason else '',
            'caregiver_contract_id': self.id,
            'payment_request_id': self.request_payment_ids[0].id if self.request_payment_ids else False,
            'move_ids': [(6, 0, self.move_ids.ids)] if self.move_ids else [(5, 0, 0)]
        }
        refund_req = self.env['sm.shifa.cancellation.refund'].create(pay_values)
        self.refund_req = refund_req.id

    @api.depends('ending_date')
    def _compute_reminder_date(self):
        for rec in self:
            rec.reminder_date = rec.ending_date - timedelta(days=5) if rec.ending_date else False

    # open payment record
    def open_payment_view(self):
        action = self.env['ir.actions.act_window']._for_xml_id(
            'smartmind_shifa_extra.sm_shifa_requested_payments_action')
        action['domain'] = [('caregiver_contract_id', '=', self.id)]
        action.update({'context': {}})
        return action

    def open_cancel_request(self):
        action = self.env['ir.actions.act_window']._for_xml_id(
            'smartmind_shifa_extra.sm_shifa_cancellation_refund_action')
        action['domain'] = [('caregiver_contract_id', '=', self.id)]
        action.update({'context': {}})
        return action

    # create caregiver record
    def create_caregiver(self):
        values = {
            'patient': self.patient_id.id,
            'caregiver': self.caregiver.id,
            'caregiver_second': self.caregiver_second.id,
            'caregiver_third': self.caregiver_third.id,
        }
        self.caregiver_id = self.env['sm.caregiver'].create(values)

    # open caregiver record
    def open_caregiver_view(self):
        action = self.env['ir.actions.act_window']._for_xml_id('sm_caregiver.sm_caregiver_action')
        action['domain'] = [('id', '=', self.caregiver_id.id)]
        action.update({'context': {}})
        return action

    # create jitsi link
    def create_jitsi_meeting(self):
        server_url = self.env['ir.config_parameter'].sudo().get_param('oehealth_jitsi.video_call_server_url')
        model = self.env['sm.caregiver.contracts'].browse(int(self.id))
        meeting_link = server_url + '/' + self._get_meeting_code()
        invitation_text = _(
            "<a href='%s' target='_blank' class='btn btn-primary btn-lg' style='font-size:bold; padding: 10px;'><span style='color:#000;'>Join Meeting</span></a>") % meeting_link
        model.write({
            'invitation_text_jitsi': invitation_text,
            'jitsi_link': meeting_link,
        })

    def _get_meeting_code(self):
        return str(uuid.uuid4()).replace('-', '')

    # get the service invoice line

    def get_invoice_lines(self):
        invoice_lines = []
        if self.patient_id.ksa_nationality == 'NON':
            company = self.env.user.company_id
            tax = company.account_sale_tax_id
        else:
            tax = False

        invoice_lines.append(
            (0, 0, {
                'product_id': self.service_id.product_id.id,
                'price_unit': self.service_id.list_price,
                'tax_ids': tax,
                'discount': self.discount,
                'sequence': 1,
                'quantity': int(self.no_caregiver),
            }))
        if self.additional_service_id:
            invoice_lines.append(
                (0, 0, {
                    'product_id': self.additional_service_id.id,
                    'price_unit': self.additional_service_id.lst_price,
                    'tax_ids': [(6, 0, self.env.user.company_id.account_sale_tax_id.ids)],
                    'sequence': 2,
                    'quantity': int(self.no_caregiver),
                }))
        return invoice_lines

    def get_credit_note_lines(self):
        invoice_lines = []

        # Determine the tax to apply
        if self.patient_id.ksa_nationality == 'NON':
            company = self.env.user.company_id
            tax = company.account_sale_tax_id
            tax_percentage = sum(tax.mapped('amount')) / 100  # Sum of all tax percentages
        else:
            tax = False
            tax_percentage = 0  # No tax applied

        # Check the state and calculate price
        if self.state in ['cancel', 'evaluation', 'assign_caregiver']:
            price = self.service_price

            # Apply discount if any
            if self.discount > 0:
                price = (1 - (self.discount / 100)) * price

            # Calculate refund price including the tax
            refund_price = -price * int(self.no_caregiver) * 0.01
            refund_price_with_tax = refund_price * (1 + tax_percentage)

            # Add main service line
            invoice_lines.append(
                (0, 0, {
                    'product_id': self.service_id.product_id.id,
                    'price_unit': self.service_price,
                    'tax_ids': [(6, 0, tax.ids)] if tax else False,  # Set tax if available
                    'discount': self.discount,
                    'sequence': 1,
                    'quantity': int(self.no_caregiver),
                })
            )

            # Add refund line with 1% deduction and include tax
            invoice_lines.append(
                (0, 0, {
                    'name': '1% Deduction',
                    'price_unit': refund_price_with_tax,
                    'tax_ids': [(6, 0, tax.ids)] if tax else [(5, 0, 0)],  # Include tax if available
                    'sequence': 2,
                    'quantity': 1,
                })
        )
        else:
            price = ((self.service_price - self.product_price) / self.duration) * self.remaining_days
            if self.service_id.refund_percent > 0:
                price = price * self.service_id.refund_percent / 100
            invoice_lines.append(
                (0, 0, {
                    'product_id': self.service_id.product_id.id,
                    'price_unit': price,
                    'tax_ids': tax,
                    'discount': self.discount,
                    'sequence': 1,
                    'quantity': int(self.no_caregiver),
                }))
        return invoice_lines

    # create invoice
    def _get_default_journal(self):
        journal = self.env['account.journal'].search([
            ('type', '=', 'sale'),
            ('analytic_account_id', '=', self.env.user.analytic_account_id.id)
        ], limit=1)
        if not journal:
            journal = self.env['account.journal'].search([
                ('type', '=', 'sale')
            ], limit=1)
        return journal

    def generate_invoice(self):
        self.create_invoice(self.payment_date)

    def open_payment_request(self):
        self.ensure_one()
        ctx = {
            'form_view_ref': 'smartmind_shifa_extra.view_shifa_requested_payments_form',
            'default_patient': self.patient_id.id,
            'default_type': 'caregiver',
            'default_caregiver_contract_id': self.id,
            'default_date_caregiver_contract': self.date,
        }
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sm.shifa.requested.payments',
            'view_mode': 'form',
            'target': 'new',
            'context': ctx,
        }

    def open_treatment_form(self):
        self.ensure_one()  # Ensure there's only one record
        ctx = {
            'form_view_ref': 'sm_search_patient.sm_treatments_form_view',
            'default_patient_id': self.patient_id.id,
            'default_caregiver_contract_id': self.id,
            'from_caregiver': True,
        }
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sm.treatments',
            'view_mode': 'form',
            'target': 'new',
            'context': ctx,
        }

    def create_invoice(self, date):
        if self.branch == 'riyadh':
            analytical_account_id = 2
        elif self.branch == 'dammam':
            analytical_account_id = 3
        if self.move_ids.filtered(lambda l: l.move_type == 'out_invoice' and l.state == 'posted'):
            return
        invoice_lines = self.get_invoice_lines()
        #default_journal = self._get_default_journal()      
        default_journal = self.env['account.journal'].sudo().search([
            ('type','=','sale'),
            ('analytic_account_id','=',analytical_account_id),
            ('company_id','=',self.env.user.company_id.id),
        ],limit=1)
        # Create Invoice
        vals = {
            'move_type': 'out_invoice',
            'journal_id': default_journal.id,
            'partner_id': self.patient_id.partner_id.id,
            # 'partner_id': self.patient_requested_id.partner_id.id,
            #'analytic_account_id': self.env.user.analytic_account_id.id,
            'analytic_account_id': analytical_account_id,
            # 'patient': self.patient_id.id,
            'patient': self.patient_id.id,
            'invoice_date': date,
            'date': datetime.now().date(),
            'caregiver_contract_id': self.id,
            'ref': 'Caregiver contract # ' + self.name,
            'invoice_line_ids': invoice_lines,
        }
        invoice = self.env['account.move'].sudo().create(vals)
        invoice.action_post()

    def create_credit_note(self, date):
        invoice_lines = self.get_credit_note_lines()
        default_journal = self._get_default_journal()
        # Create Invoice
        receivable_line = False
        vals = {
            'move_type': 'out_refund',
            'journal_id': default_journal.id,
            'partner_id': self.patient_id.partner_id.id,
            # 'partner_id': self.patient_requested_id.partner_id.id,
            'analytic_account_id': self.env.user.analytic_account_id.id,
            # 'patient': self.patient_id.id,
            'patient': self.patient_id.id,
            'invoice_date': date,
            'date': datetime.now().date(),
            'caregiver_contract_id': self.id,
            'invoice_line_ids': invoice_lines,
        }
        if self.move_ids.filtered(lambda l: l.move_type == 'out_invoice'):
            vals['reversed_entry_id'] = self.move_ids.filtered(lambda l: l.move_type == 'out_invoice')[0].id
            receivable_line = self.move_ids.filtered(lambda l: l.move_type == 'out_invoice')[0].line_ids.filtered(
                lambda l: l.account_id.user_type_id.id == 5)

        credit_note = self.env['account.move'].sudo().create(vals)
        credit_note_line = credit_note.line_ids.filtered(lambda l: l.account_id.user_type_id.id == 5)
        credit_note.action_post()
        if receivable_line and credit_note_line:
            lines = receivable_line + credit_note_line
            lines.reconcile()

    def open_invoice_view(self):
        action = self.env['ir.actions.act_window']._for_xml_id('account.action_move_out_invoice_type')
        action['domain'] = [('caregiver_contract_id', '=', self.id)]
        action.update({'context': {}})
        return action

    def open_treatment_view(self):
        action = self.env['ir.actions.act_window']._for_xml_id('sm_search_patient.sm_treatments_action')
        action['domain'] = [('caregiver_contract_id', '=', self.id)]
        action.update({'context': {}})
        return action

    def continue_action(self):
        if not self.pro_pending:
            raise UserError("You cannot move to the next action until admission pending!")
        self.create_jitsi_meeting()
        return self.write({'state': 'evaluation'})

    def set_to_cancelled(self):
        if self.state == 'unpaid':
            ctx = {
                'form_view_ref': 'sm_caregiver.sm_caregiver_contracts_form_cancellation_reason_view',
            }
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'sm.caregiver.contracts',
                'view_mode': 'form',
                'target': 'new',
                'res_id': self.id,
                'context': ctx,
            }
        if self.move_ids.filtered(lambda l: l.move_type == 'out_invoice') and self.payment_made_through != 'pending' and not self.pro_pending:
            credit_note = self.create_credit_note((fields.Datetime.now() + timedelta(hours=3)).date())
        self.write({'state': 'cancel'})
        
        if self.state != 'unpaid' and self.payment_made_through != 'pending':
            self.create_cancel_request()

    def set_to_cancelled_1(self):
        if self.move_ids.filtered(lambda l: l.move_type == 'out_invoice') and self.payment_made_through != 'pending' and not self.pro_pending:
            credit_note = self.create_credit_note((fields.Datetime.now() + timedelta(hours=3)).date())
        self.write({'state': 'cancel'})

    def set_to_holdreq(self):
        return self.write({'state': 'holdreq'})

    def set_to_terminationreq(self):
        return self.write({'state': 'terminationreq'})

    def set_to_renew(self):
        return self.write({'state': 'renew'})

    def set_to_completed(self):
        return self.write({'state': 'completed'})

    def check_completed_contracts(self):
        date = (fields.Datetime.now() + timedelta(hours=3)).date()
        records = self.sudo().search([('ending_date', '!=', False), ('ending_date', '<', date), ('auto_renew', '=', 1),
                                      ('state', '=', 'active')])
        
        for rec in records:
            new_contract = rec.copy({'state': 'renew', 'starting_date': date})
            payment_request = self.env['sm.shifa.requested.payments'].sudo().search([
                ('caregiver_contract_id','=',new_contract.id)
            ],limit=1)
            new_contract.state = 'renew'
            new_contract.additional_service_id = False
            new_contract.discount_id = False
            new_contract.payment_made_through = False
            new_contract.mobile_payment_state = False
            new_contract.deduction_amount = False
            new_contract.payment_reference = False
            new_contract.payment_method_name = False
            new_contract.onchange_service()
            new_contract._cal_net_payment()
            new_contract.ending_date = False
            new_contract.starting_date = rec.ending_date + timedelta(days=1)
            if not payment_request:
                new_contract.create_payment_request(date)
            rec.set_to_completed()

    def send_email_reminder_date(self):
        date = (fields.Datetime.now() + timedelta(hours=3)).date()
        records = self.sudo().search([('reminder_date', '=', date), ('state', '=', 'active')])
        if records:
            template = self.env['mail.template'].browse(26)
            users = self.env.ref('smartmind_shifa.group_oeh_medical_call_center').sudo().users
            users += self.env.ref('sm_caregiver.group_oeh_medical_super_caregiver').sudo().users
            users += self.env.ref('smartmind_shifa.group_oeh_medical_operation_manager').sudo().users
            partners = users.mapped('partner_id')
            for record in records:
                my_model = record._name
                if record.patient_id.mobile:
                    msg = (
                        "مرحبا " + record.patient_requested_id.name +
                        ", هذا تذكير ودي بأن عقدك من المقرر أن ينتهي في غضون 5 أيام. "
                        "لمواصلة الاستمتاع بخدماتنا. إذا كنت ترغب في إنهاء عقدك، فيمكنك ارسال طلبك بسهولة من خلال تطبيقنا المحمول او التواصل مع خدمة العملاء. "
                        "يرجى ملاحظة أنه في حال عدم إنهاء العقد خلال هذه الفترة، سيتم تجديده تلقائيًا، وسيتعين عليك سداد رسوم التجديد وفقًا لقيمة العقد. "
                        "نشكرك على اختيارنا"
                    )
                    record.send_sms(record.patient_requested_id.mobile, msg, my_model, record.id)
                partners += record.patient_requested_id.partner_id
                partner_ids_comma_separated = ','.join(map(str, partners.ids))
                template.sudo().write({"partner_to": partner_ids_comma_separated})
                template.send_mail(record.ids[0], force_send=True)



    """def unlink(self):
        for rec in self:
            if rec.state != 'cancel':
                raise UserError(_("You can delete only if it cancelled Requests"))
        return super().unlink()"""

    @api.depends('starting_date')
    def _generate_date(self):
        for rec in self:
            if rec.starting_date:
                rec.payment_date = rec.starting_date + timedelta(days=25)
            else:
                rec.payment_date = datetime.now().date() + timedelta(days=25)

    @api.model
    def create(self, vals):
        """if not self.env.context.get('from_api'):"""
        vals['name'] = self.sudo().env['ir.sequence'].next_by_code('sm.caregiver.contracts') or '/'
        if 'patient_requested_id' not in vals and 'patient_id' in vals and vals['patient_id']:
            vals['patient_requested_id'] = vals['patient_id']
        if vals['payment_made_through'] == 'call_center':
            vals['state'] = 'unpaid'
            res = super(SmCaregiverContracts, self).create(vals)
            res.create_payment_request(res['date'])
        elif vals['payment_made_through'] == 'pending':
            res = super(SmCaregiverContracts, self).create(vals)
        else:
            vals['state'] = 'unpaid'
            res = super(SmCaregiverContracts, self).create(vals)

        if not res.patient_id and res.patient_requested_id:
            res['patient_id'] = res.patient_requested_id.id
        if res.service_id:
            res.onchange_service()
        return res

    @api.onchange('payment_made_through')
    def _onchange_payment_made_through(self):
        restricted_values = ['mobile', 'package', 'aggregator_package']
        if self.payment_made_through in restricted_values:
            return {
                'warning': {
                    'title': "Invalid Selection",
                    'message': "You are not allowed to generate this type of payment method. Please select another value.",
                }
            }

    # @api.constrains('payment_made_through')
    # def _check_payment_method(self):
    #     restricted_values = ['mobile', 'package', 'aggregator_package']
    #     for record in self:
    #         # Allow 'mobile' when creating via API
    #         if record.payment_made_through in restricted_values:
    #             raise ValidationError(
    #                 "You are not allowed to save this type of payment method. Please select another value.")

    def hold_rec(self):
        self.state = 'hold'
        self.env['sm.hold.reason'].sudo().create({
            'caregiver_contract_id': self.id,
            'name': self.hold_reason,
            'date': self.hold_date,
            'remaining_days': (self.ending_date - self.hold_date).days + 1,
        })
        self.hold = True
        self.ending_date = False
        self.reactivation = False

    def write(self, vals):
        """if 'hold_reason' in vals and vals['hold_reason']:
            vals['state'] = 'hold'
            vals['hold_date'] = (fields.Datetime.now() + timedelta(hours=3)).date()
            self.env['sm.hold.reason'].sudo().create({
                'caregiver_contract_id': self.id,
                'name': vals['hold_reason'],
                'date': vals['hold_date'],
                'remaining_days': (self.ending_date - vals['hold_date']).days,
            })
            vals['hold'] = True
            vals['ending_date'] = False
            vals['reactivation'] = False"""
        """if 'reactivation_reason' in vals and vals['reactivation_reason']:
            vals['state'] = 'active'
            vals['reactivation'] = True
            vals['hold'] = False
            self.env['sm.reactivation.reason'].sudo().create({
                'caregiver_contract_id': self.id,
                'name': vals['reactivation_reason'],
                'date': vals['reactivation_date'] if 'reactivation_date' in vals else self.reactivation_date,
            })"""
        """if 'termination_reason' in vals and vals['termination_reason']:
            vals['state'] = 'terminated'
            vals['reactivation'] = False
            vals['hold'] = False
            self.create_credit_note(vals['termination_date'] if 'termination_date' in vals else self.termination_date)
            self.create_cancel_request()"""

        # if 'state' in vals and vals['state'] == 'active' and 'starting_date' in vals and vals['starting_date']:
        # vals['ending_date'] = vals['starting_date'] + timedelta(days=self.duration)
        return super().write(vals)

    def check_paid(self):
        for request_payment_id in self.request_payment_ids.filtered(lambda l: l.state not in ['Paid', 'Done','renew']):
            if request_payment_id and not self.pro_pending:
                raise UserError("You cannot move to the next action until the payment is paid or processed!")
        self.create_jitsi_meeting()

        # If all fields are True, proceed with the logic
        if not self.pro_pending:
            self.create_invoice(self.date)

        return self.write({'state': 'evaluation', 'evaluation_date': datetime.now()})

    def set_to_evaluation(self):
        self.create_jitsi_meeting()

        # If all fields are True, proceed with the logic
        if not self.pro_pending:
            self.create_invoice(self.date)

        return self.write({'state': 'evaluation', 'evaluation_date': datetime.now()})

    def send_to_patient(self):
        self.action_send_sms()
        self.send_fcm_request(self.patient_id.patient_fcm_token)

    # send sms to patient
    def action_send_sms(self):
        """
        Sends an SMS notification to the patient with the Jitsi meeting link.
        """
        my_model = self._name
        if not self.patient_id.mobile:
            raise UserError(_('Mobile number for patient "%s" is not available.') % self.patient_id.name)

        msg = f"You can join the meeting from this link {self.jitsi_link}"
        self.send_sms(self.patient_id.mobile, msg, my_model, self.id)

    # def action_send_sms(self):
    #     my_model = self._name
    #     if self.patient_id.mobile:
    #         msg = "You can join meeting from link: %s." % (self.jitsi_link)
    #         self.send_sms(self.patient_id.mobile, msg, my_model, self.id)
    #     else:
    #         raise UserError(_('mobile number for {} is not exist'.format(self.patient_id.name)))

    def send_sms(self, mobile, msg, model, rec_id):
        gatewayurl_id = self.env['gateway_setup'].search([], limit=1)
        if gatewayurl_id and gatewayurl_id.gateway_url:
            try:
                self.env['gateway_setup'].sudo().send_sms_link(msg, mobile, rec_id, model, gatewayurl_id)
            except Exception as e:
                _logger.error(e)
        else:
            raise ValidationError(_("The SMS Gateway is not configured"))

    # send notification to patient app
    def send_fcm_request(self, device_token):
        server_token = 'AAAA4_vaS1I:APA91bGU4exsgxIvb3kj9VUqWg2IqcAPoY9j9PMEe3WfqnZ601tTmHOuNe1efUF6aH8T0RwVTqHfFG5hwAmv23AZ6sUPUXd9ulVq3z4qS0jwYx0amCx3apARR92WML1DlYUa4SV2WByA'
        token = device_token

        data = {
            'notification': {'title': 'رابط الموعد',
                             'body': '{0}'.format(self.jitsi_link),
                             "apns": {
                                 "payload": {
                                     "aps": {
                                         "content-available": True,
                                         "mutable-content": True,
                                     }
                                 }
                             },

                             },
            'to': token,
            'priority': 'high',
            "apns": {
                "payload": {
                    "aps": {
                        "content-available": True,
                        "mutable-content": True,
                    }
                }
            },

            "data": {
                "title_ar": 'رابط الموعد',
                "title_en": 'Caregiver Link',
                "body_ar": '{0}'.format(self.jitsi_link),
                "body_en": '{0}'.format(self.jitsi_link),
            },

        }

        url = 'https://fcm.googleapis.com/fcm/send'

        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'key={0}'.format(server_token)
        }

        response = requests.post(url=url, data=json.dumps(data), headers=headers, timeout=120)

    def set_to_assign_caregiver(self):
        # List of fields to check
        fields_to_check = [
            'is_patient_conscious', 'have_chronic_diseases', 'use_insulin_needles',
            'can_move_or_seated', 'is_laryngeal_cleft', 'eat_food_or_tube',
            'use_oxygen_inhaled_medications', 'have_any_catheter',
            'wounds_diabetic_bed_sores', 'wear_diapers'
        ]

        # Check if any of the fields is False
        for field in fields_to_check:
            if not getattr(self, field):
                field_name = dict(self.fields_get(allfields=fields_to_check))[field]['string']
                raise UserError(f"Cannot move to the next stage because '{field_name}' is not satisfied.")

        return self.write({'state': 'assign_caregiver'})

    """def set_to_active(self):
        if self.caregiver:
            self.create_caregiver()
        #if not self.attachment_ids:
            #raise ValidationError("Upload signed contract first")
        #if not self.pro_pending:
            #self.create_invoice(self.date)
    
        date = (fields.Datetime.now() + timedelta(hours=3)).date()
        self.starting_date = date
        self.ending_date = date + timedelta(days=self.duration)
        return self.write({'state': 'active'})"""

    def set_to_active(self):
        date = (fields.Datetime.now() + timedelta(hours=3)).date()
        if self.state == 'renew':
            date = self.create_date.date()
        self.starting_date = date
        ctx = {
            'form_view_ref': 'sm_caregiver.sm_caregiver_contracts_form_start_date_view',
            'from_wizard': True,
        }
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sm.caregiver.contracts',
            'view_mode': 'form',
            'target': 'new',
            'res_id': self.id,
            'context': ctx,
        }

    def back_to_active(self):
        self.write({"state": "active"})

    def activate(self):
        self.state = 'active'
        self.ending_date = self.starting_date + timedelta(days=self.duration - 1)
        self.activate_renew()

    def activate_renew(self):
        self.create_invoice(self.starting_date)

    def action_view_caregiver_contracts(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("sm_caregiver.sm_caregiver_contracts_action")
        action['domain'] = [('id', 'in', self.patient_id.caregiver_contract_ids.ids)]
        return action


    def reactivate(self):
        self.state = 'active'
        self.reactivation = True
        self.hold = False
        remaining_days = self.hold_reason_ids[-1].remaining_days if self.hold_reason_ids else 0
        self.ending_date = self.reactivation_date + timedelta(days=remaining_days - 1)
        self.env['sm.reactivation.reason'].sudo().create({
            'caregiver_contract_id': self.id,
            'name': self.reactivation_reason,
            'date': self.reactivation_date,
        })
        self.reactivation_reason = False

    def terminate(self):
        self.state = 'terminated'
        self.reactivation = False
        self.hold = False
        if self.move_ids.filtered(lambda l: l.move_type == 'out_invoice') and self.payment_made_through != 'pending' and not self.pro_pending:
            self.create_credit_note(self.termination_date)
        self.create_cancel_request()

    def set_to_hold(self):
        self.hold_reason = False
        self.hold_date = (fields.Datetime.now() + timedelta(hours=3)).date()
        ctx = {'form_view_ref': 'sm_caregiver.sm_caregiver_contracts_form_reason_view'}
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sm.caregiver.contracts',
            'view_mode': 'form',
            'target': 'new',
            'res_id': self.id,
            'context': ctx,
        }

    def set_to_reactivated_req(self):
        self.write({'state': 'reactivation_request'})

    def set_to_reactivated(self):
        self.reactivation_date = (fields.Datetime.now() + timedelta(hours=3)).date()
        # remaining_days = self.hold_reason_ids[-1].remaining_days if self.hold_reason_ids else 0
        # self.ending_date = self.reactivation_date + timedelta(days=remaining_days)
        # self.reactivation_reason = False
        ctx = {
            'form_view_ref': 'sm_caregiver.sm_caregiver_contracts_form_reactivate_reason_view',
        }
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sm.caregiver.contracts',
            'view_mode': 'form',
            'target': 'new',
            'res_id': self.id,
            'context': ctx,
        }

    def set_to_terminated(self):
        self.termination_date = (fields.Datetime.now() + timedelta(hours=3)).date()
        self.termination_reason = False
        ctx = {
            'form_view_ref': 'sm_caregiver.sm_caregiver_contracts_form_terminate_reason_view',
        }
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sm.caregiver.contracts',
            'view_mode': 'form',
            'target': 'new',
            'res_id': self.id,
            'context': ctx,
        }

    def compute_reminder_date(self):
        check_payment = self.search([('state', '=', 'active'), ('payment_date', '=', date.today())])
        if check_payment:
            for i in check_payment:
                i.write({
                    'payment_date': i.payment_date + timedelta(days=30)
                })
                i.notify()

    def notify(self):
        msg = "Caregiver contract reference [ %s ] complete a month" % (self.name)
        msg_vals = {"message": msg, "title": "Reminder caregiver contract", "sticky": True}
        admin_group_ids = [
            self.env.ref('oehealth.group_oeh_medical_manager').id,
            self.env.ref('smartmind_shifa.group_oeh_medical_operation_manager').id,
            self.env.ref('smartmind_shifa.group_oeh_medical_call_center').id
        ]
        for group_id in admin_group_ids:
            group_users = self.env['res.users'].search([('groups_id', 'in', group_id)])
            for user in group_users:
                user.notify_success(**msg_vals)


# class SmCaregiverPayment(models.Model):
#     _inherit = 'sm.shifa.requested.payments'
#
#     caregiver_contract_id = fields.Many2one('sm.caregiver.contracts', string="Caregiver Contract")
#

class SmCaregiverInvoice(models.Model):
    _inherit = 'account.move'

    caregiver_contract_id = fields.Many2one('sm.caregiver.contracts', string="Caregiver Contract")

    @api.onchange('partner_id')
    def onchange_partner_patient(self):
        patient = self.env['oeh.medical.patient'].sudo().search([
            ('partner_id','=',self.partner_id.id),
        ],limit=1)
        if patient:
            self.patient = patient.id
            self.id_number = patient.ssn


class HoldReason(models.Model):
    _name = 'sm.hold.reason'
    name = fields.Char('Reason')
    date = fields.Date()
    remaining_days = fields.Integer()
    caregiver_contract_id = fields.Many2one('sm.caregiver.contracts', string="Caregiver Contract")


class ReactivationReason(models.Model):
    _name = 'sm.reactivation.reason'
    name = fields.Char('Reason')
    date = fields.Date()
    remaining_days = fields.Integer()
    caregiver_contract_id = fields.Many2one('sm.caregiver.contracts', string="Caregiver Contract")


