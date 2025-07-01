import datetime
from datetime import timedelta, datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from math import modf


class ShifaPCRAppointment(models.Model):
    _name = 'sm.shifa.pcr.appointment'
    _description = 'Home Health Care Appointment Management'
    _rec_name = 'display_name'

    HOURS = [
        ('8:00 AM - 9:00 AM', '8:00 AM - 9:00 AM'),
        ('9:00 AM - 10:00 AM', '9:00 AM - 10:00 AM'),
        ('10:00 AM - 11:00 AM', '10:00 AM - 11:00 AM'),
        ('11:00 AM - 12:00 PM', '11:00 AM - 12:00 PM'),
        ('2:00 PM - 3:00 PM', '2:00 PM - 3:00 PM'),
        ('3:00 PM - 4:00 PM', '3:00 PM - 4:00 PM'),
        ('4:00 PM - 5:00 PM', '4:00 PM - 5:00 PM'),
        ('5:00 PM - 6:00 PM', '5:00 PM - 6:00 PM'),
        ('6:00 PM - 7:00 PM', '6:00 PM - 7:00 PM'),
        ('7:00 PM - 8:00 PM', '7:00 PM - 8:00 PM'),
    ]

    APPOINTMENT_STATUS = [
        ('scheduled', 'Scheduled'),
        ('operation_manager', 'Operation Manager'),
        ('team', 'Team'),
        ('in_progress', 'In progress'),
        ('visit_done', 'Visit Done'),
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
    pay_made_throu = [
        ('mobile', 'Mobile App'),
        ('call_center', 'Call Center'),
        ('on_spot', 'On spot'),
    ]

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
            apm.appointment_date_time = end_date
        return True

    def _compute_tax(self, price, ksa):
        percent = (price * 0.15)
        if ksa == 'NON':
            return price + percent
        else:
            return price

    def _join_name_pcr(self):
        for rec in self:
            if rec.patient:
                rec.display_name = rec.patient.name + ' ' + rec.name

    def _pcr_duration(self):
        pcr_duration = self.env['ir.config_parameter'].sudo().get_param('smartmind_shifa.appointment_duration_pcr')
        return float(pcr_duration)

    name = fields.Char(string='PCR #', size=64, readonly=False, default=lambda *a: '/')
    display_name = fields.Char(compute=_join_name_pcr)
    state = fields.Selection(APPOINTMENT_STATUS, string='State',
                             default='scheduled')  # , readonly=False, default=lambda *a: 'scheduled'
    patient = fields.Many2one('oeh.medical.patient', string='Patient', required=True, readonly=False,
                              states={'scheduled': [('readonly', False)]})

    ksa_nationality = fields.Selection(NATIONALITY_STATE, related='patient.ksa_nationality', readonly=False,
                                       states={'scheduled': [('readonly', False)]})

    # patient details
    dob = fields.Date(string='Date of Birth', related='patient.dob', readonly=False,
                      states={'scheduled': [('readonly', False)]})
    marital_status = fields.Selection(string='Marital Status', related='patient.marital_status')
    sex = fields.Selection(string='Sex', related='patient.sex', readonly=False,
                           states={'scheduled': [('readonly', False)]})
    blood_type = fields.Selection(string='Blood Type', related='patient.blood_type')
    rh = fields.Selection(string='Rh', related='patient.rh')

    ssn = fields.Char(string='ID Number', readonly=False,
                      states={'in_progress': [('readonly', True)], 'operation_manager': [('readonly', True)],
                              'team': [('readonly', True)],
                              'visit_done': [('readonly', False)]}, related='patient.ssn')
    mobile = fields.Char(string='Mobile', readonly=False,
                         states={'in_progress': [('readonly', True)], 'operation_manager': [('readonly', True)],
                                 'team': [('readonly', True)],
                                 'visit_done': [('readonly', False)]}, related='patient.mobile')
    age = fields.Char(string='Age', readonly=False,
                      states={'in_progress': [('readonly', True)], 'operation_manager': [('readonly', True)],
                              'team': [('readonly', True)],
                              'visit_done': [('readonly', False)]}, related='patient.age')
    # is_ksa = fields.Selection(string='Nationality', related='patient.ksa_nationality')
    nationality = fields.Char(string='Nationality', readonly=False,
                              states={'in_progress': [('readonly', True)], 'operation_manager': [('readonly', True)],
                                      'team': [('readonly', True)],
                                      'visit_done': [('readonly', False)]}, related='patient.nationality')
    patient_weight = fields.Float(string='Weight(kg)', readonly=False,
                                  states={'in_progress': [('readonly', True)],
                                          'operation_manager': [('readonly', True)],
                                          'team': [('readonly', True)],
                                          'visit_done': [('readonly', False)]}, related='patient.weight')
    patient_comment = fields.Text(string='Patient Comment')
    service = fields.Many2one('sm.shifa.service', string='Service Name', required=True,
                              domain=[('show', '=', True), ('service_type', '=', 'PCR')],
                              readonly=False, states={'scheduled': [('readonly', False)]})
    # we need this filed for visible page related to service name
    service_name = fields.Char(string='Service Name', related='service.abbreviation', readonly=False, store=False)
    service_price = fields.Float(string='Service Price', readonly=False)
    payment_type = fields.Char(readonly=False, states={'team': [('readonly', False)]})
    deduction_amount = fields.Float(string="Deduction Amount")
    payment_made_through = fields.Selection(pay_made_throu, string="Payment Made through", default="mobile")
    payment_reference = fields.Char(string='Payment Reference #', readonly=False,
                                    states={'team': [('readonly', False)]})
    location = fields.Char(string='Mobile location', readonly=False, states={'scheduled': [('readonly', False)]})
    attached_file = fields.Binary(string='Attached File 1', readonly=False, states={'scheduled': [('readonly', False)]})
    attached_file_2 = fields.Binary(string='Attached File 2', readonly=False,
                                    states={'scheduled': [('readonly', False)]})
    # attached_file_3 = fields.Binary(string='Attached File 3', readonly=False, states={'scheduled': [('readonly', False)]})
    move_id = fields.Many2one('account.move', string='Invoice #')
    checkup_comment = fields.Text(readonly=False, states={'scheduled': [('readonly', False)]})
    active = fields.Boolean('Active', default=True)

    head_doctor = fields.Many2one('oeh.medical.physician', string='Head Doctor',
                                  domain=[('role_type', '=', 'HD'), ('active', '=', True)],
                                  readonly=False, states={'operation_manager': [('readonly', False)]},
                                  default=_get_physician)

    treatment_comment = fields.Text(string='Comments', readonly=False,
                                    states={'operation_manager': [('readonly', False)]})

    prescribed_medicine = fields.Boolean(string='Prescribed Medicine', readonly=False,
                                         states={'operation_manager': [('readonly', False)]})
    visit_comment = fields.Text(string='Comments', readonly=False, states={'team_leader': [('readonly', False)]})
    apt_invoice_count = fields.Integer(string='Invoice Count', compute='_get_apt_invoiced', readonly=False)
    comments = fields.Text(string='Comments', readonly=False, states={'in_progress': [('readonly', False)]})
    # notebook pages fields
    is_service_done = fields.Boolean(string="Is Service Done")
    service_note = fields.Text(string="Remarks")
    service_image = fields.Binary(string="Picture")
    apt_invoice_count = fields.Integer(string='Invoice Count', compute='_get_apt_invoiced', readonly=False)
    lab_technician = fields.Many2one('oeh.medical.physician', string='Lab Technician', readonly=False,
                                     states={'operation_manager': [('readonly', False)]}
                                     , domain=[('role_type', '=', 'LT'), ('active', '=', True)])
    nurse = fields.Many2one('oeh.medical.physician', string='Nurse',
                            domain=[('role_type', 'in', ['HN', 'HHCN']), ('active', '=', True)], readonly=False,
                            states={'operation_manager': [('readonly', False)]})
    start_process_date = fields.Datetime(string='STRT. PROC. date', readonly=False)
    complete_process_date = fields.Datetime(string='CMPLT. PROC. date', readonly=False)
    insurance = fields.Many2one('sm.shifa.insurance', string='Insurance', help="Insurance Company Name",
                                domain=[('state', '=', 'Active')],
                                readonly=False, states={'Scheduled': [('readonly', False)]})

    patient_followers = fields.Text("Swabs Owners' Details")
    # patient_followers_count = fields.Integer("Swabs Owners' Details Count")
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
    meeting_id = fields.Many2one('calendar.event', string='Calendar', copy=False, readonly=False)
    duration = fields.Float(string='Duration', default=_pcr_duration, readonly=False)
    payment_method_name = fields.Char(string="Payment Method Name")
    # Indicates whether an appointment has been cancelled.
    # This field is typically updated when a user cancels an appointment via the mobile app or other channels.
    cancellation_requested = fields.Boolean(string='Cancellation Requested', default=lambda *a: 0)

    @api.onchange('appointment_date_only')
    def _onchange_date(self):
        if self.appointment_date_only:
            a = datetime.strptime(str(self.appointment_date_only), "%Y-%m-%d")
            self.day = str(a.strftime("%A"))
            self.appointment_day = self.day

    # @api.model
    # def create(self, vals):
    #     team_obj = self.env['sm.shifa.team.period.pcr']
    #     team = team_obj.search([('date', '=', vals['appointment_date_only']), ('hour', '=', vals['appointment_time'])], limit=1)
    #     print('team available: ', str(team.available))
    #     if team.available > 0:
    #         sequence = self.env['ir.sequence'].next_by_code('sm.shifa.pcr.appointment')
    #         vals['name'] = sequence
    #         return super(ShifaPCRAppointment, self).create(vals)
    #     else:
    #         raise ValidationError('%s hour is full or not determined yet, please book appointment in another hour.' % vals['appointment_time'])

    def _reset_token_number_sequences(self):
        # just use write directly on the result this will execute one update query
        sequences = self.env['ir.sequence'].search([('name', '=', 'PCR Appointment')])
        sequences.write({'number_next_actual': 1})

    def _get_default_journal(self):
        journal = self.env['account.journal'].search([('type', '=', 'sale')], limit=1)
        return journal

    def set_to_operation_manager(self):
        return self.write({'state': 'operation_manager'})

    def set_to_start(self):
        return self.write({'state': 'in_progress', 'start_process_date': datetime.now()})

    def set_to_canceled(self):
        return self.write({'state': 'canceled'})

    def set_to_team_leader(self):
        return self.write({'state': 'team_leader'})

    def set_to_operation_manager(self):
        return self.write({'state': 'operation_manager'})

    def set_back_to_operation_manager(self):
        return self.write({'state': 'operation_manager'})

    def set_to_team(self):
        if self.nurse:
            self.calendar_appointment_event(self.nurse)
        if self.lab_technician:
            self.calendar_appointment_event(self.lab_technician)
        return self.write({'state': 'team'})

    def set_to_visit_done(self):
        return self.write({'state': 'visit_done', 'complete_process_date': datetime.now()})

    def set_back_to_call_center(self):
        return self.write({'state': 'scheduled'})

    @api.onchange('is_drug_allergy_done')
    def get_selection(self):
        done = self.is_drug_allergy_done
        if done:
            self.has_drug_allergy = "yes"
        else:
            self.has_drug_allergy = "no"

    # this set only hours
    @api.onchange('appointment_time')
    def get_appointment_time(self):
        minutes, hours = modf(self.appointment_time)
        self.appointment_time = hours

    @api.onchange('ssn')
    def get_patient(self):
        ssn = self.ssn
        if ssn:
            therapist_obj = self.env['oeh.medical.patient']
            domain = [('ssn', '=', self.ssn)]
            patient_id = therapist_obj.search(domain)
            self.patient = patient_id
            print(patient_id.name)

    def calendar_appointment_event(self, medical_user):
        for rec in self:
            date_time = datetime.fromordinal(rec.appointment_date_only.toordinal())
            time = rec.appointment_time
            start_appointment = date_time + timedelta(seconds=time * 3600)
            start_appointment = start_appointment - timedelta(hours=3)
            meeting_values = {
                'name': rec.display_name,
                'duration': rec.duration,
                'description': " PCR appointment",
                'user_id': medical_user.oeh_user_id.id,
                'start': start_appointment,
                'stop': start_appointment + timedelta(hours=1),
                'allday': False,
                'recurrency': False,
                'privacy': 'confidential',
                'event_tz': medical_user.oeh_user_id.tz,
                'activity_ids': [(5, 0, 0)],
            }

            # Add the partner_id (if exist) as an attendee
            if medical_user.oeh_user_id and medical_user.oeh_user_id.partner_id:
                meeting_values['partner_ids'] = [
                    (4, medical_user.oeh_user_id.partner_id.id)]

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


class ShifaAppointmentSaleOrder(models.Model):
    _inherit = 'sm.shifa.pcr.appointment'

    def _get_default_hvf(self):
        miscellaneous_obj = self.env['sm.shifa.miscellaneous.charge.service']
        domain = [('name', '=', 'Home Visit Fee')]
        hvf = miscellaneous_obj.search(domain, limit=1)
        if hvf:
            return hvf.id or False
        else:
            return False

    def _compute_payment_count(self):
        oe_apps = self.env['sale.order']
        for acc in self:
            domain = [('pcr_appointment', '=', acc.id)]
            app_ids = oe_apps.search(domain)
            apps = oe_apps.browse(app_ids)
            app_count = 0
            for ap in apps:
                app_count += 1
            acc.sale_order_count = app_count
        return True

    @api.onchange('miscellaneous_charge')
    def _get_miscellaneous_price(self):
        for rec in self:
            rec.miscellaneous_price = rec.miscellaneous_charge.list_price

    sale_order_count = fields.Integer(compute=_compute_payment_count, string="Sale Orders")
    order_id = fields.Many2one('sale.order', string='Order #')

    miscellaneous_charge = fields.Many2one('sm.shifa.miscellaneous.charge.service', string='Other Charges Type',
                                           required=True, readonly=False, default=_get_default_hvf)
    miscellaneous_price = fields.Float(string='Home Visit Fee', readonly=False)

    def action_create_sale_order(self):
        for acc in self:
            if acc.service:
                if acc.insurance:
                    partner_val = acc.insurance.partner_id.id
                else:
                    partner_val = acc.patient.partner_id.id

                sale_order = self.env["sale.order"].sudo().create({
                    'partner_id': partner_val,
                    'client_order_ref': "PCR Appointment # : " + acc.service.product_id.name,
                    'pcr_appointment': acc.id,
                    'state': 'sale',
                })
                if acc.service:
                    self.create_sale_order_line(acc.service.name, acc.service.product_id.id, acc.service.list_price,
                                                acc.discount,
                                                acc.ksa_nationality, sale_order.id)

                self.write({'state': 'visit_done', 'order_id': sale_order.id, 'complete_process_date': datetime.now()})

            else:
                raise UserError(_('Configuration error!\nCould not find any appointment to create the sale order !'))
        return True

    @api.model
    def create(self, vals):
        appointment = super(ShifaAppointmentSaleOrder, self).create(vals)
        payment_method = vals['payment_made_through']
        if payment_method == 'mobile':
            patient = vals.get('patient')
            print('patient', patient)
            # self.create_payment(vals)
        return appointment

    def create_sale_order_line(self, name, product_id, price, discount, ksa, order_id):
        sale_order_line = self.env['sale.order.line'].create({
            'name': name,
            'product_id': product_id,
            'product_uom_qty': 1,
            'price_unit': price,
            'discount': discount,
            'order_id': order_id,
        })
        if ksa == 'NON':
            sale_order_line.product_id_change()


class ShifaAppointmentInSaleOrder(models.Model):
    _inherit = 'sale.order'

    pcr_appointment = fields.Many2one('sm.shifa.pcr.appointment', string="PCR Appointment #")


class SmartMindShifaDoctorScheduleTimeSlot(models.Model):
    _inherit = "sm.shifa.pcr.appointment"

    @api.onchange('appointment_date_only', 'appointment_time')
    def _get_appointment_date(self):
        for apm in self:
            # if apm.appointment_time: # apm.time_slot and apm.appointment_time:
            if apm.appointment_date_only:
                apm.appointment_date = datetime.strptime(apm.appointment_date_only.strftime("%Y-%m-%d %H:%M:%S"),
                                                         "%Y-%m-%d %H:%M:%S") + timedelta(
                    hours=apm.appointment_time - 3)

    # APPOINTMENT DATES------------------------------------------------------------------------------------
    appointment_date_only = fields.Date(string='Date', required=True, readonly=False,
                                        states={'scheduled': [('readonly', False)],
                                                'team_leader': [('readonly', False)],
                                                'operation_manager': [('readonly', False)]},
                                        default=lambda *a: datetime.now())
    appointment_time = fields.Float(string='Time (HH:MM)', default=01.00, readonly=False)
    timeslot = fields.Many2one('sm.shifa.physician.schedule.timeslot', string='Timeslot',
                               domain="[('physician_id', '=', head_doctor), ('date', '=', appointment_date_only), ('is_available', '=', True)]",
                               readonly=False, states={'scheduled': [('readonly', False)],
                                                       'team_leader': [
                                                           ('readonly', False)],
                                                       'operation_manager': [
                                                           ('readonly', False)]})
    appointment_date = fields.Datetime(compute=_get_appointment_date, string='Apt. DateTime', readonly=False,
                                       store=True)

    # ---------------------------------------------------------------------------------------------------------

    @api.onchange('timeslot')
    def onchange_timeslot(self):
        if self.timeslot:
            hm = self.timeslot.available_time.split(':')
            sch_time = int(hm[0]) + int(hm[1]) / 60
            print('time: ', str(sch_time))
            self.appointment_time = sch_time

    def timeslot_is_available(self, tm_id, action):
        timeslot = self.env['sm.shifa.physician.schedule.timeslot'].sudo().browse(int(tm_id))
        timeslot.sudo().write({
            'is_available': action,
        })

    def active_timeslot(self):
        for rec in self.filtered(lambda rec: rec.state in ['scheduled', 'operation_manager', 'team']):
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


class ShifaPCRAppointmentInAccountMove(models.Model):
    _inherit = 'account.move'

    pcr_appointment = fields.Many2one('sm.shifa.pcr.appointment', string="PCR Appointment #")


class ShifaDoctorInstructionForPCR(models.Model):
    _inherit = 'sm.shifa.doctor.instruction'

    pcr_appointment = fields.Many2one('sm.shifa.pcr.appointment', 'PCR Appointment', ondelete='cascade',
                                      index=True)
