from odoo import models, fields, api, _
from datetime import timedelta, datetime
from odoo.exceptions import UserError, ValidationError
import requests

class RequestedPayments(models.Model):
    _name = 'sm.shifa.requested.payments'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'sequence.mixin']
    _description = 'Requested Payments'

    REQUESTED_STATES = [
        ('Start', 'Start'),
        ('Send', 'Send'),
        ('Paid', 'Paid'),
        ('Done', 'Done'),
        ('Reject', 'Reject'),
        ('cancel', 'Cancelled'),
    ]
    PAY_TYPE = [
        ('hhc_appointment', 'HHC Appointment'),
        ('tele_appointment', 'Tele Appointment'),
        ('hvd_appointment', 'HVD Appointment'),
        ('phy_appointment', 'Phy Appointment'),
        ('pcr_appointment', 'PCR Appointment'),
        ('package', 'Package'),
        ('multipackage', 'Multi-Package'),
        ('instant','Instant')
    ]
    PAY_METHOD = [
        ('cash', 'Cash'),
        ('point_of_sale', 'Point of Sale'),
        ('bank_transfer', 'Bank Transfer'),
        ('mobile', 'Mobile App'),
        ('portal', 'Portal Link'),
    ]

    def _get_create_by(self):
        """Return default create by value"""
        req_pay_obj = self.env['hr.employee']
        # print(self.env.uid)
        domain = [('user_id', '=', self.env.uid)]
        user_ids = req_pay_obj.search(domain, limit=1)
        if user_ids:
            return user_ids.id or False
        else:
            return False

    name = fields.Char('Reference', index=True, copy=False)
    patient = fields.Many2one('oeh.medical.patient', string='Patient', help="Patient Name", required=True,
                              readonly=True, states={'Start': [('readonly', False)]})
    state = fields.Selection(REQUESTED_STATES, string='State', default=lambda *a: 'Start', readonly=True,tracking=True)
    date = fields.Date(string='Date', readonly=True, states={'Start': [('readonly', False)]})
    payment_amount = fields.Float(string='Payment Amount', required=True, readonly=True,
                                  states={'Cancel': [('readonly', True)]})
    payment_reference = fields.Char(string='Payment Reference', readonly=True,
                                    states={'Start': [('readonly', False)], 'Send': [('readonly', False)]})
    payment_document = fields.Binary(readonly=True,
                                     states={'Send': [('readonly', False)], 'Payed': [('readonly', False)]},
                                     string='Payment Document')
    details = fields.Text(string='Details', readonly=True, states={'Start': [('readonly', False)]})
    call_center_note = fields.Text(string='Call Center Comment', readonly=True
                                   , states={'Start': [('readonly', False)], 'Send': [('readonly', False)]})

    appointment_details_show = fields.Boolean()
    type = fields.Selection(PAY_TYPE, string="type", readonly=True, states={'Start': [('readonly', False)]})

    hhc_appointment = fields.Many2one('sm.shifa.hhc.appointment', string='HHC-App', readonly=True,
                                      states={'Start': [('readonly', False)]})

    date_hhc_appointment = fields.Date(string='Date', related="hhc_appointment.appointment_date_only", readonly=True,
                                       states={'Start': [('readonly', False)]})

    appointment = fields.Many2one('oeh.medical.appointment', string='Tele-App', readonly=True,
                                       domain="[('patient','=',patient)]",
                                       states={'Start': [('readonly', False)]})
    date_appointment = fields.Datetime(string='Date', related="appointment.appointment_date", readonly=True,
                                            states={'Start': [('readonly', False)]})

    hvd_appointment = fields.Many2one('sm.shifa.hvd.appointment', string='HVD-App', readonly=True,
                                      domain="[('patient','=',patient)]",
                                      states={'Start': [('readonly', False)]})
    date_hvd_appointment = fields.Datetime(string='Date', related="hvd_appointment.appointment_date", readonly=True,
                                           domain="[('patient','=',patient)]",
                                           states={'Start': [('readonly', False)]})
    phy_appointment = fields.Many2one('sm.shifa.physiotherapy.appointment', string='Phy-App', readonly=True,
                                      domain="[('patient','=',patient)]",
                                      states={'Start': [('readonly', False)]})
    date_phy_appointment = fields.Date(string='Date', related="phy_appointment.appointment_date_only", readonly=True,
                                       states={'Start': [('readonly', False)]})

    pcr_appointment = fields.Many2one('sm.shifa.pcr.appointment', string='PCR-App', readonly=True,
                                      domain="[('patient','=',patient)]",
                                      states={'Start': [('readonly', False)]})
    date_pcr_appointment = fields.Date(string='Date', related="pcr_appointment.appointment_date_only", readonly=True,
                                       states={'Start': [('readonly', False)]})
    create_by = fields.Many2one('hr.employee', string="Create By", default=_get_create_by, readonly=True,
                                states={'Start': [('readonly', False)]})
    deduction_amount = fields.Float(string="Deduction Amount", readonly=True,
                                    states={'Start': [('readonly', False)], 'Send': [('readonly', False)]})
    payment_method = fields.Selection(PAY_METHOD, readonly=True,
                                      states={'Start': [('readonly', False)], 'Send': [('readonly', False)]})
    payment_method_name = fields.Char(string="Payment Method Name")
    payment_note = fields.Char(string="Payment Note")
    memo = fields.Char(string="Ref#", compute="_display_name")
    date_tele_appointment = fields.Char() # temp field only. we will remove it latter.
    payment_id = fields.Many2one('account.payment', string='Payment #')
    active = fields.Boolean(default=True)

    package_id = fields.Many2one('sm.shifa.package.appointments', string='Package')
    package_date = fields.Date(string='Date')
    multi_package_id = fields.Many2one('sm.shifa.package.appointments.multi', string='Multi-Package')
    multi_package_date = fields.Date(string='Date')    
    instant_id = fields.Many2one('sm.shifa.instant.consultation','Consultation')
    instant_date = fields.Date(string='Date')
    journal_id = fields.Many2one('account.journal',string='Journal',domain="[('type','=','bank')]")


    def action_archive(self):
        for rec in self:
            if rec.state not in ['Done', 'Reject']:
                raise UserError(_("You can archive only if it done or reject requested payment"))
        return super().action_archive()

    @api.depends('payment_reference', 'payment_method_name')
    def _display_name(self):
        if self.payment_method_name and self.payment_reference:
            self.memo = self.payment_method_name +"/" + self.payment_reference
        else:
            self.memo = self.payment_reference
    def set_to_send(self):
        if self.payment_amount == 0.0:
            raise UserError(_("Please enter a valid payment amount"))
        if not self.date:
            self.date = datetime.now().date()
        return self.write({'state': 'Send'})

    def set_to_done(self):
        return self.write({'state': 'Done'})

    def set_to_reject(self):
        return self.write({'state': 'Reject'})

    def set_to_cancel(self):
        return self.write({'state': 'cancel'})

    def set_to_paid(self):
        if self.deduction_amount == 0.0:
            raise UserError(_("Please enter a valid deduction amount"))
        return self.write({'state': 'Paid'})

    # create account payment
    def create_account_payment(self):
        ic = self.env['ir.config_parameter'].sudo()
        journal_cash = ic.get_param('smartmind_odoo.journal_cash')
        journal_bank = ic.get_param('smartmind_odoo.journal_bank')
        journal_point_sale = ic.get_param('smartmind_odoo.journal_point_sale')
        journal_mobile = ic.get_param('smartmind_odoo.journal_mobile')
        journal_portal = ic.get_param('smartmind_odoo.journal_portal')
        journal = False
        if self.payment_method == 'cash':
            journal = journal_cash
        elif self.payment_method == 'bank_transfer':
            journal = journal_bank
            if self.journal_id:
                journal = self.journal_id
        elif self.payment_method == 'mobile':
            journal = journal_mobile
        elif self.payment_method == 'point_of_sale':
            journal = journal_point_sale
        elif self.payment_method == 'portal':
            journal = journal_portal
        else:
            journal = False
        if journal:
            payment = self.env['account.payment'].create({
            'payment_type' : 'inbound',
            'partner_type' : 'customer',
            'partner_id' : self.patient.partner_id.id,
            #'destination_account_id' : self.get_property_account_receivable_id(self.patient.id),
            'amount' : self.deduction_amount,
            'date' : self.date,
            'requested_payment' : self.id,
            'ref': self.memo,
            'journal_id': int(journal),
            })
            # payment is draft
            payment.action_post()
            self.payment_id = payment.id
        else:
            raise UserError(_(' you should add journal from settings first'))

    def open_account_payment(self):
        action = self.env['ir.actions.act_window']._for_xml_id('account.action_account_payments')
        action['domain'] = [('id', '=', self.payment_id.id)]
        action.update({'context': {}})
        return action
    @api.onchange('payment_amount')
    def _check_payment_amount(self):
        if self.payment_amount > 100000:
            raise ValidationError("invalid Payment Amount")

    @api.onchange('hhc_appointment')
    def _check_hhc_appointment(self):
        if self.hhc_appointment:
            self.hvd_appointment = None
            self.pcr_appointment = None
            self.phy_appointment = None
            self.appointment = None

    @api.onchange('hvd_appointment')
    def _check_hvd_appointment(self):
        if self.hvd_appointment:
            self.hhc_appointment = None
            self.pcr_appointment = None
            self.phy_appointment = None
            self.appointment = None

    @api.onchange('pcr_appointment')
    def _check_pcr_appointment(self):
        if self.pcr_appointment:
            self.hhc_appointment = None
            self.hvd_appointment = None
            self.phy_appointment = None
            self.appointment = None

    @api.onchange('phy_appointment')
    def _check_pcr_appointment(self):
        if self.phy_appointment:
            self.hhc_appointment = None
            self.hvd_appointment = None
            self.pcr_appointment = None
            self.appointment = None

    @api.onchange('appointment')
    def _check_pcr_appointment(self):
        if self.appointment:
            self.hhc_appointment = None
            self.hvd_appointment = None
            self.pcr_appointment = None
            self.phy_appointment = None

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('sm.shifa.requested.payments')
        # Create the payment request record
        record = super(RequestedPayments, self).create(vals)

        # Assign the created record ID to the corresponding appointment's pay_req_id
        if 'hhc_appointment' in vals:
            appointment = self.env['sm.shifa.hhc.appointment'].browse(vals['hhc_appointment'])
            appointment.pay_req_id = record.id
        if 'phy_appointment' in vals:
            appointment = self.env['sm.shifa.physiotherapy.appointment'].browse(vals['phy_appointment'])
            appointment.pay_req_id = record.id

        return record


    def set_to_pay(self):
        if self.deduction_amount == 0.0:
            raise UserError(_("Please enter a valid deduction amount"))
        self.create_account_payment()
        return self.write({'state': 'Done'})

    def generate_pay_link(self):
        url = "https://glob-care.com/api/payment-request/send-sms"
        data = {'id': str(self.id)}
        response = requests.request("POST", url, headers={}, data=data, files=[])
        #print(response.text)


    def get_property_account_receivable_id(self, patient_id):
        patient = self.env['oeh.medical.patient'].browse(patient_id)
        return patient.partner_id.property_account_receivable_id.id

    # def open_payment_form(self):
    #     return {
    #         'res_model': 'account.payment',
    #         'type': 'ir.actions.act_window',
    #         'view_type': 'form',
    #         'view_mode': 'form',
    #         'context': dict(
    #             self.env.context,
    #             default_payment_type='inbound',
    #             default_partner_type='customer',
    #             default_partner_id=self.patient.partner_id.id,
    #             default_destination_account_id=self.get_property_account_receivable_id(self.patient.id),
    #             default_amount=self.deduction_amount,
    #             default_date=self.date,
    #             default_ref=self.payment_reference,
    #             default_requested_payment=self.id,
    #             search_default_checks_to_send=1,
    #             # journal_id=self.id,
    #             # default_journal_id=self.id,
    #             # default_payment_type='outbound',
    #             # default_payment_method_id=check_method.id,
    #         )
    #     }

    #  send notification if payment method is from mobile app or portal link
    def notification(self):
        msg = "[ %s ] new payment has been successfully received" % (self.name)
        msg_vals = {"message": msg, "title": "Requested Payment", "sticky": True}
        admin_group_ids = [self.env.ref('oehealth.group_oeh_medical_manager').id,
                           self.env.ref('smartmind_shifa.group_oeh_medical_operation_manager').id,
                           self.env.ref('smartmind_shifa.group_oeh_medical_call_center').id]
        for group_id in admin_group_ids:
            group_users = self.env['res.users'].search([('groups_id', 'in', group_id)])
            for user in group_users:
                user.notify_success(**msg_vals)

class RequestedPaymentsInPayment(models.Model):
    _inherit = 'account.payment'

    requested_payment = fields.Many2one('sm.shifa.requested.payments', string="Requested Payment #")
