from datetime import timedelta, datetime

from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError, ValidationError

import logging
import pytz
import requests
import jwt
import time
import json
import uuid
from random import choice

_logger = logging.getLogger(__name__)


class ShifaAppointment(models.Model):
    _inherit = "oeh.medical.appointment"
    _rec_name = 'display_name'

    APPOINTMENT_STATE = [
        ('Scheduled', 'Scheduled'),
        ('Confirmed', 'Confirmed'),
        ('Start', 'Start'),
        ('Completed', 'Completed'),
        ('canceled', 'Canceled'),
        ('requestCancellation', 'Request Cancellation'),
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
    pay_made_throu = [
        ('pending', 'Free Service'),
        ('mobile', 'Mobile App'),
        ('call_center', 'Call Center'),
        ('on_spot', 'On spot'),
        ('aggregator', 'Aggregator'),
        ('package', 'Package')
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

    def _join_name_tele(self):
        for rec in self:
            if rec.patient:
                rec.display_name = rec.patient.name + ' ' + rec.name

    state = fields.Selection(APPOINTMENT_STATE, string='State', readonly=True, default=lambda *a: 'Scheduled')
    name = fields.Char(string='Tel #', size=64, readonly=True, default=lambda *a: '/')
    display_name = fields.Char(compute=_join_name_tele)
    # patient details
    dob = fields.Date(string='Date of Birth', related='patient.dob', readonly=True,
                      states={'Scheduled': [('readonly', False)]})
    marital_status = fields.Selection(string='Marital Status', related='patient.marital_status')
    sex = fields.Selection(string='Sex', related='patient.sex', readonly=True,
                           states={'Scheduled': [('readonly', False)]})
    blood_type = fields.Selection(string='Blood Type', related='patient.blood_type')
    rh = fields.Selection(string='Rh', related='patient.rh')
    ssn = fields.Char(string='ID Number', readonly=False,
                      states={'Start': [('readonly', True)], 'Confirmed': [('readonly', True)],
                              'Completed': [('readonly', True)], 'canceled': [('readonly', True)]},
                      related='patient.ssn')
    mobile = fields.Char(string='Mobile', readonly=False,
                         states={'Start': [('readonly', True)], 'Confirmed': [('readonly', True)],
                                 'Completed': [('readonly', True)], 'canceled': [('readonly', True)]},
                         related='patient.mobile')
    age = fields.Char(string='Age', readonly=False,
                      states={'Start': [('readonly', True)], 'Confirmed': [('readonly', True)],
                              'Completed': [('readonly', True)], 'canceled': [('readonly', True)]},
                      related='patient.age')
    nationality = fields.Char(string='Nationality', readonly=False,
                              states={'Start': [('readonly', True)], 'Confirmed': [('readonly', True)],
                                      'Completed': [('readonly', True)], 'canceled': [('readonly', True)]},
                              related='patient.nationality')
    patient_weight = fields.Float(string='Weight(kg)', readonly=False,
                                  states={'Start': [('readonly', True)], 'Confirmed': [('readonly', True)],
                                          'Completed': [('readonly', True)], 'canceled': [('readonly', True)]},
                                  related='patient.weight')
    patient_comment = fields.Text(readonly=True, states={'Scheduled': [('readonly', False)]})
    doctor = fields.Many2one('oeh.medical.physician', string='Consultancy Responsible',
                             help="Current primary care / family doctor",
                             domain=[('role_type', 'in',
                                      ['TD', 'HD', 'HHCD', 'HN', 'HHCN', 'HP', 'HHCP', 'RT', 'SW', 'HE', 'DE', 'CD']), ('active', '=', True)],
                             required=True, readonly=True,
                             states={'Scheduled': [('readonly', False)]}, default=_get_physician)

    active = fields.Boolean('Active', default=True)
    payment_type = fields.Char('Payment Type', readonly=True, states={'Confirmed': [('readonly', False)]})
    payment_reference = fields.Char('Payment Reference', readonly=True, states={'Confirmed': [('readonly', False)]})
    location = fields.Char(string='Mobile location', readonly=True)
    service = fields.Char()
    attached_file = fields.Binary("Attached File 1", readonly=True, states={'Scheduled': [('readonly', False)]})
    attached_file_2 = fields.Binary("Attached File 2", readonly=True, states={'Scheduled': [('readonly', False)]})
    # attached_file_3 = fields.Binary("Attached File 3", readonly=True, states={'Scheduled': [('readonly', False)]})
    checkup_comment = fields.Text(readonly=True, states={'Scheduled': [('readonly', False)]})

    labtest_line = fields.One2many('sm.shifa.lab.request', 'appointment', string='Lab Request')
    prescription_ids = fields.One2many('oeh.medical.prescription', 'appointment', string='Prescription')
    # end
    investigation_ids = fields.One2many('sm.shifa.investigation', 'appointment', string='Telemedicine Appointment')
    referral_ids = fields.One2many('sm.shifa.referral', 'appointment')
    chief_complaint = fields.Char(string='Chief Complaint', readonly=True, states={'Start': [('readonly', False)]})
    # Zoom password field
    apw = fields.Char("Attendee password", default=lambda self: self.create_password())
    zoom_link = fields.Text()  # mobile zoom link
    jitsi_link = fields.Text()  # mobile jitsi link
    invitation_text_jitsi = fields.Html(string='Invitation Link', readonly=True)
    comments = fields.Text(string='Comments', readonly=True,
                           states={'Start': [('readonly', False)], 'Scheduled': [('readonly', False)]})
    start_process_date = fields.Datetime(string='Process Started at', readonly=True)
    complete_process_date = fields.Datetime(string='Process Completed at', readonly=True)
    insurance = fields.Many2one('sm.shifa.insurance', string='Insurance', help="Insurance Company Name",
                                domain=[('state', '=', 'Active')],
                                readonly=True, states={'Scheduled': [('readonly', False)]})

    ksa_nationality = fields.Selection(NATIONALITY_STATE, related='patient.ksa_nationality', readonly=True,
                                       states={'Scheduled': [('readonly', False)]})

    appointment_day = fields.Selection(PHY_DAY, string='Day', required=False)
    day = fields.Char(string='Day', store=True)
    send_sms_doctor = fields.Boolean()
    send_sms_patient = fields.Boolean()

    meeting_id = fields.Many2one('calendar.event', string='Calendar', copy=False)
    lab_request_test_line = fields.One2many('sm.shifa.lab.request.line', 'appointment', string='Lab Request',
                                            readonly=False, states={'Completed': [('readonly', True)]})
    image_request_test_ids = fields.One2many('sm.shifa.imaging.request.line', 'appointment', string='Image Request',
                                             readonly=False, states={'Completed': [('readonly', True)]})
    deduction_amount = fields.Float(string="Ded. Amount", readonly=True)
    payment_made_through = fields.Selection(pay_made_throu, string="Pay. Made Thru.", default="mobile",readonly=False, states={'Scheduled': [('readonly', True)]})
    payment_method_name = fields.Char(string="Payment Method Name", readonly=True)
    pay_req_id = fields.Many2one('sm.shifa.requested.payments', string='Payment Request#', copy=False, readonly=True)
    check_pres = fields.Boolean()
    branch = fields.Selection([
        ('riyadh', 'Riyadh'),
        ('dammam', 'Dammam'),
        ('jeddah', 'Jeddah'),
    ], string="Branch", readonly=True, states={'Scheduled': [('readonly', False)]})
    '''
        Indicates whether an appointment has been cancelled. 
        This field is typically updated when a user cancels an appointment via the mobile app or other channels.
    '''
    cancellation_requested = fields.Boolean(string='Cancellation Requested', default=lambda *a: 0)
    pro_pending = fields.Boolean(string="Pro. Free Service")

    def unlink(self):
        self.active_timeslot()
        for rec in self:
            if rec.state != 'canceled':
                raise UserError(_("You can delete only if it cancelled Appointments"))
        return super().unlink()

    def action_archive(self):
        for rec in self:
            if rec.state not in ['canceled', 'Completed']:
                raise UserError(_("You can archive only if it cancelled or completed Appointments "))
        return super().action_archive()

    def create_payement_request(self, appointment):
        pay_values = {
            'patient': appointment.patient.id,
            'type': 'tele_appointment',
            'details': 'Tele appointment',
            'date': appointment.appointment_date,
            'appointment': appointment.id,
            'payment_method': 'cash',
            'state': 'Send',
            'payment_amount': appointment.amount_payable,
        }
        pay_req = self.env['sm.shifa.requested.payments'].create(pay_values)
        pay_req.set_to_send()
        appointment.pay_req_id = pay_req.id

    # def create_payement_request(self):
    #     pay_values = {
    #         'patient': self.patient.id,
    #         'type': 'tele_appointment',
    #         'details': 'Tele appointment',
    #         'date': self.appointment_date,
    #         'appointment': self.id,
    #         'payment_method': 'cash',
    #         'state': 'Send',
    #         'payment_amount': self.amount_payable,
    #     }
    #     pay_req = self.env['sm.shifa.requested.payments'].create(pay_values)
    #     pay_req.set_to_send()
    #     self.pay_req_id = pay_req.id

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

    def create_zoom_meeting(self):
        for record in self:
            company = self.env.company
            if company.oeh_zoom_api_key and company.oeh_zoom_secret_key and company.oeh_zoom_email:
                api_key = company.oeh_zoom_api_key
                api_secret_key = company.oeh_zoom_secret_key
                zoom_email = company.oeh_zoom_email
                settings = {'host_video': company.host_video,
                            'participant_video': company.participant_video,
                            'join_before_host': company.join_before_host,
                            'mute_upon_entry': company.mute_upon_entry,
                            'watermark': company.watermark,
                            'enforce_login': company.enforce_login,
                            'close_registration': company.close_registration,
                            'waiting_room': company.waiting_room, }

                if not api_key or not api_secret_key:
                    raise AccessError(
                        _('Please Configure Zoom Credentials'))
                base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                if not base_url:
                    raise AccessError(
                        _('Please Configure URL in System Parameters'))
                usr_data = {'email': zoom_email, 'login_type': 2}
                header = {"alg": "HS256", "typ": "JWT"}
                payload = {"iss": api_key, "exp": int(time.time() + 3600)}
                token = jwt.encode(payload, api_secret_key, algorithm="HS256", headers=header)
                # header_token = token.decode("utf-8")
                header = {'Authorization': 'Bearer %s' % token}
                usr_url = "https://api.zoom.us/v2/users?email=%s&login_type=%d" % (
                    usr_data['email'], usr_data['login_type'])
                res_user = requests.get(usr_url, params=usr_data, headers=header)
                data = json.loads(res_user.content)
                #print(data)
                user_id = False
                for d in data['users']:
                    if d['email'] == usr_data['email']:
                        user_id = d['id']
                meeting_date = record.appointment_date_only.strftime("%Y-%m-%dT%H:%M:%SZ")
                url = "https://api.zoom.us/v2/users/%s/meetings" % user_id
                meeting_data = {'topic': record.name,
                                'type': 2,
                                'start_time': meeting_date,
                                'duration': record.duration,
                                'timezone': 'Asia/Aden',
                                'password': record.apw,
                                'agenda': record.name,
                                'user_id': '%s' % user_id,
                                'settings': settings,
                                }
                meeting_info = requests.post(url, json=meeting_data, headers=header)
                meeting_json = json.loads(meeting_info.content)
                #print(meeting_json)
                invitation_text = _("<a href='%s' target='_blank'>Click here to start meeting</a>") % meeting_json[
                    'start_url']
                invitation_text += '<br/><br/>Password: ' + meeting_json['password']
                record.write({
                    'invitation_text': invitation_text
                })
                return True
            else:
                raise ValidationError("Unable to reach server")

    def create_jitsi_meeting(self):
        # server_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url') #+ '/videocall'
        server_url = self.env['ir.config_parameter'].sudo().get_param('oehealth_jitsi.video_call_server_url')
        appointment = self.env['oeh.medical.appointment'].browse(int(self.id))
        meeting_link = server_url + '/' + self._get_meeting_code()
        invitation_text = _("<a href='%s' target='_blank'>Click here to start meeting</a>") % meeting_link

        appointment.write({
            'invitation_text_jitsi': invitation_text,
            'jitsi_link': meeting_link,
        })

    def _get_meeting_code(self):
        return str(uuid.uuid4()).replace('-', '')

    @api.model
    def default_get(self, fields):
        rec = models.Model.default_get(self, fields)
        rec['patient_status'] = 'Outpatient'
        return rec


    def set_to_confirmed(self):
        self.create_jitsi_meeting()
        # comment next line for sms send
        self.send_sms_appointment()
        self.calendar_appointment_event()
        # self.create_payement_request()
        if self.payment_made_through not in ['pending', 'on_spot', 'aggregator', 'package',
                                             'aggregator_package'] and self.pay_req_id and self.pay_req_id.state not in [
            'Paid', 'Done']:
            raise UserError("You cannot move to the next action until the payment is paid or processed!")
        if self.payment_made_through == 'pending' and not self.pro_pending:
            raise UserError("Waiting for Admin approval!")
        return self.write({'state': 'Confirmed'})

    def set_to_canceled(self):
        return self.write({'state': 'canceled'})

    def set_to_start(self):
        return self.write({'state': 'Start', 'start_process_date': datetime.now()})


    def set_to_completed(self):
        # if self.pres_tele_line.id:
        for rec in self:
            if not rec.pres_tele_line:
                pass
            else:
                rec.env['oeh.medical.prescription'].create({
                    'patient': rec.patient.id,
                    'doctor': rec.doctor.id,
                    'appointment': rec.id,
                    'provisional_diagnosis': rec.provisional_diagnosis.id,
                    'provisional_diagnosis_add_other': rec.provisional_diagnosis_add_other,
                    'provisional_diagnosis_add': rec.provisional_diagnosis_add.id,
                    'provisional_diagnosis_add_other2': rec.provisional_diagnosis_add_other2,
                    'provisional_diagnosis_add2': rec.provisional_diagnosis_add2.id,
                    'provisional_diagnosis_add_other3': rec.provisional_diagnosis_add_other3,
                    'provisional_diagnosis_add3': rec.provisional_diagnosis_add3.id,
                    'allergies_show': rec.allergies_show,
                    'has_drug_allergy': rec.has_drug_allergy,
                    'drug_allergy': rec.drug_allergy,
                    'drug_allergy_content': rec.drug_allergy_content,
                    'has_food_allergy': rec.has_food_allergy,
                    'food_allergy': rec.food_allergy,
                    'food_allergy_content': rec.food_allergy_content,
                    'has_other_allergy': rec.has_other_allergy,
                    'other_allergy': rec.other_allergy,
                    'other_allergy_content': rec.other_allergy_content,
                    'prescription_line': rec.pres_tele_line,
                })
            if not rec.lab_request_test_line:
                pass
            else:
                # print("Lab")
                rec.env['sm.shifa.lab.request'].create({
                    'patient': rec.patient.id,
                    'doctor': rec.doctor.id,
                    'appointment': rec.id,
                    'lab_request_ids': rec.lab_request_test_line,
                })

            if not rec.image_request_test_ids:
                pass
            else:
                # print("Image")
                rec.env['sm.shifa.imaging.request'].create({
                    'patient': rec.patient.id,
                    'doctor': rec.doctor.id,
                    'appointment': rec.id,
                    'image_req_test_ids': rec.image_request_test_ids,
                })
        return self.write({'state': 'Completed', 'complete_process_date': datetime.now()})

    def set_back_to_call_center(self):
        return self.write({'state': 'Scheduled'})

    def _reset_token_number_sequences(self):
        # just use write directly on the result this will execute one update query
        sequences = self.env['ir.sequence'].search([('name', '=', 'Appointments')])
        sequences.write({'number_next_actual': 1})

    def unlink(self):
        return super(ShifaAppointment, self).unlink()

    def download_pdf(self):
        therapist_obj = self.env['oeh.medical.prescription']
        domain = [('appointment', '=', self.id)]
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
            #print(patient_id.name)

    def _check_sms(self):
        appointment = self.search([
            ('state', '=', 'Confirmed'),
        ])
        if appointment:
            for rec in appointment:
                pa_msg = ""
                dr_msg = ""
                my_model = rec._name
                # print(not(app.send_sms_patient and app.send_sms_doctor))
                if not (rec.send_sms_patient and rec.send_sms_doctor):
                    appointment = rec.convert_utc_to_local(str(rec.appointment_date))
                    pa_msg = "تم حجز موعد الاستشارة الطبية فيديو ل %s في تاريخ: %s الساعة :%s مع تمنياتنا لكم بدوام الصحة" % (
                        rec.patient.name, appointment[:11], appointment[11:])
                    dr_msg = "تم حجز موعد الاستشارة الطبية فيديو ل %s في تاريخ: %s الساعة :%s " % (
                        rec.doctor.name, appointment[:11], appointment[11:])
                    #print(pa_msg)
                    #print(dr_msg)
                    rec.send_sms(rec.patient.mobile, pa_msg, my_model, rec.id)
                    rec.send_sms(rec.doctor.mobile, dr_msg, my_model, rec.id)
                    rec.send_sms_doctor = True
                    rec.send_sms_patient = True

    def _before_30min_sms_alarm(self):
        appointment = self.search([
            ('state', '=', 'Confirmed'),
        ])
        if appointment:
            for rec in appointment:
                pa_msg = ""
                dr_msg = ""
                my_model = rec._name
                if rec.appointment_date_only == datetime.now().date():
                    reminder_time = rec.appointment_time - 0.5
                    reminder_sms_time = '{0:02.0f}:{1:02.0f}'.format(*divmod(reminder_time * 60, 60))
                    # print(reminder_sms_time)
                    now_time = datetime.now() + timedelta(hours=3)
                    now_time_sms = now_time.strftime("%H:%M")
                    # print(now_time_sms)
                    # print(rec.convert_utc_to_local(str(rec.appointment_date)))
                    if reminder_sms_time == now_time_sms:
                        appointment = rec.convert_utc_to_local(str(rec.appointment_date))
                        pa_msg = "نذكركم بموعد الاستشارة الطبية فيديو ل %s في تاريخ: %s الساعة :%s مع تمنياتنا لكم بدوام الصحة" % (
                            rec.patient.name, appointment[:11], appointment[11:])
                        dr_msg = "نذكركم بموعد الاستشارة الطبية فيديو ل %s في تاريخ: %s الساعة :%s " % (
                            rec.doctor.name, appointment[:11], appointment[11:])
                        # print(pa_msg)
                        # print(dr_msg)
                        rec.send_sms(rec.patient.mobile, pa_msg, my_model, rec.id)
                        rec.send_sms(rec.doctor.mobile, dr_msg, my_model, rec.id)

    def convert_utc_to_local(self, date):
        date_format = "%Y-%m-%d %H:%M:%S"
        # print(self.env.user.tz)
        # print(pytz.timezone('Asia/Riyadh'))
        # _logger.error(self.env.user.tz)
        # _logger.error(pytz.utc)
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


class SmartMindShifaDoctorScheduleTimeSlot(models.Model):
    _inherit = "oeh.medical.appointment"

    @api.onchange('appointment_date_only', 'appointment_time')
    def _get_appointment_date(self):
        for apm in self:
            # if apm.appointment_time: # apm.time_slot and apm.appointment_time:
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
                               readonly=False, states={'Start': [('readonly', True)], 'Confirmed': [('readonly', True)],
                                                       'Completed': [('readonly', True)],
                                                       'canceled': [('readonly', True)]})
    appointment_date = fields.Datetime(compute=_get_appointment_date, string='Apt. DateTime', readonly=True, store=True)
    appointment_end = fields.Datetime(compute=_get_appointment_end, string='Apt. End Date', store=True)

    # ------------------------------------------------------------------------------------------------------------------

    @api.onchange('timeslot')
    def onchange_timeslot(self):
        if self.timeslot:
            hm = self.timeslot.available_time.split(':')
            sch_time = int(hm[0]) + int(hm[1]) / 60
            #print('time: ', str(sch_time))
            self.appointment_time = sch_time

    def timeslot_is_available(self, tm_id, action):
        #print('timeslot id', str(tm_id))
        timeslot = self.env['sm.shifa.physician.schedule.timeslot'].sudo().browse(int(tm_id))
        #print('timeslot', str(timeslot.available_time))
        #print('action', str(action))
        timeslot.sudo().write({
            'is_available': action,
        })

    def active_timeslot(self):
        for rec in self.filtered(lambda rec: rec.state in ['Scheduled', 'Confirmed']):
            self.timeslot_is_available(self.timeslot, True)

    @api.model
    def create(self, vals):
        doc_time = vals.get('timeslot')
        appointment = super(SmartMindShifaDoctorScheduleTimeSlot, self).create(vals)
        if doc_time:
            self.timeslot_is_available(vals['timeslot'], False)
        self.create_payement_request(appointment)
        return appointment

    def write(self, vals):
        for rec in self:
            if rec.timeslot:
                self.timeslot_is_available(rec.timeslot, False)
        return super(SmartMindShifaDoctorScheduleTimeSlot, self).write(vals)


    def set_to_canceled(self):
        self.active_timeslot()
        return self.write({'state': 'canceled'})


class ShifaAppointmentMedicalCareTab(models.Model):
    _inherit = "oeh.medical.appointment"
    # medical care plan tab
    medical_care_plan = fields.Text(string='Medical Care Plan', readonly=True, states={'Start': [('readonly', False)]})
    program_chronic_anticoagulation = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    program_general_nursing_care = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    program_wound_care = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    program_palliative_care = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    program_acute_anticoagulation = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    program_home_infusion = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    program_other = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    program_other_text = fields.Text(readonly=True, states={'Start': [('readonly', False)]})
    services_provided_oxygen_dependent = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    services_provided_tracheostomy = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    services_provided_wound_care = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    services_provided_pain_management = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    services_provided_hydration_therapy = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    services_provided_o2_via_nasal_cannula = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    services_provided_hypodermoclysis = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    services_provided_tpn = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    services_provided_stoma_care = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    services_provided_peg_tube = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    services_provided_inr_monitoring = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    services_provided_prevention_pressure = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    services_provided_vac_therapy = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    services_provided_drain_tube = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    services_provided_medication_management = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    services_provided_warfarin_stabilization = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    services_provided_parenteral_antimicrobial = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    services_provided_indwelling_foley_catheter = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    services_provided_ngt = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    services_provided_other = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    services_provided_other_text = fields.Text(readonly=True, states={'Start': [('readonly', False)]})
    patient_condition = fields.Selection([
        ('Declined', 'Declined'),
        ('Unstable', 'Unstable'),
        ('Unchanged', 'Unchanged'),
        ('Improved', 'Improved'),
        ('Stable', 'Stable'),
    ], readonly=True, states={'Start': [('readonly', False)]})
    prognosis = fields.Selection([
        ('Poor', 'Poor'),
        ('Guarded', 'Guarded'),
        ('Fair', 'Fair'),
        ('Good', 'Good'),
        ('Excellent', 'Excellent'),
    ], readonly=True, states={'Start': [('readonly', False)]})
    potential_risk = fields.Text(readonly=True, states={'Start': [('readonly', False)]})
    admission_goal = fields.Text(readonly=True, states={'Start': [('readonly', False)]})
    final_plan = fields.Text(readonly=True, states={'Start': [('readonly', False)]})


class ShifaPhysicianDiagnosisTab(models.Model):
    _inherit = 'oeh.medical.appointment'

    # diagnosis tab
    provisional_diagnosis = fields.Many2one('oeh.medical.pathology', string='Disease', readonly=True,
                                            states={'Start': [('readonly', False)]})
    provisional_diagnosis_add_other = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    provisional_diagnosis_add = fields.Many2one('oeh.medical.pathology', string='Disease', readonly=True,
                                                states={'Start': [('readonly', False)]})
    provisional_diagnosis_add_other2 = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    provisional_diagnosis_add2 = fields.Many2one('oeh.medical.pathology', string='Disease', readonly=True,
                                                 states={'Start': [('readonly', False)]})
    provisional_diagnosis_add_other3 = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    provisional_diagnosis_add3 = fields.Many2one('oeh.medical.pathology', string='Disease', readonly=True,
                                                 states={'Start': [('readonly', False)]})

    differential_diagnosis = fields.Many2one('oeh.medical.pathology', string='Disease', readonly=True,
                                             states={'Start': [('readonly', False)]})

    differential_diagnosis_add = fields.Many2one('oeh.medical.pathology', string='Disease', readonly=True,
                                                 states={'Start': [('readonly', False)]})
    differential_diagnosis_add_other = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})


class ShifaAppointmentHistoryTab(models.Model):
    _inherit = 'oeh.medical.appointment'

    YES_NO = [
        ('yes', 'Yes'),
        ('no', 'No'),
    ]
    # History tab
    # History of present illness
    history_present_illness_show = fields.Boolean()
    history_present_illness = fields.Text(readonly=False,
                                          states={'Scheduled': [('readonly', True)], 'Confirmed': [('readonly', True)],
                                                  'Completed': [('readonly', True)]})
    # review systems details
    review_systems_show = fields.Boolean()
    constitutional = fields.Boolean(readonly=False,
                                    states={'Scheduled': [('readonly', True)], 'Confirmed': [('readonly', True)],
                                            'Completed': [('readonly', True)]})
    constitutional_content = fields.Char(readonly=False,
                                         states={'Scheduled': [('readonly', True)], 'Confirmed': [('readonly', True)],
                                                 'Completed': [('readonly', True)]})
    head = fields.Boolean(default=True, readonly=False,
                          states={'Scheduled': [('readonly', True)], 'Confirmed': [('readonly', True)],
                                  'Completed': [('readonly', True)]})
    head_content = fields.Char(readonly=False,
                               states={'Scheduled': [('readonly', True)], 'Confirmed': [('readonly', True)],
                                       'Completed': [('readonly', True)]})
    cardiovascular = fields.Boolean(default=True, readonly=False,
                                    states={'Scheduled': [('readonly', True)], 'Confirmed': [('readonly', True)],
                                            'Completed': [('readonly', True)]})
    cardiovascular_content = fields.Char(readonly=False,
                                         states={'Scheduled': [('readonly', True)], 'Confirmed': [('readonly', True)],
                                                 'Completed': [('readonly', True)]})
    pulmonary = fields.Boolean(default=True, readonly=False,
                               states={'Scheduled': [('readonly', True)], 'Confirmed': [('readonly', True)],
                                       'Completed': [('readonly', True)]})
    pulmonary_content = fields.Char(readonly=False,
                                    states={'Scheduled': [('readonly', True)], 'Confirmed': [('readonly', True)],
                                            'Completed': [('readonly', True)]})
    gastroenterology = fields.Boolean(default=True, readonly=False,
                                      states={'Scheduled': [('readonly', True)], 'Confirmed': [('readonly', True)],
                                              'Completed': [('readonly', True)]})
    gastroenterology_content = fields.Char(readonly=False,
                                           states={'Scheduled': [('readonly', True)], 'Confirmed': [('readonly', True)],
                                                   'Completed': [('readonly', True)]})
    genitourinary = fields.Boolean(default=True, readonly=False,
                                   states={'Scheduled': [('readonly', True)], 'Confirmed': [('readonly', True)],
                                           'Completed': [('readonly', True)]})
    genitourinary_content = fields.Char(readonly=False,
                                        states={'Scheduled': [('readonly', True)], 'Confirmed': [('readonly', True)],
                                                'Completed': [('readonly', True)]})
    dermatological = fields.Boolean(default=True, readonly=False,
                                    states={'Scheduled': [('readonly', True)], 'Confirmed': [('readonly', True)],
                                            'Completed': [('readonly', True)]})
    dermatological_content = fields.Char(readonly=False,
                                         states={'Scheduled': [('readonly', True)], 'Confirmed': [('readonly', True)],
                                                 'Completed': [('readonly', True)]})
    musculoskeletal = fields.Boolean(default=True, readonly=False,
                                     states={'Scheduled': [('readonly', True)], 'Confirmed': [('readonly', True)],
                                             'Completed': [('readonly', True)]})
    musculoskeletal_content = fields.Char(readonly=False,
                                          states={'Scheduled': [('readonly', True)], 'Confirmed': [('readonly', True)],
                                                  'Completed': [('readonly', True)]})
    neurological = fields.Boolean(default=True, readonly=False,
                                  states={'Scheduled': [('readonly', True)], 'Confirmed': [('readonly', True)],
                                          'Completed': [('readonly', True)]})
    neurological_content = fields.Char(readonly=False,
                                       states={'Scheduled': [('readonly', True)], 'Confirmed': [('readonly', True)],
                                               'Completed': [('readonly', True)]})
    psychiatric = fields.Boolean(default=True, readonly=False,
                                 states={'Scheduled': [('readonly', True)], 'Confirmed': [('readonly', True)],
                                         'Completed': [('readonly', True)]})
    psychiatric_content = fields.Char(readonly=False,
                                      states={'Scheduled': [('readonly', True)], 'Confirmed': [('readonly', True)],
                                              'Completed': [('readonly', True)]})
    endocrine = fields.Boolean(default=True, readonly=False,
                               states={'Scheduled': [('readonly', True)], 'Confirmed': [('readonly', True)],
                                       'Completed': [('readonly', True)]})
    endocrine_content = fields.Char(readonly=False,
                                    states={'Scheduled': [('readonly', True)], 'Confirmed': [('readonly', True)],
                                            'Completed': [('readonly', True)]})
    hematology = fields.Boolean(default=True, readonly=False,
                                states={'Scheduled': [('readonly', True)], 'Confirmed': [('readonly', True)],
                                        'Completed': [('readonly', True)]})
    hematology_content = fields.Char(readonly=False,
                                     states={'Scheduled': [('readonly', True)], 'Confirmed': [('readonly', True)],
                                             'Completed': [('readonly', True)]})

    # Past medical History
    past_medical_history_show = fields.Boolean()
    past_medical_history = fields.Many2one('oeh.medical.pathology', string='Disease', readonly=False,
                                           states={'Scheduled': [('readonly', True)], 'Confirmed': [('readonly', True)],
                                                   'Completed': [('readonly', True)]},
                                           related='patient.past_medical_history')
    # last edit 8/2/2022
    past_medical_history_date = fields.Date(string='Date', readonly=False, states={'Scheduled': [('readonly', True)],
                                                                                   'Confirmed': [('readonly', True)],
                                                                                   'Completed': [('readonly', True)]},
                                            related='patient.past_medical_history_date')
    past_medical_history_1st_add = fields.Many2one('oeh.medical.pathology.category', string='Disease',
                                                   readonly=False, states={'Scheduled': [('readonly', True)],
                                                                           'Confirmed': [('readonly', True)],
                                                                           'Completed': [('readonly', True)]},
                                                   related='patient.past_medical_history_1st_add')
    past_medical_history_1st_add_other = fields.Boolean(readonly=False, states={'Scheduled': [('readonly', True)],
                                                                                'Confirmed': [('readonly', True)],
                                                                                'Completed': [('readonly', True)]},
                                                        related='patient.past_medical_history_1st_add_other')
    past_medical_history_1st_add_date = fields.Date(string='Date', readonly=False,
                                                    states={'Scheduled': [('readonly', True)],
                                                            'Confirmed': [('readonly', True)],
                                                            'Completed': [('readonly', True)]},
                                                    related='patient.past_medical_history_1st_add_date')
    # last edit 8/2/2022
    past_medical_history_2nd_add = fields.Many2one('oeh.medical.pathology.category', string='Disease',
                                                   readonly=False, states={'Scheduled': [('readonly', True)],
                                                                           'Confirmed': [('readonly', True)],
                                                                           'Completed': [('readonly', True)]},
                                                   related='patient.past_medical_history_2nd_add')
    past_medical_history_2nd_add_date = fields.Date(string='Date', readonly=False,
                                                    states={'Scheduled': [('readonly', True)],
                                                            'Confirmed': [('readonly', True)],
                                                            'Completed': [('readonly', True)]},
                                                    related='patient.past_medical_history_2nd_add_date')
    past_medical_history_2nd_add_other = fields.Boolean(readonly=False, states={'Scheduled': [('readonly', True)],
                                                                                'Confirmed': [('readonly', True)],
                                                                                'Completed': [('readonly', True)]},
                                                        related='patient.past_medical_history_2nd_add_other')

    # Surgical History
    surgical_history_show = fields.Boolean()
    surgical_history_procedures = fields.Many2one('oeh.medical.procedure', string='Procedures', readonly=False,
                                                  states={'Scheduled': [('readonly', True)],
                                                          'Confirmed': [('readonly', True)],
                                                          'Completed': [('readonly', True)]},
                                                  related='patient.surgical_history_procedures')
    surgical_history_procedures_date = fields.Date(string='Date', readonly=False,
                                                   states={'Scheduled': [('readonly', True)],
                                                           'Confirmed': [('readonly', True)],
                                                           'Completed': [('readonly', True)]},
                                                   related='patient.surgical_history_procedures_date')
    # last edit 8/2/2022
    surgical_history_procedures_1st_add_other = fields.Boolean(readonly=False,
                                                               states={'Scheduled': [('readonly', True)],
                                                                       'Confirmed': [('readonly', True)],
                                                                       'Completed': [('readonly', True)]},
                                                               related='patient.surgical_history_procedures_1st_add_other')
    surgical_history_procedures_1st_add = fields.Many2one('oeh.medical.procedure', string='Procedures',
                                                          readonly=False, states={'Scheduled': [('readonly', True)],
                                                                                  'Confirmed': [('readonly', True)],
                                                                                  'Completed': [('readonly', True)]},
                                                          related='patient.surgical_history_procedures_1st_add')
    surgical_history_procedures_1st_add_date = fields.Date(string='Date', readonly=False,
                                                           states={'Scheduled': [('readonly', True)],
                                                                   'Confirmed': [('readonly', True)],
                                                                   'Completed': [('readonly', True)]},
                                                           related='patient.surgical_history_procedures_1st_add_date')
    # last edit 8/2/2022
    surgical_history_procedures_2nd_add_other = fields.Boolean(readonly=False,
                                                               states={'Scheduled': [('readonly', True)],
                                                                       'Confirmed': [('readonly', True)],
                                                                       'Completed': [('readonly', True)]},
                                                               related='patient.surgical_history_procedures_2nd_add_other')
    surgical_history_procedures_2nd_add = fields.Many2one('oeh.medical.procedure', string='Procedures',
                                                          readonly=False, states={'Scheduled': [('readonly', True)],
                                                                                  'Confirmed': [('readonly', True)],
                                                                                  'Completed': [('readonly', True)]},
                                                          related='patient.surgical_history_procedures_2nd_add')
    surgical_history_procedures_2nd_add_date = fields.Date(string='Date', readonly=False,
                                                           states={'Scheduled': [('readonly', True)],
                                                                   'Confirmed': [('readonly', True)],
                                                                   'Completed': [('readonly', True)]},
                                                           related='patient.surgical_history_procedures_2nd_add_date')
    # Family History
    family_history_show = fields.Boolean()
    family_history = fields.Text(readonly=False,
                                 states={'Scheduled': [('readonly', True)], 'Confirmed': [('readonly', True)],
                                         'Completed': [('readonly', True)]}, related='patient.family_history')

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
        #print(self.drug_allergy)
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
                                        states={'Scheduled': [('readonly', True)], 'Confirmed': [('readonly', True)],
                                                'Completed': [('readonly', True)]})
    drug_allergy = fields.Boolean(default=False, readonly=False,
                                  states={'Scheduled': [('readonly', True)], 'Confirmed': [('readonly', True)],
                                          'Completed': [('readonly', True)]},
                                  related='patient.drug_allergy')
    drug_allergy_content = fields.Char(readonly=False,
                                       states={'Scheduled': [('readonly', True)], 'Confirmed': [('readonly', True)],
                                               'Completed': [('readonly', True)]},
                                       related='patient.drug_allergy_content')

    has_food_allergy = fields.Selection(YES_NO, string='Food Allergy', readonly=False,
                                        related='patient.has_food_allergy',
                                        states={'Scheduled': [('readonly', True)], 'Confirmed': [('readonly', True)],
                                                'Completed': [('readonly', True)]})
    food_allergy = fields.Boolean(default=False, readonly=False,
                                  states={'Scheduled': [('readonly', True)], 'Confirmed': [('readonly', True)],
                                          'Completed': [('readonly', True)]},
                                  related='patient.food_allergy')
    food_allergy_content = fields.Char(readonly=False,
                                       states={'Scheduled': [('readonly', True)], 'Confirmed': [('readonly', True)],
                                               'Completed': [('readonly', True)]},
                                       related='patient.food_allergy_content')

    has_other_allergy = fields.Selection(YES_NO, string='Other Allergy', readonly=False,
                                         related='patient.has_other_allergy',
                                         states={'Scheduled': [('readonly', True)], 'Confirmed': [('readonly', True)],
                                                 'Completed': [('readonly', True)]})
    other_allergy = fields.Boolean(default=False, readonly=False,
                                   states={'Scheduled': [('readonly', True)], 'Confirmed': [('readonly', True)],
                                           'Completed': [('readonly', True)]},
                                   related='patient.other_allergy')
    other_allergy_content = fields.Char(readonly=False,
                                        states={'Scheduled': [('readonly', True)], 'Confirmed': [('readonly', True)],
                                                'Completed': [('readonly', True)]},
                                        related='patient.other_allergy_content')

    # Personal Habits
    personal_habits_show = fields.Boolean()
    # Physical Exercise
    # last edit 8/2/2022
    exercise = fields.Boolean(string='Exercise', readonly=False,
                              states={'Scheduled': [('readonly', True)], 'Confirmed': [('readonly', True)],
                                      'Completed': [('readonly', True)]}, related='patient.exercise')
    exercise_minutes_day = fields.Integer(string='Minutes / day',
                                          help="How many minutes a day the patient exercises",
                                          readonly=False,
                                          states={'Scheduled': [('readonly', True)], 'Confirmed': [('readonly', True)],
                                                  'Completed': [('readonly', True)]},
                                          related='patient.exercise_minutes_day')
    # sleep
    sleep_hours = fields.Integer(string='Hours of Sleep', help="Average hours of sleep per day", readonly=False,
                                 states={'Scheduled': [('readonly', True)], 'Confirmed': [('readonly', True)],
                                         'Completed': [('readonly', True)]}, related='patient.sleep_hours')
    sleep_during_daytime = fields.Boolean(string='Sleeps at Daytime',
                                          help="Check if the patient sleep hours are during daylight rather than at night",
                                          readonly=False,
                                          states={'Scheduled': [('readonly', True)], 'Confirmed': [('readonly', True)],
                                                  'Completed': [('readonly', True)]},
                                          related='patient.sleep_during_daytime')
    # Smoking
    smoking = fields.Boolean(string='Smokes', readonly=False,
                             states={'Scheduled': [('readonly', True)], 'Confirmed': [('readonly', True)],
                                     'Completed': [('readonly', True)]}, related='patient.smoking')
    # last edit 8/2/2022
    smoking_number = fields.Integer(string='Cigarretes a Day', readonly=False,
                                    states={'Scheduled': [('readonly', True)], 'Confirmed': [('readonly', True)],
                                            'Completed': [('readonly', True)]}, related='patient.smoking_number')
    age_start_smoking = fields.Integer(string='Age Started to Smoke', readonly=False,
                                       states={'Scheduled': [('readonly', True)], 'Confirmed': [('readonly', True)],
                                               'Completed': [('readonly', True)]}, related='patient.age_start_smoking')

    ex_smoker = fields.Boolean(string='Ex-smoker', readonly=False,
                               states={'Scheduled': [('readonly', True)], 'Confirmed': [('readonly', True)],
                                       'Completed': [('readonly', True)]}, related='patient.ex_smoker')
    age_start_ex_smoking = fields.Integer(string='Age Started to Smoke', readonly=False,
                                          states={'Scheduled': [('readonly', True)], 'Confirmed': [('readonly', True)],
                                                  'Completed': [('readonly', True)]},
                                          related='patient.age_start_ex_smoking')
    age_quit_smoking = fields.Integer(string='Age of Quitting', help="Age of quitting smoking", readonly=False,
                                      states={'Scheduled': [('readonly', True)], 'Confirmed': [('readonly', True)],
                                              'Completed': [('readonly', True)]}, related='patient.age_quit_smoking')
    second_hand_smoker = fields.Boolean(string='Passive Smoker',
                                        help="Check it the patient is a passive / second-hand smoker",
                                        readonly=False,
                                        states={'Scheduled': [('readonly', True)], 'Confirmed': [('readonly', True)],
                                                'Completed': [('readonly', True)]},
                                        related='patient.second_hand_smoker')
    # drink
    alcohol = fields.Boolean(string='Drinks Alcohol', readonly=False,
                             states={'Scheduled': [('readonly', True)], 'Confirmed': [('readonly', True)],
                                     'Completed': [('readonly', True)]}, related='patient.alcohol')
    age_start_drinking = fields.Integer(string='Age Started to Drink ', help="Date to start drinking",
                                        readonly=False,
                                        states={'Scheduled': [('readonly', True)], 'Confirmed': [('readonly', True)],
                                                'Completed': [('readonly', True)]},
                                        related='patient.age_start_drinking')

    alcohol_beer_number = fields.Integer(string='Beer / day', readonly=False,
                                         states={'Scheduled': [('readonly', True)], 'Confirmed': [('readonly', True)],
                                                 'Completed': [('readonly', True)]},
                                         related='patient.alcohol_beer_number')
    alcohol_liquor_number = fields.Integer(string='Liquor / day', readonly=False,
                                           states={'Scheduled': [('readonly', True)], 'Confirmed': [('readonly', True)],
                                                   'Completed': [('readonly', True)]},
                                           related='patient.alcohol_liquor_number')
    ex_alcoholic = fields.Boolean(string='Ex Alcoholic', readonly=False,
                                  states={'Scheduled': [('readonly', True)], 'Confirmed': [('readonly', True)],
                                          'Completed': [('readonly', True)]}, related='patient.ex_alcoholic')
    # last edit 8/2/2022
    alcohol_wine_number = fields.Integer(string='Wine / day', readonly=False,
                                         states={'Scheduled': [('readonly', True)], 'Confirmed': [('readonly', True)],
                                                 'Completed': [('readonly', True)]},
                                         related='patient.alcohol_wine_number')
    age_quit_drinking = fields.Integer(string='Age Quit Drinking ', help="Date to stop drinking", readonly=False,
                                       states={'Scheduled': [('readonly', True)], 'Confirmed': [('readonly', True)],
                                               'Completed': [('readonly', True)]}, related='patient.age_quit_drinking')

    # Vaccination
    vaccination_show = fields.Boolean()
    Vaccination = fields.Many2one('sm.shifa.generic.vaccines', string='Vaccine', readonly=False,
                                  states={'Scheduled': [('readonly', True)], 'Confirmed': [('readonly', True)],
                                          'Completed': [('readonly', True)]}, related='patient.Vaccination')
    vaccination_date = fields.Date(string='Date', readonly=False,
                                   states={'Scheduled': [('readonly', True)], 'Confirmed': [('readonly', True)],
                                           'Completed': [('readonly', True)]}, related='patient.vaccination_date')
    # last edit 8/2/2022
    Vaccination_1st_add_other = fields.Boolean(readonly=False, states={'Scheduled': [('readonly', True)],
                                                                       'Confirmed': [('readonly', True)],
                                                                       'Completed': [('readonly', True)]},
                                               related='patient.Vaccination_1st_add_other')
    Vaccination_1st_add = fields.Many2one('sm.shifa.generic.vaccines', string='Procedures', readonly=False,
                                          states={'Scheduled': [('readonly', True)], 'Confirmed': [('readonly', True)],
                                                  'Completed': [('readonly', True)]},
                                          related='patient.Vaccination_1st_add')
    Vaccination_1st_add_date = fields.Date(string='Date', readonly=False,
                                           states={'Scheduled': [('readonly', True)], 'Confirmed': [('readonly', True)],
                                                   'Completed': [('readonly', True)]},
                                           related='patient.Vaccination_1st_add_date')

    Vaccination_2nd_add_other = fields.Boolean(readonly=False, states={'Scheduled': [('readonly', True)],
                                                                       'Confirmed': [('readonly', True)],
                                                                       'Completed': [('readonly', True)]},
                                               related='patient.Vaccination_2nd_add_other')
    # last edit 8/2/2022
    Vaccination_2nd_add = fields.Many2one('sm.shifa.generic.vaccines', string='Procedures', readonly=False,
                                          states={'Scheduled': [('readonly', True)], 'Confirmed': [('readonly', True)],
                                                  'Completed': [('readonly', True)]},
                                          related='patient.Vaccination_2nd_add')
    Vaccination_2nd_add_date = fields.Date(string='Date', readonly=False,
                                           states={'Scheduled': [('readonly', True)], 'Confirmed': [('readonly', True)],
                                                   'Completed': [('readonly', True)]},
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


class ShifaImageTestInherit(models.Model):
    _inherit = 'oeh.medical.imaging'

    appointment = fields.Many2one("oeh.medical.appointment", string='Appointment',
                                  ondelete='cascade')


class ShifaReferralInherit(models.Model):
    _inherit = 'sm.shifa.referral'

    appointment = fields.Many2one("oeh.medical.appointment", string='Appointment',
                                  ondelete='cascade')


class ShifaInvestigationInherit(models.Model):
    _inherit = 'sm.shifa.investigation'

    appointment = fields.Many2one("oeh.medical.appointment", string='Appointment')


class ShifaAppointmentInvestigation(models.Model):
    _inherit = "oeh.medical.appointment"
    # last edit 8/2/2022
    lab_test_ids = fields.One2many('sm.shifa.lab.request', 'appointment', string='Lab Request')
    image_test_id = fields.One2many('sm.shifa.imaging.request', 'appointment', string='Imaging Request')
    investigation_ids = fields.One2many('sm.shifa.investigation', 'appointment', string='Appointment')


# last edit 8/2/2022
class ShifaLabTestAppointment(models.Model):
    _inherit = 'sm.shifa.lab.request'

    appointment = fields.Many2one("oeh.medical.appointment", string='Appointment')


# last edit 8/2/2022
class ShifaImagingTestForAppointment(models.Model):
    _inherit = 'sm.shifa.imaging.request'

    appointment = fields.Many2one("oeh.medical.appointment", string='Appointment')


class ShifaEvaluationForAppointment(models.Model):
    _inherit = 'oeh.medical.evaluation'

    appointment = fields.Many2one("oeh.medical.appointment", string='Appointment')


class ShifaAppointmentExamination(models.Model):
    _inherit = "oeh.medical.appointment"

    home_rounding_ids = fields.One2many('sm.shifa.home.rounding', 'admission_id', string='Home Rounding')

    # , readonly = True,
    # states = {'Hospitalized': [('readonly', False)],
    #           'On Ventilation': [('readonly', False)],
    #           'Ventilation Removed': [('readonly', False)]}
    # Anthropometry
    weight = fields.Float(string="Weight (kg)")
    height = fields.Float(string="Height (cm)")
    abdominal_circ = fields.Float(string="Abdominal Circumference")
    head_circumference = fields.Float(string="Head Circumference")
    bmi = fields.Float(string="Body Mass Index (BMI)")

    # Vital Signs
    temperature = fields.Float(string="Temperature (celsius)")
    systolic = fields.Integer(string="Systolic Pressure")
    respiratory_rate = fields.Integer(string="Respiratory Rate")
    osat = fields.Integer(string="Oxygen Saturation")
    diastolic = fields.Integer(string="Diastolic Pressure")
    bpm = fields.Integer(string="Heart Rate")

    # Glucose
    glycemia = fields.Float(string="Glycemia")
    hba1c = fields.Float(string="Glycated Hemoglobin")

    # Nutrition
    malnutrition = fields.Boolean(string="Malnutrition")
    dehydration = fields.Boolean(string="Dehydration")

    head_neck = fields.Boolean()
    head_neck_content = fields.Char()

    cardiovascular = fields.Boolean()
    cardiovascular_content = fields.Char()

    chest = fields.Boolean()
    chest_content = fields.Char()

    abdomen = fields.Boolean()
    abdomen_content = fields.Char()

    musculo = fields.Boolean()
    musculo_content = fields.Char()

    cns = fields.Boolean()
    cns_content = fields.Char()

    psychiatric = fields.Boolean()
    psychiatric_content = fields.Char()

    rectal = fields.Boolean()
    rectal_content = fields.Char()

    skin = fields.Boolean()
    skin_content = fields.Char()

    urine_test = fields.Boolean()
    urine_test_content = fields.Char()

    develop = fields.Boolean()
    develop_content = fields.Char()

    # Photo Images
    image1 = fields.Binary(string="Image 1")
    image2 = fields.Binary(string="Image 2")


class ShifaPrescribedMedicineForAppointment(models.Model):
    _inherit = 'oeh.medical.inpatient.prescribed.medicine'

    appointment = fields.Many2one("oeh.medical.appointment", string='Appointment', index=True)


class ShifaConsumedMedicineForAppointment(models.Model):
    _inherit = 'oeh.medical.inpatient.consumed.medicine'

    appointment = fields.Many2one("oeh.medical.appointment", string='Appointment', index=True)


class ShifaAppointmentExaminationTab(models.Model):
    _inherit = "oeh.medical.appointment"
    pain_score = [
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
    yes_no = [
        ('Yes', 'Yes'),
        ('No', 'No'),
    ]
    musculoskeletal_extremity = [
        ('Active Against Gravity and Resistance', 'Active Against Gravity and Resistance'),
        ('Active with Gravity Eliminated', 'Active with Gravity Eliminated'),
        ('Contracture', 'Contracture'),
        ('Deformity', 'Deformity'),
        ('Dislocation', 'Dislocation'),
        ('Fracture', 'Fracture'),
        ('Paralysis', 'Paralysis'),
        ('Prosthesis', 'Prosthesis'),
        ('Stiffness', 'Stiffness'),
        ('Weak', 'Weak'),
        ('Other', 'Other'),
    ]
    number_neuralogical = [
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
    level_consciousness = [
        ('Alert', 'Alert'),
        ('Awake', 'Awake'),
        ('Decrease response to environment', 'Decrease response to environment'),
        ('Delirious', 'Delirious'),
        ('Drowsiness', 'Drowsiness'),
        ('Irritable', 'Irritable'),
        ('Lathargy', 'Lathargy'),
        ('Obtunded', 'Obtunded'),
        ('Restless', 'Restless'),
        ('Stuper', 'Stuper'),
        ('Unresponsnsive', 'Unresponsnsive'),
    ]
    eye_momement = [
        ('Spontaneous', 'Spontaneous'),
        ('To speech', 'To speech'),
        ('To pain', 'To pain'),
        ('No respond', 'No respond'),
    ]

    cal_score_eye = {
        'Spontaneous': 4,
        'To speech': 3,
        'To pain': 2,
        'No respond': 1,
    }
    cal_score_motor = {
        'Spontaneous movements': 6,
        'Localizes pain': 5,
        'Flexion withdrawal': 4,
        'Abnormal flexion': 3,
        'Abnormal extension': 2,
        'No response': 1,
    }
    cal_score_verbal = {
        'Coos and smiles appropriate': 5,
        'Cries': 4,
        'Inappropriate crying/screaming': 3,
        'Grunts': 2,
        'No response': 1,
    }
    cal_score_verbal_2_5 = {
        'Appropriate Words': 5,
        'Inappropriate Word': 4,
        'Cries/Screams': 3,
        'Grunts': 2,
        'No response': 1,
    }
    cal_score_verbal_5 = {
        'Orient': 5,
        'Confused': 4,
        'Inappropriate': 3,
        'Incompratensive': 2,
        'No verable response': 1,
    }
    motor_response = [
        ('Obeys command', 'Obeys command'),
        ('Localizes pain', 'Localizes pain'),
        ('Withdraws from pain', 'Withdraws from pain'),
        ('Flexion response to pain', 'Flexion response to pain'),
        ('Extension response to pain', 'Extension response to pain'),
        ('No motor response', 'No motor response'),
    ]
    motor_response_dec = {
        'Obeys command': 6,
        'Localizes pain': 5,
        'Withdraws from pain': 4,
        'Flexion response to pain': 3,
        'Extension response to pain': 2,
        'No motor response': 1,
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
                #print(r.bmi)
                return r.bmi

    # Examination tab
    vital_signs_show = fields.Boolean()
    temperature = fields.Float(string="Temperature (c)", readonly=True, states={'Start': [('readonly', False)]})
    systolic = fields.Integer(string="Systolic BP(mmHg)", readonly=True, states={'Start': [('readonly', False)]})
    respiratory_rate = fields.Integer(string="RR (/min)", readonly=True,
                                      states={'Start': [('readonly', False)]})
    # osat = fields.Float(string="O2 Sat(%)", readonly=True, states={'Start': [('readonly', False)]})
    at_room_air = fields.Boolean(string="at room air", readonly=True, states={'Start': [('readonly', False)]})
    with_oxygen_support = fields.Boolean(string="with oxygen Support", readonly=True,
                                         states={'Start': [('readonly', False)]})
    char_other_oxygen = fields.Char(readonly=True, states={'Start': [('readonly', False)]})
    diastolic = fields.Integer(string="Diastolic BR(mmHg)", readonly=True,
                               states={'Start': [('readonly', False)]})
    bpm = fields.Integer(string="HR (/min)", readonly=True, states={'Start': [('readonly', False)]})
    # metabolic
    metabolic_show = fields.Boolean()
    weight = fields.Float(string='Weight (kg)', readonly=True, states={'Start': [('readonly', False)]})
    waist_circ = fields.Float(string='Waist Circumference (cm)', readonly=True, states={'Start': [('readonly', False)]})
    bmi = fields.Float(compute=_compute_bmi, string='Body Mass Index (BMI)', store=True)
    height = fields.Float(string='Height (cm)', readonly=True, states={'Start': [('readonly', False)]})
    head_circumference = fields.Float(string='Head Circumference(cm)', help="Head circumference", readonly=True,
                                      states={'Start': [('readonly', False)]})

    # Pain Assessment
    pain_present_show = fields.Boolean()
    admission_pain_score = fields.Selection([
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
    ], readonly=True, states={'Start': [('readonly', False)]})
    admission_scale_used = fields.Selection([
        ('Numerical', 'Numerical'),
        ('Faces', 'Faces'),
        ('FLACC', 'FLACC'),
        ('ABBEY', 'ABBEY'),
    ], readonly=True, states={'Start': [('readonly', False)]})

    location_head = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    location_face = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    location_limbs = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    location_chest = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    location_abdomen = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    location_back = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    location_of_pain = fields.Text(readonly=True, states={'Start': [('readonly', False)]})

    Characteristics_dull = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    Characteristics_sharp = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    Characteristics_burning = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    Characteristics_throbbing = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    Characteristics_other = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    Characteristics_patient_own_words = fields.Text(readonly=True, states={'Start': [('readonly', False)]})

    onset_time_sudden = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    onset_time_gradual = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    onset_time_constant = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    onset_time_intermittent = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    onset_time_other = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    onset_time_fdv = fields.Text(readonly=True, states={'Start': [('readonly', False)]})

    provoking_factors_food = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    provoking_factors_rest = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    provoking_factors_movement = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    provoking_factors_palpation = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    provoking_factors_other = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    provoking_factors_patient_words = fields.Text(readonly=True, states={'Start': [('readonly', False)]})

    relieving_factors_rest = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    relieving_factors_medication = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    relieving_factors_heat = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    relieving_factors_distraction = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    relieving_factors_other = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    relieving_factors_patient_words = fields.Text(readonly=True, states={'Start': [('readonly', False)]})

    expressing_pain_verbal = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    expressing_pain_facial = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    expressing_pain_body = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    expressing_pain_other = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    expressing_pain_when_pain = fields.Text(readonly=True, states={'Start': [('readonly', False)]})

    effect_of_pain_nausea = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    effect_of_pain_vomiting = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    effect_of_pain_appetite = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    effect_of_pain_activity = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    effect_of_pain_relationship = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    effect_of_pain_emotions = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    effect_of_pain_concentration = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    effect_of_pain_sleep = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    effect_of_pain_other = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    effect_of_pain_other_text = fields.Text(readonly=True, states={'Start': [('readonly', False)]})
    # last edit 8/2/2022
    # previous_methods_pain = fields.Text(readonly=True, states={'Start': [('readonly', False)]})
    # previous_methods_pain_not = fields.Text(readonly=True, states={'Start': [('readonly', False)]})

    pain_management_advice_analgesia = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    pain_management_change_of = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    pain_management_refer_physician = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    pain_management_refer_physician_home = fields.Boolean(string="Home Care", readonly=True,
                                                          states={'Start': [('readonly', False)]})
    pain_management_refer_physician_palliative = fields.Boolean(string="palliative", readonly=True,
                                                                states={'Start': [('readonly', False)]})
    pain_management_refer_physician_primary = fields.Boolean(string="primary", readonly=True,
                                                             states={'Start': [('readonly', False)]})
    pain_management_refer_hospital = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    pain_management_other = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    pain_management_other_text = fields.Text(readonly=True, states={'Start': [('readonly', False)]})
    pain_management_comment = fields.Text(readonly=True, states={'Start': [('readonly', False)]})

    # General Condition
    general_condition_show = fields.Boolean()
    general_condition = fields.Text(string='General Condition', readonly=True, states={'Start': [('readonly', False)]})

    # EENT
    EENT_show = fields.Boolean()
    eent_eye = fields.Boolean(default=True, readonly=True, states={'Start': [('readonly', False)]})
    eent_eye_condition = fields.Char(readonly=True, states={'Start': [('readonly', False)]})
    eent_eye_vision = fields.Char(readonly=True, states={'Start': [('readonly', False)]})
    eent_ear = fields.Boolean(default=True, readonly=True, states={'Start': [('readonly', False)]})
    eent_ear_content = fields.Char(readonly=True, states={'Start': [('readonly', False)]})
    eent_nose = fields.Boolean(default=True, readonly=True, states={'Start': [('readonly', False)]})
    eent_nose_content = fields.Char(readonly=True, states={'Start': [('readonly', False)]})
    eent_throut = fields.Boolean(default=True, readonly=True, states={'Start': [('readonly', False)]})
    eent_throut_content = fields.Char(readonly=True, states={'Start': [('readonly', False)]})
    eent_neck = fields.Boolean(default=True, readonly=True, states={'Start': [('readonly', False)]})
    eent_neck_content = fields.Char(readonly=True, states={'Start': [('readonly', False)]})
    # last edit 8/2/2022
    eent_remarks = fields.Text(readonly=True, states={'Start': [('readonly', False)]})

    # csv
    csv_show = fields.Boolean()
    cvs_h_sound_1_2 = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    cvs_h_sound_3 = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    cvs_h_sound_4 = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    cvs_h_sound_click = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    cvs_h_sound_murmurs = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    cvs_h_sound_other = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    cvs_h_sound_other_text = fields.Char(readonly=True, states={'Start': [('readonly', False)]})

    cvs_rhythm = fields.Selection([
        ('Regular', 'Regular'),
        ('Irregular', 'Irregular'),
        ('Regular Irregular', 'Regular Irregular'),
        ('Irregular Irregular', 'Irregular Irregular'),
    ], default='Regular', readonly=True, states={'Start': [('readonly', False)]})
    cvs_peripherial_pulse = fields.Selection([
        ('Normal Palpable', 'Normal Palpable'),
        ('Absent Without Pulse', 'Absent Without Pulse'),
        ('Diminished', 'Diminished'),
        ('Bounding', 'Bounding'),
        ('Full and brisk', 'Full and brisk'),
    ], default='Normal Palpable', readonly=True, states={'Start': [('readonly', False)]})

    cvs_edema_yes_no = fields.Selection(yes_no, readonly=True, states={'Start': [('readonly', False)]})
    cvs_edema_yes_type = fields.Selection([
        ('Pitting', 'Pitting'),
        ('Non-Pitting', 'Non-Pitting'),
    ], readonly=True, states={'Start': [('readonly', False)]})
    cvs_edema_yes_location = fields.Text(readonly=True, states={'Start': [('readonly', False)]})
    cvs_edema_yes_grade = fields.Selection([
        ('I- 2mm Depth', 'I- 2mm Depth'),
        ('II- 4mm Depth', 'II- 4mm Depth'),
        ('III- 6mm Depth', 'III- 6mm Depth'),
        ('IV- 8mm Depth', 'IV- 8mm Depth'),
    ], readonly=True, states={'Start': [('readonly', False)]})
    cvs_edema_yes_capillary = fields.Selection([
        ('Less than', 'Less than'),
        ('2-3', '2-3'),
        ('3-4', '3-4'),
        ('4-5', '4-5'),
        ('More than 5', 'More than 5'),
    ], readonly=True, states={'Start': [('readonly', False)]})

    cvs_parenteral_devices_yes_no = fields.Selection(yes_no, readonly=True, states={'Start': [('readonly', False)]})
    cvs_parenteral_devices_yes_sel = fields.Selection([
        ('Central Line', 'Central Line'),
        ('TPN', 'TPN'),
        ('IV Therapy', 'IV Therapy'),
        ('PICC Line', 'PICC Line'),
        ('Other', 'Other'),
    ], readonly=True, states={'Start': [('readonly', False)]})
    cvs_remarks = fields.Text(readonly=True, states={'Start': [('readonly', False)]})
    # Respiratory
    respiratory_show = fields.Boolean()
    lung_sounds_clear = fields.Boolean(default=True, readonly=True, states={'Start': [('readonly', False)]})
    lung_sounds_diminished = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    lung_sounds_absent = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    lung_sounds_fine_crackles = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    lung_sounds_rhonchi = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    lung_sounds_stridor = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    lung_sounds_wheeze = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    lung_sounds_coarse_crackles = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})

    Location_bilateral = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    Location_left_lower = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    Location_left_middle = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    Location_left_upper = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    Location_lower = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    Location_upper = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    Location_right_lower = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    Location_right_middle = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    Location_right_upper = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})

    type_regular = fields.Boolean(default=True, readonly=True, states={'Start': [('readonly', False)]})
    type_irregular = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    type_rapid = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    type_dyspnea = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    type_apnea = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    type_tachypnea = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    type_orthopnea = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    type_accessory_muscles = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    type_snoring_mechanical = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    Cough_yes_no = fields.Selection(yes_no, readonly=True, states={'Start': [('readonly', False)]})
    cough_yes_type = fields.Selection([
        ('Productive', 'Productive'),
        ('none-productive', 'none-productive'),
        ('Spontaneous', 'Spontaneous'),
    ], readonly=True, states={'Start': [('readonly', False)]})
    cough_yes_frequency = fields.Selection([
        ('Spontaneous', 'Spontaneous'),
        ('Occassional', 'Occassional'),
        ('Persistent', 'Persistent'),
    ], readonly=True, states={'Start': [('readonly', False)]})
    cough_yes_amount = fields.Selection([
        ('Scanty', 'Scanty'),
        ('Moderate', 'Moderate'),
        ('Large', 'Large'),
    ], readonly=True, states={'Start': [('readonly', False)]})
    cough_yes_characteristic = fields.Selection([
        ('Clear', 'Clear'),
        ('Yellow', 'Yellow'),
        ('Mucoid', 'Mucoid'),
        ('Mucopurulent', 'Mucopurulent'),
        ('Purulent', 'Purulent'),
        ('Pink Frothy', 'Pink Frothy'),
        ('Blood streaked', 'Blood streaked'),
        ('Bloody', 'Bloody'),
    ], readonly=True, states={'Start': [('readonly', False)]})

    respiratory_support_yes_no = fields.Selection(yes_no, readonly=True, states={'Start': [('readonly', False)]})
    respiratory_support_yes_oxygen = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    respiratory_support_yes_oxygen_text = fields.Text(readonly=True, states={'Start': [('readonly', False)]})
    respiratory_support_yes_trachestory = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    respiratory_support_yes_trachestory_text = fields.Text(readonly=True, states={'Start': [('readonly', False)]})
    respiratory_support_yes_ventilator = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    respiratory_support_yes_ventilator_text = fields.Text(readonly=True, states={'Start': [('readonly', False)]})

    suction_yes_no = fields.Selection(yes_no, readonly=True, states={'Start': [('readonly', False)]})
    suction_yes_type = fields.Selection([
        ('Nasal', 'Nasal'),
        ('Oral', 'Oral'),
        ('Trachestory', 'Trachestory'),
    ], readonly=True, states={'Start': [('readonly', False)]})
    suction_yes_frequency = fields.Integer(readonly=True, states={'Start': [('readonly', False)]})

    nebulization_yes_no = fields.Selection(yes_no, readonly=True, states={'Start': [('readonly', False)]})
    nebulization_yes_frequency = fields.Integer(readonly=True, states={'Start': [('readonly', False)]})
    nebulization_yes_medication = fields.Many2one('oeh.medical.medicines', string='Medicines', readonly=True,
                                                  states={'Start': [('readonly', False)]})
    respiratory_remarks = fields.Text(readonly=True, states={'Start': [('readonly', False)]})

    # Neuralogical

    neuralogical_show = fields.Boolean()
    neuralogical_left_eye = fields.Selection(number_neuralogical, readonly=True,
                                             states={'Start': [('readonly', False)]})
    neuralogical_right_eye = fields.Selection(number_neuralogical, readonly=True,
                                              states={'Start': [('readonly', False)]})
    neuralogical_pupil_reaction = fields.Selection([
        ('Equal round, reactive', 'Equal round, reactive'),
        ('Equal round, none reactive', 'Equal round, none reactive'),
        ('Miosis', 'Miosis'),
        ('Mydriasis', 'Mydriasis'),
        ('Sluggish', 'Sluggish'),
        ('Brisk', 'Brisk'),
        ('Elliptical', 'Elliptical'),
        ('Anisocoria', 'Anisocoria'),
    ], default='Equal round, reactive', readonly=True, states={'Start': [('readonly', False)]})
    neuralogical_old = fields.Selection([
        ('Greater Than 5 years Old', 'Greater Than 5 years Old'),
        ('2 to 5 Years Old', '2 to 5 Years Old'),
        ('Less than 2 Years Old', 'Less than 2 Years Old'),
    ], readonly=True, states={'Start': [('readonly', False)]})
    neuralogical_greater_than_5_years_mental = fields.Selection([
        ('Alert', 'Alert'),
        ('Disoriented', 'Disoriented'),
        ('Lethargy', 'Lethargy'),
        ('Minimally responsive', 'Minimally responsive'),
        ('No response', 'No response'),
        ('Obtunded', 'Obtunded'),
        ('Orient to person', 'Orient to person'),
        ('Orient to place', 'Orient to place'),
        ('Orient to situation', 'Orient to situation'),
        ('Orient to time', 'Orient to time'),
        ('Stupor', 'Stupor'),
    ], readonly=True, states={'Start': [('readonly', False)]})
    neuralogical_greater_than_5_years_facial = fields.Selection([
        ('Symmetric', 'Symmetric'),
        ('Unequal facial movement', 'Unequal facial movement'),
        ('Drooping left side of face', 'Drooping left side of face'),
        ('Drooping left side of mouth', 'Drooping left side of mouth'),
        ('Drooping right side of face', 'Drooping right side of face'),
        ('Drooping right side of mouth', 'Drooping right side of mouth'),
    ], readonly=True, states={'Start': [('readonly', False)]})
    neuralogical_greater_than_5_years_glascow = fields.Float(compute=_compute_greater_5_old)
    neuralogical_greater_than_5_years_eye = fields.Selection(eye_momement, readonly=True,
                                                             states={'Start': [('readonly', False)]})
    neuralogical_greater_than_5_years_motor = fields.Selection(motor_response, readonly=True,
                                                               states={'Start': [('readonly', False)]})
    neuralogical_greater_than_5_years_verbal = fields.Selection([
        ('Orient', 'Orient'),
        ('Confused', 'Confused'),
        ('Inappropriate', 'Inappropriate'),
        ('Incompratensive', 'Incompratensive'),
        ('No verable response', 'No verable response'),
    ], readonly=True, states={'Start': [('readonly', False)]})
    neuralogical_2_to_5_level = fields.Selection(level_consciousness, readonly=True,
                                                 states={'Start': [('readonly', False)]})
    neuralogical_2_to_5_glascow = fields.Float(compute=_compute_2_5_old)
    neuralogical_2_to_5_eye = fields.Selection(eye_momement, readonly=True, states={'Start': [('readonly', False)]})
    neuralogical_2_to_5_motor = fields.Selection(motor_response, readonly=True, states={'Start': [('readonly', False)]})
    neuralogical_2_to_5_verbal = fields.Selection([
        ('Appropriate Words', 'Appropriate Words'),
        ('Inappropriate Word', 'Inappropriate Word'),
        ('Cries/Screams', 'Cries/Screams'),
        ('Grunts', 'Grunts'),
        ('No response', 'No response'),
    ], readonly=True, states={'Start': [('readonly', False)]})
    neuralogical_less_than_2_level = fields.Selection(level_consciousness, readonly=True,
                                                      states={'Start': [('readonly', False)]})
    neuralogical_less_than_2_glascow = fields.Float(compute=_compute_less_2)
    neuralogical_less_than_2_eye = fields.Selection(eye_momement, readonly=True,
                                                    states={'Start': [('readonly', False)]})
    neuralogical_less_than_2_motor = fields.Selection([
        ('Spontaneous movements', 'Spontaneous movements'),
        ('Localizes pain', 'Localizes pain'),
        ('Flexion withdrawal', 'Flexion withdrawal'),
        ('Abnormal flexion', 'Abnormal flexion'),
        ('Abnormal extension', 'Abnormal extension'),
        ('No response', 'No response'),
    ], readonly=True, states={'Start': [('readonly', False)]})
    neuralogical_less_than_2_verbal = fields.Selection([
        ('Coos and smiles appropriate', 'Coos and smiles appropriate'),
        ('Cries', 'Cries'),
        ('Inappropriate crying/screaming', 'Inappropriate crying/screaming'),
        ('Grunts', 'Grunts'),
        ('No response', 'No response'),
    ], readonly=True, states={'Start': [('readonly', False)]})
    # last edit 8/2/2022
    neuralogical_remarks = fields.Text(readonly=True, states={'Start': [('readonly', False)]})
    # Gastrointestinal
    gastrointestinal_show = fields.Boolean()
    gastrointestinal_bowel_sound = fields.Selection([
        ('Active', 'Active'),
        ('Absent', 'Absent'),
        ('Hypoactive', 'Hypoactive'),
        ('Hyperactive', 'Hyperactive'),
    ], default='Active', readonly=True, states={'Start': [('readonly', False)]})
    gastrointestinal_abdomen_lax = fields.Boolean(default=True, readonly=True, states={'Start': [('readonly', False)]})
    gastrointestinal_abdomen_soft = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    gastrointestinal_abdomen_firm = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    gastrointestinal_abdomen_distended = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    gastrointestinal_abdomen_tender = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    gastrointestinal_stool_color = fields.Selection([
        ('Brown', 'Brown'),
        ('Yellow', 'Yellow'),
        ('Black', 'Black'),
        ('Bright Red', 'Bright Red'),
        ('Dark Red', 'Dark Red'),
        ('Clay', 'Clay'),
    ], default='Brown', readonly=True, states={'Start': [('readonly', False)]})
    gastrointestinal_stool_loose = fields.Boolean(default=True, readonly=True, states={'Start': [('readonly', False)]})
    gastrointestinal_stool_hard = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    gastrointestinal_stool_mucoid = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    gastrointestinal_stool_soft = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    gastrointestinal_stool_tarry = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    gastrointestinal_stool_formed = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    gastrointestinal_stool_semi_formed = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    gastrointestinal_stool_bloody = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    gastrointestinal_stoma_none = fields.Boolean(default=True, readonly=True, states={'Start': [('readonly', False)]})
    gastrointestinal_stoma_colostory = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    gastrointestinal_stoma_ileostomy = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    gastrointestinal_stoma_peg = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    gastrointestinal_stoma_pej = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    gastrointestinal_stoma_urostomy = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    gastrointestinal_problem_none = fields.Boolean(default=True, readonly=True, states={'Start': [('readonly', False)]})
    gastrointestinal_problem_nausea = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    gastrointestinal_problem_vomiting = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    gastrointestinal_problem_colic = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    gastrointestinal_problem_diarrhea = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    gastrointestinal_problem_constipation = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    gastrointestinal_problem_dysphagia = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    gastrointestinal_problem_hemorrhoids = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    gastrointestinal_problem_anal_fissure = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    gastrointestinal_problem_anal_fistula = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    gastrointestinal_problem_other = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    gastrointestinal_problem_other_text = fields.Text(readonly=True, states={'Start': [('readonly', False)]})
    gastrointestinal_bowel_movement_none = fields.Boolean(default=True, readonly=True,
                                                          states={'Start': [('readonly', False)]})
    gastrointestinal_bowel_movement_laxative = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    gastrointestinal_bowel_movement_enema = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    gastrointestinal_bowel_movement_stoma = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    gastrointestinal_bowel_movement_stool_softener = fields.Boolean(readonly=True,
                                                                    states={'Start': [('readonly', False)]})
    gastrointestinal_bowel_movement_suppository = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    gastrointestinal_bowel_movement_digital = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    gastrointestinal_bowel_movement_other = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    gastrointestinal_bowel_movement_other_text = fields.Text(readonly=True, states={'Start': [('readonly', False)]})
    gastrointestinal_enteral_device_none = fields.Boolean(default=True, readonly=True,
                                                          states={'Start': [('readonly', False)]})
    gastrointestinal_enteral_device_nasogastric_tube = fields.Boolean(readonly=True,
                                                                      states={'Start': [('readonly', False)]})
    gastrointestinal_enteral_device_orogastric_tube = fields.Boolean(readonly=True,
                                                                     states={'Start': [('readonly', False)]})
    gastrointestinal_enteral_device_gastro_jejunal = fields.Boolean(readonly=True,
                                                                    states={'Start': [('readonly', False)]})
    gastrointestinal_enteral_device_peg = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    gastrointestinal_enteral_device_pej = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    gastrointestinal_enteral_device_pd = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    gastrointestinal_enteral_device_other = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    gastrointestinal_enteral_device_other_text = fields.Text(readonly=True, states={'Start': [('readonly', False)]})
    gastrointestinal_remarks = fields.Text(readonly=True, states={'Start': [('readonly', False)]})

    # Genitourinary
    genitourinary_show = fields.Boolean()
    genitourinary_urine_color = fields.Selection([
        ('Pale Yellow', 'Pale Yellow'),
        ('Dark Yellow', 'Dark Yellow'),
        ('Yellow', 'Yellow'),
        ('Tea-Colored', 'Tea-Colored'),
        ('Red', 'Red'),
        ('Blood Tinged', 'Blood Tinged'),
        ('Green', 'Green'),
    ], default='Pale Yellow', readonly=True, states={'Start': [('readonly', False)]})
    genitourinary_urine_appearance = fields.Selection([
        ('Clear', 'Clear'),
        ('Cloudy', 'Cloudy'),
        ('With Sediment', 'With Sediment'),
    ], default='Clear', readonly=True, states={'Start': [('readonly', False)]})
    genitourinary_urine_amount = fields.Selection([
        ('Adequate', 'Adequate'),
        ('Scanty', 'Scanty'),
        ('Large', 'Large'),
    ], default='Adequate', readonly=True, states={'Start': [('readonly', False)]})
    genitourinary_urination_none = fields.Boolean(default=True, readonly=True, states={'Start': [('readonly', False)]})
    genitourinary_urination_dysuria = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    genitourinary_urination_frequency = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    genitourinary_urination_urgency = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    genitourinary_urination_hesitancy = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    genitourinary_urination_incontinence = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    genitourinary_urination_inability_to_void = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    genitourinary_urination_nocturia = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    genitourinary_urination_retention = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    genitourinary_urination_suprapubic_pain = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    genitourinary_urination_loin_pain = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    genitourinary_urination_colicky_pain = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    genitourinary_urination_difficult_control = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    genitourinary_urination_other = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    genitourinary_urination_other_text = fields.Text(readonly=True, states={'Start': [('readonly', False)]})
    genitourinary_urination_assistance = fields.Selection([
        ('None', 'None'),
        ('Indwelling Catheter', 'Indwelling Catheter'),
        ('Condom Catheter', 'Condom Catheter'),
        ('Intermittent bladder Wash', 'Intermittent bladder Wash'),
        ('Urostomy', 'Urostomy'),
        ('Suprapubic Catheter', 'Suprapubic Catheter'),
    ], default='None', readonly=True, states={'Start': [('readonly', False)]})
    genitourinary_remarks = fields.Text(readonly=True, states={'Start': [('readonly', False)]})
    # Integumentary
    # last edit 8/2/2022
    integumentary_show = fields.Boolean()
    appearance_normal = fields.Boolean(string='Normal', default=True, readonly=True,
                                       states={'Start': [('readonly', False)]})
    appearance_dry = fields.Boolean(string='Dry', readonly=True, states={'Start': [('readonly', False)]})
    appearance_edema = fields.Boolean(string='Edema', readonly=True, states={'Start': [('readonly', False)]})
    appearance_flushed = fields.Boolean(string='Flushed', readonly=True, states={'Start': [('readonly', False)]})
    # last edit 8/2/2022
    appearance_pale = fields.Boolean(string='clay', readonly=True, states={'Start': [('readonly', False)]})
    appearance_rash = fields.Boolean(string='Rash', readonly=True, states={'Start': [('readonly', False)]})
    # last edit 8/2/2022
    appearance_jundiced = fields.Boolean(string='Jandiced', readonly=True, states={'Start': [('readonly', False)]})
    appearance_eczema = fields.Boolean(string='Eczema', readonly=True, states={'Start': [('readonly', False)]})
    appearance_hemayome = fields.Boolean(string='Hemayome', readonly=True, states={'Start': [('readonly', False)]})
    appearance_rusty = fields.Boolean(string='Rusty', readonly=True, states={'Start': [('readonly', False)]})
    appearance_cyanotic = fields.Boolean(string='Cyanotic', readonly=True, states={'Start': [('readonly', False)]})
    appearance_bruises = fields.Boolean(string='Bruises', readonly=True, states={'Start': [('readonly', False)]})
    appearance_abrasion = fields.Boolean(string='Abrasion', readonly=True, states={'Start': [('readonly', False)]})
    appearance_sores = fields.Boolean(string='Sores', readonly=True, states={'Start': [('readonly', False)]})
    integumentary_turgor = fields.Selection([
        ('Elastic', 'Elastic'),
        ('Normal for age', 'Normal for age'),
        ('Poor', 'Poor'),
    ], default='Elastic', readonly=True, states={'Start': [('readonly', False)]})
    integumentary_temperature = fields.Selection([
        ('Normal', 'Normal'),
        ('Cool', 'Cool'),
        ('Cold', 'Cold'),
        ('Warm', 'Warm'),
        ('Hot', 'Hot'),
    ], default='Normal', readonly=True, states={'Start': [('readonly', False)]})
    integumentary_remarks = fields.Text(readonly=True, states={'Start': [('readonly', False)]})

    # Infections
    infection_show = fields.Boolean()
    infection_nad = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    infection_content = fields.Char(readonly=True, states={'Start': [('readonly', False)]})

    # psychological
    psychological_show = fields.Boolean()
    psychological_nad = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    psychological_content = fields.Char(readonly=True, states={'Start': [('readonly', False)]})
    # reproductive
    reproductive_show = fields.Boolean()
    reproductive_nad = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    reproductive_content = fields.Char(readonly=True, states={'Start': [('readonly', False)]})
    # musculoskeletal
    musculoskeletal_show = fields.Boolean()
    musculoskeletal_left_upper_extremity = fields.Selection(musculoskeletal_extremity,
                                                            default='Active Against Gravity and Resistance',
                                                            readonly=True, states={'Start': [('readonly', False)]})
    musculoskeletal_right_upper_extremity = fields.Selection(musculoskeletal_extremity,
                                                             default='Active Against Gravity and Resistance',
                                                             readonly=True, states={'Start': [('readonly', False)]})
    musculoskeletal_left_lower_extremity = fields.Selection(musculoskeletal_extremity,
                                                            default='Active Against Gravity and Resistance',
                                                            readonly=True, states={'Start': [('readonly', False)]})
    musculoskeletal_right_lower_extremity = fields.Selection(musculoskeletal_extremity,
                                                             default='Active Against Gravity and Resistance',
                                                             readonly=True, states={'Start': [('readonly', False)]})
    musculoskeletal_gait = fields.Selection([
        ('Normal', 'Normal'),
        ('Asymmetrical', 'Asymmetrical'),
        ('Dragging', 'Dragging'),
        ('Impaired', 'Impaired'),
        ('Jerky', 'Jerky'),
        ('Shuffling', 'Shuffling'),
        ('Spastic', 'Spastic'),
        ('Steady', 'Steady'),
        ('Unsteady', 'Unsteady'),
        ('Wide Based', 'Wide Based'),
        ('Other', 'Other'),
    ], default='Normal', readonly=True, states={'Start': [('readonly', False)]})
    musculoskeletal_remarks = fields.Text(readonly=True, states={'Start': [('readonly', False)]})

    # sensory
    sensory_show = fields.Boolean()
    sensory_nad = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    sensory_content = fields.Char(readonly=True, states={'Start': [('readonly', False)]})

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
    # last edit 8/2/2022
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


class ShifaAppointmentMedicalHistory(models.Model):
    _inherit = "oeh.medical.appointment"

    # override medical history fields and make them active in start process
    hbv_infection_chk = fields.Boolean(string='HBV Infection')
    hbv_infection_remarks = fields.Text(string='HBV Infection Remarks')
    dm_chk = fields.Boolean(string='DM')
    dm_remarks = fields.Text(string='DM Remarks')
    ihd_chk = fields.Boolean(string='IHD')
    ihd_remarks = fields.Text(string='IHD Remarks')
    cold_chk = fields.Boolean(string='Cold')
    cold_remarks = fields.Text(string='Cold Remarks')
    hypertension_chk = fields.Boolean(string='Hypertension')
    hypertension_remarks = fields.Text(string='Hypertension Remarks')
    surgery_chk = fields.Boolean(string='Surgery')
    surgery_remarks = fields.Text(string='Surgery Remarks')
    others_past_illness = fields.Text(string='Others Past Illness')
    nsaids_chk = fields.Boolean(string='Nsaids')
    nsaids_remarks = fields.Text(string='Nsaids Remarks')
    aspirin_chk = fields.Boolean(string='Aspirin')
    aspirin_remarks = fields.Text(string='Aspirin Remarks')
    laxative_chk = fields.Boolean(string='Laxative')
    laxative_remarks = fields.Text(string='Laxative Remarks')
    others_drugs = fields.Text(string='Others Drugs')
    lmp_chk = fields.Boolean(string='LMP')
    lmp_dt = fields.Date(string='Date')
    menorrhagia_chk = fields.Boolean(string='Menorrhagia')
    menorrhagia_remarks = fields.Text(string='Menorrhagia Remarks')
    dysmenorrhoea_chk = fields.Boolean(string='Dysmenorrhoea')
    dysmenorrhoea_remarks = fields.Text(string='Dysmenorrhoea Remarks')
    bleeding_pv_chk = fields.Boolean(string='Bleeding PV')
    bleeding_pv_remarks = fields.Text(string='Bleeding PV Remarks')
    last_pap_smear_chk = fields.Boolean(string='Last PAP smear')
    last_pap_smear_remarks = fields.Text(string='Last PAP smear Remarks')

    # Signs Page fields:
    temperature = fields.Float(string='Temperature (celsius)')
    diastolic = fields.Integer(string='Diastolic Pressure')
    respiratory_rate = fields.Integer(string='Respiratory Rate',
                                      help="Respiratory rate expressed in breaths per minute")
    systolic = fields.Integer(string='Systolic Pressure')
    bpm = fields.Integer(string='Heart Rate', help="Heart rate expressed in beats per minute")
    osat = fields.Integer(string='Oxygen Saturation', help="Oxygen Saturation (arterial).")
    weight = fields.Float(string='Weight (kg)')
    abdominal_circ = fields.Float(string='Abdominal Circumference')
    bmi = fields.Float(string='Body Mass Index (BMI)')
    height = fields.Float(string='Height (cm)')
    head_circumference = fields.Float(string='Head Circumference', help="Head circumference")
    edema = fields.Boolean(string='Edema',
                           help="Please also encode the correspondent disease on the patient disease history. For example,  R60.1 in ICD-10 encoding")
    petechiae = fields.Boolean(string='Petechiae')
    hematoma = fields.Boolean(string='Hematomas')
    cyanosis = fields.Boolean(string='Cyanosis',
                              help="If not associated to a disease, please encode it on the patient disease history. For example,  R23.0 in ICD-10 encoding")
    acropachy = fields.Boolean(string='Acropachy', help="Check if the patient shows acropachy / clubbing")
    nystagmus = fields.Boolean(string='Nystagmus',
                               help="If not associated to a disease, please encode it on the patient disease history. For example,  H55 in ICD-10 encoding")
    miosis = fields.Boolean(string='Miosis',
                            help="If not associated to a disease, please encode it on the patient disease history. For example,  H57.0 in ICD-10 encoding")
    mydriasis = fields.Boolean(string='Mydriasis',
                               help="If not associated to a disease, please encode it on the patient disease history. For example,  H57.0 in ICD-10 encoding")
    cough = fields.Boolean(string='Cough',
                           help="If not associated to a disease, please encode it on the patient disease history.")
    palpebral_ptosis = fields.Boolean(string='Palpebral Ptosis',
                                      help="If not associated to a disease, please encode it on the patient disease history")
    arritmia = fields.Boolean(string='Arritmias',
                              help="If not associated to a disease, please encode it on the patient disease history")
    heart_murmurs = fields.Boolean(string='Heart Murmurs')
    heart_extra_sounds = fields.Boolean(string='Heart Extra Sounds',
                                        help="If not associated to a disease, please encode it on the patient disease history")
    jugular_engorgement = fields.Boolean(string='Tremor',
                                         help="If not associated to a disease, please encode it on the patient disease history")
    ascites = fields.Boolean(string='Ascites',
                             help="If not associated to a disease, please encode it on the patient disease history")
    lung_adventitious_sounds = fields.Boolean(string='Lung Adventitious sounds', help="Crackles, wheezes, ronchus..")
    bronchophony = fields.Boolean(string='Bronchophony')
    increased_fremitus = fields.Boolean(string='Increased Fremitus')
    jaundice = fields.Boolean(string='Jaundice',
                              help="If not associated to a disease, please encode it on the patient disease history")
    jaundice = fields.Boolean(string='Jaundice',
                              help="If not associated to a disease, please encode it on the patient disease history")
    lynphadenitis = fields.Boolean(string='Linphadenitis',
                                   help="If not associated to a disease, please encode it on the patient disease history")
    breast_lump = fields.Boolean(string='Breast Lumps')
    nipple_inversion = fields.Boolean(string='Nipple Inversion')
    peau_dorange = fields.Boolean(string='Peau d orange',
                                  help="Check if the patient has prominent pores in the skin of the breast")
    masses = fields.Boolean(string='Masses', help="Check when there are findings of masses / tumors / lumps")
    hypotonia = fields.Boolean(string='Hypotonia',
                               help="Please also encode the correspondent disease on the patient disease history.")
    hypertonia = fields.Boolean(string='Hypertonia',
                                help="Please also encode the correspondent disease on the patient disease history.")
    pressure_ulcers = fields.Boolean(string='Pressure Ulcers',
                                     help="Check when Decubitus / Pressure ulcers are present")
    goiter = fields.Boolean(string='Goiter')
    alopecia = fields.Boolean(string='Alopecia', help="Check when alopecia - including androgenic - is present")
    xerosis = fields.Boolean(string='Xerosis')
    erithema = fields.Boolean(string='Erithema',
                              help="Please also encode the correspondent disease on the patient disease history.")
    malnutrition = fields.Boolean(string='Malnutrition',
                                  help="Check this box if the patient show signs of malnutrition. If not associated to a disease, please encode the correspondent disease on the patient disease history. For example, Moderate protein-energy malnutrition, E44.0 in ICD-10 encoding")
    dehydration = fields.Boolean(string='Dehydration',
                                 help="Check this box if the patient show signs of dehydration. If not associated to a disease, please encode the correspondent disease on the patient disease history. For example, Volume Depletion, E86 in ICD-10 encoding")
    glycemia = fields.Float(string='Glycemia', help="Last blood glucose level. It can be approximative.")
    hba1c = fields.Float(string='Glycated Hemoglobin', help="Last Glycated Hb level. It can be approximative.")
    cholesterol_total = fields.Integer(string='Last Cholesterol',
                                       help="Last cholesterol reading. It can be approximative")
    hdl = fields.Integer(string='Last HDL', help="Last HDL Cholesterol reading. It can be approximative")
    ldl = fields.Integer(string='Last LDL', help="Last LDL Cholesterol reading. It can be approximative")
    tag = fields.Integer(string='Last TAGs', help="Triacylglycerols (triglicerides) level. It can be approximative")
    decreased_fremitus = fields.Boolean(string='Decreased Fremitus')
    breast_asymmetry = fields.Boolean(string='Breast Asymmetry')
    nipple_discharge = fields.Boolean(string='Nipple Discharge')
    gynecomastia = fields.Boolean(string='Gynecomastia')


class ShifaAppointmentSigns(models.Model):
    _inherit = "oeh.medical.appointment"

    MOOD = [
        ('Normal', 'Normal'),
        ('Sad', 'Sad'),
        ('Fear', 'Fear'),
        ('Rage', 'Rage'),
        ('Happy', 'Happy'),
        ('Disgust', 'Disgust'),
        ('Euphoria', 'Euphoria'),
        ('Flat', 'Flat'),
    ]

    # signs - rest fields
    masses = fields.Boolean(string='Masses', help="Check when there are findings of masses / tumors / lumps")
    hypotonia = fields.Boolean(string='Hypotonia',
                               help="Please also encode the correspondent disease on the patient disease history.")
    hypertonia = fields.Boolean(string='Hypertonia',
                                help="Please also encode the correspondent disease on the patient disease history.")
    pressure_ulcers = fields.Boolean(string='Pressure Ulcers',
                                     help="Check when Decubitus / Pressure ulcers are present")
    goiter = fields.Boolean(string='Goiter')
    alopecia = fields.Boolean(string='Alopecia', help="Check when alopecia - including androgenic - is present")
    xerosis = fields.Boolean(string='Xerosis')
    erithema = fields.Boolean(string='Erithema',
                              help="Please also encode the correspondent disease on the patient disease history.")
    loc = fields.Integer(string='Level of Consciousness',
                         help="Level of Consciousness - on Glasgow Coma Scale :  1=coma - 15=normal")
    loc_eyes = fields.Integer(string='Level of Consciousness - Eyes',
                              help="Eyes Response - Glasgow Coma Scale - 1 to 4", default=lambda *a: 4)
    loc_verbal = fields.Integer(string='Level of Consciousness - Verbal',
                                help="Verbal Response - Glasgow Coma Scale - 1 to 5", default=lambda *a: 5)
    loc_motor = fields.Integer(string='Level of Consciousness - Motor',
                               help="Motor Response - Glasgow Coma Scale - 1 to 6", default=lambda *a: 6)
    violent = fields.Boolean(string='Violent Behaviour',
                             help="Check this box if the patient is agressive or violent at the moment")
    mood = fields.Selection(MOOD, string='Mood', index=True)
    indication = fields.Many2one('oeh.medical.pathology', string='Indication',
                                 help="Choose a disease for this medicament from the disease list. It can be an existing disease of the patient or a prophylactic.")
    orientation = fields.Boolean(string='Orientation',
                                 help="Check this box if the patient is disoriented in time and/or space")
    memory = fields.Boolean(string='Memory',
                            help="Check this box if the patient has problems in short or long term memory")
    knowledge_current_events = fields.Boolean(string='Knowledge of Current Events',
                                              help="Check this box if the patient can not respond to public notorious events")
    judgment = fields.Boolean(string='Jugdment',
                              help="Check this box if the patient can not interpret basic scenario solutions")
    abstraction = fields.Boolean(string='Abstraction',
                                 help="Check this box if the patient presents abnormalities in abstract reasoning")
    vocabulary = fields.Boolean(string='Vocabulary',
                                help="Check this box if the patient lacks basic intelectual capacity, when she/he can not describe elementary objects")
    calculation_ability = fields.Boolean(string='Calculation Ability',
                                         help="Check this box if the patient can not do simple arithmetic problems")
    object_recognition = fields.Boolean(string='Object Recognition',
                                        help="Check this box if the patient suffers from any sort of gnosia disorders, such as agnosia, prosopagnosia ...")
    praxis = fields.Boolean(string='Praxis', help="Check this box if the patient is unable to make voluntary movements")
    info_diagnosis = fields.Text(string='Presumptive Diagnosis')
    directions = fields.Text(string='Plan')
    notes = fields.Text(string='Notes')


class ShifaLabRequestTestTeleAppointment(models.Model):
    _inherit = 'sm.shifa.lab.request.line'

    appointment = fields.Many2one("oeh.medical.appointment", string='tele Appointment')


class ShifaImagingRequestTestTeleAppointment(models.Model):
    _inherit = 'sm.shifa.imaging.request.line'

    appointment = fields.Many2one("oeh.medical.appointment", string='tele Appointment')

