from odoo import models, fields, api
import datetime
from odoo.exceptions import ValidationError
from datetime import date
from psycopg2._psycopg import List


class EnteralFeeding(models.Model):
    _name = 'sm.shifa.enteral.feeding'
    _description = 'Enteral Feeding'
    _rec_name = 'enteral_feeding_code'

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
    yes_no_na_competent = [
        ('Competent', 'Competent'),
        ('Yes', 'Yes'),
        ('No', 'No'),
        ('NA', 'NA'),
    ]
    competent_no_na = [
        ('Competent', 'Competent'),
        ('No', 'No'),
        ('NA', 'NA'),
    ]

    def _get_enteral(self):
        """Return default enteral value"""
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

    enteral_feeding_code = fields.Char('Reference', index=True, copy=False)
    patient = fields.Many2one('oeh.medical.patient', string='Patient', help="Patient Name", required=True,
                              readonly=True, states={'Draft': [('readonly', False)]})
    hhc_appointment = fields.Many2one('sm.shifa.hhc.appointment', string='HHC-Appointment',
                                      readonly=True, states={'Draft': [('readonly', False)]})
    doctor = fields.Many2one('oeh.medical.physician', string='Nurse', help="Current primary care / family doctor",
                             readonly=True, states={'Draft': [('readonly', False)]},
                             domain=[('role_type', '=', ['HHCN', 'HN'])], required=True, default=_get_enteral)
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

    type_of_enteral_feeding_show = fields.Boolean()
    type_of_enteral_feeding = fields.Selection([
        ('Nasogastric Tube', 'Nasogastric Tube'),
        ('Gastrostomy Tube', 'Gastrostomy Tube'),
        ('Nasojejustomy', 'Nasojejustomy'),
        ('NA', 'NA'),
    ], readonly=True, states={'Start': [('readonly', False)]})
    feeding_regimen_show = fields.Boolean()
    feeding_regimen = fields.Selection([
        ('Bolus', 'Bolus'),
        ('Continuous', 'Continuous'),
    ], readonly=True, states={'Start': [('readonly', False)]})
    potential_actual_risk_show = fields.Boolean()
    potential_actual_complications_related = fields.Selection(yes_no_na,
                                                              readonly=True, states={'Start': [('readonly', False)]})
    potential_actual_risk_for_aspiration = fields.Selection(yes_no_na,
                                                            readonly=True, states={'Start': [('readonly', False)]})
    potential_actual_nutritional_status_changes = fields.Selection(yes_no_na,
                                                                   readonly=True, states={'Start': [('readonly', False)]})
    measurable_goals_show = fields.Boolean()
    measurable_goals_will_remain_free = fields.Selection(yes_no_na,
                                                         readonly=True, states={'Start': [('readonly', False)]})
    measurable_goals_will_maintain_adequate = fields.Selection(yes_no_na,
                                                               readonly=True, states={'Start': [('readonly', False)]})
    measurable_goals_will_not_develop = fields.Selection(yes_no_na,
                                                         readonly=True, states={'Start': [('readonly', False)]})
    patient_assessment_show = fields.Boolean()
    patient_assessment_signs_of_aspiration = fields.Selection(yes_no_na,
                                                              readonly=True, states={'Start': [('readonly', False)]})
    patient_assessment_presence_of_bowel_sounds = fields.Selection(yes_no_na,
                                                                   readonly=True, states={'Start': [('readonly', False)]})
    patient_assessment_presence_of_constipation = fields.Selection(yes_no_na,
                                                                   readonly=True, states={'Start': [('readonly', False)]})
    patient_assessment_presence_of_diarrhoea = fields.Selection(yes_no_na,
                                                                readonly=True, states={'Start': [('readonly', False)]})
    patient_assessment_presence_nausea_vomiting = fields.Selection(yes_no_na,
                                                                   readonly=True, states={'Start': [('readonly', False)]})
    # patient_assessment_presence_abdominal_pain = fields.Selection(yes_no_na,
    #                                                               readonly=True, states={'Start': [('readonly', False)]})
    patient_assessment_peg_tube_site = fields.Selection([
        ('Dry and Intact', 'Dry and Intact'),
        ('Excoriation', 'Excoriation'),
        ('Redness', 'Redness'),
        ('Blisters', 'Blisters'),
        ('Hypergranulation', 'Hypergranulation'),
        ('Leaking', 'Leaking'),
        ('NA', 'NA'),
    ], readonly=True, states={'Start': [('readonly', False)]})
    patient_assessment_facial_skin = fields.Selection([
        ('Dry and Intact', 'Dry and Intact'),
        ('Hypergranulation', 'Hypergranulation'),
        ('NA', 'NA'),
        ('Excoriation', 'Excoriation'),
        ('Redness', 'Redness'),
        ('Blisters', 'Blisters'),
    ], readonly=True, states={'Start': [('readonly', False)]})
    nutritional_assessment_show = fields.Boolean()
    patient_assessment_type_of_supplement = fields.Selection([
        ('NA', 'NA'),
        ('Ensure', 'Ensure'),
        ('Ensure Plus', 'Ensure Plus'),
        ('Fortisip', 'Fortisip'),
        ('Glucerna', 'Glucerna'),
        ('Glucerna Plus', 'Glucerna Plus'),
        ('Pulmocare', 'Pulmocare'),
        ('Resource ', 'Resource '),
        ('Resource Plus', 'Resource Plus'),
        ('Jevity', 'Jevity'),
        ('Infantrini', 'Infantrini'),
    ], readonly=True, states={'Start': [('readonly', False)]})
    patient_assessment_frequency_of_feeds = fields.Selection([
        ('Continous', 'Continous'),
        ('4 hourly', '4 hourly'),
        ('Hourly', 'Hourly'),
    ], readonly=True, states={'Start': [('readonly', False)]})
    patient_assessment_daily_nutritional_intake = fields.Selection([
        ('NA', 'NA'),
        ('Adequate', 'Adequate'),
        ('InAdequate', 'InAdequate'),
    ], readonly=True, states={'Start': [('readonly', False)]})
    patient_assessment_weight_change = fields.Selection([
        ('No Change', 'No Change'),
        ('Decrease', 'Decrease'),
        ('Increase', 'Increase'),
        ('NA', 'NA'),
    ], readonly=True, states={'Start': [('readonly', False)]})
    patient_assessment_change_nutritional_status = fields.Selection([
        ('No Change', 'No Change'),
        ('Positive Change', 'Positive Change'),
        ('Negative Change', 'Negative Change'),
    ], readonly=True, states={'Start': [('readonly', False)]})
    patient_assessment_nutritional_status = fields.Selection([
        ('Good', 'Good'),
        ('Fair', 'Fair'),
        ('Poor', 'Poor'),
        ('Cachexic', 'Cachexic'),
        ('Dehydrated', 'Dehydrated'),
        ('Emaciated', 'Emaciated'),
    ], readonly=True, states={'Start': [('readonly', False)]})
    patient_assessment_physical_apearance = fields.Selection([
        ('Adequately Nourished ', 'Adequately Nourished '),
        ('Malnourished', 'Malnourished'),
        ('At Risk of Malnutrition', 'At Risk of Malnutrition'),
        ('Obese', 'Obese'),
        ('NA', 'NA'),
    ], readonly=True, states={'Start': [('readonly', False)]})
    patient_assessment_refer_to_Dietician = fields.Selection(yes_no_na,
                                                             readonly=True, states={'Start': [('readonly', False)]})

    tube_change_show = fields.Boolean()
    tube_change_tube_change_done = fields.Selection(yes_no_na,
                                                    readonly=True, states={'Start': [('readonly', False)]})
    tube_change_type_of_tube = fields.Selection([
        ('Ryles', 'Ryles'),
        ('Silicone', 'Silicone'),
        ('PEG', 'PEG'),
        ('NA', 'NA'),
    ], readonly=True, states={'Start': [('readonly', False)]})
    tube_change_presence_gastric_residual_volume_checked = fields.Selection([
        ('Yes', 'Yes'),
        ('Nil', 'Nil'),
        ('NA', 'NA'),
    ], readonly=True, states={'Start': [('readonly', False)]})
    tube_change_gastric_ph_result = fields.Selection([
        ('less than 4.5', 'less than 4.5'),
        ('between 4.5 -5.5', 'between 4.5 -5.5'),
        ('Nil', 'Nil'),
        ('NA', 'NA'),
    ], readonly=True, states={'Start': [('readonly', False)]})
    tube_change_gastric_ph_checked = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    tube_change_initiate_feeding = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    tube_change_internal_ngt = fields.Integer(readonly=True, states={'Start': [('readonly', False)]})
    tube_change_external_ngt = fields.Integer(readonly=True, states={'Start': [('readonly', False)]})
    tube_change_ngt_size = fields.Float(readonly=True, states={'Start': [('readonly', False)]})
    tube_change_consent_signed_by = fields.Text(readonly=True, states={'Start': [('readonly', False)]})
    tube_change_next_due = fields.Date(readonly=True, states={'Start': [('readonly', False)]})

    caregiver_assessment_show = fields.Boolean()
    caregiver_assessment_perform_tube_placement = fields.Selection(competent_no_na,
                                                                   readonly=True, states={'Start': [('readonly', False)]})
    caregiver_assessment_perform_enteral_feeding = fields.Selection(competent_no_na,
                                                                    readonly=True, states={'Start': [('readonly', False)]})
    caregiver_assessment_perform_gastrostomy_site = fields.Selection(yes_no_na_competent,
                                                                     readonly=True, states={'Start': [('readonly', False)]})
    caregiver_assessment_perform_mouth_care = fields.Selection(yes_no_na_competent,
                                                               readonly=True, states={'Start': [('readonly', False)]})

    caregiver_education_show = fields.Boolean()
    caregiver_education_wash_hands_thoroughly = fields.Selection(yes_no_na,
                                                                 readonly=True, states={'Start': [('readonly', False)]})
    caregiver_education_check_the_placement = fields.Selection(yes_no_na,
                                                               readonly=True, states={'Start': [('readonly', False)]})
    caregiver_education_raise_the_head = fields.Selection(yes_no_na,
                                                          readonly=True, states={'Start': [('readonly', False)]})
    caregiver_education_inform_home_care = fields.Selection(yes_no_na,
                                                            readonly=True, states={'Start': [('readonly', False)]})
    caregiver_education_reemphasize_education = fields.Selection(yes_no_na,
                                                                 readonly=True, states={'Start': [('readonly', False)]})
    remarks_show = fields.Boolean()
    remarks = fields.Text(readonly=True, states={'Start': [('readonly', False)]})

    enteral_follow_up_id = fields.One2many('sm.shifa.enteral.feeding.follow.up', 'enteral_feeding_id',
                                           string='enteral follow up')
    referral_id = fields.One2many('sm.shifa.referral', 'enteral_feeding_ref_id',
                                  string='enteral referral')
    consent_show = fields.Boolean()
    consent_file1 = fields.Binary()
    consent_file2 = fields.Binary()

    @api.onchange('tube_change_internal_ngt', 'tube_change_external_ngt')
    def _check_respiratory_frequency(self):
        if self.tube_change_internal_ngt > 100:
            raise ValidationError("invalid Internal NGT Tube Length")
        if self.tube_change_external_ngt > 100:
            raise ValidationError("invalid External NGT Tube Length")

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

    @api.model
    def create(self, vals):
        vals['enteral_feeding_code'] = self.env['ir.sequence'].next_by_code('enteral.feeding')
        return super(EnteralFeeding, self).create(vals)


class ShifaReferralInherit(models.Model):
    _inherit = 'sm.shifa.referral'

    enteral_feeding_ref_id = fields.Many2one('sm.shifa.enteral.feeding',
                                             string='enteral feeding', ondelete='cascade')