from datetime import timedelta

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
from datetime import timedelta
from datetime import date

"""
patient medicine model used for control medicine start date and end date also, choose time duration for take medicine by 
caregiver that help patient.
"""


class SmMainPatientMedicine(models.Model):
    _name = "sm.caregiver.main.patient.medicine"
    _description = "Main Patient Medicines"
    _rec_name = 'patient'

    ADDED_BY = [
        ('nurse', 'Nurse'),
        ('patient_custodian', 'Patient Custodian'),
    ]
    STATE = [
        ('draft', 'Draft'),
        ('activate', 'Activate'),
        ('deactivate', 'Deactivate'),
    ]
    read_state = {
        'draft': [('readonly', False)]
    }

    MISSED_TIME = [
        ('0.5', '00:30'),
        ('1.0', '01:00'),
        ('1.5', '01:30'),
        ('2.0', '02:00'),
        ('2.5', '02:30'),
        ('3.0', '03:00'),
        ('3.5', '03:30'),
        ('4.0', '04:00'),
        ('4.5', '04:30'),
        ('5.0', '05:00'),
        ('5.5', '05:30'),
        ('6.0', '06:00'),
    ]

    DURATION_UNIT = [
        ('Minutes', 'Minutes'),
        ('Hours', 'Hours'),
        ('Days', 'Days'),
        ('Weeks', 'Weeks'),
        ('Months', 'Months'),
        ('Years', 'Years'),
        ('Indefinite', 'Indefinite'),
    ]

    @api.depends('patient', 'added_by')
    def custodian_patient(self):
        for rec in self:
            if rec.added_by == 'patient_custodian':
                rec.patient_custodian = rec.patient.parent_id.id
            else:
                rec.patient_custodian = False

    state = fields.Selection(STATE, string="state", readonly=True, default=lambda *a: 'draft')
    patient = fields.Many2one('oeh.medical.patient', string='Patient', help="Patient Name", readonly=True,
                              states=read_state)
    added_by = fields.Selection(ADDED_BY, string="Add by", readonly=True, default="nurse", states=read_state)
    nurse = fields.Many2one('oeh.medical.physician', string='Nurse', help="Current primary care",
                            domain=[('role_type', 'in', ('HN', 'HHCN'))], readonly=True, states=read_state)
    patient_custodian = fields.Many2one('oeh.medical.patient', string='Patient Custodian', compute=custodian_patient)
    caregiver_id = fields.Many2one('sm.caregiver', string='Caregiver Ref#', index=True, ondelete='cascade',
                                   domain="[('patient','=',patient)]",
                                   readonly=True, states=read_state)

    # medication profile for active medicine with details
    medication_profile_id = fields.Many2one('sm.shifa.medication.profile')
    prescribed_medicine = fields.Many2one('sm.shifa.generic.medicines', string='Medicine', help="Prescribed Medicines",
                                          readonly=True, states=read_state)
    indication = fields.Many2one('oeh.medical.pathology', string="Indication",
                                 related="medication_profile_id.p_indication")
    dose = fields.Float(string="Dose", related="medication_profile_id.p_dose")
    dose_unit = fields.Many2one('oeh.medical.dose.unit', related="medication_profile_id.p_dose_unit",
                                string="Dose Unit")
    dose_form = fields.Many2one('oeh.medical.drug.form', related="medication_profile_id.p_dose_form", string="Form")
    common_dosage = fields.Many2one('oeh.medical.dosage', related="medication_profile_id.p_common_dosage",
                                    string="Frequency")
    duration = fields.Integer(related="medication_profile_id.p_duration", string="Duration")
    duration_period = fields.Selection(DURATION_UNIT, related="medication_profile_id.p_duration_period", string='Duration Period')
    qty = fields.Integer(related="medication_profile_id.p_qty", string="Quantity")
    dose_route = fields.Many2one('oeh.medical.drug.route', related="medication_profile_id.p_dose_route", string='Administration Route')
    comment = fields.Char(string="Comment", related="medication_profile_id.comment")

    # medicine list that given by nurse or patient Custodian
    medicine = fields.Char(string="Medicine", readonly=True, states=read_state)
    medicine_image = fields.Binary(attachment=True, readonly=True, states=read_state)
    prescribed_frequency = fields.Many2one('oeh.medical.dosage', string='Frequency', readonly=True, states=read_state,
                                           help="Common / standard dosage frequency for this medicines")
    prescribed_dose = fields.Float(string='Dose', readonly=True, states=read_state,
                                   help="Amount of medicines (eg, 250 mg ) each time the patient takes it")
    prescribed_dose_unit = fields.Many2one('oeh.medical.dose.unit', string='Dose Unit', readonly=True, states=read_state,
                                           help="Unit of measure for the medication to be taken")
    prescribed_dose_route = fields.Many2one('oeh.medical.drug.route', string='Administration Route', readonly=True, states=read_state,
                                            help="HL7 or other standard drug administration route code.")
    # prescribed_dose_form = fields.Many2one('oeh.medical.drug.form', 'Form', help="Drug form, such as tablet or gel")
    # prescribed_duration = fields.Integer(string='Duration')
    # prescribed_qty = fields.Integer(string='Quantity')

    # main parameters that generate schedule
    medicine_frequency = fields.Many2one("sm.medicines.frequencies", readonly=True, states=read_state)
    number_times = fields.Selection(related="medicine_frequency.number_of_times", string="Number of times a day")
    is_missed = fields.Boolean(related="medicine_frequency.is_missed", string="is missed?")

    duration_time = fields.Float(string="Duration", readonly=True, states=read_state)
    missed_time = fields.Selection(MISSED_TIME, string="Missed Time", readonly=True, states=read_state)

    start_date = fields.Date(string="Start Date", readonly=True, states=read_state)
    stop_date = fields.Date(string="Stop Date", readonly=True, states=read_state)
    deactivate_date = fields.Datetime(string="Deactivate Date", readonly=True)

    time1 = fields.Float(default=0.01, readonly=True, states=read_state)
    time2 = fields.Float(default=0.01, readonly=True, states=read_state)
    time3 = fields.Float(default=0.01, readonly=True, states=read_state)
    time4 = fields.Float(default=0.01, readonly=True, states=read_state)
    time5 = fields.Float(default=0.01, readonly=True, states=read_state)
    time6 = fields.Float(default=0.01, readonly=True, states=read_state)
    time7 = fields.Float(default=0.01, readonly=True, states=read_state)
    time8 = fields.Float(default=0.01, readonly=True, states=read_state)
    #  schedule field
    schedule_lines = fields.One2many('sm.caregiver.medicine.schedule', 'patient_medicine_id', ondelete='cascade',
                                     readonly=True)

    def set_to_deactivate(self):
        return self.write({'state': 'deactivate', 'deactivate_date': datetime.now()})

    def set_to_generate(self):
        self.generate_schedule()
        return self.write({'state': 'activate'})

    @api.onchange('patient')
    def get_medication_medicine(self):
        therapist_obj = self.env['sm.shifa.medication.profile']
        domain = [('patient', '=', self.patient.id)]
        s = therapist_obj.search(domain)
        medicine_id = []
        if s:
            for i in s:
                if i.state_app == "active":
                    if i.p_generic_name:
                        medicine_id.append(i.p_generic_name.id)
                    elif i.p_brand_medicine:
                        medicine_id.append(i.p_brand_medicine.generic_name.id)
                    else:
                        pass
                else:
                    pass
        return {'domain': {'prescribed_medicine': [('id', 'in', medicine_id)]}}

    @api.onchange('prescribed_medicine')
    def get_medicine_details(self):
        if self.prescribed_medicine:
            patient_profile = self.patient.med_pro_id
            print(patient_profile)
            for i in patient_profile:
                if self.prescribed_medicine == i.p_generic_name:
                    print(i)
                    self.medication_profile_id = i
                    return {'domain': {'medication_profile_id': [('id', '=', i.id)]}}

                if self.prescribed_medicine == i.p_brand_medicine.generic_name:
                    print(i)
                    self.medication_profile_id = i
                    return {'domain': {'medication_profile_id': [('id', '=', i.id)]}}
                else:
                    self.medication_profile_id = False

    @api.onchange('stop_date')
    def onchange_end_date(self):
        if self.stop_date:
            if self.stop_date < self.start_date:
                raise ValidationError('Sorry, Stop date must be greater than start date')

    @api.onchange('number_times')
    def onchange_duration(self):
        if self.number_times:
            self.duration_time = round(24 / int(self.number_times), 1)

    @api.onchange('number_times')
    def onchange_times(self):
        if self.duration_time == 12:
            self.time1 = 7.0
            self.time2 = self.time1 + self.duration_time
        elif self.duration_time == 8:
            self.time1 = 7.0
            self.time2 = self.time1 + self.duration_time
            self.time3 = self.time2 + self.duration_time
        elif self.duration_time == 6:
            self.time1 = 6.0
            self.time2 = self.time1 + self.duration_time
            self.time3 = self.time2 + self.duration_time
            self.time4 = 0.0
        elif self.duration_time == 4.80:
            self.time1 = 0.0
            self.time2 = self.time1 + self.duration_time
            self.time3 = self.time2 + self.duration_time
            self.time4 = self.time3 + self.duration_time
            self.time5 = self.time4 + self.duration_time
        elif self.duration_time == 4:
            self.time1 = 0.0
            self.time2 = self.time1 + self.duration_time
            self.time3 = self.time2 + self.duration_time
            self.time4 = self.time3 + self.duration_time
            self.time5 = self.time4 + self.duration_time
            self.time6 = self.time5 + self.duration_time
        elif self.duration_time == 3.40:
            self.time1 = 0.0
            self.time2 = self.time1 + self.duration_time
            self.time3 = self.time2 + self.duration_time
            self.time4 = self.time3 + self.duration_time
            self.time5 = self.time4 + self.duration_time
            self.time6 = self.time5 + self.duration_time
            self.time7 = self.time6 + self.duration_time
        elif self.duration_time == 3:
            self.time1 = 0.0
            self.time2 = self.time1 + self.duration_time
            self.time3 = self.time2 + self.duration_time
            self.time4 = self.time3 + self.duration_time
            self.time5 = self.time4 + self.duration_time
            self.time6 = self.time5 + self.duration_time
            self.time7 = self.time6 + self.duration_time
            self.time8 = self.time7 + self.duration_time


        else:
            pass

    def time_list(self, number_times):
        time = []
        if number_times == '1':
            time.append(self.time1)
        elif number_times == '2':
            time.extend((self.time1, self.time2))
        elif number_times == '3':
            time.extend((self.time1, self.time2, self.time3))
        elif number_times == '4':
            time.extend((self.time1, self.time2, self.time3, self.time4))
        elif number_times == '5':
            time.extend((self.time1, self.time2, self.time3, self.time4, self.time5))
        elif number_times == '6':
            time.extend((self.time1, self.time2, self.time3, self.time4, self.time5, self.time6))
        elif number_times == '7':
            time.extend((self.time1, self.time2, self.time3, self.time4, self.time5, self.time6, self.time7))
        elif number_times == '8':
            time.extend(
                (self.time1, self.time2, self.time3, self.time4, self.time5, self.time6, self.time7, self.time8))
        else:
            pass
        return time

    def generate_schedule(self):
        sch_date = self.start_date
        sch_days = (self.stop_date - self.start_date).days
        schedule_obj = self.env['sm.caregiver.medicine.schedule']
        for date in range(sch_days+1):
            if sch_date <= self.stop_date:
                for i in range(int(self.number_times)):
                    time = self.time_list(self.number_times)
                    schedule_obj.create({
                        'medicine': self.medicine,
                        'date': sch_date,
                        'time': time[i],
                        'is_missed': self.medicine_frequency.is_missed,
                        'time_missed': self.missed_time,
                        'caregiver_id': self.caregiver_id.id,
                        'patient_medicine_id': self.id,
                    })
            sch_date = sch_date + timedelta(days=1)
    def process_generate_medicine(self):
        medicine = self.search([
            ('state', '=', 'draft')
        ])
        if medicine:
            for rec in medicine:
                rec.generate_schedule()
                rec.state = 'activate'

    def make_expired(self):
        print(fields.Date.to_string(date.today()))
        self.search([('state', '=', 'activate'), ('stop_date', '<', fields.Date.to_string(date.today()))]).write({
            'state': 'deactivate',
            'deactivate_date': datetime.now()
        })

    @api.model
    def create(self, values):
        new_medicine = super(SmMainPatientMedicine, self).create(values)

        # Log the creation in the chatter of the related caregiver record
        subtype_id = self.env['mail.message.subtype'].search([('name', '=', 'Comment')], limit=1).id
        if new_medicine.caregiver_id:
            caregiver = new_medicine.caregiver_id
            caregiver.message_post(
                body=f"Added new prescribed medicine: {new_medicine.medicine}",
                subtype_id=subtype_id, # Use the appropriate subtype
            )

        return new_medicine
class MedicineSchedule(models.Model):
    _name = "sm.caregiver.medicine.schedule"
    _description = "Patient Medicines schedule"

    STATE = [
        ('given', 'Given'),
        ('canceled', 'Canceled'),
        ('missed', 'Missed'),
        ('no_need', 'No need'),
    ]

    state = fields.Selection(STATE, string='State')
    medicine = fields.Char(string="Medicine")
    date = fields.Date(string="Date")
    time = fields.Float(string='Time')
    is_missed = fields.Boolean()
    time_missed = fields.Char()
    caregiver_id = fields.Many2one('sm.caregiver', string="Caregiver Ref")
    patient_medicine_id = fields.Many2one('sm.caregiver.main.patient.medicine', string="Medicine Ref")
    caregiver = fields.Many2one('oeh.medical.physician', string='Caregiver')
    comment = fields.Char(string='Comment')

    # -------- missed action ----------- #
    def process_missed_medicine(self):
        medicine = self.search([
            ('state', '=', False),
            ('date', '=', datetime.now().date())
        ])
        if medicine:
            for rec in medicine:
                time = '{0:02.0f}:{1:02.0f}'.format(*divmod(rec.time * 60, 60))
                missed_time = '{0:02.0f}:{1:02.0f}'.format(*divmod((rec.time + float(rec.time_missed)) * 60, 60))
                now_time = (datetime.now() + timedelta(hours=3)).time().strftime("%H:%M")
                not_need_time = '{0:02.0f}:{1:02.0f}'.format(*divmod((rec.time + 1) * 60, 60))
                if rec.is_missed:
                    if now_time == missed_time:
                        rec.write({'state': 'missed'})
                else:
                    if now_time == not_need_time:
                        rec.write({'state': 'no_need'})
