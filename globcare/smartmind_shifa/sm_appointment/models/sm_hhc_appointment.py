import datetime
import logging
from datetime import timedelta, datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class ShifaHHCAppointment(models.Model):
    _name = 'sm.shifa.hhc.appointment'
    _description = 'Home Health Care Appointment Management'
    _rec_name = 'display_name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    TIME_SLOT = [('morning', 'Morning'), ('afternoon', 'Afternoon'), ('evening', 'Evening')]
    APPOINTMENT_STATUS = [
        ('scheduled', 'Scheduled'),
        ('head_doctor', 'Head Doctor'),
        ('head_nurse', 'Head Nurse'),
        ('operation_manager', 'Operation Manager'),
        ('team', 'Team'),
        ('in_progress', 'In progress'),
        ('visit_done', 'Visit Done'),
        ('incomplete', 'Incomplete'),
        ('canceled', 'Canceled'),
        ('requestCancellation', 'Request Cancellation'),
    ]

    pay_made_throu = [
        ('pending', 'Free Service'),
        ('mobile', 'Mobile App'),
        ('call_center', 'Call Center'),
        ('on_spot', 'On spot'),
        ('aggregator', 'Aggregator'),
        ('package', 'Package'),
        ('aggregator_package', 'Aggregator Package'),
        ('sleepmedicine','Sleep Medicine'),
        ('deferred','Deferred'),
    ]

    TYPE = [
        ('N', 'Nurse'),
        ('MH', 'Man’s Health'),
        ('GCP', 'Geriatric Care Program'),
        ('SM', 'Sleep Medicine'),
        ('Car', 'Caregiver'),
        ('Diab', 'Diabetic Care'),
    ]

    YES_NO = [
        ('yes', 'Yes'),
        ('no', 'No'),
    ]

    NATIONALITY_STATE = [
        ('KSA', 'Saudi'),
        ('NON', 'Non-Saudi')
    ]
    PHY_DAY = [
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
    ]

    TYPE_SERVICE = [
        ('main', 'Main'),
        ('followup', 'Follow-up'),
    ]

    Main = [
        ('HHC', 'HHC Appointment'),
        ('PHY', 'Physiotherapy Appointments'),
        ('PCR', 'PCR Appointment'),
        ('L', 'Laboratory'),
        ('LP', 'Laboratory Package'),
        ('R', 'Radiology'),
        ('WBSDFC', 'Wound Care'),
        ('GCP', 'Geriatric Care Program'),
        ('MH', 'Men\'s Health'),
        ('IVT', 'IV Therapy'),
        ('SM', 'Sleep Medicine'),
        ('V', 'Muscular/Subcut/Vaccines  Injection'),
        ('Car', 'Caregiver'),
        ('Diab', 'Diabetic Care'),
        ('Tel', 'Telemedicine'),
        ('HVD', 'Home Visit Doctor'),
    ]
    Followup = [
        ('FUPH', 'HHC Follow Up'),
        ('FUPP', 'Physiotherapy Follow Up'),
    ]


    # service dynamic domain
    @api.onchange('service_type_choice')
    def _get_service_list(self):
        if self.service_type_choice == "main":
            return {'domain': {'service': [('service_type', 'in',
                                            ['HHC', 'L', 'WBSDFC', 'R', 'LP', 'GCP', 'MH',
                                             'IVT', 'SM', 'V', 'Car',
                                             'Diab', 'HVD', 'IVFA', 'IV'])]}}
        elif self.service_type_choice == "followup":
            return {'domain': {'service': [('service_type', '=', 'FUPH')]}}
        else:
            return {'domain': {'service': [('service_type', '=', False)]}}

    @api.onchange('service_type_choice_2')
    def _get_service_list2(self):
        if self.service_type_choice_2 == "main":
            return {'domain': {'service_2': [('service_type', 'in',
                                              ['HHC', 'L', 'WBSDFC', 'R', 'LP', 'GCP', 'MH',
                                               'IVT', 'SM', 'V', 'Car',
                                               'Diab', 'HVD', 'IVFA', 'IV', 'PHY'])]}}
        elif self.service_type_choice_2 == "followup":
            return {'domain': {'service_2': [('service_type', '=', 'FUPH')]}}
        else:
            return {'domain': {'service_2': [('service_type', '=', False)]}}

    @api.onchange('service_type_choice_3')
    def _get_service_list3(self):
        if self.service_type_choice_3 == "main":
            return {'domain': {'service_3': [('service_type', 'in',
                                              ['HHC', 'L', 'WBSDFC', 'R', 'LP', 'GCP', 'MH',
                                               'IVT', 'SM', 'V', 'Car',
                                               'Diab', 'HVD', 'IVFA', 'IV', 'PHY'])]}}
        elif self.service_type_choice_3 == "followup":
            return {'domain': {'service_3': [('service_type', '=', 'FUPH')]}}
        else:
            # raise ValidationError('Choose visit type First')
            return {'domain': {'service_3': [('service_type', '=', False)]}}

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

    # @api.depends('appointment_date_only', 'appointment_time')
    # def _get_appointment_date(self):
    #     for apm in self:
    #         apm.appointment_date = datetime.strptime(apm.appointment_date_only.strftime("%Y-%m-%d %H:%M:%S"),
    #                                                  "%Y-%m-%d %H:%M:%S") + timedelta(
    #             hours=apm.appointment_time - 3)
    #     return True

    def _get_appointment_end(self):
        for apm in self:
            end_date = False
            duration = 1
            if apm.appointment_time:
                duration = apm.appointment_time
            if apm.appointment_date_only:
                end_date = datetime.strptime(apm.appointment_date_only.strftime("%Y-%m-%d %H:%M:%S"),
                                             "%Y-%m-%d %H:%M:%S") + timedelta(hours=duration - 3)
            # apm.appointment_date_time = end_date
        return True

    @api.onchange('service')
    def _get_service_price(self):
        for rec in self:
            rec.service_price = rec.service.list_price

    @api.onchange('service_2')
    def _get_service_2_price(self):
        for rec in self:
            rec.service_2_price = rec.service_2.list_price

    @api.onchange('service_3')
    def _get_service_3_price(self):
        for rec in self:
            rec.service_3_price = rec.service_3.list_price

    def _join_name_hhc(self):
        for rec in self:
            if rec.patient:
                rec.display_name = rec.patient.name
            elif rec.name:
                rec.display_name = rec.name
            elif rec.name and rec.patient:
                rec.display_name = rec.patient.name + ' ' + rec.name

    def _hhc_duration(self):
        hhc_duration = self.env['ir.config_parameter'].sudo().get_param('smartmind_shifa.appointment_duration_hhc')
        return float(hhc_duration)

    name = fields.Char(string='HHC #', size=64, readonly=True, default=lambda *a: '/')
    display_name = fields.Char(compute=_join_name_hhc)
    state = fields.Selection(APPOINTMENT_STATUS, string='State', default='scheduled', tracking=True)
    patient = fields.Many2one('oeh.medical.patient', string='Patient', required=True, readonly=True, tracking=True,
                              states={'scheduled': [('readonly', False)]})
    ksa_nationality = fields.Selection(NATIONALITY_STATE, related='patient.ksa_nationality', readonly=True,
                                       states={'scheduled': [('readonly', False)]})
    # patient details
    dob = fields.Date(string='Date of Birth', related='patient.dob', readonly=True,
                      states={'scheduled': [('readonly', False)]})
    marital_status = fields.Selection(string='Marital Status', related='patient.marital_status')
    sex = fields.Selection(string='Sex', related='patient.sex', readonly=True,
                           states={'scheduled': [('readonly', False)]})
    blood_type = fields.Selection(string='Blood Type', related='patient.blood_type')
    rh = fields.Selection(string='Rh', related='patient.rh')
    ssn = fields.Char(string='ID Number', readonly=False,
                      states={'head_doctor': [('readonly', True)], 'head_nurse': [('readonly', True)],
                              'in_progress': [('readonly', True)], 'team': [('readonly', True)],
                              'operation_manager': [('readonly', True)], 'visit_done': [('readonly', True)],
                              'canceled': [('readonly', True)]}, related='patient.ssn')
    mobile = fields.Char(string='Mobile', readonly=False,
                         states={'head_doctor': [('readonly', True)], 'head_nurse': [('readonly', True)],
                                 'in_progress': [('readonly', True)], 'team': [('readonly', True)],
                                 'operation_manager': [('readonly', True)], 'visit_done': [('readonly', True)],
                                 'canceled': [('readonly', True)]}, related='patient.mobile')
    age = fields.Char(string='Age', readonly=False,
                      states={'head_doctor': [('readonly', True)], 'head_nurse': [('readonly', True)],
                              'in_progress': [('readonly', True)], 'team': [('readonly', True)],
                              'operation_manager': [('readonly', True)], 'visit_done': [('readonly', True)],
                              'canceled': [('readonly', True)]}, related='patient.age')
    house_location = fields.Char(string='House Location', readonly=False,
                                 states={'head_doctor': [('readonly', True)], 'head_nurse': [('readonly', True)],
                                         'in_progress': [('readonly', True)], 'team': [('readonly', True)],
                                         'operation_manager': [('readonly', True)], 'visit_done': [('readonly', True)],
                                         'canceled': [('readonly', True)]}, related='patient.house_location')
    house_number = fields.Char(string='House Number', readonly=False,
                               states={'head_doctor': [('readonly', True)], 'head_nurse': [('readonly', True)],
                                       'in_progress': [('readonly', True)], 'team': [('readonly', True)],
                                       'operation_manager': [('readonly', True)], 'visit_done': [('readonly', True)],
                                       'canceled': [('readonly', True)]}, related='patient.house_number')
    nationality = fields.Char(string='Nationality', readonly=False,
                              states={'head_doctor': [('readonly', True)], 'head_nurse': [('readonly', True)],
                                      'in_progress': [('readonly', True)], 'team': [('readonly', True)],
                                      'operation_manager': [('readonly', True)], 'visit_done': [('readonly', True)],
                                      'canceled': [('readonly', True)]}, related='patient.nationality')

    patient_comment = fields.Text(string='Patient Comment')
    patient_weight = fields.Float(string='Weight(kg)', readonly=False,
                                  states={'head_doctor': [('readonly', True)], 'head_nurse': [('readonly', True)],
                                          'in_progress': [('readonly', True)], 'team': [('readonly', True)],
                                          'operation_manager': [('readonly', True)], 'visit_done': [('readonly', True)],
                                          'canceled': [('readonly', True)]}, related='patient.weight')

    period = fields.Selection(TIME_SLOT, string='Period', required=True, readonly=True, tracking=True,
                              states={'scheduled': [('readonly', False)], 'operation_manager': [('readonly', False)],
                                      'team': [
                                          ('readonly', False)]})

    service = fields.Many2one('sm.shifa.service', string='First Service', required=True, tracking=True,
                              readonly=True,
                              states={'scheduled': [('readonly', False)], 'operation_manager': [('readonly', False)]})
    service_price = fields.Float(string='Service Price', readonly=True)

    service_2 = fields.Many2one('sm.shifa.service', string='2nd Service',
                                readonly=True,
                                states={'scheduled': [('readonly', False)], 'operation_manager': [('readonly', False)]})
    service_2_price = fields.Float(string='2nd Ser. Price', readonly=True)

    service_3 = fields.Many2one('sm.shifa.service', string='3rd Service',
                                readonly=True, states={'scheduled': [('readonly', False)],
                                                       'operation_manager': [('readonly', False)]})
    service_3_price = fields.Float(string='3rd Ser. Price', readonly=True)
    service_name = fields.Char(related='service.abbreviation', readonly=True, store=False)
    service_name_2 = fields.Char(related='service_2.abbreviation', readonly=True, store=False)
    service_name_3 = fields.Char(related='service_3.abbreviation', readonly=True, store=False)

    service_type = fields.Selection(string='Service type', related='service.service_type', readonly=True, store=False)
    service_code = fields.Char(string='Service Code', related='service.type_code', readonly=True, store=False)
    service_code_2 = fields.Char(string='Service 2 Code', related='service_2.type_code', readonly=True, store=False)
    service_code_3 = fields.Char(string='Service 3 Code', related='service_3.type_code', readonly=True, store=False)

    payment_type = fields.Char(readonly=True)  # , states={'in_progress': [('readonly', False)]}
    deduction_amount = fields.Float(string="Ded. Amount", readonly=True)
    pro_pending = fields.Boolean(string="Pro. Free Service")
    payment_made_through = fields.Selection(pay_made_throu, string="Pay. Made Thru.", required=True, tracking=True,
                                            readonly=False, states={'scheduled': [('readonly', False)]})
    payment_reference = fields.Char(string='Payment Ref. #', readonly=True)
    location = fields.Char(string='Mobile location', readonly=True)
    attached_file = fields.Binary(string='Attached File 1', readonly=True, states={'scheduled': [('readonly', False)]})
    attached_file_2 = fields.Binary(string='Attached File 2', readonly=True,
                                    states={'scheduled': [('readonly', False)]})

    # order_id = fields.Many2one('sale.order', string='Sale Order #')
    checkup_comment = fields.Char(string="Call Center", tracking=True)
    # doctor instruction
    doctor_instruction = fields.One2many('sm.shifa.doctor.instruction', 'hhc_appointment', string='Doctor Instruction',
                                         readonly=True, states={'head_doctor': [('readonly', False)],
                                                                'in_progress': [('readonly', False)]})
    head_doctor = fields.Many2one('oeh.medical.physician', string='Head Doctor',
                                  domain=[('role_type', '=', 'HD'), ('active', '=', True)],
                                  readonly=True, states={'head_doctor': [('readonly', False)]}, default=_get_physician)

    treatment_comment = fields.Text(string='', readonly=True, states={'head_doctor': [('readonly', False)]})
    # Allergies
    allergy_test = fields.Boolean(string='Allergy Test', readonly=True, states={'head_doctor': [('readonly', False)]})
    drug_allergy_test_done = fields.Boolean(string='Test Done', readonly=False)
    is_drug_allergy_done = fields.Boolean(string='Yes_NO', related='patient.drug_allergy', readonly=False)
    has_drug_allergy = fields.Selection(YES_NO, string='Drug Allergy')
    drug_allergy_content = fields.Char(string='Drug Allergy', related='patient.drug_allergy_content', readonly=False)

    prescribed_medicine = fields.Boolean(string='Prescribed Medicine', readonly=False)

    nurse = fields.Many2one('oeh.medical.physician', string='Nurse', help="Current primary care / family doctor",
                            tracking=True,
                            readonly=False, domain=[('role_type', 'in', ['HN', 'HHCN']), ('active', '=', True)],
                            states={'canceled': [('readonly', True)],
                                    'incomplete': [('readonly', True)], 'in_progress': [('readonly', True)],
                                    'visit_done': [('readonly', True)]})

    respiratory_therapist = fields.Many2one('oeh.medical.physician', string='Clinician #7',
                                            help="Current primary care / family doctor",
                                            # domain=[('role_type', '=', ('RT'))],
                                            readonly=False, states={'canceled': [('readonly', True)],
                                                                    'visit_done': [('readonly', True)]})

    #                                         domain=[('role_type', '=', ('DE'))],
    diabetic_educator = fields.Many2one('oeh.medical.physician', string='Clinician #5',
                                        help="Current primary care / family doctor",
                                        readonly=False,
                                        states={'canceled': [('readonly', True)], 'visit_done': [('readonly', True)]}
                                        )
    #                                          domain=[('role_type', '=', ('CD'))],
    clinical_dietitian = fields.Many2one('oeh.medical.physician', string='Clinician #6',
                                         help="Current primary care / family doctor",
                                         readonly=False,
                                         states={'canceled': [('readonly', True)], 'visit_done': [('readonly', True)]}
                                         )
    #                                     domain=[('role_type', '=', 'SW')],
    social_worker = fields.Many2one('oeh.medical.physician', string='Clinician #4',
                                    help="Current primary care / family doctor",
                                    readonly=False,
                                    states={'canceled': [('readonly', True)], 'visit_done': [('readonly', True)]})

    doctor = fields.Many2one('oeh.medical.physician', string='Physician', tracking=True,
                             readonly=False, domain=[('role_type', 'in', ['HHCD', 'HD']), ('active', '=', True)],
                             states={'canceled': [('readonly', True)],
                                     'incomplete': [('readonly', True)],
                                     'in_progress': [('readonly', True)],
                                     'visit_done': [('readonly', True)]})
    # social_worker = fields.Many2one('oeh.medical.physician', string='Doctor', domain=[('role_type', 'in', 'SW')],
    #                                 readonly=False, states={'head_nurse': [('readonly', False)]})

    physiotherapist = fields.Many2one('oeh.medical.physician', string='Physiotherapist', tracking=True,
                                      readonly=False,
                                      domain=[('role_type', 'in', ['HP', 'HHCP']), ('active', '=', True)],
                                      states={'canceled': [('readonly', True)],
                                              'incomplete': [('readonly', True)],
                                              'in_progress': [('readonly', True)],
                                              'visit_done': [('readonly', True)]})
    visit_comment = fields.Char(string='Team Leader', tracking=True)
    operation_comment = fields.Char(string='Operation Manager', tracking=True)
    comments = fields.Text(string='Comments')  # , readonly=False, states={'Scheduled': [('readonly', False)]}
    # notebook pages fields
    is_service_done = fields.Boolean(string="Is Service Done")
    service_note = fields.Text(string="Remarks")
    service_image = fields.Binary(string="Picture")
    # apt_invoice_count = fields.Integer(string='Invoice Count', compute='_get_apt_invoiced', readonly=False)
    type = fields.Char('Type')  # for mobile app
    start_process_date = fields.Datetime(string='STRT. TM. HV', readonly=True,
                                         states={'visit_done': [('readonly', False)]})
    complete_process_date = fields.Datetime(string='END TM. HV', readonly=True,
                                            states={'visit_done': [('readonly', False)]})
    appointment_duration = fields.Char(string="HHC Duration", compute='_compute_hhc_duration', default="0")
    insurance = fields.Many2one('sm.shifa.insurance', string='Insurance', help="Insurance Company Name",
                                domain=[('state', '=', 'Active')],
                                readonly=True, states={'scheduled': [('readonly', False)]})
    active = fields.Boolean('Active', default=True)
    appointment_day = fields.Selection(PHY_DAY, string='Day', readonly=True)
    day = fields.Char(string='Day', compute='_get_day')
    available_appointment = fields.Integer(string='Available Appts. #', compute='_count_availability', readonly=True)
    meeting_id = fields.Many2one('calendar.event', string='Calendar', copy=False, readonly=True)
    duration = fields.Float(string='Duration', default=_hhc_duration, readonly=True)
    service_type_choice = fields.Selection(TYPE_SERVICE, string="Service Type", readonly=True,
                                           states={'scheduled': [('readonly', False)],
                                                   'operation_manager': [('readonly', False)]})
    service_type_choice_2 = fields.Selection(TYPE_SERVICE, string="Service Type", readonly=True,
                                             states={'scheduled': [('readonly', False)],
                                                     'operation_manager': [('readonly', False)]})
    service_type_choice_3 = fields.Selection(TYPE_SERVICE, string="Service Type", readonly=True,
                                             states={'scheduled': [('readonly', False)],
                                                     'operation_manager': [('readonly', False)]})

    main_type = fields.Selection(Main, domain=[('show', '=', True)],
                                 readonly=True, states={'scheduled': [('readonly', False)]})
    followup_type = fields.Selection(Followup, domain=[('show', '=', True)],
                                     readonly=True, states={'scheduled': [('readonly', False)]})
    payment_method_name = fields.Char(string="Payment Method Name",
                                      readonly=True)  # , states={'scheduled': [('readonly', False)]}
    team_id = fields.Many2one('sm.shifa.team.period', compute="_count_availability", store=True)
    branch = fields.Selection([
        ('riyadh', 'Riyadh'),
        ('dammam', 'Dammam'),
        ('jeddah', 'Jeddah'),
    ], string="Branch", readonly=True, states={'scheduled': [('readonly', False)]})
    # Indicates whether an appointment has been cancelled.
    # This field is typically updated when a user cancels an appointment via the mobile app or other channels.
    cancellation_requested = fields.Boolean(string='Cancellation Requested', default=lambda *a: 0)
    pro_deferred_pay = fields.Boolean(string="Pro. Deferred Pay")

    @api.depends('start_process_date', 'complete_process_date')
    def _compute_hhc_duration(self):
        for r in self:
            if r.start_process_date and r.complete_process_date:
                duration_time = str(r.complete_process_date - r.start_process_date)
                r.appointment_duration = duration_time.split('.')[0]
            else:
                r.appointment_duration = "0"

    @api.onchange('appointment_date_only', 'period', 'service')
    def _count_availability(self):
        for rec in self:
            if rec.team_id:
                rec.team_id._compute_appointment_count()
            team_obj = rec.env['sm.shifa.team.period']
            service_type = rec._get_type(rec.service_type)
            domain = [('date', '=', rec.appointment_date_only), ('period', '=', rec.period),
                      ('type', '=', service_type)]
            team = team_obj.search(domain, limit=1)
            rec.available_appointment = team.available
            rec.team_id = team.id
            team._compute_appointment_count()

    def _get_type(self, service_type):
        default_type = False
        not_nurse = ['MH', 'GCP', 'SM', 'Car', 'Diab']
        if service_type not in not_nurse:
            default_type = 'N'
        else:
            default_type = service_type
        return default_type

    @api.depends('appointment_date_only')
    def _get_day(self):
        for rec in self:
            if rec.appointment_date_only:
                a = datetime.strptime(str(rec.appointment_date_only), "%Y-%m-%d")
                rec.day = str(a.strftime("%A"))
                rec.appointment_day = rec.day

    def set_team_type(self, service_id):
        team_type = False
        serv_obj = self.env['sm.shifa.service'].sudo().browse(int(service_id))
        nurse_list = ['HHC', 'FUPH', 'WBSDFC', 'L', 'R', 'LP', 'IVT', 'V']
        if serv_obj.type_code in nurse_list:
            team_type = 'N'
        else:
            team_type = serv_obj.type_code

        return team_type

    def count_team_available(self, date, period, service_id):
        serv_obj = self.env['sm.shifa.service'].sudo().browse(int(service_id))
        nurse_list = ['HHC', 'FUPH', 'WBSDFC', 'L', 'R', 'LP', 'IVT', 'V']
        print('serv_obj.type_code: ', str(serv_obj.type_code))
        if serv_obj.type_code in nurse_list:
            team_type = 'N'
        else:
            team_type = serv_obj.type_code

        domain = [('date', '=', date), ('period', '=', period), ('type', '=', team_type)]
        team_obj = self.env['sm.shifa.team.period'].sudo().search(domain, limit=1)
        print('team_obj.available: ', str(team_obj.available))
        print('team_type: ', str(team_type))
        return team_obj.available

    @api.model
    def create(self, vals):  # on create use vals['field']

        # solve key error issue
        team_obj = self.env['sm.shifa.team.period']
        service_obj = self.env['sm.shifa.service'].sudo().browse(vals['service'])
        service_type = self._get_type(service_obj.service_type)
        domain = [('date', '=', vals['appointment_date_only']), ('period', '=', vals['period']),
                  ('type', '=', service_type)]
        team = team_obj.search(domain, limit=1)
        vals['type'] = self.set_team_type(vals['service'])

        # if team.available:
        sequence = self.env['ir.sequence'].next_by_code('sm.shifa.hhc.appointment')
        vals['name'] = sequence
        res = super(ShifaHHCAppointment, self).create(vals)
        msg = "New HHC appointment called [ %s ] has been created" % (res.name)
        msg_vals = {"message": msg, "title": "New HHC appointment", "sticky": True}
        admin_group_ids = [self.env.ref('oehealth.group_oeh_medical_manager').id,
                           self.env.ref('smartmind_shifa.group_oeh_medical_operation_manager').id,
                           self.env.ref('smartmind_shifa.group_oeh_medical_call_center').id,
                           self.env.ref('smartmind_shifa.group_oeh_medical_head_doctor').id,
                           self.env.ref('smartmind_shifa.group_oeh_medical_head_physiotherapist').id,
                           self.env.ref('smartmind_shifa.group_oeh_medical_head_nurse').id,
                           ]
        for group_id in admin_group_ids:
            group_users = self.env['res.users'].search([('groups_id', 'in', group_id)])
            for user in group_users:
                user.notify_success(**msg_vals)
        return res

        # else:
        #     raise ValidationError(
        #         '%s period is full or not determined yet, please book appointment in another period.' % vals['period'])

    def _reset_token_number_sequences(self):
        # just use write directly on the result this will execute one update query
        sequences = self.env['ir.sequence'].search([('name', '=', 'HHC Appointment')])
        sequences.write({'number_next_actual': 1})

    def write(self, vals):  # on update we use self.field
        for rec in self:
            vals['type'] = rec.set_team_type(rec.service)
        users = self.env.ref('smartmind_shifa.group_oeh_medical_operation_manager').sudo().users
        users += self.env.ref('smartmind_shifa.group_oeh_medical_call_center').sudo().users
        users += self.env.ref('oehealth.group_oeh_medical_manager').sudo().users
        # if 'nurse' in vals or 'timeslot' in vals or 'doctor' in vals or 'timeslot_doctor' in vals or 'physiotherapist' in vals or 'timeslot_phy':
        # if self.env.user.id not in users.ids:
        # raise UserError("You don't have access to edit these fields!")
        return super(ShifaHHCAppointment, self).write(vals)
        # if self.available_appointment > 0: # you can get its value using this way because the field is not read only
        #     return super(ShifaHHCAppointment, self).write(vals)
        # else:
        #     raise ValidationError('%s period is full or not determined yet, please book appointment in another period.' % self.period)

    def set_to_head_doctor(self):
        if self.payment_made_through not in ['package', 'aggregator_package', 'mobile']:
            msg = "HHC Appointment [ %s ] is at Head Doctor state" % (self.name)
            msg_vals = {"message": msg, "title": "Head doctor state", "sticky": True}
            admin_group_ids = [self.env.ref('oehealth.group_oeh_medical_manager').id,
                               self.env.ref('smartmind_shifa.group_oeh_medical_operation_manager').id,
                               self.env.ref('smartmind_shifa.group_oeh_medical_head_doctor').id]
            for group_id in admin_group_ids:
                group_users = self.env['res.users'].search([('groups_id', 'in', group_id)])
                for user in group_users:
                    user.notify_success(**msg_vals)
        elif self.payment_made_through == 'mobile':
            pass
        return self.write({'state': 'head_doctor'})

    def set_to_start(self):
        return self.write({'state': 'in_progress', 'start_process_date': datetime.now()})

    def set_to_end_hiv(self):
        self.write({'state': 'visit_done', 'complete_process_date': datetime.now()})

    def set_to_Head_Nurse(self):
        msg = "HHC appointment [ %s ] is at Head Nurse state" % (self.name)
        msg_vals = {"message": msg, "title": "Head Nurse State", "sticky": True}
        admin_group_ids = [self.env.ref('oehealth.group_oeh_medical_manager').id,
                           self.env.ref('smartmind_shifa.group_oeh_medical_operation_manager').id,
                           self.env.ref('smartmind_shifa.group_oeh_medical_head_nurse').id,
                           ]
        for group_id in admin_group_ids:
            group_users = self.env['res.users'].search([('groups_id', 'in', group_id)])
            for user in group_users:
                user.notify_success(**msg_vals)
        return self.write({'state': 'head_nurse'})

    def set_to_operation_manager(self):
        msg = "HHC appointment [ %s ] is at Operation Manager state" % (self.name)
        msg_vals = {"message": msg, "title": "Operation Manager State", "sticky": True}
        admin_group_ids = [self.env.ref('oehealth.group_oeh_medical_manager').id,
                           self.env.ref('smartmind_shifa.group_oeh_medical_operation_manager').id,
                           ]
        for group_id in admin_group_ids:
            group_users = self.env['res.users'].search([('groups_id', 'in', group_id)])
            for user in group_users:
                user.notify_success(**msg_vals)
        self.change_timeslot()
        return self.write({'state': 'operation_manager'})

    def set_to_team(self):
        if self.doctor:
            self.calendar_appointment_event(self.doctor)
        if self.nurse:
            self.calendar_appointment_event(self.nurse)
        if self.physiotherapist:
            self.calendar_appointment_event(self.physiotherapist)
        if self.social_worker:
            self.calendar_appointment_event(self.social_worker)
        msg = "HHC appointment [ %s ] is at Team state" % (self.name)
        msg_vals = {"message": msg, "title": "Team State", "sticky": True}
        admin_group_ids = [self.env.ref('oehealth.group_oeh_medical_manager').id,
                           self.env.ref('smartmind_shifa.group_oeh_medical_operation_manager').id,
                           self.env.ref('smartmind_shifa.group_oeh_medical_head_doctor').id,
                           self.env.ref('oehealth.group_oeh_medical_physician').id,
                           self.env.ref('smartmind_shifa.group_oeh_medical_head_physiotherapist').id,
                           self.env.ref('smartmind_shifa.group_oeh_medical_hhc_physiotherapist').id,
                           self.env.ref('smartmind_shifa.group_oeh_medical_head_nurse').id,
                           self.env.ref('smartmind_shifa.group_oeh_medical_hhc_nurse').id,
                           ]
        for group_id in admin_group_ids:
            group_users = self.env['res.users'].search([('groups_id', 'in', group_id)])
            for user in group_users:
                user.notify_success(**msg_vals)
        self.submit_timeslot()
        return self.write({'state': 'team'})

    def set_back_to_head_doctor(self):
        return self.write({'state': 'head_doctor'})

    def set_back_to_Head_Nurse(self):
        return self.write({'state': 'head_nurse'})

    def set_back_to_operation_manager(self):
        self.change_timeslot()
        return self.write({'state': 'operation_manager'})

    def set_back_to_call_center(self):
        return self.write({'state': 'scheduled'})

    @api.onchange('is_drug_allergy_done')
    def get_selection(self):
        done = self.is_drug_allergy_done
        if done:
            self.has_drug_allergy = "yes"
        else:
            self.has_drug_allergy = "no"

    @api.onchange('has_drug_allergy')
    def get_boolean(self):
        if self.has_drug_allergy == "yes":
            self.is_drug_allergy_done = True
        else:
            self.is_drug_allergy_done = False

    def calendar_appointment_event(self, Medical_user):
        for rec in self:
            date_time = datetime.fromordinal(rec.appointment_date_only.toordinal())
            time = rec.appointment_time
            start_appointment = date_time + timedelta(seconds=time * 3600)
            start_appointment = start_appointment - timedelta(hours=3)
            meeting_values = {
                'name': rec.display_name,
                'duration': rec.duration,
                'description': "HHC appointment",
                'user_id': Medical_user.oeh_user_id.id,
                'start': start_appointment,
                'stop': start_appointment + timedelta(hours=1),
                'allday': False,
                'recurrency': False,
                'privacy': 'confidential',
                'event_tz': Medical_user.oeh_user_id.tz,
                'activity_ids': [(5, 0, 0)],
            }

            # Add the partner_id (if exist) as an attendee
            if Medical_user.oeh_user_id and Medical_user.oeh_user_id.partner_id:
                meeting_values['partner_ids'] = [
                    (4, Medical_user.oeh_user_id.partner_id.id)]

        meetings = self.env['calendar.event'].with_context(
            no_mail_to_attendees=True,
            active_model=self._name
        ).create(meeting_values)
        for meeting in meetings:
            self.meeting_id = meeting

    @api.onchange('mobile')
    def get_patient_mobile(self):
        mobile = self.mobile
        if mobile:
            therapist_obj = self.env['oeh.medical.patient']
            domain = [('mobile', '=', self.mobile)]
            patient_obj = therapist_obj.search(domain)
            patient_ids = []
            for i in list(patient_obj):
                patient_ids.append(i.id)
            # print(patient_ids)
            return {'domain': {'patient': [('id', 'in', patient_ids)]}}
        else:
            self._cr.execute(
                "select id from oeh_medical_patient")
            record = self._cr.fetchall()
            patient_ids = [item for t in record for item in t]
            return {'domain': {'patient': [('id', 'in', patient_ids)]}}

    def set_to_Head_Nurse_followup(self):
        self.write({'state': 'head_nurse'})

    def unlink(self):
        for rec in self:
            if rec.state != 'canceled':
                raise UserError(_("You can delete only if it cancelled Appointments"))
        return super().unlink()

    def action_archive(self):
        for rec in self:
            if rec.state not in ['canceled', 'visit_done']:
                raise UserError(_("You can archive only if it cancelled Appointments or visit done"))
        return super().action_archive()

    @api.onchange('payment_made_through')
    def _onchange_payment_made_through(self):
        restricted_values = ['mobile', 'package', 'aggregator_package','sleepmedicine']
        if self.payment_made_through in restricted_values:
            return {
                'warning': {
                    'title': "Invalid Selection",
                    'message': "You are not allowed to generate this type of payment method. Please select another value.",
                }
            }

    def open_treatment_form(self):
        self.ensure_one()  # Ensure there's only one record
        ctx = {
            'form_view_ref': 'sm_search_patient.sm_treatments_form_view',
            'default_patient_id': self.patient.id,
            'default_hhc_appointment_id': self.id,
        }
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sm.treatments',
            'view_mode': 'form',
            'target': 'new',
            'context': ctx,
        }


    # @api.constrains('payment_made_through')
    # def _check_payment_method(self):
    #     restricted_values = ['mobile', 'package', 'aggregator_package']
    #     for record in self:
    #         if record.payment_made_through in restricted_values:
    #             raise ValidationError(
    #                 "You are not allowed to save this type of payment method. Please select another value.")


class SmartMindShifaDoctorScheduleTimeSlot(models.Model):
    _inherit = "sm.shifa.hhc.appointment"

    @api.depends('appointment_date_only', 'appointment_time')
    def _get_appointment_date(self):
        for apm in self:
            # if apm.appointment_time: # apm.time_slot and apm.appointment_time:
            if apm.appointment_date_only:
                apm.appointment_date = datetime.strptime(apm.appointment_date_only.strftime("%Y-%m-%d %H:%M:%S"),
                                                         "%Y-%m-%d %H:%M:%S") + timedelta(
                    hours=apm.appointment_time - 3)

    # APPOINTMENT DATES------------------------------------------------------------------------------------
    appointment_date_only = fields.Date(string='Date', required=True, readonly=True,
                                        states={'scheduled': [('readonly', False)], 'team': [('readonly', False)],
                                                'operation_manager': [
                                                    ('readonly', False)]},
                                        default=lambda *a: datetime.now())
    appointment_time = fields.Float(string='Time (HH:MM)', readonly=False, default=1.0)
    timeslot = fields.Many2one('sm.shifa.physician.schedule.timeslot', string='Timeslot', copy=False,
                               domain="[('physician_id', '=', nurse), ('date', '=', appointment_date_only), ('is_available', '=', True)]",
                               readonly=True, states={'scheduled': [('readonly', False)],
                                                      'head_nurse': [
                                                          ('readonly', False)],
                                                      'operation_manager': [
                                                          ('readonly', False)],
                                                      'team': [
                                                          ('readonly', False)],
                                                      'head_doctor': [
                                                          ('readonly', False)]})
    timeslot_doctor = fields.Many2one('sm.shifa.physician.schedule.timeslot', string='Timeslot', copy=False,
                                      domain="[('physician_id', '=', doctor), ('date', '=', appointment_date_only), ('is_available', '=', True)]",
                                      readonly=True, states={'scheduled': [('readonly', False)],
                                                             'head_nurse': [
                                                                 ('readonly', False)],
                                                             'operation_manager': [
                                                                 ('readonly', False)],
                                                             'team': [
                                                                 ('readonly', False)],
                                                             'head_doctor': [
                                                                 ('readonly', False)]})
    timeslot_phy = fields.Many2one('sm.shifa.physician.schedule.timeslot', string='Timeslot', copy=False,
                                   domain="[('physician_id', '=', physiotherapist), ('date', '=', appointment_date_only), ('is_available', '=', True)]",
                                   readonly=True, states={'scheduled': [('readonly', False)],
                                                          'head_nurse': [
                                                              ('readonly', False)],
                                                          'team': [
                                                              ('readonly', False)],
                                                          'operation_manager': [
                                                              ('readonly', False)],
                                                          'head_doctor': [
                                                              ('readonly', False)]})

    changed_timeslot = fields.Boolean(default=False)

    appointment_date = fields.Datetime(compute=_get_appointment_date, string='Apt. DateTime', readonly=False,
                                       store=True)

    # change timeslot for nurse doctor and physiotherapy
    def change_timeslot(self):
        self.changed_timeslot = True
        if self.timeslot:
            self.timeslot_done(self.nurse.id, self.appointment_date_only, self.timeslot.available_time, True)
        if self.timeslot_doctor:
            self.timeslot_done(self.doctor.id, self.appointment_date_only, self.timeslot.available_time, True)
        if self.timeslot_phy:
            self.timeslot_done(self.physiotherapist.id, self.appointment_date_only, self.timeslot.available_time, True)

    # submit timeslot for nurse doctor and physiotherapy
    def submit_timeslot(self):
        self.changed_timeslot = False
        if self.timeslot:
            self.timeslot.is_available = False
        if self.timeslot_phy:
            self.timeslot_phy.is_available = False
        if self.timeslot_doctor:
            self.timeslot.is_available = False

    # ------------------------------------------------------------------------------------------------------------------

    def change_appointment_timeslot(self):
        if self.timeslot:
            self.timeslot_done(self.nurse.id, self.appointment_date_only, self.timeslot.available_time, True)
            self.changed_timeslot = True

    @api.onchange('timeslot')
    def onchange_timeslot(self):
        if self.timeslot:
            hm = self.timeslot.available_time.split(':')
            sch_time = int(hm[0]) + int(hm[1]) / 60
            self.appointment_time = sch_time
            self.changed_timeslot = False

    def timeslot_done(self, person_id, date, available_time, action):
        for rec in self:
            timeslot = rec.env['sm.shifa.physician.schedule.timeslot'].sudo().search(
                [('physician_id', '=', person_id), ('date', '=', date), ('available_time', '=', available_time)],
                limit=1)
            if timeslot:
                timeslot.sudo().write({
                    'is_available': action,
                })

    def timeslot_is_available(self, person_id, date, available_time, action):
        timeslot_model = 'sm.shifa.physician.schedule.timeslot'
        is_found_timeslot = self.env[timeslot_model].sudo().search_count(
            [('physician_id', '=', person_id), ('date', '=', date), ('available_time', '=', available_time),
             ('is_available', '=', True)])
        if is_found_timeslot > 0:
            timeslot = self.env[timeslot_model].sudo().search(
                [('physician_id', '=', person_id), ('date', '=', date), ('available_time', '=', available_time)],
                limit=1)
            if timeslot:
                timeslot.sudo().write({
                    'is_available': action,
                })

    def remove_old_timeslot(self):
        for rec in self:
            if rec.nurse:
                timeslot_obj = self.env['sm.shifa.physician.schedule.timeslot'].sudo().search(
                    [('physician_id', '=', rec.nurse.id), ('date', '=', rec.timeslot.date),
                     ('available_time', '!=', rec.timeslot.available_time)], limit=1)
                if timeslot_obj:
                    timeslot_obj.write({
                        'active': False
                    })

    def update_multi_timeslots(self, rec, action):
        if rec.nurse:
            self.timeslot_is_available(rec.nurse.id, rec.appointment_date_only, rec.timeslot.available_time, action)
        if rec.doctor:
            self.timeslot_is_available(rec.doctor.id, rec.appointment_date_only, rec.timeslot.available_time, action)
        if rec.physiotherapist:
            self.timeslot_is_available(rec.physiotherapist.id, rec.appointment_date_only, rec.timeslot.available_time,
                                       action)
        if rec.social_worker:
            self.timeslot_is_available(rec.social_worker.id, rec.appointment_date_only, rec.timeslot.available_time,
                                       action)
        if rec.diabetic_educator:
            self.timeslot_is_available(rec.diabetic_educator.id, rec.appointment_date_only, rec.timeslot.available_time,
                                       action)
        if rec.clinical_dietitian:
            self.timeslot_is_available(rec.clinical_dietitian.id, rec.appointment_date_only,
                                       rec.timeslot.available_time,
                                       action)
        if rec.respiratory_therapist:
            self.timeslot_is_available(rec.respiratory_therapist.id, rec.appointment_date_only,
                                       rec.timeslot.available_time,
                                       action)

    # def is_timeslot_available(self, clinician_id, date, available_time):
    #     model_name = 'sm.shifa.physician.schedule.timeslot'
    #     domain = [('physician_id', '=', clinician_id), ('date', '=', date), ('available_time', '=', available_time),
    #               ('is_available', '=', True)]
    #     count = self.env[model_name].sudo().search_count(domain)
    #     if count > 0:
    #         return True
    #     else:
    #         return False

    def active_timeslot(self):
        for rec in self.filtered(
                lambda rec: rec.state in ['scheduled', 'head_doctor', 'head_nurse', 'operation_manager', 'team']):
            if rec.timeslot:
                self.update_multi_timeslots(rec, True)

    @api.model
    def create(self, vals):
        available_time = vals.get('appointment_time')
        if vals.get('nurse'):
            self.timeslot_is_available(vals.get('nurse'), vals.get('appointment_date_only'), available_time, False)
        if vals.get('doctor'):
            self.timeslot_is_available(vals.get('doctor'), vals.get('appointment_date_only'), available_time, False)
        if vals.get('physiotherapist'):
            self.timeslot_is_available(vals.get('physiotherapist'), vals.get('appointment_date_only'), available_time,
                                       False)
        if vals.get('social_worker'):
            self.timeslot_is_available(vals.get('social_worker'), vals.get('appointment_date_only'), available_time,
                                       False)
        if vals.get('diabetic_educator'):
            self.timeslot_is_available(vals.get('diabetic_educator'), vals.get('appointment_date_only'), available_time,
                                       False)
        if vals.get('clinical_dietitian'):
            self.timeslot_is_available(vals.get('clinical_dietitian'), vals.get('appointment_date_only'),
                                       available_time, False)
        if vals.get('respiratory_therapist'):
            self.timeslot_is_available(vals.get('respiratory_therapist'), vals.get('appointment_date_only'),
                                       available_time,
                                       False)

        return super(SmartMindShifaDoctorScheduleTimeSlot, self).create(vals)

    def write(self, vals):
        for rec in self:
            if not rec.changed_timeslot:
                self.update_multi_timeslots(rec, False)
            if rec.changed_timeslot:
                self.timeslot_done(self.nurse.id, self.appointment_date_only, self.timeslot.available_time, True)
                self.active_timeslot()
        return super(SmartMindShifaDoctorScheduleTimeSlot, self).write(vals)

    def write(self, vals):
        for rec in self:
            if not rec.changed_timeslot:
                self.update_multi_timeslots(rec, False)
            if rec.changed_timeslot:
                self.timeslot_done(self.nurse.id, self.appointment_date_only, self.timeslot.available_time, True)
                self.active_timeslot()
        return super(SmartMindShifaDoctorScheduleTimeSlot, self).write(vals)

    def unlink(self):
        self.active_timeslot()
        return super(SmartMindShifaDoctorScheduleTimeSlot, self).unlink()

    def unlink(self):
        self.active_timeslot()
        return super(SmartMindShifaDoctorScheduleTimeSlot, self).unlink()

    def set_to_incomplete(self):
        return self.write({'state': 'incomplete'})

    def set_to_incomplete(self):
        return self.write({'state': 'incomplete'})

    def set_to_canceled(self):
        self.active_timeslot()
        return self.write({'state': 'canceled'})

    def set_to_canceled(self):
        self.active_timeslot()
        return self.write({'state': 'canceled'})

    def set_to_req_cancellation(self):
        self.active_timeslot()
        return self.write({'state': 'canceled'})

    def set_to_req_cancellation(self):
        self.active_timeslot()
        return self.write({'state': 'canceled'})

    @api.onchange('timeslot_doctor')
    def _get_doctor_match_timeslot(self):
        for rec in self:
            if rec.doctor and rec.nurse:
                if rec.timeslot.available_time != rec.timeslot_doctor.available_time:
                    raise ValidationError("The timeslot must be the Same")
                # self.is_timeslot_available(rec.doctor.id, rec.appointment_date_only, rec.timeslot.available_time)

    @api.onchange('timeslot_doctor')
    def _get_doctor_match_timeslot(self):
        for rec in self:
            if rec.doctor and rec.nurse:
                if rec.timeslot.available_time != rec.timeslot_doctor.available_time:
                    raise ValidationError("The timeslot must be the Same")
                # self.is_timeslot_available(rec.doctor.id, rec.appointment_date_only, rec.timeslot.available_time)

    @api.onchange('timeslot_phy')
    def _get_physiotherapist_match_timeslot(self):
        for rec in self:
            if rec.physiotherapist and rec.doctor and rec.nurse:
                if rec.timeslot.available_time != rec.timeslot_phy.available_time:
                    raise ValidationError("The timeslot must be the Same")
                # self.is_timeslot_available(rec.doctor.id, rec.appointment_date_only, rec.timeslot.available_time)

    @api.onchange('timeslot_phy')
    def _get_physiotherapist_match_timeslot(self):
        for rec in self:
            if rec.physiotherapist and rec.doctor and rec.nurse:
                if rec.timeslot.available_time != rec.timeslot_phy.available_time:
                    raise ValidationError("The timeslot must be the Same")
                # self.is_timeslot_available(rec.doctor.id, rec.appointment_date_only, rec.timeslot.available_time)

    @api.onchange('social_worker')
    def _get_social_worker_match_timeslot(self):
        for rec in self:
            if rec.social_worker:
                self.is_timeslot_available(rec.doctor.id, rec.appointment_date_only, rec.timeslot.available_time)

    @api.onchange('social_worker')
    def _get_social_worker_match_timeslot(self):
        for rec in self:
            if rec.social_worker:
                self.is_timeslot_available(rec.doctor.id, rec.appointment_date_only, rec.timeslot.available_time)

    @api.onchange('diabetic_educator')
    def _get_diabetic_educator_match_timeslot(self):
        for rec in self:
            if rec.diabetic_educator:
                self.is_timeslot_available(rec.doctor.id, rec.appointment_date_only, rec.timeslot.available_time)

    @api.onchange('diabetic_educator')
    def _get_diabetic_educator_match_timeslot(self):
        for rec in self:
            if rec.diabetic_educator:
                self.is_timeslot_available(rec.doctor.id, rec.appointment_date_only, rec.timeslot.available_time)

    @api.onchange('clinical_dietitian')
    def _get_clinical_dietitian_match_timeslot(self):
        for rec in self:
            if rec.clinical_dietitian:
                self.is_timeslot_available(rec.doctor.id, rec.appointment_date_only, rec.timeslot.available_time)

    @api.onchange('clinical_dietitian')
    def _get_clinical_dietitian_match_timeslot(self):
        for rec in self:
            if rec.clinical_dietitian:
                self.is_timeslot_available(rec.doctor.id, rec.appointment_date_only, rec.timeslot.available_time)

    @api.onchange('respiratory_therapist')
    def _get_respiratory_therapist_match_timeslot(self):
        for rec in self:
            if rec.respiratory_therapist:
                self.is_timeslot_available(rec.doctor.id, rec.appointment_date_only, rec.timeslot.available_time)

    @api.onchange('respiratory_therapist')
    def _get_respiratory_therapist_match_timeslot(self):
        for rec in self:
            if rec.respiratory_therapist:
                self.is_timeslot_available(rec.doctor.id, rec.appointment_date_only, rec.timeslot.available_time)

    def is_timeslot_available(self, physician_id, date, available_time):
        count = self.env['sm.shifa.physician.schedule.timeslot'].sudo().search_count(
            [('physician_id', '=', physician_id), ('date', '=', date),
             ('available_time', '=', available_time), ('is_available', '=', True)])
        if count == 0:
            raise ValidationError('Sorry, the selected physiotherapist has no same timeslot to nurse.')

    def is_timeslot_available(self, physician_id, date, available_time):
        count = self.env['sm.shifa.physician.schedule.timeslot'].sudo().search_count(
            [('physician_id', '=', physician_id), ('date', '=', date),
             ('available_time', '=', available_time), ('is_available', '=', True)])
        if count == 0:
            raise ValidationError('Sorry, the selected physiotherapist has no same timeslot to nurse.')


class ShifaHHCAppointmentInAccountMove(models.Model):
    _inherit = 'account.move'

    hhc_appointment = fields.Many2one('sm.shifa.hhc.appointment', string="HHC Appointment #")


class ShifaDoctorInstructionForHHC(models.Model):
    _name = 'sm.shifa.doctor.instruction'
    _description = 'Record Doctor instruction information in HHC Appointment'

    hhc_appointment = fields.Many2one('sm.shifa.hhc.appointment', 'HHC Appointment', required=True, ondelete='cascade',
                                      index=True)

    medicine = fields.Many2one('sm.shifa.generic.medicines', string='Medicines', required=True)
    qty = fields.Integer(string='Qty', help="Quantity of units (eg, 2 capsules) of the medicament",
                         default=lambda *a: 1.0)
    dose = fields.Integer(string='Dose', help="Amount of medicines (eg, 250 mg ) each time the patient takes it")
    dose_unit = fields.Many2one('oeh.medical.dose.unit', string='Dose Unit',
                                help="Unit of measure for the medication to be taken")
