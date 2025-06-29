import datetime
from datetime import timedelta, datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class ShifaPhysiotherapy(models.Model):
    _name = 'sm.shifa.physiotherapy.appointment'
    _description = 'Physiotherapy Appointment Management'
    _rec_name = 'display_name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    TIME_SLOT = [('morning', 'Morning'), ('afternoon', 'Afternoon'), ('evening', 'Evening')]

    GENDER = [('Male', 'Male'), ('Female', 'Female')]

    APPOINTMENT_STATUS = [
        ('scheduled', 'Scheduled'),
        ('head_physiotherapist', 'Head Physiotherapist'),
        ('operation_manager', 'Operation Manager'),
        ('team', 'Team'),
        ('in_progress', 'In progress'),
        ('visit_done', 'Visit Done'),
        ('incomplete', 'Incomplete'),
        ('canceled', 'Canceled'),
        ('requestCancellation', 'Request Cancellation'),
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
    pay_made_throu = [
        ('pending', 'Free Service'),
        ('mobile', 'Mobile App'),
        ('call_center', 'Call Center'),
        ('on_spot', 'On spot'),
        ('aggregator', 'Aggregator'),
        ('package', 'Package'),
        ('aggregator_package', 'Aggregator Package'),
        ('deferred', 'Deferred'),
    ]
    TYPE_SERVICE = [
        ('main', 'Main'),
        ('followup', 'Follow-up'),
    ]

    def get_schedule_in_time(self):
        model_name = 'oeh.medical.physician.line'
        for rec in self:
            model = self.env[model_name].sudo().search(
                [('physician_id', '=', int(rec.physiotherapist)), ('date', '=', rec.appointment_date_only)],
                limit=1)
            lst = []
            if model:
                lst.append(model.name)

    # Automatically detect logged in physician
    def _get_physician(self):
        """Return default physician value"""
        therapist_obj = self.env['oeh.medical.physician']
        domain = [('oeh_user_id', '=', self.env.uid)]
        user_ids = therapist_obj.search(domain)
        if user_ids:
            return user_ids.id or False
        else:
            return False

    @api.depends('appointment_date_only', 'appointment_time')
    def _get_appointment_date(self):
        for apm in self:
            apm.appointment_date = datetime.strptime(apm.appointment_date_only.strftime("%Y-%m-%d %H:%M:%S"),
                                                     "%Y-%m-%d %H:%M:%S") + timedelta(hours=apm.appointment_time - 3)
        return True

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

    def _join_name_phy(self):
        for rec in self:
            if rec.patient:
                rec.display_name = rec.patient.name
            elif rec.name:
                rec.display_name = rec.name
            elif rec.name and rec.patient:
                rec.display_name = rec.patient.name + ' ' + rec.name

    def _phy_duration(self):
        phy_duration = self.env['ir.config_parameter'].sudo().get_param('smartmind_shifa.appointment_duration_phy')
        return float(phy_duration)

    # service dynamic domain
    @api.onchange('service_type_choice')
    def _get_service_list(self):
        if self.service_type_choice == "main":
            return {'domain': {'service': [('service_type', '=', 'PHY')]}}
        elif self.service_type_choice == "followup":
            return {'domain': {'service': [('service_type', '=', 'FUPP')]}}
        else:
            # raise ValidationError('Choose visit type First')
            return {'domain': {'service': [('service_type', '=', False)]}}

    name = fields.Char(string='Phys #', size=128, readonly=True, default=lambda *a: '/')
    display_name = fields.Char(compute=_join_name_phy)
    state = fields.Selection(APPOINTMENT_STATUS, string='State', tracking=True,
                             default='scheduled')  # , readonly=False, default=lambda *a: 'scheduled'
    patient = fields.Many2one('oeh.medical.patient', string='Patient', required=True, readonly=True, tracking=True,
                              states={'scheduled': [('readonly', False)]})

    physiotherapist = fields.Many2one('oeh.medical.physician', string='Physiotherapist', tracking=True,
                                      help="Current primary care / family doctor",
                                      domain=[('role_type', 'in', ['HP', 'HHCP']), ('active', '=', True)],
                                      readonly=True, states={'scheduled': [('readonly', False)],
                                                             'operation_manager': [('readonly', False)],
                                                             'team': [('readonly', False)],
                                                             'head_physiotherapist': [('readonly', False)]})
    operation_comment = fields.Char(string='Operation Manager', tracking=True)

    ksa_nationality = fields.Selection(NATIONALITY_STATE, related='patient.ksa_nationality', readonly=True,
                                       states={'scheduled': [('readonly', False)]})

    gender = fields.Selection(GENDER, string='Type', required=True, readonly=True, tracking=True,
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
                      states={'head_physiotherapist': [('readonly', True)],
                              'in_progress': [('readonly', True)], 'team': [('readonly', True)],
                              'operation_manager': [('readonly', True)], 'visit_done': [('readonly', True)],
                              'canceled': [('readonly', True)]}, related='patient.ssn')
    mobile = fields.Char(string='Mobile', readonly=False,
                         states={'head_physiotherapist': [('readonly', True)],
                                 'in_progress': [('readonly', True)], 'team': [('readonly', True)],
                                 'operation_manager': [('readonly', True)], 'visit_done': [('readonly', True)],
                                 'canceled': [('readonly', True)]}, related='patient.mobile')
    age = fields.Char(string='Age', readonly=False,
                      states={'head_physiotherapist': [('readonly', True)],
                              'in_progress': [('readonly', True)], 'team': [('readonly', True)],
                              'operation_manager': [('readonly', True)], 'visit_done': [('readonly', True)],
                              'canceled': [('readonly', True)]}, related='patient.age')

    house_location = fields.Char(string='House Location', readonly=False,
                                 states={'head_physiotherapist': [('readonly', True)],
                                         'in_progress': [('readonly', True)], 'team': [('readonly', True)],
                                         'operation_manager': [('readonly', True)], 'visit_done': [('readonly', True)],
                                         'canceled': [('readonly', True)]}, related='patient.house_location')
    house_number = fields.Char(string='House Number', readonly=False,
                               states={'head_physiotherapist': [('readonly', True)],
                                       'in_progress': [('readonly', True)], 'team': [('readonly', True)],
                                       'operation_manager': [('readonly', True)], 'visit_done': [('readonly', False)],
                                       'canceled': [('readonly', True)]}, related='patient.house_number')

    nationality = fields.Char(string='Nationality', readonly=False,
                              states={'head_physiotherapist': [('readonly', True)],
                                      'in_progress': [('readonly', True)], 'team': [('readonly', True)],
                                      'operation_manager': [('readonly', True)], 'visit_done': [('readonly', True)],
                                      'canceled': [('readonly', True)]}, related='patient.nationality')
    patient_weight = fields.Float(string='Weight(kg)', readonly=False,
                                  states={'head_physiotherapist': [('readonly', True)],
                                          'in_progress': [('readonly', True)], 'team': [('readonly', True)],
                                          'operation_manager': [('readonly', True)], 'visit_done': [('readonly', True)],
                                          'canceled': [('readonly', True)]}, related='patient.weight')
    patient_comment = fields.Text(string='Patient Comment')

    service = fields.Many2one('sm.shifa.service', string='Service Name', required=True, tracking=True,
                              domain=[('show', '=', True), ('service_type', 'in', ['PHY', 'FUPP'])],
                              readonly=True,
                              states={'scheduled': [('readonly', False)], 'operation_manager': [('readonly', False)]})
    # we need this filed for visible page related to service name
    service_name = fields.Char(string='Service Name', related='service.abbreviation', readonly=True, store=False)
    service_price = fields.Float(string='Service Price', readonly=True)

    service_code = fields.Char(string='Service Code', related='service.type_code', readonly=True, store=False)
    service_type_choice = fields.Selection(TYPE_SERVICE, string="Service Type", readonly=True,
                                           states={'scheduled': [('readonly', False)],
                                                   'operation_manager': [('readonly', False)]}, required=True)
    active = fields.Boolean('Active', default=True)

    period = fields.Selection(TIME_SLOT, string='Period', required=True, readonly=True, tracking=True,
                              states={'scheduled': [('readonly', False)], 'team': [('readonly', False)],
                                      'operation_manager': [('readonly', False)]})

    payment_type = fields.Char(readonly=True, states={'in_progress': [('readonly', False)]})
    deduction_amount = fields.Float(string="Ded. Amount", readonly=True,
                                    states={'in_progress': [('readonly', False)]})
    pro_pending = fields.Boolean(string="Pro. Free Service")
    payment_made_through = fields.Selection(pay_made_throu, string="Pay. Made Thru.", required=True, readonly=False,
                                            states={'scheduled': [('readonly', False)]}, tracking=True)
    payment_reference = fields.Char(string='Payment Ref. #', readonly=True)
    location = fields.Char(string='Mobile location', readonly=True, states={'scheduled': [('readonly', False)]})
    attached_file = fields.Binary(string='Attached File 1', readonly=True, states={'scheduled': [('readonly', False)]})
    attached_file_2 = fields.Binary(string='Attached File 2', readonly=True,
                                    states={'scheduled': [('readonly', False)]})

    # attached_file_3 = fields.Binary(string='Attached File 3', readonly=True, states={'scheduled': [('readonly', False)]})
    checkup_comment = fields.Char(string="Call Center", tracking=True)
    visit_comment = fields.Char(string='Team Leader', tracking=True)
    apt_invoice_count = fields.Integer(string='Invoice Count', compute='_get_apt_invoiced', readonly=True)
    comments = fields.Text(string='Comments')  # , readonly=False, states={'Scheduled': [('readonly', False)]}
    # notebook pages fields
    is_service_done = fields.Boolean(string="Is Service Done")
    service_note = fields.Text(string="Remarks")
    service_image = fields.Binary(string="Picture")
    start_process_date = fields.Datetime(string='Starting Time HV', readonly=True,
                                         states={'visit_done': [('readonly', False)]})
    complete_process_date = fields.Datetime(string='Ending Time HV', readonly=True,
                                            states={'visit_done': [('readonly', False)]})
    appointment_duration = fields.Char(string="Appointment Duration", compute='_compute_hhc_duration', default="0")
    insurance = fields.Many2one('sm.shifa.insurance', string='Insurance', help="Insurance Company Name",
                                domain=[('state', '=', 'Active')],
                                readonly=True, states={'scheduled': [('readonly', False)]})

    appointment_day = fields.Selection(PHY_DAY, string='Day', required=False)
    day = fields.Char(string='Day', compute="_get_day")
    available_appointment = fields.Integer(string='Available Appts. #', compute='_count_availability',
                                           readonly=True)
    time_slot = fields.Selection(PHY_DAY, string='Time Solt')  # selection='_list_time_slot' , required=True
    meeting_id = fields.Many2one('calendar.event', string='Calendar', copy=False, readonly=True)
    duration = fields.Float(string='Duration', default=_phy_duration, readonly=True)
    payment_method_name = fields.Char(string="Payment Method Name", readonly=True)
    branch = fields.Selection([
        ('riyadh', 'Riyadh'),
        ('dammam', 'Dammam'),
        ('jeddah', 'Jeddah'),
    ], string="Branch", readonly=True, states={'scheduled': [('readonly', False)]})
    # Indicates whether an appointment has been cancelled.
    # This field is typically updated when a user cancels an appointment via the mobile app or other channels.
    cancellation_requested = fields.Boolean(string='Cancellation Requested', default=lambda *a: 0)
    pro_deferred_pay = fields.Boolean(string="Pro. Deferred Pay")

    @api.onchange('time_slot')
    def _list_time_slot(self):
        model_name = 'oeh.medical.physician.line'
        for rec in self:
            model = self.env[model_name].sudo().search([('date', '=', rec.appointment_date_only)],
                                                       limit=1)  # ('physician_id', '=', int(rec.hhc_physiotherapist)),
            lst = []
            if model:
                lst.append(model.name)
                _logger.error(model.name)

    @api.depends('start_process_date', 'complete_process_date')
    def _compute_hhc_duration(self):
        for r in self:
            if r.start_process_date and r.complete_process_date:
                duration_time = str(r.complete_process_date - r.start_process_date)
                r.appointment_duration = duration_time.split('.')[0]
            else:
                r.appointment_duration = "0"

    @api.onchange('appointment_date', 'period', 'gender')
    def _count_availability(self):
        team_obj = self.env['sm.shifa.team.period.physiotherapy']
        domain = [('date', '=', self.appointment_date_only), ('period', '=', self.period),
                  ('gender', '=', self.gender)]
        team = team_obj.search(domain, limit=1)
        self.available_appointment = team.available

    @api.depends('appointment_date_only')
    def _get_day(self):
        for rec in self:
            if rec.appointment_date_only:
                a = datetime.strptime(str(rec.appointment_date_only), "%Y-%m-%d")
                rec.day = str(a.strftime("%A"))
                rec.appointment_day = rec.day

    @api.model
    def create(self, vals):
        # this is for test key error issue s
        team_obj = self.env['sm.shifa.team.period.physiotherapy']
        domain = [('date', '=', vals['appointment_date_only']), ('period', '=', vals['period']),
                  ('gender', '=', vals['gender'])]
        team = team_obj.search(domain, limit=1)
        # print(team.available)
        # if team.available:
        sequence = self.env['ir.sequence'].next_by_code('sm.shifa.physiotherapy.appointment')
        vals['name'] = sequence
        return super(ShifaPhysiotherapy, self).create(vals)
        # else:
        #     raise ValidationError(
        #         '%s period is full or not determined yet, please book appointment in another period.' % vals['period'])

    def _reset_token_number_sequences(self):
        # just use write directly on the result this will execute one update query
        sequences = self.env['ir.sequence'].search([('name', '=', 'Physiotherapy Appointment')])
        sequences.write({'number_next_actual': 1})

    def _get_default_journal(self):
        journal = self.env['account.journal'].search([('type', '=', 'sale')], limit=1)
        return journal

    def set_to_head_physiotherapist(self):
        if self.payment_made_through in ['package', 'aggregator_package', 'mobile']:
            raise UserError("Please change the payment made thru to do this action!")
        msg = "HHC appointment [ %s ] is at Team state" % (self.name)
        msg_vals = {"message": msg, "title": "Team State", "sticky": True}
        admin_group_ids = [self.env.ref('oehealth.group_oeh_medical_manager').id,
                           self.env.ref('smartmind_shifa.group_oeh_medical_operation_manager').id,
                           self.env.ref('smartmind_shifa.group_oeh_medical_head_physiotherapist').id,
                           ]
        for group_id in admin_group_ids:
            group_users = self.env['res.users'].search([('groups_id', 'in', group_id)])
            for user in group_users:
                user.notify_success(**msg_vals)
        return self.write({'state': 'head_physiotherapist'})

    def set_to_start(self):
        return self.write({'state': 'in_progress', 'start_process_date': datetime.now()})

    def set_to_end_hiv(self):
        self.write({'state': 'visit_done', 'complete_process_date': datetime.now()})

    def set_to_incomplete(self):
        return self.write({'state': 'incomplete'})

    def set_to_canceled(self):
        return self.write({'state': 'canceled'})

    def set_to_req_cancellation(self):
        return self.write({'state': 'canceled'})

    def set_to_team_leader(self):
        return self.write({'state': 'team'})

    def set_to_operation_manager(self):
        msg = "Physiotherapy appointment [ %s ] is at Operation Manager state" % (self.name)
        msg_vals = {"message": msg, "title": "Physiotherapy Appointment", "sticky": True}
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
        self.calendar_appointment_event()
        msg = "Physiotherapy appointment [ %s ] is at Team state" % (self.name)
        msg_vals = {"message": msg, "title": "Team State", "sticky": True}
        admin_group_ids = [self.env.ref('oehealth.group_oeh_medical_manager').id,
                           self.env.ref('smartmind_shifa.group_oeh_medical_operation_manager').id,
                           self.env.ref('smartmind_shifa.group_oeh_medical_head_doctor').id,
                           self.env.ref('oehealth.group_oeh_medical_physician').id,
                           self.env.ref('smartmind_shifa.group_oeh_medical_head_physiotherapist').id,
                           self.env.ref('smartmind_shifa.group_oeh_medical_hhc_physiotherapist').id
                           ]
        for group_id in admin_group_ids:
            group_users = self.env['res.users'].search([('groups_id', 'in', group_id)])
            for user in group_users:
                user.notify_success(**msg_vals)
        self.submit_timeslot()
        return self.write({'state': 'team'})

    def set_back_to_team_leader(self):
        return self.write({'state': 'head_physiotherapist'})

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

    def calendar_appointment_event(self):
        for rec in self:
            date_time = datetime.fromordinal(rec.appointment_date_only.toordinal())
            time = rec.appointment_time
            start_appointment = date_time + timedelta(seconds=time * 3600)
            start_appointment = start_appointment - timedelta(hours=3)
            meeting_values = {
                'name': rec.display_name,
                'duration': rec.duration,
                'description': "Physiotherapy appointment",
                'user_id': rec.physiotherapist.oeh_user_id.id,
                'start': start_appointment,
                'stop': start_appointment + timedelta(hours=1),
                'allday': False,
                'recurrency': False,
                'privacy': 'confidential',
                'event_tz': rec.physiotherapist.oeh_user_id.tz,
                'activity_ids': [(5, 0, 0)],
            }

            # Add the partner_id (if exist) as an attendee
            if rec.physiotherapist.oeh_user_id and rec.physiotherapist.oeh_user_id.partner_id:
                meeting_values['partner_ids'] = [
                    (4, rec.physiotherapist.oeh_user_id.partner_id.id)]

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
        restricted_values = ['mobile', 'package', 'aggregator_package']
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
            'default_phy_appointment_id': self.id,
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


class ShifaAppointmentInSaleOrder(models.Model):
    _inherit = 'sale.order'

    physiotherapy = fields.Many2one('sm.shifa.physiotherapy.appointment', string="Physiotherapy Appointment #")


class SmartMindShifaDoctorScheduleTimeSlot(models.Model):
    _inherit = "sm.shifa.physiotherapy.appointment"

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
    appointment_time = fields.Float(string='Time (HH:MM)', readonly=True, default=1.0)
    timeslot = fields.Many2one('sm.shifa.physician.schedule.timeslot', string='Timeslot', copy=False,
                               domain="[('physician_id', '=', physiotherapist), ('date', '=', appointment_date_only), ('is_available', '=', True)]",
                               readonly=True, states={'scheduled': [('readonly', False)], 'operation_manager': [
            ('readonly', False)], 'team': [('readonly', False)],
                                                      'head_physiotherapist': [
                                                          ('readonly', False)]})

    appointment_date = fields.Datetime(compute=_get_appointment_date, string='Apt. DateTime', readonly=False,
                                       store=True)
    changed_timeslot = fields.Boolean(default=False)

    # ---------------------------------------------------------------------------------------------------------
    # change timeslot for nurse doctor and physiotherapy
    def change_timeslot(self):
        self.changed_timeslot = True
        if self.timeslot:
            self.timeslot_done(self.physiotherapist.id, self.appointment_date_only, self.timeslot.available_time, True)

    # submit timeslot for physiotherapist doctor and physiotherapy
    def submit_timeslot(self):
        self.changed_timeslot = False
        if self.timeslot:
            self.timeslot.is_available = False

    @api.onchange('timeslot')
    def onchange_timeslot(self):
        if self.timeslot:
            hm = self.timeslot.available_time.split(':')
            sch_time = int(hm[0]) + int(hm[1]) / 60
            # print('time: ', str(sch_time))
            self.appointment_time = sch_time
            self.changed_timeslot = False

    def timeslot_is_available(self, tm_id, action):
        timeslot = self.env['sm.shifa.physician.schedule.timeslot'].sudo().browse(int(tm_id))
        timeslot.sudo().write({
            'is_available': action,
        })

    def active_timeslot(self):
        for rec in self.filtered(
                lambda rec: rec.state in ['scheduled', 'head_physiotherapist', 'operation_manager', 'team']):
            if rec.timeslot:
                self.timeslot_is_available(rec.timeslot, True)

    def change_appointment_timeslot(self):
        if self.timeslot:
            # self.active_timeslot()
            self.timeslot_done(self.physiotherapist.id, self.appointment_date_only, self.timeslot.available_time, True)
            self.changed_timeslot = True

    @api.model
    def create(self, vals):
        doc_time = vals.get('timeslot')
        if doc_time:
            self.timeslot_is_available(vals['timeslot'], False)
        res = super(SmartMindShifaDoctorScheduleTimeSlot, self).create(vals)
        msg = "New Physiotherapy appointment called [ %s ] has been created" % (res.name)
        msg_vals = {"message": msg, "title": "New Physiotherapy appointment", "sticky": True}
        admin_group_ids = [self.env.ref('oehealth.group_oeh_medical_manager').id,
                           self.env.ref('smartmind_shifa.group_oeh_medical_operation_manager').id,
                           self.env.ref('smartmind_shifa.group_oeh_medical_call_center').id]
        for group_id in admin_group_ids:
            group_users = self.env['res.users'].search([('groups_id', 'in', group_id)])
            for user in group_users:
                user.notify_success(**msg_vals)
        return res

    def timeslot_done(self, person_id, date, available_time, action):
        timeslot = self.env['sm.shifa.physician.schedule.timeslot'].sudo().search(
            [('physician_id', '=', person_id), ('date', '=', date), ('available_time', '=', available_time)], limit=1)
        if timeslot:
            timeslot.sudo().write({
                'is_available': action,
            })

    def write(self, vals):
        for rec in self:
            if rec.timeslot:
                self.timeslot_is_available(rec.timeslot, False)
            if rec.changed_timeslot:
                self.timeslot_done(self.physiotherapist.id, self.appointment_date_only, self.timeslot.available_time,
                                   True)
                self.active_timeslot()

        return super(SmartMindShifaDoctorScheduleTimeSlot, self).write(vals)

    def unlink(self):
        self.active_timeslot()
        return super(SmartMindShifaDoctorScheduleTimeSlot, self).unlink()

    def set_to_canceled(self):
        self.active_timeslot()
        return self.write({'state': 'canceled'})


class ShifaPhysiotherapyInAccountMove(models.Model):
    _inherit = 'account.move'

    physiotherapy = fields.Many2one('sm.shifa.physiotherapy.appointment', string="Physiotherapy Appointment #")
