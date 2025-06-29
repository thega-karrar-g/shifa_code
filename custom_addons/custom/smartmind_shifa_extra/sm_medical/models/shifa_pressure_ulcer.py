from odoo import models, fields, api
import datetime
from odoo.exceptions import ValidationError


class PressureUlcer(models.Model):
    _name = 'sm.shifa.pressure.ulcer'
    _description = 'Pressure Ulcer'
    _rec_name = 'pressure_ulcer_code'

    ADMISSION_STATES = [
        ('Draft', 'Draft'),
        ('Start', 'Start'),
        ('Admitted', 'Admitted'),
        ('Discharged', 'Discharged'),
    ]
    yes_no_na = [
        ('Yes', 'Yes'),
        ('No', 'No'),
        ('NA', 'NA'),
    ]
    competent_yes_no_na = [
        ('Competent', 'Competent'),
        ('Yes', 'Yes'),
        ('No', 'No'),
        ('NA', 'NA'),
    ]

    def _get_pressure(self):
        """Return default pressure value"""
        therapist_obj = self.env['oeh.medical.physician']
        domain = [('oeh_user_id', '=', self.env.uid)]
        user_ids = therapist_obj.search(domain, limit=1)
        if user_ids:
            return user_ids.id or False
        else:
            return False

    @api.onchange('hhc_appointment')
    def _onchange_hhc_appointment(self):
        if self.hhc_appointment:
            self.patient = self.hhc_appointment.patient

    #     draft method
    def set_to_start(self):
        return self.write({'state': 'Start'})

        #     Clinical Documentation Completed

    def set_to_admitted(self):
        admission_date = False
        for ina in self:
            if ina.admission_date:
                admission_date = ina.admission_date
            else:
                admission_date = datetime.datetime.now()
        return self.write({'state': 'Admitted', 'admission_date': admission_date})

        #     discharge date time method

    def set_to_discharged(self):
        discharged_date = False
        for ina in self:
            if ina.discharge_date:
                discharged_date = ina.discharge_date
            else:
                discharged_date = datetime.datetime.now()
        return self.write({'state': 'Discharged', 'discharge_date': discharged_date})

    pressure_ulcer_code = fields.Char('Reference', index=True, copy=False)
    patient = fields.Many2one('oeh.medical.patient', string='Patient', help="Patient Name", required=True,
                              readonly=True, states={'Draft': [('readonly', False)]})
    hhc_appointment = fields.Many2one('sm.shifa.hhc.appointment', string='HHC-Appointment',
                                      readonly=True, states={'Draft': [('readonly', False)]})
    doctor = fields.Many2one('oeh.medical.physician', string='Nurse', help="Current primary care / family doctor",
                             readonly=True, states={'Draft': [('readonly', False)]},
                             domain=[('role_type', '=', ['HHCN', 'HN'])], required=True, default=_get_pressure)
    state = fields.Selection(ADMISSION_STATES, string='State', default=lambda *a: 'Draft', readonly=True)
    weight = fields.Float(string='Weight', related='patient.weight')
    age = fields.Char(string='Age', related='patient.age')
    marital_status = fields.Selection(string='Marital Status', related='patient.marital_status')
    sex = fields.Selection(string='Sex', related='patient.sex')
    blood_type = fields.Selection(string='Blood Type', related='patient.blood_type')
    rh = fields.Selection(string='Rh', related='patient.rh')
    admission_date = fields.Datetime(string='Admission Date', readonly='1')
    discharge_date = fields.Datetime(string='Discharge Date', readonly='1')

    conscious_state_show = fields.Boolean()
    conscious_state = fields.Selection([
        ('Alert', 'Alert'),
        ('Response to Voice', 'Response to Voice'),
        ('Response to pain', 'Response to pain'),
        ('Unresponsive', 'Unresponsive'),
    ], readonly=True, states={'Start': [('readonly', False)]})
    pain_present_show = fields.Boolean()
    pain_score = fields.Selection([
        ('0', '0'),
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
    scale_used = fields.Selection([
        ('Numerical', 'Numerical'),
        ('Faces', 'Faces'),
        ('FLACC', 'FLACC'),
        ('ABBEY', 'ABBEY'),
    ], readonly=True, states={'Start': [('readonly', False)]})
    functional_activity_show = fields.Boolean()
    functional_activity = fields.Selection([
        ('No Limitation', 'No Limitation'),
        ('Mild Limitation', 'Mild Limitation'),
        ('Severe Limitation', 'Severe Limitation'),
    ], readonly=True, states={'Start': [('readonly', False)]})

    vital_signs_show = fields.Boolean()
    systolic_bp = fields.Integer(readonly=True, states={'Start': [('readonly', False)]})
    hr_min = fields.Integer(readonly=True, states={'Start': [('readonly', False)]})
    diastolic_br = fields.Integer(readonly=True, states={'Start': [('readonly', False)]})
    rr_min = fields.Integer(readonly=True, states={'Start': [('readonly', False)]})
    temperature_c = fields.Float(readonly=True, states={'Start': [('readonly', False)]})
    # o2_sat = fields.Float(readonly=True, states={'Start': [('readonly', False)]})
    o2_sat = fields.Selection([
        ('at room air', 'at room air'),
        ('with oxygen Support', 'with oxygen Support')
    ], readonly=True, states={'Start': [('readonly', False)]})
    char_other_oxygen = fields.Float(readonly=True, states={'Start': [('readonly', False)]})

    type_impaired_show = fields.Boolean()
    bedridden = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    wheelchair = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    ambulates_assistance = fields.Selection([
        ('Cane', 'Cane'),
        ('Walking Frame', 'Walking Frame'),
        ('Elbow Crutches', 'Elbow Crutches'),
        ('Axillary Crutches', 'Axillary Crutches'),
        ('Patient is Ambulatory', 'Patient is Ambulatory'),
        ('NA', 'NA'),
    ], readonly=True, states={'Start': [('readonly', False)]})

    press_potential_actual_risk_show = fields.Boolean()
    risk_for_falls_related_to_impaired_mobility = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    fall_risk_assessment_done = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    pressure_ulcer_altered_skin_integrity_related = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    complications_related_to_urinary_bowel_incontinence = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})

    press_measurable_goals_show = fields.Boolean()
    free_from_injury_related_to_falls = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    free_from_skin_redness_blisters_or_discoloration = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    skin_will_be_clean_dry_with_appropriate_and_prompt = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})

    patient_assessment_show = fields.Boolean()
    skin_clean_dry_odor = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    any_changes_skin = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    use_pressure_relief = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    patient_assessment_other = fields.Text(readonly=True, states={'Start': [('readonly', False)]})

    caregiver_assessment_show = fields.Boolean()
    maintained_patients_general = fields.Selection([
        ('Well', 'Well'),
        ('Very Well', 'Very Well'),
        ('Fair', 'Fair'),
        ('Poor', 'Poor'),
    ], readonly=True, states={'Start': [('readonly', False)]})
    performed_hourly_turning = fields.Selection(competent_yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    continence_care = fields.Selection(competent_yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    skin_care = fields.Selection(competent_yes_no_na, readonly=True, states={'Start': [('readonly', False)]})

    nutrition_show = fields.Boolean()
    specific_dietary_needs = fields.Selection([
        ('Normal', 'Normal'),
        ('Soft', 'Soft'),
        ('Liquid', 'Liquid'),
        ('Diabetic', 'Diabetic'),
        ('Enteral', 'Enteral'),
    ], readonly=True, states={'Start': [('readonly', False)]})
    maintain_oral_intake = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})

    Patient_caregiver_education_show = fields.Boolean()
    ensure_that_patient_hygiene = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    turn_change_patient_position = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    apply_moisturiser_skin = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    inform_home_care_nurse = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})

    key_performance_indicator_show = fields.Boolean()
    development_new_pressure = fields.Selection([
        ('No', 'No'),
        ('Yes-Home Acquired', 'Yes-Home Acquired'),
        ('Yes-Hospital Acquired', 'Yes-Hospital Acquired'),
    ], readonly=True, states={'Start': [('readonly', False)]})
    since_last_visit = fields.Selection([
        ('No Event', 'No Event'),
        ('Presented to Emergency Unit', 'Presented to Emergency Unit'),
        ('Readmitted to KFMC Hospital', 'Readmitted to KFMC Hospital'),
        ('Readmitted to Other Hospital', 'Readmitted to Other Hospital'),
        ('Seen by private doctor', 'Seen by private doctor'),
    ], readonly=True, states={'Start': [('readonly', False)]})
    remarks_show = fields.Boolean()
    remarks = fields.Text(readonly=True, states={'Start': [('readonly', False)]})

    pressure_follow_up_id = fields.One2many('sm.shifa.pressure.ulcer.follow.up', 'pressure_ulcer_id',
                                            string='pressure follow up')
    referral_id = fields.One2many('sm.shifa.referral', 'pressure_ulcer_ref_id', string='pressure referral')
    consent_show = fields.Boolean()
    consent_file1 = fields.Binary()
    consent_file2 = fields.Binary()

    @api.model
    def create(self, vals):
        vals['pressure_ulcer_code'] = self.env['ir.sequence'].next_by_code('pressure.ulcer')
        return super(PressureUlcer, self).create(vals)

    @api.onchange('systolic_bp', 'hr_min', 'diastolic_br', 'rr_min', 'temperature_c', 'char_other_oxygen')
    def _check_vital_signs(self):
        if self.systolic_bp > 1000:
            raise ValidationError("invalid systolic BP(mmHg)")
        if self.hr_min > 1000:
            raise ValidationError("invalid HR(/min)")
        if self.temperature_c > 100:
            raise ValidationError("invalid Temperature(C)")
        if self.diastolic_br > 1000:
            raise ValidationError("invalid Diastolic BR(mmHg)")
        if self.rr_min > 100:
            raise ValidationError("invalid RR(/min)")
        if self.char_other_oxygen > 1000:
            raise ValidationError("invalid O2 Sat(%)")


class ShifaReferralInherit(models.Model):
    _inherit = 'sm.shifa.referral'

    pressure_ulcer_ref_id = fields.Many2one('sm.shifa.pressure.ulcer', string='pressure ulcer', ondelete='cascade')
