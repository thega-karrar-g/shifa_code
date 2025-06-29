import base64
import datetime
import logging
import uuid
from datetime import datetime
from datetime import timedelta
import json
import requests
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class InstantConsultation(models.Model):
    _name = 'sm.shifa.instant.consultation'
    _description = 'Instant Consultation'

    Instant_STATE = [
        ('waiting', 'Waiting'),
        ('approved', 'Approved'),
        ('ready', 'Ready'),
        ('in_process', 'In Process'),
        ('evaluation', 'Evaluation'),
        ('completed', 'Completed'),
        ('dr_canceled', 'Cancelled by Dr'),
        ('canceled', 'Canceled'),
    ]

    NATIONALITY_STATE = [
        ('KSA', 'Saudi'),
        ('NON', 'Non-Saudi')
    ]

    def _get_physician(self):
        """Return default physician value"""
        therapist_obj = self.env['oeh.medical.physician']
        domain = [('oeh_user_id', '=', self.env.uid)]
        user_ids = therapist_obj.search(domain,limit=1)
        # print(user_ids)
        if user_ids:
            return user_ids.id or False
        else:
            return False

    def _get_current_user(self):
        self.user_sign = self.env.user

        # getting default bank id from bank accounts

    # @api.model
    @api.onchange('pharmacy_chain')
    def _set_pharmacy_chain_discount(self):
        self.discount = self.pharmacy_chain.discount

    @api.onchange('discount')
    def _compute_percent_from_discount(self):
        for rec in self:
            value = (rec.discount / rec.price) * 100
            rec.discount_percent = value

    @api.onchange('patient')
    def _set_service_price(self):
        instance = self.env['sm.shifa.instant.consultancy.charge'].search([('code', '=', 'ICP')], limit=1)
        self.price = instance.charge

    @api.depends('price', 'discount', 'tax')
    def _compute_amount_payable(self):
        for rec in self:
            if rec.price > 0 and rec.discount >= 0:
                rec.amount_payable = rec.price - rec.discount + rec.tax
            else:
                rec.amount_payable = rec.price + rec.tax

    @api.depends('price', 'discount')
    def _compute_pri_dis(self):
        for rec in self:
            if rec.price > 0 and rec.discount >= 0:
                rec.amount_pri_dis = (rec.price - rec.discount)

    @api.depends('amount_pri_dis', 'ksa_nationality')
    def _set_tax_value(self):
        for rec in self:
            percent = (rec.amount_pri_dis * 0.15)
            if rec.ksa_nationality == 'NON':
                rec.tax = percent
            else:
                rec.tax = 0

    def _get_pdf_link(self):
        link = ""
        config_obj = self.env['ir.config_parameter'].get_param('web.base.url')
        attachment_url = config_obj + "/web/attachments/token/"
        # print("URL", str(attachment_url))
        attach_name = self.env['ir.attachment'].search(
            ['|', ('name', '=', self.name + '.pdf'), ('res_model', '=', "sm.shifa.instant.consultation")])
        # print("attach name: ", str(attach_name))
        for att_obj in attach_name:
            if att_obj.name == str(self.name) + ".pdf":
                link = attachment_url + str(att_obj.access_token)
        return link

    # calculate approved duration
    @api.depends('approved_date', 'ready_date')
    def _approved_duration(self):
        for r in self:
            if r.ready_date and r.approved_date:
                duration_time = str(r.ready_date - r.approved_date)
                r.approved_duration = duration_time.split('.')[0]
            else:
                r.approved_duration = "0"
            return r.approved_duration

    # calculate waiting duration
    @api.depends('start_date', 'ready_date')
    def _waiting_duration(self):
        for r in self:
            if r.ready_date and r.start_date:
                duration_time = str(r.start_date - r.ready_date)
                r.waiting_duration = duration_time.split('.')[0]
                return r.waiting_duration
            else:
                r.waiting_duration = "0"
                return r.waiting_duration

    # calculate cansultation duration
    @api.depends('start_date', 'evaluation_date')
    def _cansultation_duration(self):
        for r in self:
            if r.evaluation_date and r.start_date:
                duration_time = str(r.evaluation_date - r.start_date)
                r.cansultation_duration = duration_time.split('.')[0]
                return r.cansultation_duration
            else:
                r.cansultation_duration = "0"
                return r.cansultation_duration

    name = fields.Char('Reference', index=True, copy=False)
    state = fields.Selection(Instant_STATE, string='State', readonly=True, default=lambda *a: 'waiting')
    # time_counter_show = fields.Boolean()
    date = fields.Datetime(default=lambda *a: datetime.now(), readonly=True)
    approved_date = fields.Datetime(readonly=True)
    ready_date = fields.Datetime(readonly=True)
    start_date = fields.Datetime(readonly=True)
    evaluation_date = fields.Datetime(readonly=True)
    time_id = fields.Many2one('sm.shifa.time.counters')

    patient = fields.Many2one('oeh.medical.patient', string='Patient', required=True, readonly=True,
                              states={'waiting': [('readonly', False)]})
    dob = fields.Date(string='Date of Birth', related='patient.dob', readonly=True,
                      states={'waiting': [('readonly', False)]})
    patient_id = fields.Integer(related='patient.id')
    marital_status = fields.Selection(string='Marital Status', related='patient.marital_status')
    gender = fields.Selection(string='Sex', related='patient.sex', readonly=True,
                              states={'waiting': [('readonly', False)]})
    blood_type = fields.Selection(string='Blood Type', related='patient.blood_type')
    rh = fields.Selection(string='Rh', related='patient.rh')
    ssn = fields.Char(string='ID Number', readonly=True,
                      states={'waiting': [('readonly', False)]}, related='patient.ssn')
    mobile = fields.Char(string='Mobile', readonly=True,
                         states={'waiting': [('readonly', False)]}, related='patient.mobile')
    age = fields.Char(string='Age', readonly=True,
                      states={'waiting': [('readonly', False)]}, related='patient.age')
    nationality = fields.Char(string='Nationality', readonly=True,
                              states={'waiting': [('readonly', False)]}, related='patient.nationality')
    patient_weight = fields.Float(string='Weight(kg)', readonly=True,
                                  states={'waiting': [('readonly', False)]}, related='patient.weight')

    ksa_nationality = fields.Selection(NATIONALITY_STATE, related='patient.ksa_nationality', readonly=True,
                                       states={'waiting': [('readonly', False)]})
    pharmacy_chain = fields.Many2one('sm.shifa.pharmacy.chain', domain=[('state', '=', 'Active')],
                                     readonly=True, states={'waiting': [('readonly', False)]})
    pharmacy = fields.Many2one('sm.shifa.pharmacies', string='Pharmacy', readonly=False,
                               states={'send': [('readonly', True)]})
    pharmacist = fields.Many2one('sm.shifa.pharmacist', string='Pharmacist', domain="[('pharmacy', '=', pharmacy)]",
                                 readonly=False, states={'send': [('readonly', True)]})
    deduction_amount = fields.Float(string="Ded. Amount", readonly=True)

    price = fields.Integer(string='Service Price', readonly=True)
    discount = fields.Integer(string='Discount', readonly=True)
    discount_percent = fields.Float(string='Discount %', readonly=True, compute='_compute_percent_from_discount')
    tax = fields.Float('Vat(+) 15%', compute='_set_tax_value')
    amount_payable = fields.Float('Amount Payable', compute='_compute_amount_payable', store=True)
    amount_pri_dis = fields.Float('Amounts', compute='_compute_pri_dis', store=True)

    doctor = fields.Many2one('oeh.medical.physician', domain=[('active', '=', True)],
                             readonly=True, states={'waiting': [('readonly', False)],
                                                    'in_process': [('readonly', False)],
                                                    'approved': [('readonly', False)]
                                                    }, default=_get_physician)

    insurance = fields.Many2one('sm.shifa.insurance', string='Insurance', help="Company Name",
                                domain=[('state', '=', 'Active')],
                                readonly=True, states={'approved': [('readonly', False)]})
    payment_type = fields.Char(string='Payment Type', readonly=True, states={'approved': [('readonly', False)]})
    payment_reference = fields.Char(string='Payment Reference #', readonly=True,
                                    states={'approved': [('readonly', False)]})
    order_id = fields.Many2one('sale.order', string='Sale Order #', ondelete='restrict', copy=False)
    move_id = fields.Many2one('account.move', string='Invoice #', ondelete='restrict', copy=False)
    bill_id = fields.Many2one('account.move', string='Bill #', ondelete='restrict', copy=False)
    evaluation = fields.Selection([
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
    ], readonly=False, states={'completed': [('readonly', True)], 'canceled': [('readonly', True)],
                               'dr_canceled': [('readonly', True)]})

    # invitation_link = fields.Char(string='Link', readonly=True,
    #                                 states={'ready': [('readonly', False)]})

    chief_complaint = fields.Text(readonly=True,
                                  states={'ready': [('readonly', False)], 'in_process': [('readonly', False)]})
    history = fields.Text(readonly=True,
                          states={'ready': [('readonly', False)], 'in_process': [('readonly', False)]})

    diagnosis = fields.Many2one('oeh.medical.pathology', readonly=True,
                                states={'ready': [('readonly', False)], 'in_process': [('readonly', False)]})
    diagnosis_yes_no = fields.Boolean(readonly=True,
                                      states={'ready': [('readonly', False)], 'in_process': [('readonly', False)]})
    diagnosis_add2 = fields.Many2one('oeh.medical.pathology', readonly=True,
                                     states={'ready': [('readonly', False)], 'in_process': [('readonly', False)]})
    diagnosis_yes_no_2 = fields.Boolean(readonly=True,
                                        states={'ready': [('readonly', False)], 'in_process': [('readonly', False)]})
    diagnosis_add3 = fields.Many2one('oeh.medical.pathology', readonly=True,
                                     states={'ready': [('readonly', False)], 'in_process': [('readonly', False)]})

    drug_allergy = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
        ('not_know', 'Not know'),
    ], readonly=False,
        states={'waiting': [('readonly', True)], 'approved': [('readonly', True)], 'completed': [('readonly', True)],
                'canceled': [('readonly', True)], 'dr_canceled': [('readonly', True)]},
    )  # , store=True, related='patient.has_drug_allergy'
    drug_allergy_text = fields.Char(readonly=False,
                                    states={'waiting': [('readonly', True)], 'approved': [('readonly', True)],
                                            'completed': [('readonly', True)], 'canceled': [('readonly', True)],
                                            'dr_canceled': [('readonly', True)]},
                                    )  # , store=True , related='patient.drug_allergy_content'
    # in_process ready
    prescription_line = fields.One2many('sm.shifa.prescription.line', 'prescription_extra_ids',
                                        readonly=True,
                                        states={'ready': [('readonly', False)], 'in_process': [('readonly', False)]})

    jitsi_link = fields.Text()  # mobile jitsi link
    invitation_text_jitsi = fields.Html(string='Invitation Link', readonly=True)

    user_sign = fields.Many2one('res.users', compute='_get_current_user')

    active = fields.Boolean('Active', default=True)

    user_id = fields.Many2one('res.users', string='send user', index=True, tracking=2,
                              default=lambda self: self.env.user)
    link = fields.Char(readonly=True)
    PHY_DAY = [
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
    ]
    appointment_day = fields.Selection(PHY_DAY, string='Day', required=False)
    day = fields.Char(string='Day')

    lab_test_ids = fields.One2many('sm.shifa.lab.request', 'hvd_appointment', string='Lab Request')

    # vital_signs_show = fields.Boolean()
    weight = fields.Float('Weight(kg)', readonly=False,
                          states={'completed': [('readonly', True)], 'canceled': [('readonly', True)],
                                  'dr_canceled': [('readonly', True)]})
    heart_rate = fields.Integer('Heart Rate(bpm)', readonly=False,
                                states={'completed': [('readonly', True)], 'canceled': [('readonly', True)],
                                        'dr_canceled': [('readonly', True)]})
    o2_saturation = fields.Float('O2 Saturation(%)', readonly=False,
                                 states={'completed': [('readonly', True)],
                                         'canceled': [('readonly', True)],
                                         'dr_canceled': [('readonly', True)]})
    blood_sugar = fields.Float('Blood Sugar(mg/dl)', readonly=False,
                               states={'completed': [('readonly', True)], 'canceled': [('readonly', True)],
                                       'dr_canceled': [('readonly', True)]})
    blood_pressure_s = fields.Integer('Blood Pressure(S/D)', readonly=False,
                                      states={'completed': [('readonly', True)], 'canceled': [('readonly', True)],
                                              'dr_canceled': [('readonly', True)]})
    blood_pressure_d = fields.Integer(readonly=False,
                                      states={'completed': [('readonly', True)], 'canceled': [('readonly', True)],
                                              'dr_canceled': [('readonly', True)]})
    respiration = fields.Integer('Respiration(bpm)', readonly=False,
                                 states={'completed': [('readonly', True)], 'canceled': [('readonly', True)],
                                         'dr_canceled': [('readonly', True)]})
    temperature = fields.Integer('Temperature(C)', readonly=False,
                                 states={'completed': [('readonly', True)], 'canceled': [('readonly', True)],
                                         'dr_canceled': [('readonly', True)]})
    recommendations = fields.Text(readonly=False,
                                  states={'completed': [('readonly', True)], 'canceled': [('readonly', True)],
                                          'dr_canceled': [('readonly', True)]})
    other_prescription_1 = fields.Char(readonly=False,
                                       states={'completed': [('readonly', True)], 'canceled': [('readonly', True)]})
    other_prescription_1_done = fields.Boolean('it was dispensed', readonly=False,
                                               states={'completed': [('readonly', True)],
                                                       'canceled': [('readonly', True)]})
    other_prescription_2 = fields.Char(readonly=False,
                                       states={'completed': [('readonly', True)], 'canceled': [('readonly', True)]})
    other_prescription_2_done = fields.Boolean('it was dispensed', readonly=False,
                                               states={'completed': [('readonly', True)],
                                                       'canceled': [('readonly', True)]})
    other_prescription_3 = fields.Char(readonly=False,
                                       states={'completed': [('readonly', True)], 'canceled': [('readonly', True)]})
    other_prescription_3_done = fields.Boolean('it was dispensed', readonly=False,
                                               states={'completed': [('readonly', True)],
                                                       'canceled': [('readonly', True)]})
    done = fields.Boolean('Done')
    dr_comment = fields.Text(string="Comment", states={'dr_canceled': [('readonly', True)]})

    # consultancy requested by patient
    cunsultancy_requested = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                                             string="Consultancy Requested by Patient",
                                             readonly=False,
                                             states={'completed': [('readonly', True)],
                                                     'canceled': [('readonly', True)]})
    cunsultancy_id = fields.Char(string="ID", readonly=False,
                                 states={'completed': [('readonly', True)],
                                         'canceled': [('readonly', True)]})
    cunsultancy_name = fields.Char(string="Name", readonly=False,
                                   states={'completed': [('readonly', True)],
                                           'canceled': [('readonly', True)]})
    cunsultancy_age = fields.Char(string="Age", readonly=False,
                                  states={'completed': [('readonly', True)],
                                          'canceled': [('readonly', True)]})
    cunsultancy_sex = fields.Char(string="Sex", readonly=False,
                                  states={'completed': [('readonly', True)],
                                          'canceled': [('readonly', True)]})

    approved_duration = fields.Char(string="Approved Duration", compute=_approved_duration, default="0")
    waiting_duration = fields.Char(string="Waiting Duration", compute=_waiting_duration, default="0")
    cansultation_duration = fields.Char(string="Consultation Duration", compute=_cansultation_duration, default="0")
    payment_method_name = fields.Char(string="Payment Method Name", readonly=True)
    credit_note_id = fields.Many2one('account.move', 'Credit Note', copy=False)
    refund_request_id = fields.Many2one('sm.shifa.cancellation.refund', string='Refund Request#', copy=False,
                                        readonly=True)
    pay_req_id = fields.Many2one('sm.shifa.requested.payments', string='Payment Request#', copy=False, readonly=True)

    @api.onchange('date')
    def _onchange_date(self):
        if self.date:
            date = str(self.date)
            a = datetime.strptime(date[:10], "%Y-%m-%d")
            self.day = str(a.strftime("%A"))
            #print(self.day)
            self.appointment_day = self.day

    def generate_link(self):
        self.state = 'completed'
        self.link = self._get_pdf_link()

    def _reset_token(self):
        prescriptions = self.search([
            ('state', 'in', ['completed']),

        ])
        if prescriptions:
            for pres in prescriptions:
                if pres.state == "completed":
                    pres.generate_link()

    def set_to_approved(self):
        payment_id = self.create_requested_payment('Send', 'cash')
        return self.write({'state': 'approved', 'approved_date': datetime.now()})

    # def _create_date(self):
    #     return self.write({'date': datetime.datetime.now()})

    def set_to_ready(self):
        self.create_jitsi_meeting()
        if not self.move_id:
            self.create_invoice()
        return self.write({'state': 'ready', 'ready_date': datetime.now()})

    def open_invoice_view(self):
        action = self.env['ir.actions.act_window']._for_xml_id('account.action_move_out_invoice_type')
        # Collect moves in a list
        moves = [self.move_id.id]

        if self.credit_note_id:
            moves.append(self.credit_note_id.id)
        # Ensure moves is a list
        action['domain'] = [('id', 'in', moves)]
        action.update({'context': {}})
        return action


    def open_vendor_bill(self):
        action = self.env['ir.actions.act_window']._for_xml_id('account.action_move_in_invoice_type')
        action['domain'] = [('id', '=', self.bill_id.id)]
        action.update({'context': {}})
        return action

    # get default journal to invoice
    def _get_default_journal(self):
        journal = self.env['account.journal'].search([('type', '=', 'sale')], limit=1)
        return journal

    # get the service invoice line
    def get_invoice_lines(self):
        invoice_lines = []
        if self.patient.ksa_nationality == 'NON':
            company = self.env.user.company_id
            tax = company.account_sale_tax_id
        else:
            tax = False
        for line in self:
            sequence = 0
            if line.miscellaneous_charge:
                sequence += 1
                invoice_lines.append(
                    (0, 0, {
                        'product_id': self.miscellaneous_charge.product_id.id,
                        'price_unit': self.miscellaneous_charge.list_price,
                        'tax_ids': tax,
                        'discount': self.discount_percent,
                        'sequence': sequence,
                    }))

        return invoice_lines

    # create an invoice for services
    def create_invoice(self):
        invoice_lines = self.get_invoice_lines()
        default_journal = self._get_default_journal()
        # Create Invoice
        invoice = self.env['account.move'].sudo().create({
            'move_type': 'out_invoice',
            'journal_id': default_journal.id,
            'partner_id': self.patient.partner_id.id,
            'patient': self.patient.id,
            'invoice_date': datetime.now().date(),
            'date': datetime.now().date(),
            'ref': "Instant Consultation # : " + self.name if self.name else 'Instant Consultation #',
            'invoice_line_ids': invoice_lines
        })
        invoice.action_post()
        self.move_id = invoice

    # create a credit note for services
    def create_credit_note(self):
        if self.move_id.move_type == 'out_invoice':
            invoice_lines = self.get_invoice_lines()
            default_journal = self._get_default_journal()
            # Create Invoice
            ref = "Appointment # : " + self.name if self.name else 'Appointment #' if not self.move_id.name else self.move_id.name
            partner = self.patient.partner_id.id
            credit_note = self.env['account.move'].sudo().create({
                'move_type': 'out_refund',
                'journal_id': default_journal.id,
                'partner_id': partner,
                'patient': self.patient.id,
                'analytic_account_id': self.env.user.analytic_account_id.id,
                'invoice_date': datetime.now().date(),
                'date': datetime.now().date(),
                'ref': ref,
                'invoice_line_ids': invoice_lines,
                'reversed_entry_id': self.move_id.id,
            })
            receivable_line = self.move_id.line_ids.filtered(lambda l: l.account_id.user_type_id.id == 5)
            credit_note_line = credit_note.line_ids.filtered(lambda l: l.account_id.user_type_id.id == 5)
            credit_note.action_post()
            if receivable_line and credit_note_line:
                lines = receivable_line + credit_note_line
                lines.reconcile()
            self.credit_note_id = credit_note.id

    def create_refund_request(self):
        pay_values = {
            'patient': self.patient.id,
            'type': 'instant',
            'date': self.date,
            'instant_date': self.date,
            'instant_id': self.id,
        }
        refund_request = self.env['sm.shifa.cancellation.refund'].create(pay_values)
        refund_request.set_to_operation_manager()
        refund_request.set_to_accept()
        refund_request.set_to_refund_request()
        self.refund_request_id = refund_request.id

    # create Bill for doctor
    def create_bill(self):
        invoice_vals = {
            'move_type': 'in_invoice',
            'partner_id': self.doctor.oeh_user_id.partner_id.id,
            'patient': self.patient.id,
            'invoice_date': self.date,
            'date': self.date,
            'invoice_line_ids': [(0, 0, {
                'name': self.name,
                'product_id': self.miscellaneous_charge.product_id.id,
                'quantity': 1,
                'price_unit': self.miscellaneous_charge.standard_price,
                'tax_ids': [(6, 0, [])],
            })]
        }

        invoice = self.env['account.move'].create(invoice_vals)
        invoice.action_post()
        self.bill_id = invoice.id

    def set_to_in_process(self):
        return self.write({'state': 'in_process'})

    def set_to_evaluation(self):
        for rec in self:
            report = self.env.ref('smartmind_shifa_extra.sm_shifa_medical_pharmacy_report')._render_qweb_pdf(
                rec.id)[0]
            attachment_obj = self.env['ir.attachment']
            domain = [('res_model', '=', "sm.shifa.instant.consultation"), ('res_id', '=', self.id)]
            attachment_ids = attachment_obj.search(domain)
            if attachment_ids:
                config_obj = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                access_token = attachment_ids.access_token
                attachment_url = config_obj + "/web/attachments/token/" + access_token
                rec.link = attachment_url
            rec.env['sm.shifa.instant.prescriptions'].create({
                'name': rec.name,
                'patient': rec.patient.id,
                'doctor': rec.doctor.id,
                'inst_con': rec.name,
                'diagnosis': rec.diagnosis.id,
                'diagnosis_yes_no': rec.diagnosis_yes_no,
                'diagnosis_add2': rec.diagnosis_add2.id,
                'diagnosis_yes_no_2': rec.diagnosis_yes_no_2,
                'diagnosis_add3': rec.diagnosis_add3.id,
                'drug_allergy': rec.drug_allergy,
                'drug_allergy_text': rec.drug_allergy_text,
                'inst_prescription_line': rec.prescription_line,
                'other_prescription_1': rec.other_prescription_1,
                'other_prescription_1_done': rec.other_prescription_1_done,
                'other_prescription_2': rec.other_prescription_2,
                'other_prescription_2_done': rec.other_prescription_2_done,
                'other_prescription_3': rec.other_prescription_3,
                'other_prescription_3_done': rec.other_prescription_3_done,
                'recommendations': rec.recommendations,
                'pharmacy_chain': rec.pharmacy_chain.id,
                'link': rec.link,
                'cunsultancy_requested': rec.cunsultancy_requested,
                'cunsultancy_id': rec.cunsultancy_id,
                'cunsultancy_name': rec.cunsultancy_name,
                'cunsultancy_age': rec.cunsultancy_age,
                'cunsultancy_sex': rec.cunsultancy_sex,
                'weight': rec.weight,
                # separate  pharmacist model
                # 'pharmacy': rec.pharmacy.id,
                # 'pharmacist': rec.pharmacist.id,
            })
            report = base64.b64encode(report)

        # this code for send sms to patient
        for pre in self:
            therapist_obj = pre.env['sm.shifa.instant.prescriptions']
            domain = [('inst_con', '=', pre.name)]
            instance_obj = therapist_obj.search(domain, limit=1)
            my_model = instance_obj._name
            if pre.patient.mobile:
                msg = "رقم وصفتك هي:%s" % (instance_obj.name)
                if pre.pharmacy_chain:
                    prs_msg = msg + " يمكنك صرفها من صيدلية %s ستجدها في ملفك الطبي" % (pre.pharmacy_chain.name)
                    self.send_fcm_request(prs_msg, pre.patient.patient_fcm_token)
                else:
                    prs_msg = msg + "سيتم إرسال الوصفة الى تطبيقك خلال 10 دقائق و ستجدها في ملفك الطبي"
                    self.send_fcm_request(prs_msg, pre.patient.patient_fcm_token)
                self.send_sms(pre.patient.mobile, prs_msg, my_model, instance_obj.id)
            self.state = 'evaluation'
            self.evaluation_date = datetime.now()
            return True

    # send sms for patient with the jitsi link
    # def send_jitsi_sms(self):
    #     if self.patient.mobile:
    #         my_model = self._name
    #         msg = " %s  الطبيب بانتظارك, رابط الاجتماع " % (self.jitsi_link)
    #         self.send_sms(self.patient.mobile, msg, my_model, self.id)
    #         self.send_fcm_request(msg, self.patient.patient_fcm_token)
    def send_jitsi_sms(self):
        if self.patient.mobile:
            my_model = self._name
            msg = f" {self.jitsi_link} الطبيب بانتظارك, رابط الاجتماع "
            # self.send_sms(self.patient.mobile, msg, my_model, self.id)
            self.send_fcm_request(msg, self.patient.patient_fcm_token)

    # send firebase notification for patient
    def send_fcm_request(self, massage, device_token):
        server_token = 'AAAA4_vaS1I:APA91bGU4exsgxIvb3kj9VUqWg2IqcAPoY9j9PMEe3WfqnZ601tTmHOuNe1efUF6aH8T0RwVTqHfFG5hwAmv23AZ6sUPUXd9ulVq3z4qS0jwYx0amCx3apARR92WML1DlYUa4SV2WByA'
        token = device_token
        data = {
            'notification': {'title': 'استشارة فورية',
                             'body': '{0}'.format(massage),
                             "apple": {},
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
                "title": 'استشارة فورية',
                "body": '{0}'.format(massage)
            },
        }
        url = 'https://fcm.googleapis.com/fcm/send'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'key={0}'.format(server_token)
        }
        response = requests.post(url=url, data=json.dumps(data), headers=headers, timeout=120)

    def set_to_completed(self):
        return self.write({'state': 'completed'})

    def send_sms(self, mobile, msg, model, rec_id):
        gatewayurl_id = self.env['gateway_setup'].search([], limit=1)
        if gatewayurl_id and gatewayurl_id.gateway_url:
            try:
                self.env['gateway_setup'].sudo().send_sms_link(msg, mobile, rec_id, model, gatewayurl_id)
            except Exception as e:
                _logger.error(e)
        else:
            raise ValidationError(_("The SMS Gateway is not configured"))

    def set_to_canceled(self):
        self.create_credit_note()
        self.create_refund_request()
        return self.write({'state': 'canceled'})

    def set_to_dr_canceled(self):
        return self.write({'state': 'dr_canceled'})

    def download_pdf(self):
        return self.env.ref('smartmind_shifa_extra.sm_shifa_medical_pharmacy_report').report_action(self)

    def create_jitsi_meeting(self):
        # server_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url') #+ '/videocall'
        server_url = self.env['ir.config_parameter'].sudo().get_param('oehealth_jitsi.video_call_server_url')
        modle = self.env['sm.shifa.instant.consultation'].browse(int(self.id))
        meeting_link = server_url + '/' + self._get_meeting_code()
        invitation_text = _("<a href='%s' target='_blank'>Click here to start meeting</a>") % meeting_link

        modle.write({
            'invitation_text_jitsi': invitation_text,
            'jitsi_link': meeting_link,
        })

    def _get_meeting_code(self):
        return str(uuid.uuid4()).replace('-', '')

    @api.onchange('patient')
    def get_boolean(self):
        therapist_obj = self.env['sm.shifa.instant.consultancy.charge']
        domain = [('consultancy_name', '=', 'Instant Consultation (Pharmacy)')]
        # self.instance = therapist_obj.search(domain)
        therapist_t_obj = self.env['sm.shifa.time.counters']
        domain_t = [('id', '=', 1)]
        self.time_id = therapist_t_obj.search(domain_t)

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('sm.shifa.instant.consultation')
        return super(InstantConsultation, self).create(vals)

    def process_next_waiting_state(self):
        instant = self.search([
            ('state', '=', 'waiting')
        ])
        if instant:
            for rec in instant:
                if datetime.now().date() >= rec.date.date():
                    waiting_time = (rec.date + timedelta(hours=3)).time().strftime("%H:%M")
                    ending_time = (rec.date + timedelta(hours=3, minutes=7)).time().strftime("%H:%M")
                    now_time = (datetime.now() + timedelta(hours=3)).strftime("%H:%M")
                    if now_time >= ending_time:
                        rec.write({
                            'state': 'canceled'
                        })

    # ++++++++++ sch action for canceled instance cons. +++++++++++++++++++ #
    def process_next_approved_state(self):
        instant = self.search([
            ('state', '=', 'approved')
        ])
        if instant:
            for rec in instant:
                if datetime.now().date() >= rec.approved_date.date():
                    approved_time = (rec.approved_date + timedelta(hours=3)).time().strftime("%H:%M")
                    ending_time = (rec.approved_date + timedelta(hours=3, minutes=10)).time().strftime("%H:%M")
                    now_time = (datetime.now() + timedelta(hours=3)).strftime("%H:%M")
                    if now_time >= ending_time:
                        rec.write({
                            'state': 'canceled'
                        })

    # ++++++++++ sch action for complete instance cons. +++++++++++++++++++ #
    def process_next_evaluation_state(self):
        instant = self.search([
            ('state', '=', 'evaluation'),
        ])

        if instant:
            for rec in instant:
                if datetime.now().date() >= rec.evaluation_date.date():
                    evaluation_time = (rec.evaluation_date + timedelta(hours=3)).time().strftime("%H:%M")
                    ending_time = (rec.evaluation_date + timedelta(hours=3, minutes=3)).time().strftime("%H:%M")
                    now_time = (datetime.now() + timedelta(hours=3)).strftime("%H:%M")
                    if now_time >= ending_time:
                        rec.write({
                            'state': 'completed'
                        })

    def open_refund_request(self):
        action = self.env['ir.actions.act_window']._for_xml_id(
            'smartmind_shifa_extra.sm_shifa_cancellation_refund_action')
        action['domain'] = [('id', '=', self.refund_request_id.id)]
        action.update({'context': {}})
        return action


class ShifaPrescriptionLinesInherit(models.Model):
    _inherit = "sm.shifa.prescription.line"

    prescription_extra_ids = fields.Many2one('sm.shifa.instant.consultation', 'prescription_line', ondelete='cascade',
                                             index=True)


class ShifaInstantConsultationInAccountMove(models.Model):
    _inherit = 'account.move'

    instant_consultation = fields.Many2one('sm.shifa.instant.consultation', string="Instant Consultation #")


class ShifaInstantConsultationInSaleOrder(models.Model):
    _inherit = 'sale.order'

    instant_consultation = fields.Many2one('sm.shifa.instant.consultation', string="Instant Consultation #")


class ShifaInstantConsultationInRequestedPayment(models.Model):
    _inherit = 'sm.shifa.requested.payments'

    instant_consultation = fields.Many2one('sm.shifa.instant.consultation', string="Instant Consultation #")


class ShifaInstantConsultationRequestedPayment(models.Model):
    _inherit = 'sm.shifa.instant.consultation'

    def create_requested_payment(self, state, payment_type):
        model_name = 'sm.shifa.requested.payments'
        for rec in self:
            rp = self.env[model_name].sudo().create({
                'patient': int(rec.patient),
                'type': 'instant',
                'date': datetime.now().date(),
                'instant_consultation': rec.id,
                'payment_amount': rec.amount_payable,
                'deduction_amount': rec.deduction_amount,
                'payment_reference': rec.payment_reference,
                'details': rec.name,
                'payment_method_name': rec.payment_method_name,
                'payment_method': payment_type,
                'state': state,
                'instant_id': self.id,
            })
            rec.pay_req_id = rp.id
            return rp


class ShifaInstantConsultationInPurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    instant_consultation = fields.Many2one('sm.shifa.instant.consultation', string="Instant Consultation #")


class ShifaInstantConsultationPurchaseOrder(models.Model):
    _inherit = 'sm.shifa.instant.consultation'

    def _get_default_icf(self):
        miscellaneous_obj = self.env['sm.shifa.miscellaneous.charge.service']
        domain = [('name', '=', 'Instant Consultation (Pharmacy)')]
        hvf = miscellaneous_obj.search(domain, limit=1)
        if hvf:
            return hvf.id or False
        else:
            return False

    purchase_id = fields.Many2one('purchase.order', string='Purchase #')

    miscellaneous_charge = fields.Many2one('sm.shifa.miscellaneous.charge.service', string='Other Charges Type',
                                           required=True, readonly=True, default=_get_default_icf)
    miscellaneous_price = fields.Float(string='Instant Consultation (Pharmacy)',
                                       related='miscellaneous_charge.standard_price', readonly=True)
