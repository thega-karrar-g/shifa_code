from odoo import models, fields, api
import datetime
from odoo.exceptions import ValidationError
from datetime import date
from psycopg2._psycopg import List


class DiabeticCare(models.Model):
    _name = 'sm.shifa.diabetic.care'
    _description = 'Diabetic Care'
    _rec_name = 'diabetic_care_code'

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

    def _get_diabetic(self):
        """Return default diabetic value"""
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

    diabetic_care_code = fields.Char('Reference', index=True, copy=False)
    patient = fields.Many2one('oeh.medical.patient', string='Patient', help="Patient Name", required=True,
                              readonly=True, states={'Draft': [('readonly', False)]})
    hhc_appointment = fields.Many2one('sm.shifa.hhc.appointment', string='HHC-Appointment',
                                      readonly=True, states={'Draft': [('readonly', False)]})
    doctor = fields.Many2one('oeh.medical.physician', string='Nurse', help="Current primary care / family doctor",
                             readonly=True, states={'Draft': [('readonly', False)]},
                             domain=[('role_type', '=', ['HHCN', 'HN']), ('active', '=', True)], required=True, default=_get_diabetic)
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

    type_hypoglycemic_show = fields.Boolean()
    oral = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    injection = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    oral_medication = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    oral_other = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    oral_other_text = fields.Text(readonly=True, states={'Start': [('readonly', False)]})
    injection_medication = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    injection_units = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    injection_other = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    injection_other_text = fields.Text(readonly=True, states={'Start': [('readonly', False)]})

    dia_potential_actual_risk_show = fields.Boolean()
    hyper_hypoglycemia_related_to_diabetes_mellitus = fields.Selection(yes_no_na, readonly=True,
                                                                       states={'Start': [('readonly', False)]})
    other_complications_related_to_diabetes_mellitus = fields.Selection(yes_no_na, readonly=True,
                                                                        states={'Start': [('readonly', False)]})

    dia_measurable_goals_show = fields.Boolean()
    complications_related_to_diabetes_mellitus = fields.Selection(yes_no_na, readonly=True,
                                                                  states={'Start': [('readonly', False)]})
    maintain_blood_sugar_level_within_acceptable = fields.Selection(yes_no_na, readonly=True,
                                                                    states={'Start': [('readonly', False)]})
    blood_sugar_levels_are_monitored_and_recorded = fields.Selection(yes_no_na, readonly=True,
                                                                     states={'Start': [('readonly', False)]})

    patient_assessment_show = fields.Boolean()
    vital_signs_within_normal = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    skin_integrity_intact = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    blood_sugar_level = fields.Integer(readonly=True, states={'Start': [('readonly', False)]})
    mmol_mmol_bolin = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    mg_di_bolin = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    mmol_mmol = fields.Selection([
        ('Pre Meal', 'Pre Meal'),
        ('Post Meal', 'Post Meal'),
        ('2 hrs Post Meal', '2 hrs Post Meal'),
        ('4 hrs Post Meal', '4 hrs Post Meal'),
    ], readonly=True, states={'Start': [('readonly', False)]})
    blood_sugar_control = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})

    nutrition_show = fields.Boolean()
    specific_dietary_needs = fields.Selection([
        ('Normal', 'Normal'),
        ('Soft', 'Soft'),
        ('Liquid', 'Liquid'),
        ('Diabetic', 'Diabetic'),
        ('Enteral', 'Enteral'),
    ], readonly=True, states={'Start': [('readonly', False)]})
    observing_dietary_intake = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    physical_appearance = fields.Selection([
        ('Adequately Nourished', 'Adequately Nourished'),
        ('Malnourished', 'Malnourished'),
        ('At Risk of Malnutrition', 'At Risk of Malnutrition'),
        ('NA', 'NA'),
    ], readonly=True, states={'Start': [('readonly', False)]})

    medication_show = fields.Boolean()
    diabetic_medication_discussed = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    compliant_medication_regimen = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    medication_review_done = fields.Text(readonly=True, states={'Start': [('readonly', False)]})

    patient_caregiver_education_show = fields.Boolean()
    ensure_that_patient_monitors = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    patient_taking_appropriate = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    check_feet_daily_any = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    encourages_activities = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    aware_of_managing_hypoglycaemic_event = fields.Selection(yes_no_na, readonly=True,
                                                             states={'Start': [('readonly', False)]})
    remarks_show = fields.Boolean()
    remarks = fields.Text(readonly=True, states={'Start': [('readonly', False)]})

    diabetic_follow_up_id = fields.One2many('sm.shifa.diabetic.care.follow.up', 'diabetic_care_id',
                                            string='diabetic follow up')
    referral_id = fields.One2many('sm.shifa.referral', 'diabetic_care_ref_id', string='diabetic referral')
    consent_show = fields.Boolean()
    consent_file1 = fields.Binary()
    consent_file2 = fields.Binary()

    @api.onchange('systolic_bp', 'hr_min', 'diastolic_br', 'rr_min', 'temperature_c', 'blood_sugar_level',
                  'char_other_oxygen')
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
        if self.blood_sugar_level > 1000:
            raise ValidationError("invalid Blood sugar level")
        if self.char_other_oxygen > 1000:
            raise ValidationError("invalid O2 Sat(%)")

    @api.model
    def create(self, vals):
        vals['diabetic_care_code'] = self.env['ir.sequence'].next_by_code('diabetic.care')
        return super(DiabeticCare, self).create(vals)


class ShifaReferralInherit(models.Model):
    _inherit = 'sm.shifa.referral'

    diabetic_care_ref_id = fields.Many2one('sm.shifa.diabetic.care', string='diabetic care', ondelete='cascade')
