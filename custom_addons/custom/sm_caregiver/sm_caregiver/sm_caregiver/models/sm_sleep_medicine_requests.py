from odoo import models, fields, api, _
import uuid
from datetime import timedelta, datetime
from odoo.exceptions import UserError, ValidationError
import json
import requests
import logging

_logger = logging.getLogger(__name__)


class SmSleepMedicineRequest(models.Model):
    _name = 'sm.sleep.medicine.request'
    _description = 'Sleep Medicine Requests'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    STATE = [
        ('draft', 'Draft'),
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid'),
        ('evaluation', 'Evaluation'),
        ('scheduling', 'Scheduling'),
        ('cancel', 'Canceled'),
        ('create_appointment', 'Appointment Created'),
    ]

    YES_NO = [
        ('yes', 'Yes'),
        ('no', 'No'),
    ]

    # calculate vat
    @api.depends('ssn', 'service_price')
    def _calculate_vat(self):
        for rec in self:
            if rec.ssn and rec.ssn[0] == '2':
                rec.vat = (rec.service_price - rec.discount_val) * 0.15
            else:
                rec.vat = 0.0

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
    @api.depends('discount', 'discount_id', 'service_price')
    def _calculate_discount(self):
        for rec in self:
            if rec.discount_id:
                rec.discount_val = rec.service_price * (rec.discount_id.fixed_type / 100)
            else:
                rec.discount_val = rec.service_price * (rec.discount / 100)

    # calculate total amount of sleep request
    @api.depends('service_price', 'discount_val', 'vat')
    def _cal_net_payment(self):
        for rec in self:
            rec.amount_payable = rec.service_price - rec.discount_val + rec.vat

    # get discount percentage value from discount model
    @api.depends('discount_id')
    def _compute_discount_value(self):
        for rec in self:
            if rec.discount_id:
                rec.discount = rec.discount_id.fixed_type
            else:
                rec.discount = 0

    # get day of the week
    @api.depends('appointment_date')
    def _get_day(self):
        for rec in self:
            if rec.appointment_date:
                a = datetime.strptime(str(rec.appointment_date), "%Y-%m-%d")
                rec.day = str(a.strftime("%A"))
            else:
                rec.day = ''

    state = fields.Selection(STATE, string='State', readonly=False, default=lambda *a: 'draft')
    name = fields.Char('Reference', index=True, copy=False)

    # patient details
    patient_id = fields.Many2one('oeh.medical.patient', string='Patient', help="Patient Name", required=True,
                                 readonly=True,
                                 states={'draft': [('readonly', False)]}, tracking=True)
    nationality = fields.Selection([
        ('KSA', 'Saudi'),
        ('NON', 'Non-Saudi')
    ], related='patient_id.ksa_nationality', string="Nationality")
    house_location = fields.Char(string='House Location', readonly=True,
                                 states={'draft': [('readonly', False)]})
    house_number = fields.Char(string='House Number', readonly=True,
                               states={'draft': [('readonly', False)]})
    branch = fields.Selection([
        ('riyadh', 'Riyadh'),
        ('dammam', 'Dammam'),
        ('jeddah', 'Jeddah'),
    ], string="Branch", readonly=True, states={'draft': [('readonly', False)]})
    ssn = fields.Char(string='ID Number', related='patient_id.ssn')

    # service details
    date = fields.Date(string="Date", required=True, readonly=True,
                       states={'draft': [('readonly', False)]}, tracking=True)
    service_id = fields.Many2one('sm.shifa.service', string='Service', required=True,
                                 domain=[('service_type', '=', 'SM')], readonly=True,
                                 states={'draft': [('readonly', False)]}, tracking=True)
    service_price = fields.Float(string="Service Price", related='service_id.list_price', store=True)
    vat = fields.Float(string='VAT(+) 15%', compute=_calculate_vat)
    discount_id = fields.Many2one('sm.shifa.discounts', string='Discount Name',
                                  domain=[('state', '=', 'Active')], readonly=True,
                                  states={'draft': [('readonly', False)]}, tracking=True)
    discount = fields.Float(string='Discount %', compute=_compute_discount_value, store=True)
    discount_val = fields.Float(string='Discount', compute=_calculate_discount, store=True)
    amount_payable = fields.Float('Amount Payable', compute=_cal_net_payment)

    # other details
    pro_pending = fields.Boolean(string="Pro. Free Service", readonly=True,
                                 states={'draft': [('readonly', False)]})
    payment_made_through = fields.Selection([
        ('pending', 'Free Service'),
        ('mobile', 'Mobile App'),
        ('call_center', 'Call Center'),
        ('on_spot', 'On spot'),
    ], string="Pay. Made Thru.", required=True, readonly=True,
        states={'draft': [('readonly', False)], 'unpaid': [('readonly', False)]})
    mobile_payment_state = fields.Char(string='Mobile payment state', readonly=True)
    deduction_amount = fields.Float(string="Ded. Amount", readonly=True)
    payment_reference = fields.Char(string='Payment Ref. #', readonly=True)
    payment_method_name = fields.Char(string="Payment Method Name", readonly=True)

    # questionnaire details
    height = fields.Float(string='Height (cm)', readonly=False, states={'create_appointment': [('readonly', True)]})
    weight = fields.Float(string='Weight (kg)', readonly=False, states={'create_appointment': [('readonly', True)]})
    bmi = fields.Float(compute=_compute_bmi, string='BMI', store=True)
    is_snore = fields.Selection(YES_NO, readonly=False, states={'create_appointment': [('readonly', True)]})
    has_not_feeling_slept = fields.Selection(YES_NO, readonly=False,
                                             states={'create_appointment': [('readonly', True)]})
    is_stop_breathing = fields.Selection(YES_NO, readonly=False, states={'create_appointment': [('readonly', True)]})
    is_high_blood_pressure = fields.Selection(YES_NO, readonly=False,
                                              states={'create_appointment': [('readonly', True)]})
    is_male = fields.Selection(YES_NO, readonly=False, states={'create_appointment': [('readonly', True)]})
    is_50years_older = fields.Selection(YES_NO, readonly=False, states={'create_appointment': [('readonly', True)]})
    comment = fields.Char(String="Comment", readonly=False, states={'create_appointment': [('readonly', True)]})

    # evaluation
    is_bmi_greater_28 = fields.Selection(YES_NO, readonly=False, states={'create_appointment': [('readonly', True)]})
    is_neck_circumference = fields.Selection(YES_NO, readonly=False,
                                             states={'create_appointment': [('readonly', True)]})
    jitsi_link = fields.Text()  # mobile jitsi link
    invitation_text_jitsi = fields.Html(string='Invitation Link', readonly=True)

    # appointment details
    appointment_date = fields.Date(readonly=False, states={'create_appointment': [('readonly', True)]})
    day = fields.Char(string='Day', compute=_get_day)
    appointment_time = fields.Float(string='Time (HH:MM)', store=True, compute='get_timeslot')
    period = fields.Selection([('morning', 'Morning'), ('afternoon', 'Afternoon'), ('evening', 'Evening')],
                              string='Period', readonly=False,
                              states={'create_appointment': [('readonly', True)]})
    nurse_id = fields.Many2one('oeh.medical.physician', string='Nurse', domain=[('role_type', 'in', ('HN', 'HHCN'))],
                               readonly=False, states={'create_appointment': [('readonly', True)]})
    nurse_timeslot_id = fields.Many2one('sm.shifa.physician.schedule.timeslot', string='Timeslot', copy=False,
                                        domain="[('physician_id', '=', nurse_id), ('date', '=', appointment_date), ('is_available', '=', True)]"
                                        , readonly=False, states={'create_appointment': [('readonly', True)]})
    physician_id = fields.Many2one('oeh.medical.physician', string='Physician',
                                   domain=[('role_type', 'in', ('HHCD', 'HD'))], readonly=False,
                                   states={'create_appointment': [('readonly', True)]})
    timeslot_physician_id = fields.Many2one('sm.shifa.physician.schedule.timeslot', string='Timeslot', copy=False,
                                            domain="[('physician_id', '=', physician_id), ('date', '=', appointment_date), ('is_available', '=', True)]"
                                            , readonly=False, states={'create_appointment': [('readonly', True)]})
    # accounting and payment request
    request_payment_id = fields.Many2one('sm.shifa.requested.payments', string='Payment Request#', copy=False,
                                         readonly=True)
    move_id = fields.Many2one('account.move', string='account move', ondelete='restrict', readonly=True, copy=False)
    hhc_appointment_id = fields.Many2one('sm.shifa.hhc.appointment', string="HHC Appointment #")
    refund_req = fields.Many2one('sm.shifa.cancellation.refund', string='Refund Request')
    active = fields.Boolean(default=True)
    move_ids = fields.One2many('account.move', 'sleep_medicine_id', string='account move', ondelete='restrict',
                               readonly=True, copy=False)

    # get charge service
    def _get_miscellaneous_id(self):
        miscellaneous_obj = self.env['sm.shifa.miscellaneous.charge.service']
        domain = [('code', '=', 'HHC-HVF')]
        hvf = miscellaneous_obj.search(domain, limit=1)
        result = {
            "id": hvf.id or False,
            "home_visit_fee": hvf.list_price or 0,
        }

        return result

    # create HHC appointment record
    def create_hhc_appointment(self, sch_date, day):
        model_name = 'sm.shifa.hhc.appointment'
        values = {
            'patient': self.patient_id.id,
            'ssn': self.ssn,
            'appointment_date_only': sch_date,
            'appointment_day': day,
            'period': self.period,
            'branch': self.branch,
            'pro_pending': self.pro_pending,
            'service_type_choice': 'main',
            'service': self.service_id.id,
            'service_price': self.service_price,
            'miscellaneous_charge': self._get_miscellaneous_id()['id'],
            'miscellaneous_price': self._get_miscellaneous_id()['home_visit_fee'],
            # 'payment_made_through': self.payment_made_through,
            'payment_made_through': 'sleepmedicine',
            'nurse': self.nurse_id.id,
            'doctor': self.physician_id.id,
            'timeslot': self.nurse_timeslot_id.id,
            'timeslot_doctor': self.timeslot_physician_id.id,
            'appointment_time': self.appointment_time,
            'pay_req_id': self.request_payment_id.id,
            'move_id': self.move_id.id,
            'discount_name': self.discount_id.id,
            'state': 'team',
        }
        hhc = self.env[model_name].sudo().create(values)
        self.hhc_appointment_id = hhc.id

    # timeslot for nurse and physician should be same
    @api.onchange('timeslot_physician_id', 'nurse_timeslot_id')
    def _match_timeslot(self):
        for rec in self:
            if rec.timeslot_physician_id and rec.timeslot_physician_id:
                if rec.nurse_timeslot_id.available_time != rec.timeslot_physician_id.available_time:
                    raise ValidationError("The timeslot must be the Same")

    # create payment request
    def create_payment_request(self):
        pay_values = {
            'patient': self.patient_id.id,
            'type': 'sleep_medicine_request',
            'details': "Sleep Medicine" + self.name,
            'date': self.date,
            'payment_method': 'point_of_sale',
            'state': 'Send',
            'payment_amount': self.amount_payable,
            'sleep_medicine_request': self.id,
        }
        pay_req = self.env['sm.shifa.requested.payments'].create(pay_values)
        pay_req.set_to_send()
        self.request_payment_id = pay_req.id

    # open payment record
    def open_payment_view(self):
        payment_request = self.env['sm.shifa.requested.payments'].sudo().search([
            ('sleep_medicine_request','=',self.id)
        ])
        payment_request += self.request_payment_id
        action = self.env['ir.actions.act_window']._for_xml_id(
            'smartmind_shifa_extra.sm_shifa_requested_payments_action')
        action['domain'] = [('id', 'in', payment_request.ids)]
        action.update({'context': {}})
        return action

    # open appointment record
    def open_appointment_view(self):
        action = self.env['ir.actions.act_window']._for_xml_id(
            'smartmind_shifa.sm_hhc_appointment_action_tree')
        action['domain'] = [('id', '=', self.hhc_appointment_id.id)]
        action.update({'context': {}})
        return action

    # constrain for timeslot
    @api.depends('nurse_timeslot_id')
    def get_timeslot(self):
        if self.nurse_timeslot_id:
            hm = self.nurse_timeslot_id.available_time.split(':')
            sch_time = int(hm[0]) + int(hm[1]) / 60
            self.appointment_time = sch_time

    # create jitsi link
    def create_jitsi_meeting(self):
        server_url = self.env['ir.config_parameter'].sudo().get_param('oehealth_jitsi.video_call_server_url')
        model = self.env['sm.sleep.medicine.request'].browse(int(self.id))
        meeting_link = server_url + '/' + self._get_meeting_code()
        invitation_text = _(
            "<a href='%s' target='_blank' class='btn btn-primary btn-lg' style='font-size:bold; padding: 10px;'><span style='color:#000;'>Join Meeting</span></a>") % meeting_link
        model.write({
            'invitation_text_jitsi': invitation_text,
            'jitsi_link': meeting_link,
        })

    def _get_meeting_code(self):
        return str(uuid.uuid4()).replace('-', '')

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
                'price_unit': self.service_price,
                'tax_ids': tax,
                'discount': self.discount,
                'sequence': 1,
            }))
        return invoice_lines

    def create_invoice(self):
        if self.branch == 'riyadh':
            analytical_account_id = 2
        elif self.branch == 'dammam':
            analytical_account_id = 3
        invoice_lines = self.get_invoice_lines()
        #default_journal = self._get_default_journal()
        default_journal = self.env['account.journal'].sudo().search([
            ('type','=','sale'),
            ('analytic_account_id','=',analytical_account_id),
            ('company_id','=',self.env.user.company_id.id),
        ],limit=1)   
        # Create Invoice

        if not self.move_id:
            vals = {
                'move_type': 'out_invoice',
                'journal_id': default_journal.id,
                'partner_id': self.patient_id.partner_id.id,
                'analytic_account_id': analytical_account_id,
                'patient': self.patient_id.id,
                'invoice_date': datetime.now().date(),
                'date': datetime.now().date(),
                'ref': "Sleep Medicine",
                'invoice_line_ids': invoice_lines,
                'sleep_medicine_id': self.id,
            }
            invoice = self.env['account.move'].sudo().create(vals)
            invoice.action_post()
            self.move_id = invoice

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
    #         if record.payment_made_through in restricted_values:
    #             raise ValidationError(
    #                 "You are not allowed to save this type of payment method. Please select another value.")

    """def open_invoice_view(self):
        action = self.env['ir.actions.act_window']._for_xml_id('account.action_move_out_invoice_type')
        action['domain'] = [('id', '=', self.move_id.id)]
        action.update({'context': {}})
        return action"""

    def open_invoice_view(self):
        action = self.env['ir.actions.act_window']._for_xml_id('account.action_move_out_invoice_type')
        action['domain'] = ['|', ('id', 'in', self.move_ids.ids), ('id', '=', self.move_id.id)]
        action.update({'context': {}})
        return action

    def unlink(self):
        for rec in self:
            if rec.state != 'cancel':
                raise UserError(_("You can delete only if it cancelled Requests"))
        return super().unlink()

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('sm.sleep.medicine.request') or '/'
        if vals['payment_made_through'] == 'call_center':
            vals['state'] = 'unpaid'
            res = super(SmSleepMedicineRequest, self).create(vals)
            res.create_payment_request()
        elif vals['payment_made_through'] == 'pending':
            res = super(SmSleepMedicineRequest, self).create(vals)
        elif vals['payment_made_through'] == 'on_spot':
            vals['state'] = 'evaluation'
            res = super(SmSleepMedicineRequest, self).create(vals)
            res.create_payment_request()
            res.create_jitsi_meeting()
        else:
            vals['state'] = 'unpaid'
            res = super(SmSleepMedicineRequest, self).create(vals)
        return res

    def check_paid(self):

        if self.request_payment_id and self.request_payment_id.state not in ['Paid', 'Done'] and not self.pro_pending:
            raise UserError("You cannot move to the next action until the payment is paid or processed!")
        self.create_jitsi_meeting()
        return self.write({'state': 'evaluation'})

    def set_to_evaluation(self):
        self.create_jitsi_meeting()
        return self.write({'state': 'evaluation'})

    def continue_action(self):
        if not self.pro_pending:
            raise UserError("Action is restricted until admission is approved pending.")
        self.create_jitsi_meeting()
        return self.write({'state': 'evaluation'})

    def create_cancel_request(self):
        pay_values = {
            # 'patient': self.patient_id.id,
            'patient': self.patient_id.id,
            'state': 'Processed',
            'type': 'sleep_medicine_request',
            'sleep_medicine_request': self.id,
            'payment_request_id': self.request_payment_id.id if self.request_payment_id else False,
        }
        refund_req = self.env['sm.shifa.cancellation.refund'].create(pay_values)
        self.refund_req = refund_req.id

    def get_credit_note_lines(self):
        invoice_lines = []
        if self.patient_id.ksa_nationality == 'NON':
            company = self.env.user.company_id
            tax = company.account_sale_tax_id
        else:
            tax = False

        invoice_lines.append(
            (0, 0, {
                'product_id': self.service_id.product_id.id,
                'price_unit': self.service_price,
                'tax_ids': tax,
                'discount': self.discount,
                'sequence': 1,
            }))
        return invoice_lines

    def create_credit_note(self):
        invoice_lines = self.get_credit_note_lines()
        default_journal = self._get_default_journal()
        # Create Invoice
        receivable_line = False
        vals = {
            'move_type': 'out_refund',
            'journal_id': default_journal.id,
            'partner_id': self.patient_id.partner_id.id,
            'analytic_account_id': self.env.user.analytic_account_id.id,
            'patient': self.patient_id.id,
            'invoice_date': datetime.now().date(),
            'date': datetime.now().date(),
            'ref': "Sleep Medicine",
            'invoice_line_ids': invoice_lines,
            'sleep_medicine_id': self.id,
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

        return credit_note

    def set_to_cancelled(self):
        if self.move_id.state == 'posted' and self.move_id.move_type == 'out_invoice':
            credit_note = self.create_credit_note()
        self.create_cancel_request()
        if self.hhc_appointment_id:
            if self.hhc_appointment_id.state in ['in_progress', 'visit_done']:
                raise UserError("You cannot cancel the appointment in case status is in progress or visit done!")
            self.hhc_appointment_id.active_timeslot()
            self.hhc_appointment_id.write({"state": "canceled"})
            self.hhc_appointment_id.credit_note_id = credit_note.id if credit_note else False
            self.hhc_appointment_id.refund_request_id = self.refund_req.id if self.refund_req else False
        return self.write({'state': 'cancel'})

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
                             # "apple": {
                             #     "image": self.get_image_url('image', 'sm.app.notification', str(self.id))},
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
                "title_en": 'Appointment Link',
                "body_ar": '{0}'.format(self.jitsi_link),
                "body_en": '{0}'.format(self.jitsi_link),
                # "image": self.get_image_url('image', 'sm.app.notification', str(self.id))
            },

        }

        url = 'https://fcm.googleapis.com/fcm/send'

        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'key={0}'.format(server_token)
        }

        response = requests.post(url=url, data=json.dumps(data), headers=headers, timeout=120)

    def set_to_scheduling(self):
        fields_to_check = [
            'is_snore', 'has_not_feeling_slept', 'is_stop_breathing',
            'is_high_blood_pressure', 'is_male', 'is_50years_older'
        ]

        # Check if any of the fields is False
        for field in fields_to_check:
            if not getattr(self, field):
                field_name = dict(self.fields_get(allfields=fields_to_check))[field]['string']
                raise UserError(f"Cannot move to the next stage because '{field_name}' is not satisfied.")
        if not self.pro_pending:
            self.create_invoice()
        return self.write({'state': 'scheduling'})

    def create_appointment(self):
        self.create_hhc_appointment(self.appointment_date, self.day)
        return self.write({'state': 'create_appointment'})

    def open_payment_request(self):
        self.ensure_one()
        ctx = {
            'form_view_ref': 'smartmind_shifa_extra.view_shifa_requested_payments_form',
            'default_patient': self.patient_id.id,
            'default_type': 'sleep_medicine_request',
            'default_sleep_medicine_request': self.id,
            'default_date_sleep_medicine_request': self.date,
        }
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sm.shifa.requested.payments',
            'view_mode': 'form',
            'target': 'new',
            'context': ctx,
        }


class SmCaregiverInvoice(models.Model):
    _inherit = 'account.move'

    sleep_medicine_id = fields.Many2one('sm.sleep.medicine.request')
