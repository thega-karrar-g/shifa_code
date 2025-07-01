from datetime import timedelta, datetime

from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError, ValidationError

import logging
import pytz
import uuid
from random import choice

_logger = logging.getLogger(__name__)


class ShifaTeleAppointment(models.Model):
    _name = "sm.telemedicine.appointment"
    _rec_name = 'display_name'

    APPOINTMENT_STATE = [
        ('scheduled', 'Scheduled'),
        ('confirmed', 'Confirmed'),
        ('start', 'Start'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled'),
    ]
    # APPOINTMENT_STATUS = [
    #     ('Scheduled', 'Scheduled'),
    #     ('Confirmed', 'Confirmed'),
    #     ('Start', 'Start'),
    #     ('Completed', 'Completed'),
    #     ('canceled', 'Canceled'),
    #     ('requestCancellation', 'Request Cancellation'),
    # ]

    PATIENT_STATUS = [
        ('Ambulatory', 'Ambulatory'),
        ('Outpatient', 'Outpatient'),
        ('Inpatient', 'Inpatient'),
    ]
    NATIONALITY_STATE = [
        ('KSA', 'Saudi'),
        ('NON', 'Non-Saudi')
    ]
    APPOINTMENT_DAY = [
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
    ]

    URGENCY_LEVEL = [
        ('Normal', 'Normal'),
        ('Urgent', 'Urgent'),
        ('Medical Emergency', 'Medical Emergency'),
    ]

    pay_made_throu = [
        ('mobile', 'Mobile App'),
        ('call_center', 'Call Center'),
        ('on_spot', 'On spot'),
    ]

    def create_password(self):
        size = 6
        values = '0123456789'
        p = ''
        p = p.join([choice(values) for i in range(size)])
        return p
        # Automatically detect logged in physician

    def _get_physician(self):
        """Return default physician value"""
        therapist_obj = self.env['oeh.medical.physician']
        domain = [('oeh_user_id', '=', self.env.uid)]
        user_ids = therapist_obj.search(domain, limit=1)
        if user_ids:
            return user_ids.id or False
        else:
            return False

    def _get_time_slot(self):
        domain = []
        for rec in self:
            domain = [('date', '=', rec.appointment_date_only)]
        return domain

    @api.depends('appointment_date_only', 'appointment_time')
    def _get_appointment_date(self):
        for apm in self:

            if apm.appointment_date_only:
                apm.appointment_date = datetime.strptime(apm.appointment_date_only.strftime("%Y-%m-%d %H:%M:%S"),
                                                         "%Y-%m-%d %H:%M:%S") + timedelta(
                    hours=apm.appointment_time - 3)
        return True

    @api.onchange('time_slot')
    def _convert_to_time(self):
        for rec in self:
            hm = rec.time_slot.split(':')
            rec.appointment_time = int(hm[0]) + int(hm[1]) / 60

    # Calculating Appointment End date
    @api.depends('appointment_date', 'doctor', 'appointment_date_only')
    def _get_appointment_end(self):
        for rec in self:
            if rec.appointment_date_only and rec.doctor:
                schedule_list = self.env['oeh.medical.physician.line'].sudo().search(
                    [('physician_id', '=', int(rec.doctor.id)), ('date', '=', rec.appointment_date_only)], limit=1)
                rec.appointment_end = datetime.strptime(rec.appointment_date.strftime("%Y-%m-%d %H:%M:%S"),
                                                        "%Y-%m-%d %H:%M:%S") + timedelta(minutes=schedule_list.duration)

    def _join_name_tele(self):
        for rec in self:
            if rec.patient:
                rec.display_name = rec.patient.name + ' ' + rec.name

    state = fields.Selection(APPOINTMENT_STATE, string='State', readonly=True, default=lambda *a: 'scheduled')
    name = fields.Char(string='Tel #', size=64, readonly=True, default=lambda *a: '/')
    display_name = fields.Char(compute=_join_name_tele)
    # patient details
    patient = fields.Many2one('oeh.medical.patient', string='Patient', help="Patient Name", required=True,
                              readonly=True, states={'scheduled': [('readonly', False)]})

    dob = fields.Date(string='Date of Birth', related='patient.dob', readonly=True,
                      states={'scheduled': [('readonly', False)]})
    marital_status = fields.Selection(string='Marital Status', related='patient.marital_status')
    sex = fields.Selection(string='Sex', related='patient.sex', readonly=True,
                           states={'scheduled': [('readonly', False)]})
    blood_type = fields.Selection(string='Blood Type', related='patient.blood_type')
    rh = fields.Selection(string='Rh', related='patient.rh')
    ssn = fields.Char(string='ID Number', readonly=False,
                      states={'start': [('readonly', True)], 'confirmed': [('readonly', True)],
                              'completed': [('readonly', True)], 'canceled': [('readonly', True)]},
                      related='patient.ssn')
    mobile = fields.Char(string='Mobile', readonly=False,
                         states={'start': [('readonly', True)], 'confirmed': [('readonly', True)],
                                 'completed': [('readonly', True)], 'canceled': [('readonly', True)]},
                         related='patient.mobile')
    age = fields.Char(string='Age', readonly=False,
                      states={'start': [('readonly', True)], 'confirmed': [('readonly', True)],
                              'completed': [('readonly', True)], 'canceled': [('readonly', True)]},
                      related='patient.age')
    ksa_nationality = fields.Selection(NATIONALITY_STATE, related='patient.ksa_nationality', readonly=True,
                                       states={'scheduled': [('readonly', False)]})
    patient_weight = fields.Float(string='Weight(kg)', readonly=False,
                                  states={'start': [('readonly', True)], 'confirmed': [('readonly', True)],
                                          'completed': [('readonly', True)], 'canceled': [('readonly', True)]},
                                  related='patient.weight')
    # doctor details
    doctor = fields.Many2one('oeh.medical.physician', string='Consultancy Responsible',
                             help="Current primary care / family doctor",
                             domain=[('role_type', 'in',
                                      ['TD', 'HD', 'HHCD', 'HN', 'HHCN', 'HP', 'HHCP', 'RT', 'SW', 'HE', 'DE', 'CD']), ('active', '=', True)],
                             required=True, readonly=True,
                             states={'scheduled': [('readonly', False)]}, default=_get_physician)
    # APPOINTMENT DATES-------------------------------------------------------------------------------------------------
    duration = fields.Float(string='Duration (HH:MM)', readonly=True, states={'scheduled': [('readonly', False)]})
    # default=lambda self: self.env.company.appointment_duration)
    # appointment_date_only = fields.Date(string='Date', readonly=False,
    #                                     states={'start': [('readonly', True)], 'confirmed': [('readonly', True)],
    #                                             'completed': [('readonly', True)], 'canceled': [('readonly', True)]},
    #                                     default=lambda *a: datetime.now())
    # appointment_time = fields.Float(string='Time (HH:MM)', readonly=False,
    #                                 states={'start': [('readonly', True)], 'confirmed': [('readonly', True)],
    #                                         'completed': [('readonly', True)], 'canceled': [('readonly', True)]})
    # appointment_date = fields.Datetime(compute=_get_appointment_date, string='Apt. DateTime', readonly=True, store=True)
    # appointment_end = fields.Datetime(compute=_get_appointment_end, string='Apt. End Date', store=True)
    appointment_day = fields.Selection(APPOINTMENT_DAY, string='Day', required=False)
    day = fields.Char(string='Day', store=True)

    # ------------- archive field ---------------------- #
    active = fields.Boolean('Active', default=True)
    # ------------- payment details -------------------- #
    payment_type = fields.Char(readonly=True, states={'confirmed': [('readonly', False)]})
    deduction_amount = fields.Float(string="Ded. Amount", readonly=True)
    payment_made_through = fields.Selection(pay_made_throu, string="Pay. Made Thru.", default="mobile",
                                            readonly=False, states={'canceled': [('readonly', True)],
                                                                    'completed': [('readonly', True)]})
    payment_reference = fields.Char('Payment Reference', readonly=True, states={'confirmed': [('readonly', False)]})
    insurance = fields.Many2one('sm.shifa.insurance', string='Insurance', help="Insurance Company Name",
                                domain=[('state', '=', 'Active')],
                                readonly=True, states={'scheduled': [('readonly', False)]})
    move_id = fields.Many2one('account.move', string='Invoice #')
    # ------------- location details
    location = fields.Char(string='Mobile location')
    service = fields.Char()
    # ------------ Patient Uploaded Documents
    attached_file = fields.Binary("Attached File 1", readonly=True, states={'scheduled': [('readonly', False)]})
    attached_file_2 = fields.Binary("Attached File 2", readonly=True, states={'scheduled': [('readonly', False)]})
    patient_comment = fields.Text(readonly=True, states={'scheduled': [('readonly', False)]})
    # ------------ Call Center Comment
    checkup_comment = fields.Text(readonly=True, states={'scheduled': [('readonly', False)]})
    chief_complaint = fields.Char(string='Chief Complaint', readonly=True, states={'start': [('readonly', False)]})

    jitsi_link = fields.Text()  # mobile jitsi link
    invitation_text_jitsi = fields.Html(string='Invitation Link', readonly=True)
    comments = fields.Text(string='Comments', readonly=True,
                           states={'start': [('readonly', False)], 'scheduled': [('readonly', False)]})
    start_process_date = fields.Datetime(string='PROC. STRT. at', readonly=True)
    complete_process_date = fields.Datetime(string='PROC. CMPLT. at', readonly=True)

    send_sms_doctor = fields.Boolean()
    send_sms_patient = fields.Boolean()

    meeting_id = fields.Many2one('calendar.event', string='Calendar', copy=False)

    urgency_level = fields.Selection(URGENCY_LEVEL, string='Urgency Level', readonly=True,
                                     states={'Scheduled': [('readonly', False)]}, default=lambda *a: 'Normal')

    patient_status = fields.Selection(PATIENT_STATUS, string='Patient Status', readonly=True,
                                      states={'Scheduled': [('readonly', False)]}, default=lambda *a: 'Inpatient')
    payment_method_name = fields.Char(string="Payment Method Name")

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('sm.telemedicine.appointment')
        return super(ShifaTeleAppointment, self).create(vals)

    def send_sms_appointment(self):
        for rec in self:
            # print(rec.doctor.mobile)
            # appointment = False
            if rec.doctor.mobile:
                pa_msg = ""
                dr_msg = ""
                my_model = rec._name
                appointment = self.convert_utc_to_local(str(rec.appointment_date))
                pa_msg = "تم حجز موعد الاستشارة الطبية فيديو ل %s في تاريخ: %s الساعة :%s مع تمنياتنا لكم بدوام الصحة" % (
                    rec.patient.name, appointment[:11], appointment[11:])
                dr_msg = "تم حجز موعد الاستشارة الطبية فيديو ل %s في تاريخ: %s الساعة :%s " % (
                    rec.doctor.name, appointment[:11], appointment[11:])
                print(pa_msg)
                print(dr_msg)
                rec.send_sms(rec.patient.mobile, pa_msg, my_model, rec.id)
                rec.send_sms(rec.doctor.mobile, dr_msg, my_model, rec.id)
                rec.send_sms_doctor = True
                rec.send_sms_patient = True
            elif not rec.doctor.mobile:
                raise UserError(_('mobile number for {} is not exist'.format(rec.doctor.name)))

    @api.onchange('appointment_date_only')
    def _onchange_date(self):
        if self.appointment_date_only:
            a = datetime.strptime(str(self.appointment_date_only), "%Y-%m-%d")
            self.day = str(a.strftime("%A"))
            # self.appointment_day = self.day

    def create_jitsi_meeting(self):
        # server_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url') #+ '/videocall'
        server_url = self.env['ir.config_parameter'].sudo().get_param('oehealth_jitsi.video_call_server_url')
        appointment = self.env['sm.telemedicine.appointment'].browse(int(self.id))
        meeting_link = server_url + '/' + self._get_meeting_code()
        invitation_text = _("<a href='%s' target='_blank'>Click here to start meeting</a>") % meeting_link

        appointment.write({
            'invitation_text_jitsi': invitation_text,
            'jitsi_link': meeting_link,
        })

    def _get_meeting_code(self):
        return str(uuid.uuid4()).replace('-', '')

    def set_to_confirmed(self):
        self.create_jitsi_meeting()
        # comment next line for sms send
        # self.send_sms_appointment()
        self.calendar_appointment_event()
        return self.write({'state': 'confirmed'})

    # def set_to_start(self):
    #     for acc in self:
    #         invoice_lines = []
    #         consultancy_invoice_lines = []
    #         default_journal = self._get_default_journal()
    #         if acc.insurance:
    #             partner_val = acc.insurance.partner_id.id
    #         else:
    #             partner_val = acc.patient.partner_id.id
    #
    #         if not default_journal:
    #             raise UserError(_('No accounting journal with type "Sale" defined !'))
    #
    #         # Prepare Invoice lines
    #         consultancy_invoice_lines.append((0, 0, {
    #             'name': 'Consultancy',
    #             'display_type': 'line_section',
    #             'account_id': False,
    #             'sequence': 1,
    #         }))
    #         consultancy_invoice_lines.append((0, 0, {
    #             'display_type': False,
    #             'quantity': 1.0,
    #             'name': 'Consultancy Charge for ' + acc.name,
    #             'price_unit': acc.doctor.consultancy_price,
    #             'product_uom_id': self.env.ref('uom.product_uom_unit') and self.env.ref(
    #                 'uom.product_uom_unit').id or False,
    #             'sequence': 2,
    #         }))
    #
    #         # Create Invoice
    #         invoice = self.env['account.move'].sudo().create({
    #             'move_type': 'out_invoice',
    #             'journal_id': default_journal.id,
    #             'partner_id': partner_val,
    #             'patient': acc.patient.id,
    #             'invoice_date': datetime.now().date(),
    #             'date': datetime.now().date(),
    #             'ref': "Appointment : " + acc.name,
    #             'appointment': acc.id,
    #             'invoice_line_ids': consultancy_invoice_lines
    #         })
    #         if self.env.company.stock_deduction_method == 'invoice_create':
    #             invoice.oeh_process_inventories()
    #         acc.write({'state': 'start', 'move_id': invoice.id, 'start_process_date': datetime.now()})
    #     return True

    def _get_default_journal(self):
        journal = self.env['account.journal'].search([('type', '=', 'sale')], limit=1)
        return journal

    def set_back_to_call_center(self):
        return self.write({'state': 'scheduled'})

    def _reset_token_number_sequences(self):
        # just use write directly on the result this will execute one update query
        sequences = self.env['ir.sequence'].search([('name', '=', 'Tele Appointments')])
        sequences.write({'number_next_actual': 1})

    def unlink(self):
        return super(ShifaTeleAppointment, self).unlink()

    def download_pdf(self):
        for rec in self:
            if not rec.pres_tele_line:
                raise ValidationError(_("No Prescription to print"))
            else:
                therapist_obj = self.env['oeh.medical.prescription']
                domain = [('tele_appointment', '=', self.id)]
                pres_id = therapist_obj.search(domain)
                return self.env.ref('smartmind_shifa.sm_shifa_report_patient_prescriptions').report_action(pres_id)

    @api.onchange('ssn')
    def get_patient(self):
        ssn = self.ssn
        if ssn:
            therapist_obj = self.env['oeh.medical.patient']
            domain = [('ssn', '=', self.ssn)]
            patient_id = therapist_obj.search(domain)
            self.patient = patient_id
            print(patient_id.name)

    def _check_sms(self):
        appointment = self.search([
            ('state', '=', 'confirmed'),
        ])
        if appointment:
            for rec in appointment:
                pa_msg = ""
                dr_msg = ""
                my_model = rec._name
                if not (rec.send_sms_patient and rec.send_sms_doctor):
                    appointment = rec.convert_utc_to_local(str(rec.appointment_date))
                    pa_msg = "تم حجز موعد الاستشارة الطبية فيديو ل %s في تاريخ: %s الساعة :%s مع تمنياتنا لكم بدوام الصحة" % (
                        rec.patient.name, appointment[:11], appointment[11:])
                    dr_msg = "تم حجز موعد الاستشارة الطبية فيديو ل %s في تاريخ: %s الساعة :%s " % (
                        rec.doctor.name, appointment[:11], appointment[11:])
                    print(pa_msg)
                    print(dr_msg)
                    rec.send_sms(rec.patient.mobile, pa_msg, my_model, rec.id)
                    rec.send_sms(rec.doctor.mobile, dr_msg, my_model, rec.id)
                    rec.send_sms_doctor = True
                    rec.send_sms_patient = True

    def _before_30min_sms_alarm(self):
        appointment = self.search([
            ('state', '=', 'confirmed'),
        ])
        if appointment:
            for rec in appointment:
                pa_msg = ""
                dr_msg = ""
                my_model = rec._name
                if rec.appointment_date_only == datetime.now().date():
                    reminder_time = rec.appointment_time - 0.5
                    reminder_sms_time = '{0:02.0f}:{1:02.0f}'.format(*divmod(reminder_time * 60, 60))
                    now_time = datetime.now() + timedelta(hours=3)
                    now_time_sms = now_time.strftime("%H:%M")
                    if reminder_sms_time == now_time_sms:
                        appointment = rec.convert_utc_to_local(str(rec.appointment_date))
                        pa_msg = "نذكركم بموعد الاستشارة الطبية فيديو ل %s في تاريخ: %s الساعة :%s مع تمنياتنا لكم بدوام الصحة" % (
                            rec.patient.name, appointment[:11], appointment[11:])
                        dr_msg = "نذكركم بموعد الاستشارة الطبية فيديو ل %s في تاريخ: %s الساعة :%s " % (
                            rec.doctor.name, appointment[:11], appointment[11:])
                        rec.send_sms(rec.patient.mobile, pa_msg, my_model, rec.id)
                        rec.send_sms(rec.doctor.mobile, dr_msg, my_model, rec.id)

    def convert_utc_to_local(self, date):
        date_format = "%Y-%m-%d %H:%M:%S"
        print(self.env.user.tz)
        print(pytz.timezone('Asia/Riyadh'))
        _logger.error(self.env.user.tz)
        _logger.error(pytz.utc)
        user_tz = self.env.user.tz or 'Asia/Riyadh'
        local = pytz.timezone(user_tz)
        local_date = datetime.strftime(
            pytz.utc.localize(datetime.strptime(date.split('.')[0], date_format)).astimezone(local),
            date_format)
        return str(local_date)

    def send_sms(self, mobile, msg, model, rec_id):
        gatewayurl_id = self.env['gateway_setup'].search([], limit=1)
        if gatewayurl_id and gatewayurl_id.gateway_url:
            try:
                self.env['gateway_setup'].sudo().send_sms_link(msg, mobile, rec_id, model, gatewayurl_id)
            except Exception as e:
                _logger.error(e)
        else:
            raise ValidationError(_("The SMS Gateway is not configured"))

    def calendar_appointment_event(self):
        print(self.duration)
        for rec in self:
            meeting_values = {
                'name': rec.display_name,
                'duration': rec.duration,
                'description': " Telemedicine Appointment",
                'user_id': rec.doctor.oeh_user_id.id,
                'start': rec.appointment_date,
                'stop': rec.appointment_date + timedelta(hours=1),
                'allday': False,
                'recurrency': False,
                'privacy': 'confidential',
                'event_tz': rec.doctor.oeh_user_id.tz,
                'activity_ids': [(5, 0, 0)],
            }

            # Add the partner_id (if exist) as an attendee
            if rec.doctor.oeh_user_id and rec.doctor.oeh_user_id.partner_id:
                meeting_values['partner_ids'] = [
                    (4, rec.doctor.oeh_user_id.partner_id.id)]

        meetings = self.env['calendar.event'].with_context(
            no_mail_to_attendees=True,
            active_model=self._name
        ).create(meeting_values)
        for meeting in meetings:
            self.meeting_id = meeting


class ShifaAppointmentInSaleOrder(models.Model):
    _inherit = 'sale.order'

    tele_appointment = fields.Many2one('sm.telemedicine.appointment', string="Telemedicine Appointment #")


class SmartMindShifaDoctorScheduleTimeSlot(models.Model):
    _inherit = "sm.telemedicine.appointment"

    @api.onchange('appointment_date_only', 'appointment_time')
    def _get_appointment_date(self):
        for apm in self:
            if apm.appointment_date_only:
                apm.appointment_date = datetime.strptime(apm.appointment_date_only.strftime("%Y-%m-%d %H:%M:%S"),
                                                         "%Y-%m-%d %H:%M:%S") + timedelta(
                    hours=apm.appointment_time - 3)

    # Calculating Appointment End date
    @api.depends('appointment_date', 'doctor', 'appointment_date_only')
    def _get_appointment_end(self):
        for rec in self:
            if rec.appointment_date_only and rec.doctor:
                schedule_list = self.env['oeh.medical.physician.line'].sudo().search(
                    [('physician_id', '=', int(rec.doctor.id)), ('date', '=', rec.appointment_date_only)], limit=1)
                rec.appointment_end = datetime.strptime(rec.appointment_date.strftime("%Y-%m-%d %H:%M:%S"),
                                                        "%Y-%m-%d %H:%M:%S") + timedelta(minutes=schedule_list.duration)

    # APPOINTMENT DATES-------------------------------------------------------------------------------------------------
    appointment_date_only = fields.Date(string='Date', readonly=False,
                                        states={'Start': [('readonly', True)], 'Confirmed': [('readonly', True)],
                                                'Completed': [('readonly', True)], 'canceled': [('readonly', True)]},
                                        default=lambda *a: datetime.now())
    appointment_time = fields.Float(string='Time (HH:MM)', readonly=True)
    timeslot = fields.Many2one('sm.shifa.physician.schedule.timeslot', string='Timeslot',
                               domain="[('physician_id', '=', doctor), ('date', '=', appointment_date_only), ('is_available', '=', True)]",
                               states={'Start': [('readonly', True)], 'Confirmed': [('readonly', True)],
                                       'Completed': [('readonly', True)], 'canceled': [('readonly', True)]})
    appointment_date = fields.Datetime(compute=_get_appointment_date, string='Apt. DateTime', readonly=False, store=True)  #
    appointment_end = fields.Datetime(compute=_get_appointment_end, string='Apt. End Date', store=True)

    # ------------------------------------------------------------------------------------------------------------------

    @api.onchange('timeslot')
    def onchange_timeslot(self):
        if self.timeslot:
            hm = self.timeslot.available_time.split(':')
            sch_time = int(hm[0]) + int(hm[1]) / 60
            print('time: ', str(sch_time))
            self.appointment_time = sch_time

    def timeslot_is_available(self, tm_id, action):
        print('timeslot id', str(tm_id))
        timeslot = self.env['sm.shifa.physician.schedule.timeslot'].sudo().browse(int(tm_id))
        print('timeslot', str(timeslot.available_time))
        print('action', str(action))
        timeslot.sudo().write({
            'is_available': action,
        })

    def active_timeslot(self):
        for rec in self.filtered(lambda rec: rec.state in ['Scheduled', 'Confirmed']):
            self.timeslot_is_available(self.timeslot, True)

    @api.model
    def create(self, vals):
        doc_time = vals.get('timeslot')
        if doc_time:
            self.timeslot_is_available(vals['timeslot'], False)
        return super(SmartMindShifaDoctorScheduleTimeSlot, self).create(vals)

    def write(self, vals):
        for rec in self:
            if rec.timeslot:
                self.timeslot_is_available(rec.timeslot, False)
        return super(SmartMindShifaDoctorScheduleTimeSlot, self).write(vals)

    def unlink(self):
        self.active_timeslot()
        return super(SmartMindShifaDoctorScheduleTimeSlot, self).unlink()

    def set_to_canceled(self):
        self.active_timeslot()
        return self.write({'state': 'canceled'})


class ShifaTeleAppointmentMedicalCareTab(models.Model):
    _inherit = "sm.telemedicine.appointment"

    PATIENT_CONDITION = [
        ('Declined', 'Declined'),
        ('Unstable', 'Unstable'),
        ('Unchanged', 'Unchanged'),
        ('Improved', 'Improved'),
        ('Stable', 'Stable'),
    ]
    PROGNOSIS = [
        ('Poor', 'Poor'),
        ('Guarded', 'Guarded'),
        ('Fair', 'Fair'),
        ('Good', 'Good'),
        ('Excellent', 'Excellent'),
    ]
    # medical care plan tab
    medical_care_plan = fields.Text(string='Medical Care Plan', readonly=True, states={'start': [('readonly', False)]})
    program_chronic_anticoagulation = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    program_general_nursing_care = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    program_wound_care = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    program_palliative_care = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    program_acute_anticoagulation = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    program_home_infusion = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    program_other = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    program_other_text = fields.Text(readonly=True, states={'start': [('readonly', False)]})
    services_provided_oxygen_dependent = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    services_provided_tracheostomy = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    services_provided_wound_care = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    services_provided_pain_management = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    services_provided_hydration_therapy = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    services_provided_o2_via_nasal_cannula = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    services_provided_hypodermoclysis = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    services_provided_tpn = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    services_provided_stoma_care = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    services_provided_peg_tube = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    services_provided_inr_monitoring = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    services_provided_prevention_pressure = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    services_provided_vac_therapy = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    services_provided_drain_tube = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    services_provided_medication_management = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    services_provided_warfarin_stabilization = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    services_provided_parenteral_antimicrobial = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    services_provided_indwelling_foley_catheter = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    services_provided_ngt = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    services_provided_other = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    services_provided_other_text = fields.Text(readonly=True, states={'start': [('readonly', False)]})
    patient_condition = fields.Selection(PATIENT_CONDITION, readonly=True, states={'start': [('readonly', False)]})
    prognosis = fields.Selection(PROGNOSIS, readonly=True, states={'start': [('readonly', False)]})
    potential_risk = fields.Text(readonly=True, states={'start': [('readonly', False)]})
    admission_goal = fields.Text(readonly=True, states={'start': [('readonly', False)]})
    final_plan = fields.Text(readonly=True, states={'start': [('readonly', False)]})


class ShifaTeleAppointmentDiagnosisTab(models.Model):
    _inherit = 'sm.telemedicine.appointment'

    # diagnosis tab
    provisional_diagnosis = fields.Many2one('oeh.medical.pathology', string='Disease', readonly=True,
                                            states={'start': [('readonly', False)]})
    provisional_diagnosis_add_other = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    provisional_diagnosis_add = fields.Many2one('oeh.medical.pathology', string='Disease', readonly=True,
                                                states={'start': [('readonly', False)]})
    provisional_diagnosis_add_other2 = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    provisional_diagnosis_add2 = fields.Many2one('oeh.medical.pathology', string='Disease', readonly=True,
                                                 states={'start': [('readonly', False)]})
    provisional_diagnosis_add_other3 = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    provisional_diagnosis_add3 = fields.Many2one('oeh.medical.pathology', string='Disease', readonly=True,
                                                 states={'start': [('readonly', False)]})

    differential_diagnosis = fields.Many2one('oeh.medical.pathology', string='Disease', readonly=True,
                                             states={'start': [('readonly', False)]})

    differential_diagnosis_add = fields.Many2one('oeh.medical.pathology', string='Disease', readonly=True,
                                                 states={'start': [('readonly', False)]})
    differential_diagnosis_add_other = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})


class ShifaTeleAppointmentHistoryTab(models.Model):
    _inherit = 'sm.telemedicine.appointment'

    YES_NO = [
        ('yes', 'Yes'),
        ('no', 'No'),
    ]
    # History tab
    # History of present illness
    history_present_illness_show = fields.Boolean()
    history_present_illness = fields.Text(readonly=False,
                                          states={'scheduled': [('readonly', True)], 'confirmed': [('readonly', True)],
                                                  'completed': [('readonly', True)]})
    # review systems details
    review_systems_show = fields.Boolean()
    constitutional = fields.Boolean(readonly=False,
                                    states={'scheduled': [('readonly', True)], 'confirmed': [('readonly', True)],
                                            'completed': [('readonly', True)]})
    constitutional_content = fields.Char(readonly=False,
                                         states={'scheduled': [('readonly', True)], 'confirmed': [('readonly', True)],
                                                 'completed': [('readonly', True)]})
    head = fields.Boolean(default=True, readonly=False,
                          states={'scheduled': [('readonly', True)], 'confirmed': [('readonly', True)],
                                  'completed': [('readonly', True)]})
    head_content = fields.Char(readonly=False,
                               states={'scheduled': [('readonly', True)], 'confirmed': [('readonly', True)],
                                       'completed': [('readonly', True)]})
    cardiovascular = fields.Boolean(default=True, readonly=False,
                                    states={'scheduled': [('readonly', True)], 'confirmed': [('readonly', True)],
                                            'completed': [('readonly', True)]})
    cardiovascular_content = fields.Char(readonly=False,
                                         states={'scheduled': [('readonly', True)], 'confirmed': [('readonly', True)],
                                                 'completed': [('readonly', True)]})
    pulmonary = fields.Boolean(default=True, readonly=False,
                               states={'scheduled': [('readonly', True)], 'confirmed': [('readonly', True)],
                                       'completed': [('readonly', True)]})
    pulmonary_content = fields.Char(readonly=False,
                                    states={'scheduled': [('readonly', True)], 'confirmed': [('readonly', True)],
                                            'completed': [('readonly', True)]})
    gastroenterology = fields.Boolean(default=True, readonly=False,
                                      states={'scheduled': [('readonly', True)], 'confirmed': [('readonly', True)],
                                              'completed': [('readonly', True)]})
    gastroenterology_content = fields.Char(readonly=False,
                                           states={'scheduled': [('readonly', True)], 'confirmed': [('readonly', True)],
                                                   'completed': [('readonly', True)]})
    genitourinary = fields.Boolean(default=True, readonly=False,
                                   states={'scheduled': [('readonly', True)], 'confirmed': [('readonly', True)],
                                           'completed': [('readonly', True)]})
    genitourinary_content = fields.Char(readonly=False,
                                        states={'scheduled': [('readonly', True)], 'confirmed': [('readonly', True)],
                                                'completed': [('readonly', True)]})
    dermatological = fields.Boolean(default=True, readonly=False,
                                    states={'scheduled': [('readonly', True)], 'confirmed': [('readonly', True)],
                                            'completed': [('readonly', True)]})
    dermatological_content = fields.Char(readonly=False,
                                         states={'scheduled': [('readonly', True)], 'confirmed': [('readonly', True)],
                                                 'completed': [('readonly', True)]})
    musculoskeletal = fields.Boolean(default=True, readonly=False,
                                     states={'scheduled': [('readonly', True)], 'confirmed': [('readonly', True)],
                                             'completed': [('readonly', True)]})
    musculoskeletal_content = fields.Char(readonly=False,
                                          states={'scheduled': [('readonly', True)], 'confirmed': [('readonly', True)],
                                                  'completed': [('readonly', True)]})
    neurological = fields.Boolean(default=True, readonly=False,
                                  states={'scheduled': [('readonly', True)], 'confirmed': [('readonly', True)],
                                          'completed': [('readonly', True)]})
    neurological_content = fields.Char(readonly=False,
                                       states={'scheduled': [('readonly', True)], 'confirmed': [('readonly', True)],
                                               'completed': [('readonly', True)]})
    psychiatric = fields.Boolean(default=True, readonly=False,
                                 states={'scheduled': [('readonly', True)], 'confirmed': [('readonly', True)],
                                         'completed': [('readonly', True)]})
    psychiatric_content = fields.Char(readonly=False,
                                      states={'scheduled': [('readonly', True)], 'confirmed': [('readonly', True)],
                                              'completed': [('readonly', True)]})
    endocrine = fields.Boolean(default=True, readonly=False,
                               states={'scheduled': [('readonly', True)], 'confirmed': [('readonly', True)],
                                       'completed': [('readonly', True)]})
    endocrine_content = fields.Char(readonly=False,
                                    states={'scheduled': [('readonly', True)], 'confirmed': [('readonly', True)],
                                            'completed': [('readonly', True)]})
    hematology = fields.Boolean(default=True, readonly=False,
                                states={'scheduled': [('readonly', True)], 'confirmed': [('readonly', True)],
                                        'completed': [('readonly', True)]})
    hematology_content = fields.Char(readonly=False,
                                     states={'scheduled': [('readonly', True)], 'confirmed': [('readonly', True)],
                                             'completed': [('readonly', True)]})

    # Past medical History
    past_medical_history_show = fields.Boolean()
    past_medical_history = fields.Many2one('oeh.medical.pathology', string='Disease', readonly=False,
                                           states={'scheduled': [('readonly', True)], 'confirmed': [('readonly', True)],
                                                   'completed': [('readonly', True)]},
                                           related='patient.past_medical_history')

    past_medical_history_date = fields.Date(string='Date', readonly=False, states={'scheduled': [('readonly', True)],
                                                                                   'confirmed': [('readonly', True)],
                                                                                   'completed': [('readonly', True)]},
                                            related='patient.past_medical_history_date')
    past_medical_history_1st_add = fields.Many2one('oeh.medical.pathology.category', string='Disease',
                                                   readonly=False, states={'scheduled': [('readonly', True)],
                                                                           'confirmed': [('readonly', True)],
                                                                           'completed': [('readonly', True)]},
                                                   related='patient.past_medical_history_1st_add')
    past_medical_history_1st_add_other = fields.Boolean(readonly=False, states={'scheduled': [('readonly', True)],
                                                                                'confirmed': [('readonly', True)],
                                                                                'completed': [('readonly', True)]},
                                                        related='patient.past_medical_history_1st_add_other')
    past_medical_history_1st_add_date = fields.Date(string='Date', readonly=False,
                                                    states={'scheduled': [('readonly', True)],
                                                            'confirmed': [('readonly', True)],
                                                            'completed': [('readonly', True)]},
                                                    related='patient.past_medical_history_1st_add_date')

    past_medical_history_2nd_add = fields.Many2one('oeh.medical.pathology.category', string='Disease',
                                                   readonly=False, states={'scheduled': [('readonly', True)],
                                                                           'confirmed': [('readonly', True)],
                                                                           'completed': [('readonly', True)]},
                                                   related='patient.past_medical_history_2nd_add')
    past_medical_history_2nd_add_date = fields.Date(string='Date', readonly=False,
                                                    states={'scheduled': [('readonly', True)],
                                                            'confirmed': [('readonly', True)],
                                                            'completed': [('readonly', True)]},
                                                    related='patient.past_medical_history_2nd_add_date')
    past_medical_history_2nd_add_other = fields.Boolean(readonly=False, states={'scheduled': [('readonly', True)],
                                                                                'confirmed': [('readonly', True)],
                                                                                'completed': [('readonly', True)]},
                                                        related='patient.past_medical_history_2nd_add_other')

    # Surgical History
    surgical_history_show = fields.Boolean()
    surgical_history_procedures = fields.Many2one('oeh.medical.procedure', string='Procedures', readonly=False,
                                                  states={'scheduled': [('readonly', True)],
                                                          'confirmed': [('readonly', True)],
                                                          'completed': [('readonly', True)]},
                                                  related='patient.surgical_history_procedures')
    surgical_history_procedures_date = fields.Date(string='Date', readonly=False,
                                                   states={'scheduled': [('readonly', True)],
                                                           'confirmed': [('readonly', True)],
                                                           'completed': [('readonly', True)]},
                                                   related='patient.surgical_history_procedures_date')

    surgical_history_procedures_1st_add_other = fields.Boolean(readonly=False,
                                                               states={'scheduled': [('readonly', True)],
                                                                       'confirmed': [('readonly', True)],
                                                                       'completed': [('readonly', True)]},
                                                               related='patient.surgical_history_procedures_1st_add_other')
    surgical_history_procedures_1st_add = fields.Many2one('oeh.medical.procedure', string='Procedures',
                                                          readonly=False, states={'scheduled': [('readonly', True)],
                                                                                  'confirmed': [('readonly', True)],
                                                                                  'completed': [('readonly', True)]},
                                                          related='patient.surgical_history_procedures_1st_add')
    surgical_history_procedures_1st_add_date = fields.Date(string='Date', readonly=False,
                                                           states={'scheduled': [('readonly', True)],
                                                                   'confirmed': [('readonly', True)],
                                                                   'completed': [('readonly', True)]},
                                                           related='patient.surgical_history_procedures_1st_add_date')

    surgical_history_procedures_2nd_add_other = fields.Boolean(readonly=False,
                                                               states={'scheduled': [('readonly', True)],
                                                                       'confirmed': [('readonly', True)],
                                                                       'completed': [('readonly', True)]},
                                                               related='patient.surgical_history_procedures_2nd_add_other')
    surgical_history_procedures_2nd_add = fields.Many2one('oeh.medical.procedure', string='Procedures',
                                                          readonly=False, states={'scheduled': [('readonly', True)],
                                                                                  'confirmed': [('readonly', True)],
                                                                                  'completed': [('readonly', True)]},
                                                          related='patient.surgical_history_procedures_2nd_add')
    surgical_history_procedures_2nd_add_date = fields.Date(string='Date', readonly=False,
                                                           states={'scheduled': [('readonly', True)],
                                                                   'confirmed': [('readonly', True)],
                                                                   'completed': [('readonly', True)]},
                                                           related='patient.surgical_history_procedures_2nd_add_date')
    # Family History
    family_history_show = fields.Boolean()
    family_history = fields.Text(readonly=False,
                                 states={'scheduled': [('readonly', True)], 'confirmed': [('readonly', True)],
                                         'completed': [('readonly', True)]}, related='patient.family_history')

    @api.onchange('has_drug_allergy', 'has_food_allergy', 'has_other_allergy')
    def get_selection(self):
        if self.has_drug_allergy == "yes":
            self.drug_allergy = True
        else:
            self.drug_allergy = False

        if self.has_food_allergy == "yes":
            self.food_allergy = True
        else:
            self.food_allergy = False

        if self.has_other_allergy == "yes":
            self.other_allergy = True
        else:
            self.other_allergy = False

    @api.onchange('drug_allergy', 'food_allergy', 'other_allergy')
    def get_selection(self):
        print(self.drug_allergy)
        if self.drug_allergy:
            self.has_drug_allergy = "yes"
        else:
            self.has_drug_allergy = "no"

        if self.food_allergy:
            self.has_food_allergy = "yes"
        else:
            self.has_food_allergy = "no"

        if self.other_allergy:
            self.has_other_allergy = "yes"
        else:
            self.has_other_allergy = "no"

    # Allergies
    allergies_show = fields.Boolean()
    has_drug_allergy = fields.Selection(YES_NO, string='Drug Allergy', readonly=False,
                                        related='patient.has_drug_allergy',
                                        states={'scheduled': [('readonly', True)], 'confirmed': [('readonly', True)],
                                                'completed': [('readonly', True)]})
    drug_allergy = fields.Boolean(default=False, readonly=False,
                                  states={'scheduled': [('readonly', True)], 'confirmed': [('readonly', True)],
                                          'completed': [('readonly', True)]},
                                  related='patient.drug_allergy')
    drug_allergy_content = fields.Char(readonly=False,
                                       states={'scheduled': [('readonly', True)], 'confirmed': [('readonly', True)],
                                               'completed': [('readonly', True)]},
                                       related='patient.drug_allergy_content')

    has_food_allergy = fields.Selection(YES_NO, string='Food Allergy', readonly=False,
                                        related='patient.has_food_allergy',
                                        states={'scheduled': [('readonly', True)], 'confirmed': [('readonly', True)],
                                                'completed': [('readonly', True)]})
    food_allergy = fields.Boolean(default=False, readonly=False,
                                  states={'scheduled': [('readonly', True)], 'confirmed': [('readonly', True)],
                                          'completed': [('readonly', True)]},
                                  related='patient.food_allergy')
    food_allergy_content = fields.Char(readonly=False,
                                       states={'scheduled': [('readonly', True)], 'confirmed': [('readonly', True)],
                                               'completed': [('readonly', True)]},
                                       related='patient.food_allergy_content')

    has_other_allergy = fields.Selection(YES_NO, string='Other Allergy', readonly=False,
                                         related='patient.has_other_allergy',
                                         states={'scheduled': [('readonly', True)], 'confirmed': [('readonly', True)],
                                                 'completed': [('readonly', True)]})
    other_allergy = fields.Boolean(default=False, readonly=False,
                                   states={'scheduled': [('readonly', True)], 'confirmed': [('readonly', True)],
                                           'completed': [('readonly', True)]},
                                   related='patient.other_allergy')
    other_allergy_content = fields.Char(readonly=False,
                                        states={'scheduled': [('readonly', True)], 'confirmed': [('readonly', True)],
                                                'completed': [('readonly', True)]},
                                        related='patient.other_allergy_content')

    # Personal Habits
    personal_habits_show = fields.Boolean()
    # Physical Exercise
    exercise = fields.Boolean(string='Exercise', readonly=False,
                              states={'scheduled': [('readonly', True)], 'confirmed': [('readonly', True)],
                                      'completed': [('readonly', True)]}, related='patient.exercise')
    exercise_minutes_day = fields.Integer(string='Minutes / day',
                                          help="How many minutes a day the patient exercises",
                                          readonly=False,
                                          states={'scheduled': [('readonly', True)], 'confirmed': [('readonly', True)],
                                                  'completed': [('readonly', True)]},
                                          related='patient.exercise_minutes_day')
    # sleep
    sleep_hours = fields.Integer(string='Hours of Sleep', help="Average hours of sleep per day", readonly=False,
                                 states={'scheduled': [('readonly', True)], 'confirmed': [('readonly', True)],
                                         'completed': [('readonly', True)]}, related='patient.sleep_hours')
    sleep_during_daytime = fields.Boolean(string='Sleeps at Daytime',
                                          help="Check if the patient sleep hours are during daylight rather than at night",
                                          readonly=False,
                                          states={'scheduled': [('readonly', True)], 'confirmed': [('readonly', True)],
                                                  'completed': [('readonly', True)]},
                                          related='patient.sleep_during_daytime')
    # Smoking
    smoking = fields.Boolean(string='Smokes', readonly=False,
                             states={'scheduled': [('readonly', True)], 'confirmed': [('readonly', True)],
                                     'completed': [('readonly', True)]}, related='patient.smoking')

    smoking_number = fields.Integer(string='Cigarretes a Day', readonly=False,
                                    states={'scheduled': [('readonly', True)], 'confirmed': [('readonly', True)],
                                            'completed': [('readonly', True)]}, related='patient.smoking_number')
    age_start_smoking = fields.Integer(string='Age started to Smoke', readonly=False,
                                       states={'scheduled': [('readonly', True)], 'confirmed': [('readonly', True)],
                                               'completed': [('readonly', True)]}, related='patient.age_start_smoking')

    ex_smoker = fields.Boolean(string='Ex-smoker', readonly=False,
                               states={'scheduled': [('readonly', True)], 'confirmed': [('readonly', True)],
                                       'completed': [('readonly', True)]}, related='patient.ex_smoker')
    age_start_ex_smoking = fields.Integer(string='Age started to Smoke', readonly=False,
                                          states={'scheduled': [('readonly', True)], 'confirmed': [('readonly', True)],
                                                  'completed': [('readonly', True)]},
                                          related='patient.age_start_ex_smoking')
    age_quit_smoking = fields.Integer(string='Age of Quitting', help="Age of quitting smoking", readonly=False,
                                      states={'scheduled': [('readonly', True)], 'confirmed': [('readonly', True)],
                                              'completed': [('readonly', True)]}, related='patient.age_quit_smoking')
    second_hand_smoker = fields.Boolean(string='Passive Smoker',
                                        help="Check it the patient is a passive / second-hand smoker",
                                        readonly=False,
                                        states={'scheduled': [('readonly', True)], 'confirmed': [('readonly', True)],
                                                'completed': [('readonly', True)]},
                                        related='patient.second_hand_smoker')
    # drink
    alcohol = fields.Boolean(string='Drinks Alcohol', readonly=False,
                             states={'scheduled': [('readonly', True)], 'confirmed': [('readonly', True)],
                                     'completed': [('readonly', True)]}, related='patient.alcohol')
    age_start_drinking = fields.Integer(string='Age started to Drink ', help="Date to start drinking",
                                        readonly=False,
                                        states={'scheduled': [('readonly', True)], 'confirmed': [('readonly', True)],
                                                'completed': [('readonly', True)]},
                                        related='patient.age_start_drinking')

    alcohol_beer_number = fields.Integer(string='Beer / day', readonly=False,
                                         states={'scheduled': [('readonly', True)], 'confirmed': [('readonly', True)],
                                                 'completed': [('readonly', True)]},
                                         related='patient.alcohol_beer_number')
    alcohol_liquor_number = fields.Integer(string='Liquor / day', readonly=False,
                                           states={'scheduled': [('readonly', True)], 'confirmed': [('readonly', True)],
                                                   'completed': [('readonly', True)]},
                                           related='patient.alcohol_liquor_number')
    ex_alcoholic = fields.Boolean(string='Ex Alcoholic', readonly=False,
                                  states={'scheduled': [('readonly', True)], 'confirmed': [('readonly', True)],
                                          'completed': [('readonly', True)]}, related='patient.ex_alcoholic')

    alcohol_wine_number = fields.Integer(string='Wine / day', readonly=False,
                                         states={'scheduled': [('readonly', True)], 'confirmed': [('readonly', True)],
                                                 'completed': [('readonly', True)]},
                                         related='patient.alcohol_wine_number')
    age_quit_drinking = fields.Integer(string='Age Quit Drinking ', help="Date to stop drinking", readonly=False,
                                       states={'scheduled': [('readonly', True)], 'confirmed': [('readonly', True)],
                                               'completed': [('readonly', True)]}, related='patient.age_quit_drinking')

    # Vaccination
    vaccination_show = fields.Boolean()
    Vaccination = fields.Many2one('sm.shifa.generic.vaccines', string='Vaccine', readonly=False,
                                  states={'scheduled': [('readonly', True)], 'confirmed': [('readonly', True)],
                                          'completed': [('readonly', True)]}, related='patient.Vaccination')
    vaccination_date = fields.Date(string='Date', readonly=False,
                                   states={'scheduled': [('readonly', True)], 'confirmed': [('readonly', True)],
                                           'completed': [('readonly', True)]}, related='patient.vaccination_date')

    Vaccination_1st_add_other = fields.Boolean(readonly=False, states={'scheduled': [('readonly', True)],
                                                                       'confirmed': [('readonly', True)],
                                                                       'completed': [('readonly', True)]},
                                               related='patient.Vaccination_1st_add_other')
    Vaccination_1st_add = fields.Many2one('sm.shifa.generic.vaccines', string='Procedures', readonly=False,
                                          states={'scheduled': [('readonly', True)], 'confirmed': [('readonly', True)],
                                                  'completed': [('readonly', True)]},
                                          related='patient.Vaccination_1st_add')
    Vaccination_1st_add_date = fields.Date(string='Date', readonly=False,
                                           states={'scheduled': [('readonly', True)], 'confirmed': [('readonly', True)],
                                                   'completed': [('readonly', True)]},
                                           related='patient.Vaccination_1st_add_date')

    Vaccination_2nd_add_other = fields.Boolean(readonly=False, states={'scheduled': [('readonly', True)],
                                                                       'confirmed': [('readonly', True)],
                                                                       'completed': [('readonly', True)]},
                                               related='patient.Vaccination_2nd_add_other')

    Vaccination_2nd_add = fields.Many2one('sm.shifa.generic.vaccines', string='Procedures', readonly=False,
                                          states={'scheduled': [('readonly', True)], 'confirmed': [('readonly', True)],
                                                  'completed': [('readonly', True)]},
                                          related='patient.Vaccination_2nd_add')
    Vaccination_2nd_add_date = fields.Date(string='Date', readonly=False,
                                           states={'scheduled': [('readonly', True)], 'confirmed': [('readonly', True)],
                                                   'completed': [('readonly', True)]},
                                           related='patient.Vaccination_2nd_add_date')

    @api.onchange('cardiovascular', 'constitutional', 'head', 'pulmonary', 'genitourinary', 'gastroenterology',
                  'dermatological', 'musculoskeletal', 'neurological', 'psychiatric', 'endocrine', 'hematology')
    def _onchange_cardiovascular(self):
        if self.cardiovascular:
            self.cardiovascular_content = ''
        if self.constitutional:
            self.constitutional_content = ''
        if self.head:
            self.head_content = ''
        if self.pulmonary:
            self.pulmonary_content = ''
        if self.genitourinary:
            self.genitourinary_content = ''
        if self.gastroenterology:
            self.gastroenterology_content = ''
        if self.dermatological:
            self.dermatological_content = ''
        if self.musculoskeletal:
            self.musculoskeletal_content = ''
        if self.neurological:
            self.neurological_content = ''
        if self.psychiatric:
            self.psychiatric_content = ''
        if self.endocrine:
            self.endocrine_content = ''
        if self.hematology:
            self.hematology_content = ''


class ShifaTeleAppointmentExaminationTab(models.Model):
    _inherit = 'sm.telemedicine.appointment'

    # Selection list
    PAIN_SCORE = [
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
        ('6', '6'),
        ('7', '7'),
        ('8', '8'),
        ('9', '9'),
        ('10', '10'),
    ]
    YES_NO = [
        ('yes', 'Yes'),
        ('no', 'No'),
    ]
    MUSCULOSKELETAL_EXTREMITY = [
        ('active_against_gravity_resistance', 'Active Against Gravity and Resistance'),
        ('active_with_gravity_eliminated', 'Active with Gravity Eliminated'),
        ('contracture', 'Contracture'),
        ('deformity', 'Deformity'),
        ('dislocation', 'Dislocation'),
        ('fracture', 'Fracture'),
        ('paralysis', 'Paralysis'),
        ('prosthesis', 'Prosthesis'),
        ('stiffness', 'Stiffness'),
        ('weak', 'Weak'),
        ('other', 'Other'),
    ]
    MUSCULOSKELETAL_GAIT = [
        ('normal', 'Normal'),
        ('asymmetrical', 'Asymmetrical'),
        ('dragging', 'Dragging'),
        ('impaired', 'Impaired'),
        ('jerky', 'Jerky'),
        ('shuffling', 'Shuffling'),
        ('spastic', 'Spastic'),
        ('steady', 'Steady'),
        ('unsteady', 'Unsteady'),
        ('wide_based', 'Wide Based'),
        ('other', 'Other'),
    ]
    NUMBER_NEURALOGICAL = [
        ('0.5', '0.5'),
        ('1', '1'),
        ('1.5', '1.5'),
        ('2', '2'),
        ('2.5', '2.5'),
        ('3', '3'),
        ('3.5', '3.5'),
        ('4', '4'),
        ('4.5', '4.5'),
        ('5', '5'),
        ('5.5', '5.5'),
        ('6', '6'),
        ('6.5', '6.5'),
        ('7', '7'),
        ('7.5', '7.5'),
        ('8', '8'),
        ('8.5', '8.5'),
        ('9', '9'),
        ('9.5', '9.5'),
    ]
    LEVEL_CONSCIOUSNESS = [
        ('alert', 'Alert'),
        ('awake', 'Awake'),
        ('decrease_response_environment', 'Decrease response to environment'),
        ('delirious', 'Delirious'),
        ('drowsiness', 'Drowsiness'),
        ('irritable', 'Irritable'),
        ('lathargy', 'Lathargy'),
        ('obtunded', 'Obtunded'),
        ('restless', 'Restless'),
        ('stuper', 'Stuper'),
        ('unresponsnsive', 'Unresponsnsive'),
    ]
    EYE_MOMEMENT = [
        ('spontaneous', 'Spontaneous'),
        ('to_speech', 'To speech'),
        ('to_pain', 'To pain'),
        ('no_respond', 'No respond'),
    ]
    SCALE_USED = [
        ('numerical', 'Numerical'),
        ('faces', 'Faces'),
        ('fLACC', 'FLACC'),
        ('aBBEY', 'ABBEY'),
    ]

    # CVS
    CVS_RHYTHM = [
        ('regular', 'Regular'),
        ('irregular', 'Irregular'),
        ('regular_irregular', 'Regular Irregular'),
        ('irregular_irregular', 'Irregular Irregular'),
    ]
    CVS_PERIPHERIAL = [
        ('normal_palpable', 'Normal Palpable'),
        ('absent_without_pulse', 'Absent Without Pulse'),
        ('diminished', 'Diminished'),
        ('bounding', 'Bounding'),
        ('full_brisk', 'Full and brisk'),
    ]
    CVS_EDEMA_TYPE = [
        ('pitting', 'Pitting'),
        ('non-pitting', 'Non-Pitting'),
    ]
    CVS_EDEMA_GRADE = [
        ('2mm_depth', 'I- 2mm Depth'),
        ('4mm_depth', 'II- 4mm Depth'),
        ('6mm_depth', 'III- 6mm Depth'),
        ('8mm_depth', 'IV- 8mm Depth'),
    ]
    CVS_EDEMA_CAPILLARY = [
        ('less_than', 'Less than'),
        ('2-3', '2-3'),
        ('3-4', '3-4'),
        ('4-5', '4-5'),
        ('more_than_5', 'More than 5'),
    ]
    CVS_PARENTERAL_DEVICES = [
        ('central_line', 'Central Line'),
        ('TPN', 'TPN'),
        ('IV_therapy', 'IV Therapy'),
        ('PICC_line', 'PICC Line'),
        ('other', 'Other'),
    ]
    # COUGH
    COUGH_TYPE = [
        ('productive', 'Productive'),
        ('none_productive', 'None-productive'),
        ('spontaneous', 'Spontaneous'),
    ]
    COUGH_FREQUENCY = [
        ('spontaneous', 'Spontaneous'),
        ('occassional', 'Occassional'),
        ('persistent', 'Persistent'),
    ]
    COUGH_AMOUNT = [
        ('scanty', 'Scanty'),
        ('moderate', 'Moderate'),
        ('large', 'Large'),
    ]
    COUGH_CHAR = [
        ('clear', 'Clear'),
        ('yellow', 'Yellow'),
        ('mucoid', 'Mucoid'),
        ('mucopurulent', 'Mucopurulent'),
        ('purulent', 'Purulent'),
        ('pink Frothy', 'Pink Frothy'),
        ('blood streaked', 'Blood streaked'),
        ('bloody', 'Bloody'),
    ]
    # SUCTION
    SUCTION_TYPE = [
        ('nasal', 'Nasal'),
        ('oral', 'Oral'),
        ('trachestory', 'Trachestory'),
    ]
    # NEURALOGICAL
    NEURALOGICAL_REACTION = [
        ('equal_round_reactive', 'Equal round, reactive'),
        ('equal_round_none_reactive', 'Equal round, none reactive'),
        ('miosis', 'Miosis'),
        ('mydriasis', 'Mydriasis'),
        ('sluggish', 'Sluggish'),
        ('brisk', 'Brisk'),
        ('elliptical', 'Elliptical'),
        ('anisocoria', 'Anisocoria'),
    ]
    NEURALOGICAL_OLD = [
        ('greater_than_5_old', 'Greater Than 5 years Old'),
        ('2_5_old', '2 to 5 Years Old'),
        ('less_2_old', 'Less than 2 Years Old'),
    ]
    NEURALOGICAL_GREATER_5_MENTAL = [
        ('alert', 'Alert'),
        ('disoriented', 'Disoriented'),
        ('lethargy', 'Lethargy'),
        ('minimally responsive', 'Minimally responsive'),
        ('no response', 'No response'),
        ('obtunded', 'Obtunded'),
        ('orient_person', 'Orient to person'),
        ('0rient_place', 'Orient to place'),
        ('orient_situation', 'Orient to situation'),
        ('orient_time', 'Orient to time'),
        ('stupor', 'Stupor'),
    ]
    NEURALOGICAL_GREATER_5_FACIAL = [
        ('symmetric', 'Symmetric'),
        ('unequal_facial_movement', 'Unequal facial movement'),
        ('drooping_left_side_face', 'Drooping left side of face'),
        ('drooping_left_side_mouth', 'Drooping left side of mouth'),
        ('drooping_right_side_face', 'Drooping right side of face'),
        ('drooping_right_side_mouth', 'Drooping right side of mouth'),
    ]
    NEURALOGICAL_LESS_2_MOTOR = [
        ('spontaneous_movements', 'Spontaneous movements'),
        ('localizes_pain', 'Localizes pain'),
        ('flexion_withdrawal', 'Flexion withdrawal'),
        ('abnormal_flexion', 'Abnormal flexion'),
        ('abnormal_extension', 'Abnormal extension'),
        ('no_response', 'No response'),
    ]
    NEURALOGICAL_LESS_2_VERBAL = [
        ('coos_smiles_appropriate', 'Coos and smiles appropriate'),
        ('cries', 'Cries'),
        ('inappropriate_crying_screaming', 'Inappropriate crying/screaming'),
        ('grunts', 'Grunts'),
        ('no_response', 'No response'),
    ]
    NEURALOGICAL_GREATER_5_VERBAL = [
        ('orient', 'Orient'),
        ('confused', 'Confused'),
        ('inappropriate', 'Inappropriate'),
        ('incompratensive', 'Incompratensive'),
        ('no_verable_response', 'No verable response'),
    ]
    NEURALOGICAL_2_5_VERBAL = [
        ('appropriate_words', 'Appropriate Words'),
        ('inappropriate_word', 'Inappropriate Word'),
        ('cries_screams', 'Cries/Screams'),
        ('grunts', 'Grunts'),
        ('no_response', 'No response'),
    ]
    MOTOR_RESPONSE = [
        ('obeys_command', 'Obeys command'),
        ('localizes_pain', 'Localizes pain'),
        ('withdraws_pain', 'Withdraws from pain'),
        ('flexion_response_pain', 'Flexion response to pain'),
        ('extension_response_pain', 'Extension response to pain'),
        ('no_motor_response', 'No motor response'),
    ]

    # GASTRINTESTINAL
    GASTRINTESTINAL_BOWEL_SOUND = [
        ('active', 'Active'),
        ('absent', 'Absent'),
        ('hypoactive', 'Hypoactive'),
        ('hyperactive', 'Hyperactive'),
    ]
    GASTRINTESTINAL_STOOL_COLOR = [
        ('brown', 'Brown'),
        ('yellow', 'Yellow'),
        ('black', 'Black'),
        ('bright_red', 'Bright Red'),
        ('dark_red', 'Dark Red'),
        ('clay', 'Clay'),
    ]
    # Genitourinary
    GENITOURINARY_URINE_COLOR = [
        ('pale_yellow', 'Pale Yellow'),
        ('dark_yellow', 'Dark Yellow'),
        ('yellow', 'Yellow'),
        ('tea_colored', 'Tea-Colored'),
        ('red', 'Red'),
        ('blood Tinged', 'Blood Tinged'),
        ('green', 'Green'),
    ]
    GENITOURINARY_URINE_APPERANCE = [
        ('clear', 'Clear'),
        ('cloudy', 'Cloudy'),
        ('with_sediment', 'With Sediment'),
    ]
    GENITOURINARY_URINE_AMOUNT = [
        ('adequate', 'Adequate'),
        ('scanty', 'Scanty'),
        ('large', 'Large'),
    ]
    GENITOURINARY_URINATION_ASSISTANCE = [
        ('none', 'None'),
        ('indwelling_catheter', 'Indwelling Catheter'),
        ('condom_catheter', 'Condom Catheter'),
        ('intermittent_bladder Wash', 'Intermittent bladder Wash'),
        ('urostomy', 'Urostomy'),
        ('suprapubic_catheter', 'Suprapubic Catheter'),
    ]

    # INTEGUMENTARY
    INTEGUMENTARY_TURGOR = [
        ('elastic', 'Elastic'),
        ('normal_for_age', 'Normal for age'),
        ('poor', 'Poor'),
    ]
    INTEGUMENTARY_TEMP = [
        ('normal', 'Normal'),
        ('cool', 'Cool'),
        ('cold', 'Cold'),
        ('warm', 'Warm'),
        ('hot', 'Hot'),
    ]
    cal_score_eye = {
        'spontaneous': 4,
        'to_speech': 3,
        'to_pain': 2,
        'no_respond': 1,
    }
    cal_score_motor = {
        'spontaneous_movements': 6,
        'localizes_pain': 5,
        'flexion_withdrawal': 4,
        'abnormal_flexion': 3,
        'Abnormal_extension': 2,
        'no_response': 1,
    }
    cal_score_verbal = {
        'coos_smiles_appropriate': 5,
        'cries': 4,
        'inappropriate_crying_screaming': 3,
        'grunts': 2,
        'no_response': 1,
    }
    cal_score_verbal_2_5 = {
        'appropriate_words': 5,
        'inappropriate_word': 4,
        'cries_screams': 3,
        'grunts': 2,
        'no_response': 1,
    }
    cal_score_verbal_5 = {
        'orient': 5,
        'confused': 4,
        'inappropriate': 3,
        'incompratensive': 2,
        'no_verable_response': 1,
    }
    motor_response_dec = {
        'obeys_command': 6,
        'localizes_pain': 5,
        'withdraws_from_pain': 4,
        'flexion_response_pain': 3,
        'extension_response_pain': 2,
        'no_motor_response': 1,
    }

    @api.depends("neuralogical_less_than_2_eye", "neuralogical_less_than_2_motor", "neuralogical_less_than_2_verbal")
    def _compute_less_2(self):
        sum_1, sum_2, sum_3 = 0, 0, 0
        for key, value in self.cal_score_eye.items():
            if self.neuralogical_less_than_2_eye == key:
                sum_1 = value
        for key, value in self.cal_score_motor.items():
            if self.neuralogical_less_than_2_motor == key:
                sum_2 = value
        for key, value in self.cal_score_verbal.items():
            if self.neuralogical_less_than_2_verbal == key:
                sum_3 = value
        for record in self:
            record.neuralogical_less_than_2_glascow = sum_1 + sum_2 + sum_3

    @api.depends("neuralogical_2_to_5_eye", "neuralogical_2_to_5_motor", "neuralogical_2_to_5_verbal")
    def _compute_2_5_old(self):
        sum_1, sum_2, sum_3 = 0, 0, 0
        for key, value in self.cal_score_eye.items():
            if self.neuralogical_2_to_5_eye == key:
                sum_1 = value
        for key, value in self.motor_response_dec.items():
            if self.neuralogical_2_to_5_motor == key:
                sum_2 = value
        for key, value in self.cal_score_verbal_2_5.items():
            if self.neuralogical_2_to_5_verbal == key:
                sum_3 = value
        for record in self:
            record.neuralogical_2_to_5_glascow = sum_1 + sum_2 + sum_3

    @api.depends("neuralogical_greater_than_5_years_eye", "neuralogical_greater_than_5_years_motor",
                 "neuralogical_greater_than_5_years_verbal")
    def _compute_greater_5_old(self):
        sum_1, sum_2, sum_3 = 0, 0, 0
        for key, value in self.cal_score_eye.items():
            if self.neuralogical_greater_than_5_years_eye == key:
                sum_1 = value
        for key, value in self.motor_response_dec.items():
            if self.neuralogical_greater_than_5_years_motor == key:
                sum_2 = value
        for key, value in self.cal_score_verbal_5.items():
            if self.neuralogical_greater_than_5_years_verbal == key:
                sum_3 = value
        for record in self:
            record.neuralogical_greater_than_5_years_glascow = sum_1 + sum_2 + sum_3
        # calculate bmi

    @api.depends('height', 'weight')
    def _compute_bmi(self):
        for r in self:
            if not r.height:
                return 0
            else:
                r.bmi = r.weight / (r.height * r.height) * 10000
                print(r.bmi)
                return r.bmi

    # Examination tab
    vital_signs_show = fields.Boolean()
    temperature = fields.Float(string="Temperature (c)", readonly=True, states={'start': [('readonly', False)]})
    systolic = fields.Integer(string="Systolic BP(mmHg)", readonly=True, states={'start': [('readonly', False)]})
    respiratory_rate = fields.Integer(string="RR (/min)", readonly=True,
                                      states={'start': [('readonly', False)]})
    at_room_air = fields.Boolean(string="at room air", readonly=True, states={'start': [('readonly', False)]})
    with_oxygen_support = fields.Boolean(string="with oxygen Support", readonly=True,
                                         states={'start': [('readonly', False)]})
    char_other_oxygen = fields.Char(readonly=True, states={'start': [('readonly', False)]})
    diastolic = fields.Integer(string="Diastolic BR(mmHg)", readonly=True,
                               states={'start': [('readonly', False)]})
    bpm = fields.Integer(string="HR (/min)", readonly=True, states={'start': [('readonly', False)]})
    # metabolic
    metabolic_show = fields.Boolean()
    weight = fields.Float(string='Weight (kg)', readonly=True, states={'start': [('readonly', False)]})
    waist_circ = fields.Float(string='Waist Circumference (cm)', readonly=True, states={'start': [('readonly', False)]})
    bmi = fields.Float(compute=_compute_bmi, string='Body Mass Index (BMI)', store=True)
    height = fields.Float(string='Height (cm)', readonly=True, states={'start': [('readonly', False)]})
    head_circumference = fields.Float(string='Head Circumference(cm)', help="Head circumference", readonly=True,
                                      states={'start': [('readonly', False)]})

    # Pain Assessment
    pain_present_show = fields.Boolean()
    admission_pain_score = fields.Selection(PAIN_SCORE, readonly=True, states={'start': [('readonly', False)]})
    admission_scale_used = fields.Selection(SCALE_USED, readonly=True, states={'start': [('readonly', False)]})

    location_head = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    location_face = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    location_limbs = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    location_chest = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    location_abdomen = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    location_back = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    location_of_pain = fields.Text(readonly=True, states={'start': [('readonly', False)]})

    Characteristics_dull = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    Characteristics_sharp = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    Characteristics_burning = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    Characteristics_throbbing = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    Characteristics_other = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    Characteristics_patient_own_words = fields.Text(readonly=True, states={'start': [('readonly', False)]})

    onset_time_sudden = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    onset_time_gradual = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    onset_time_constant = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    onset_time_intermittent = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    onset_time_other = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    onset_time_fdv = fields.Text(readonly=True, states={'start': [('readonly', False)]})

    provoking_factors_food = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    provoking_factors_rest = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    provoking_factors_movement = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    provoking_factors_palpation = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    provoking_factors_other = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    provoking_factors_patient_words = fields.Text(readonly=True, states={'start': [('readonly', False)]})

    relieving_factors_rest = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    relieving_factors_medication = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    relieving_factors_heat = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    relieving_factors_distraction = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    relieving_factors_other = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    relieving_factors_patient_words = fields.Text(readonly=True, states={'start': [('readonly', False)]})

    expressing_pain_verbal = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    expressing_pain_facial = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    expressing_pain_body = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    expressing_pain_other = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    expressing_pain_when_pain = fields.Text(readonly=True, states={'start': [('readonly', False)]})

    effect_of_pain_nausea = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    effect_of_pain_vomiting = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    effect_of_pain_appetite = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    effect_of_pain_activity = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    effect_of_pain_relationship = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    effect_of_pain_emotions = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    effect_of_pain_concentration = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    effect_of_pain_sleep = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    effect_of_pain_other = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    effect_of_pain_other_text = fields.Text(readonly=True, states={'start': [('readonly', False)]})

    pain_management_advice_analgesia = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    pain_management_change_of = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    pain_management_refer_physician = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    pain_management_refer_physician_home = fields.Boolean(string="Home Care", readonly=True,
                                                          states={'start': [('readonly', False)]})
    pain_management_refer_physician_palliative = fields.Boolean(string="palliative", readonly=True,
                                                                states={'start': [('readonly', False)]})
    pain_management_refer_physician_primary = fields.Boolean(string="primary", readonly=True,
                                                             states={'start': [('readonly', False)]})
    pain_management_refer_hospital = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    pain_management_other = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    pain_management_other_text = fields.Text(readonly=True, states={'start': [('readonly', False)]})
    pain_management_comment = fields.Text(readonly=True, states={'start': [('readonly', False)]})

    # General Condition
    general_condition_show = fields.Boolean()
    general_condition = fields.Text(string='General Condition', readonly=True, states={'start': [('readonly', False)]})

    # EENT
    EENT_show = fields.Boolean()
    eent_eye = fields.Boolean(default=True, readonly=True, states={'start': [('readonly', False)]})
    eent_eye_condition = fields.Char(readonly=True, states={'start': [('readonly', False)]})
    eent_eye_vision = fields.Char(readonly=True, states={'start': [('readonly', False)]})
    eent_ear = fields.Boolean(default=True, readonly=True, states={'start': [('readonly', False)]})
    eent_ear_content = fields.Char(readonly=True, states={'start': [('readonly', False)]})
    eent_nose = fields.Boolean(default=True, readonly=True, states={'start': [('readonly', False)]})
    eent_nose_content = fields.Char(readonly=True, states={'start': [('readonly', False)]})
    eent_throut = fields.Boolean(default=True, readonly=True, states={'start': [('readonly', False)]})
    eent_throut_content = fields.Char(readonly=True, states={'start': [('readonly', False)]})
    eent_neck = fields.Boolean(default=True, readonly=True, states={'start': [('readonly', False)]})
    eent_neck_content = fields.Char(readonly=True, states={'start': [('readonly', False)]})
    eent_remarks = fields.Text(readonly=True, states={'start': [('readonly', False)]})

    # csv
    csv_show = fields.Boolean()
    cvs_h_sound_1_2 = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    cvs_h_sound_3 = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    cvs_h_sound_4 = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    cvs_h_sound_click = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    cvs_h_sound_murmurs = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    cvs_h_sound_other = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    cvs_h_sound_other_text = fields.Char(readonly=True, states={'start': [('readonly', False)]})

    cvs_rhythm = fields.Selection(CVS_RHYTHM, default='regular', readonly=True, states={'start': [('readonly', False)]})
    cvs_peripherial_pulse = fields.Selection(CVS_PERIPHERIAL, default='normal_palpable', readonly=True,
                                             states={'start': [('readonly', False)]})

    cvs_edema_yes_no = fields.Selection(YES_NO, readonly=True, states={'start': [('readonly', False)]})
    cvs_edema_yes_type = fields.Selection(CVS_EDEMA_TYPE, readonly=True, states={'start': [('readonly', False)]})
    cvs_edema_yes_location = fields.Text(readonly=True, states={'start': [('readonly', False)]})
    cvs_edema_yes_grade = fields.Selection(CVS_EDEMA_GRADE, readonly=True, states={'start': [('readonly', False)]})
    cvs_edema_yes_capillary = fields.Selection(CVS_EDEMA_CAPILLARY, readonly=True,
                                               states={'start': [('readonly', False)]})

    cvs_parenteral_devices_yes_no = fields.Selection(YES_NO, readonly=True, states={'start': [('readonly', False)]})
    cvs_parenteral_devices_yes_sel = fields.Selection(CVS_PARENTERAL_DEVICES, readonly=True,
                                                      states={'start': [('readonly', False)]})
    cvs_remarks = fields.Text(readonly=True, states={'start': [('readonly', False)]})
    # Respiratory
    respiratory_show = fields.Boolean()
    lung_sounds_clear = fields.Boolean(default=True, readonly=True, states={'start': [('readonly', False)]})
    lung_sounds_diminished = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    lung_sounds_absent = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    lung_sounds_fine_crackles = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    lung_sounds_rhonchi = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    lung_sounds_stridor = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    lung_sounds_wheeze = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    lung_sounds_coarse_crackles = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})

    Location_bilateral = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    Location_left_lower = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    Location_left_middle = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    Location_left_upper = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    Location_lower = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    Location_upper = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    Location_right_lower = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    Location_right_middle = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    Location_right_upper = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})

    type_regular = fields.Boolean(default=True, readonly=True, states={'start': [('readonly', False)]})
    type_irregular = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    type_rapid = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    type_dyspnea = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    type_apnea = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    type_tachypnea = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    type_orthopnea = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    type_accessory_muscles = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    type_snoring_mechanical = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    Cough_yes_no = fields.Selection(YES_NO, readonly=True, states={'start': [('readonly', False)]})
    cough_yes_type = fields.Selection(COUGH_TYPE, readonly=True, states={'start': [('readonly', False)]})
    cough_yes_frequency = fields.Selection(COUGH_FREQUENCY, readonly=True, states={'start': [('readonly', False)]})
    cough_yes_amount = fields.Selection(COUGH_AMOUNT, readonly=True, states={'start': [('readonly', False)]})
    cough_yes_characteristic = fields.Selection(COUGH_CHAR, readonly=True, states={'start': [('readonly', False)]})

    respiratory_support_yes_no = fields.Selection(YES_NO, readonly=True, states={'start': [('readonly', False)]})
    respiratory_support_yes_oxygen = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    respiratory_support_yes_oxygen_text = fields.Text(readonly=True, states={'start': [('readonly', False)]})
    respiratory_support_yes_trachestory = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    respiratory_support_yes_trachestory_text = fields.Text(readonly=True, states={'start': [('readonly', False)]})
    respiratory_support_yes_ventilator = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    respiratory_support_yes_ventilator_text = fields.Text(readonly=True, states={'start': [('readonly', False)]})

    suction_yes_no = fields.Selection(YES_NO, readonly=True, states={'start': [('readonly', False)]})
    suction_yes_type = fields.Selection(SUCTION_TYPE, readonly=True, states={'start': [('readonly', False)]})
    suction_yes_frequency = fields.Integer(readonly=True, states={'start': [('readonly', False)]})

    nebulization_yes_no = fields.Selection(YES_NO, readonly=True, states={'start': [('readonly', False)]})
    nebulization_yes_frequency = fields.Integer(readonly=True, states={'start': [('readonly', False)]})
    nebulization_yes_medication = fields.Many2one('oeh.medical.medicines', string='Medicines', readonly=True,
                                                  states={'start': [('readonly', False)]})
    respiratory_remarks = fields.Text(readonly=True, states={'start': [('readonly', False)]})

    # Neuralogical

    neuralogical_show = fields.Boolean()
    neuralogical_left_eye = fields.Selection(NUMBER_NEURALOGICAL, readonly=True,
                                             states={'start': [('readonly', False)]})
    neuralogical_right_eye = fields.Selection(NUMBER_NEURALOGICAL, readonly=True,
                                              states={'start': [('readonly', False)]})
    neuralogical_pupil_reaction = fields.Selection(NEURALOGICAL_REACTION, default='equal_round_reactive', readonly=True,
                                                   states={'start': [('readonly', False)]})
    neuralogical_old = fields.Selection(NEURALOGICAL_OLD, readonly=True, states={'start': [('readonly', False)]})
    neuralogical_greater_than_5_years_mental = fields.Selection(NEURALOGICAL_GREATER_5_MENTAL, readonly=True,
                                                                states={'start': [('readonly', False)]})
    neuralogical_greater_than_5_years_facial = fields.Selection(NEURALOGICAL_GREATER_5_FACIAL, readonly=True,
                                                                states={'start': [('readonly', False)]})
    neuralogical_greater_than_5_years_glascow = fields.Float(compute=_compute_greater_5_old)
    neuralogical_greater_than_5_years_eye = fields.Selection(EYE_MOMEMENT, readonly=True,
                                                             states={'start': [('readonly', False)]})
    neuralogical_greater_than_5_years_motor = fields.Selection(MOTOR_RESPONSE, readonly=True,
                                                               states={'start': [('readonly', False)]})
    neuralogical_greater_than_5_years_verbal = fields.Selection(NEURALOGICAL_GREATER_5_VERBAL, readonly=True,
                                                                states={'start': [('readonly', False)]})
    neuralogical_2_to_5_level = fields.Selection(LEVEL_CONSCIOUSNESS, readonly=True,
                                                 states={'start': [('readonly', False)]})
    neuralogical_2_to_5_glascow = fields.Float(compute=_compute_2_5_old)
    neuralogical_2_to_5_eye = fields.Selection(EYE_MOMEMENT, readonly=True, states={'start': [('readonly', False)]})
    neuralogical_2_to_5_motor = fields.Selection(MOTOR_RESPONSE, readonly=True, states={'start': [('readonly', False)]})
    neuralogical_2_to_5_verbal = fields.Selection(NEURALOGICAL_2_5_VERBAL, readonly=True,
                                                  states={'start': [('readonly', False)]})
    neuralogical_less_than_2_level = fields.Selection(LEVEL_CONSCIOUSNESS, readonly=True,
                                                      states={'start': [('readonly', False)]})
    neuralogical_less_than_2_glascow = fields.Float(compute=_compute_less_2)
    neuralogical_less_than_2_eye = fields.Selection(EYE_MOMEMENT, readonly=True,
                                                    states={'start': [('readonly', False)]})
    neuralogical_less_than_2_motor = fields.Selection(NEURALOGICAL_LESS_2_MOTOR, readonly=True,
                                                      states={'start': [('readonly', False)]})
    neuralogical_less_than_2_verbal = fields.Selection(NEURALOGICAL_LESS_2_VERBAL, readonly=True,
                                                       states={'start': [('readonly', False)]})
    neuralogical_remarks = fields.Text(readonly=True, states={'start': [('readonly', False)]})
    # Gastrointestinal
    gastrointestinal_show = fields.Boolean()
    gastrointestinal_bowel_sound = fields.Selection(GASTRINTESTINAL_BOWEL_SOUND, default='active', readonly=True,
                                                    states={'start': [('readonly', False)]})
    gastrointestinal_abdomen_lax = fields.Boolean(default=True, readonly=True, states={'start': [('readonly', False)]})
    gastrointestinal_abdomen_soft = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    gastrointestinal_abdomen_firm = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    gastrointestinal_abdomen_distended = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    gastrointestinal_abdomen_tender = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    gastrointestinal_stool_color = fields.Selection(GASTRINTESTINAL_STOOL_COLOR, default='brown', readonly=True,
                                                    states={'start': [('readonly', False)]})
    gastrointestinal_stool_loose = fields.Boolean(default=True, readonly=True, states={'start': [('readonly', False)]})
    gastrointestinal_stool_hard = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    gastrointestinal_stool_mucoid = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    gastrointestinal_stool_soft = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    gastrointestinal_stool_tarry = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    gastrointestinal_stool_formed = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    gastrointestinal_stool_semi_formed = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    gastrointestinal_stool_bloody = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    gastrointestinal_stoma_none = fields.Boolean(default=True, readonly=True, states={'start': [('readonly', False)]})
    gastrointestinal_stoma_colostory = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    gastrointestinal_stoma_ileostomy = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    gastrointestinal_stoma_peg = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    gastrointestinal_stoma_pej = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    gastrointestinal_stoma_urostomy = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    gastrointestinal_problem_none = fields.Boolean(default=True, readonly=True, states={'start': [('readonly', False)]})
    gastrointestinal_problem_nausea = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    gastrointestinal_problem_vomiting = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    gastrointestinal_problem_colic = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    gastrointestinal_problem_diarrhea = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    gastrointestinal_problem_constipation = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    gastrointestinal_problem_dysphagia = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    gastrointestinal_problem_hemorrhoids = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    gastrointestinal_problem_anal_fissure = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    gastrointestinal_problem_anal_fistula = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    gastrointestinal_problem_other = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    gastrointestinal_problem_other_text = fields.Text(readonly=True, states={'start': [('readonly', False)]})
    gastrointestinal_bowel_movement_none = fields.Boolean(default=True, readonly=True,
                                                          states={'start': [('readonly', False)]})
    gastrointestinal_bowel_movement_laxative = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    gastrointestinal_bowel_movement_enema = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    gastrointestinal_bowel_movement_stoma = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    gastrointestinal_bowel_movement_stool_softener = fields.Boolean(readonly=True,
                                                                    states={'start': [('readonly', False)]})
    gastrointestinal_bowel_movement_suppository = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    gastrointestinal_bowel_movement_digital = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    gastrointestinal_bowel_movement_other = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    gastrointestinal_bowel_movement_other_text = fields.Text(readonly=True, states={'start': [('readonly', False)]})
    gastrointestinal_enteral_device_none = fields.Boolean(default=True, readonly=True,
                                                          states={'start': [('readonly', False)]})
    gastrointestinal_enteral_device_nasogastric_tube = fields.Boolean(readonly=True,
                                                                      states={'start': [('readonly', False)]})
    gastrointestinal_enteral_device_orogastric_tube = fields.Boolean(readonly=True,
                                                                     states={'start': [('readonly', False)]})
    gastrointestinal_enteral_device_gastro_jejunal = fields.Boolean(readonly=True,
                                                                    states={'start': [('readonly', False)]})
    gastrointestinal_enteral_device_peg = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    gastrointestinal_enteral_device_pej = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    gastrointestinal_enteral_device_pd = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    gastrointestinal_enteral_device_other = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    gastrointestinal_enteral_device_other_text = fields.Text(readonly=True, states={'start': [('readonly', False)]})
    gastrointestinal_remarks = fields.Text(readonly=True, states={'start': [('readonly', False)]})

    # Genitourinary
    genitourinary_show = fields.Boolean()
    genitourinary_urine_color = fields.Selection(GENITOURINARY_URINE_COLOR, default='pale_yellow', readonly=True,
                                                 states={'start': [('readonly', False)]})
    genitourinary_urine_appearance = fields.Selection(GENITOURINARY_URINE_APPERANCE, default='clear', readonly=True,
                                                      states={'start': [('readonly', False)]})
    genitourinary_urine_amount = fields.Selection(GENITOURINARY_URINE_AMOUNT, default='adequate', readonly=True,
                                                  states={'start': [('readonly', False)]})
    genitourinary_urination_none = fields.Boolean(default=True, readonly=True, states={'start': [('readonly', False)]})
    genitourinary_urination_dysuria = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    genitourinary_urination_frequency = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    genitourinary_urination_urgency = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    genitourinary_urination_hesitancy = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    genitourinary_urination_incontinence = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    genitourinary_urination_inability_to_void = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    genitourinary_urination_nocturia = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    genitourinary_urination_retention = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    genitourinary_urination_suprapubic_pain = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    genitourinary_urination_loin_pain = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    genitourinary_urination_colicky_pain = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    genitourinary_urination_difficult_control = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    genitourinary_urination_other = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    genitourinary_urination_other_text = fields.Text(readonly=True, states={'start': [('readonly', False)]})
    genitourinary_urination_assistance = fields.Selection(GENITOURINARY_URINATION_ASSISTANCE, default='none',
                                                          readonly=True, states={'start': [('readonly', False)]})
    genitourinary_remarks = fields.Text(readonly=True, states={'start': [('readonly', False)]})
    # Integumentary
    integumentary_show = fields.Boolean()
    appearance_normal = fields.Boolean(string='Normal', default=True, readonly=True,
                                       states={'start': [('readonly', False)]})
    appearance_dry = fields.Boolean(string='Dry', readonly=True, states={'start': [('readonly', False)]})
    appearance_edema = fields.Boolean(string='Edema', readonly=True, states={'start': [('readonly', False)]})
    appearance_flushed = fields.Boolean(string='Flushed', readonly=True, states={'start': [('readonly', False)]})

    appearance_pale = fields.Boolean(string='clay', readonly=True, states={'start': [('readonly', False)]})
    appearance_rash = fields.Boolean(string='Rash', readonly=True, states={'start': [('readonly', False)]})

    appearance_jundiced = fields.Boolean(string='Jandiced', readonly=True, states={'start': [('readonly', False)]})
    appearance_eczema = fields.Boolean(string='Eczema', readonly=True, states={'start': [('readonly', False)]})
    appearance_hemayome = fields.Boolean(string='Hemayome', readonly=True, states={'start': [('readonly', False)]})
    appearance_rusty = fields.Boolean(string='Rusty', readonly=True, states={'start': [('readonly', False)]})
    appearance_cyanotic = fields.Boolean(string='Cyanotic', readonly=True, states={'start': [('readonly', False)]})
    appearance_bruises = fields.Boolean(string='Bruises', readonly=True, states={'start': [('readonly', False)]})
    appearance_abrasion = fields.Boolean(string='Abrasion', readonly=True, states={'start': [('readonly', False)]})
    appearance_sores = fields.Boolean(string='Sores', readonly=True, states={'start': [('readonly', False)]})
    integumentary_turgor = fields.Selection(INTEGUMENTARY_TURGOR, default='elastic', readonly=True,
                                            states={'start': [('readonly', False)]})
    integumentary_temperature = fields.Selection(INTEGUMENTARY_TEMP, default='normal', readonly=True,
                                                 states={'start': [('readonly', False)]})
    integumentary_remarks = fields.Text(readonly=True, states={'start': [('readonly', False)]})

    # Infections
    infection_show = fields.Boolean()
    infection_nad = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    infection_content = fields.Char(readonly=True, states={'start': [('readonly', False)]})

    # psychological
    psychological_show = fields.Boolean()
    psychological_nad = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    psychological_content = fields.Char(readonly=True, states={'start': [('readonly', False)]})
    # reproductive
    reproductive_show = fields.Boolean()
    reproductive_nad = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    reproductive_content = fields.Char(readonly=True, states={'start': [('readonly', False)]})
    # musculoskeletal
    musculoskeletal_show = fields.Boolean()
    musculoskeletal_left_upper_extremity = fields.Selection(MUSCULOSKELETAL_EXTREMITY,
                                                            default='active_against_gravity_resistance',
                                                            readonly=True, states={'start': [('readonly', False)]})
    musculoskeletal_right_upper_extremity = fields.Selection(MUSCULOSKELETAL_EXTREMITY,
                                                             default='active_against_gravity_resistance',
                                                             readonly=True, states={'start': [('readonly', False)]})
    musculoskeletal_left_lower_extremity = fields.Selection(MUSCULOSKELETAL_EXTREMITY,
                                                            default='active_against_gravity_resistance',
                                                            readonly=True, states={'start': [('readonly', False)]})
    musculoskeletal_right_lower_extremity = fields.Selection(MUSCULOSKELETAL_EXTREMITY,
                                                             default='active_against_gravity_resistance',
                                                             readonly=True, states={'start': [('readonly', False)]})
    musculoskeletal_gait = fields.Selection(MUSCULOSKELETAL_GAIT, default='normal', readonly=True,
                                            states={'start': [('readonly', False)]})
    musculoskeletal_remarks = fields.Text(readonly=True, states={'start': [('readonly', False)]})

    # sensory
    sensory_show = fields.Boolean()
    sensory_nad = fields.Boolean(readonly=True, states={'start': [('readonly', False)]})
    sensory_content = fields.Char(readonly=True, states={'start': [('readonly', False)]})

    @api.onchange('specify', 'effect_of_pain_other_text', 'pain_management_other_text',
                  'pain_management_refer_physician_home', 'pain_management_refer_physician_palliative',
                  'pain_management_refer_physician_primary')
    def _check(self):
        if self.effect_of_pain_other:
            self.effect_of_pain_other_text = ''
        if self.pain_management_other:
            self.pain_management_other_text = ''
        if self.pain_management_refer_physician == 'False':
            self.pain_management_refer_physician_home = ''
        if self.pain_management_refer_physician == 'False':
            self.pain_management_refer_physician_palliative = ''
        if self.pain_management_refer_physician == 'False':
            self.pain_management_refer_physician_primary = ''

    # constrains on vital signs
    @api.onchange('systolic', 'temperature', 'bpm', 'respiratory_rate', 'diastolic')
    def _check_vital_signs(self):
        digits_systolic = [int(x) for x in str(self.systolic)]
        digits_diastolic = [int(x) for x in str(self.diastolic)]
        digits_bpm = [int(x) for x in str(self.bpm)]
        if len(digits_systolic) > 3:
            raise ValidationError("invalid systolic value")
        if len(digits_diastolic) > 3:
            raise ValidationError("invalid diastolic value")
        if len(digits_bpm) > 3:
            raise ValidationError("invalid Heart rate value")
        if self.temperature > 50:
            raise ValidationError("invalid temperature value")
        if self.respiratory_rate > 90:
            raise ValidationError("invalid respiratory rate value")
        # if self.osat > 100:
        #     raise ValidationError("invalid Oxygen Saturation value")

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


class ShifaPrescriptionForTeleAppointment(models.Model):
    _inherit = 'oeh.medical.prescription'

    tele_appointment = fields.Many2one("sm.telemedicine.appointment", string='Tele Appointment')


class ShifaJitsiForAppointment(models.Model):
    _inherit = 'sm.telemedicine.appointment'

    invitation_text_jitsi = fields.Html(string='Invitation Text', readonly=True)


class ShifaInvestigationInherit(models.Model):
    _inherit = 'sm.shifa.investigation'

    telemedicine_appointment = fields.Many2one("sm.telemedicine.appointment", string='Telemedicine Appointment')
