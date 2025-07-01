from odoo import models, fields, api
import datetime
from odoo.exceptions import ValidationError
from datetime import date
from psycopg2._psycopg import List


class CareGiver(models.Model):
    _name = 'sm.shifa.care.giver'
    _description = 'Care Giver'
    _rec_name = 'care_giver_code'

    ADMISSION_STATES = [
        ('Draft', 'Draft'),
        ('Start', 'Start'),
        ('Admitted', 'Admitted'),
        ('Discharged', 'Discharged'),
    ]
    YES_NO = [
        ('Yes ', 'Yes'),
        ('No', 'No'),
    ]
    EYE = [
        ('Right', 'Right'),
        ('Left', 'Left'),
        ('Both', 'Both'),
    ]
    BREATH_SOUND = [
        ('Clear', 'Clear'),
        ('Wheezes', 'Wheezes'),
        ('Rales', 'Rales')
    ]
    RISK_SCORE = [
        ('Low Risk ', 'Low Risk '),
        ('Medium Risk', 'Medium Risk'),
        ('High Risk', 'High Risk'),
    ]
    APPETITE_STATE = [
        ('Good', 'Good'),
        ('Fair', 'Fair'),
        ('Poor', 'Poor'),
    ]
    MUSCLE_POWER = [
        ('Right ', 'Right'),
        ('Left', 'Left'),
        ('Both', 'Both'),
        ('Normal', 'Normal'),
        ('Mild Weakness', 'Mild Weakness'),
        ('Moderate Weakness', 'Moderate Weakness'),
        ('Severe Weakness', 'Severe Weakness'),
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

    def _get_giver(self):
        """Return default giver value"""
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

    care_giver_code = fields.Char('Reference', index=True, copy=False)
    patient = fields.Many2one('oeh.medical.patient', string='Patient', help="Patient Name", required=True,
                              readonly=True, states={'Draft': [('readonly', False)]})
    hhc_appointment = fields.Many2one('sm.shifa.hhc.appointment', string='HHC-Appointment',
                                      readonly=True, states={'Draft': [('readonly', False)]})
    doctor = fields.Many2one('oeh.medical.physician', string='Nurse', help="Current primary care / family doctor",
                             readonly=True, states={'Draft': [('readonly', False)]},
                             domain=[('role_type', '=', ['HHCN', 'HN']), ('active', '=', True)], required=True, default=_get_giver)
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

    # ==============  Respiratory =============#
    # Airway
    respiratory_show = fields.Boolean()
    airway = fields.Selection([
        ('Patent', 'Patent'),
        ('Dyspneic', 'Dyspneic'),
    ], default='Patent', readonly=True,
        states={'Start': [('readonly', False)]})
    # Breath Sounds:
    breath_sound_right_lung = fields.Selection(BREATH_SOUND, default='Clear', readonly=True,
                                               states={'Start': [('readonly', False)]})
    breath_sound_left_lung = fields.Selection(BREATH_SOUND, default='Clear', readonly=True,
                                              states={'Start': [('readonly', False)]})
    # Breath Pattern:
    breath_pattern = fields.Selection([
        ('Normal', 'Normal'),
        ('Dyspneic', 'Dyspneic'),
    ], default='Normal', readonly=True,
        states={'Start': [('readonly', False)]})
    # Air Entry:
    air_entry = fields.Selection([
        ('Normal', 'Normal'),
        ('Diminished', 'Diminished'),
    ], default='Normal', readonly=True,
        states={'Start': [('readonly', False)]})
    # ============== Skin/Circulation =============#
    # Skin/Circulation
    skin_circulation_show = fields.Boolean()
    skin_dry = fields.Boolean(readonly=True,
                              states={'Start': [('readonly', False)]})
    skin_intact = fields.Boolean(readonly=True,
                                 states={'Start': [('readonly', False)]})
    skin_warm = fields.Boolean(readonly=True,
                               states={'Start': [('readonly', False)]})
    skin_cool = fields.Boolean(readonly=True,
                               states={'Start': [('readonly', False)]})
    # IV Cannula
    iv_size = fields.Float(readonly=True,
                           states={'Start': [('readonly', False)]})
    location = fields.Char(readonly=True,
                           states={'Start': [('readonly', False)]})
    # color
    skin_color = fields.Selection([
        ('Brown', 'Brown'),
        ('Black', 'Black'),
        ('Pale', 'Pale'),
        ('Red', 'Red'),
    ], default='Brown', readonly=True,
        states={'Start': [('readonly', False)]})
    # wound
    wound = fields.Char(readonly=True,
                        states={'Start': [('readonly', False)]})
    # ==============  Pain Score Assessment =============#
    # Pain Score Assessment
    pain_score_show = fields.Boolean()
    score = fields.Selection([
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
    ], default='1', readonly=True,
        states={'Start': [('readonly', False)]})
    tool_used = fields.Selection([
        ('Numerical', 'Numerical'),
        ('Faces', 'Faces'),
        ('ABBEY', 'ABBEY'),
        ('FLACC', 'FLACC'),
    ], default='Numerical', readonly=True,
        states={'Start': [('readonly', False)]})
    # ==============  Head and Neck Assessment =============#
    # Head and Neck Assessment
    # vision
    head_neck_show = fields.Boolean()
    vision = fields.Selection([
        ('Normal', 'Normal'),
        ('Blind', 'Blind'),
        ('Cataract', 'Cataract'),
    ], default='Normal', readonly=True,
        states={'Start': [('readonly', False)]})
    blind_eye = fields.Selection(EYE, readonly=True,
                                 states={'Start': [('readonly', False)]})
    cataract_eye = fields.Selection(EYE, readonly=True,
                                    states={'Start': [('readonly', False)]})
    # nose
    nose = fields.Selection([
        ('Normal', 'Normal'),
        ('Flaring', 'Flaring'),
        ('Discharges', 'Discharges'),
    ], default='Normal', readonly=True,
        states={'Start': [('readonly', False)]})
    # ear hearing
    hearing = fields.Selection([
        ('Normal', 'Normal'),
        ('Diminished', 'Diminished'),
        ('Loss', 'Loss'),
        ('Use of Aid', 'Use of Aid'),
    ], default='Normal', readonly=True,
        states={'Start': [('readonly', False)]})
    # mouth
    mouth = fields.Selection([
        ('Normal', 'Normal'),
        ('Bleeding', 'Bleeding'),
        ('Ulcer', 'Ulcer'),
        ('Odor', 'Odor'),
    ], default='Normal', readonly=True,
        states={'Start': [('readonly', False)]})
    # speech
    speech = fields.Selection([
        ('Normal', 'Normal'),
        ('Slurred', 'Slurred'),
        ('Aphasic', 'Aphasic'),
        ('Incoherent', 'Incoherent'),
    ], default='Normal', readonly=True,
        states={'Start': [('readonly', False)]})
    # Lips
    lips = fields.Selection([
        ('Normal', 'Normal'),
        ('Cracked', 'Cracked'),
        ('Dry', 'Dry'),
    ], default='Normal', readonly=True,
        states={'Start': [('readonly', False)]})
    # swallowing
    swallowing = fields.Selection([
        ('Normal', 'Normal'),
        ('Impaired ', 'Impaired'),
        ('Poor', 'Poor'),
    ], default='Normal', readonly=True,
        states={'Start': [('readonly', False)]})
    # gag reflex
    gag_reflex = fields.Selection([
        ('Normal', 'Normal'),
        ('Poor', 'Poor'),
    ], default='Normal', readonly=True,
        states={'Start': [('readonly', False)]})
    head_others = fields.Text(readonly=True,
                              states={'Start': [('readonly', False)]})
    # ============== Chest and Respiratory Assessment =============#
    #      Appearance:
    chest_respiratory_show = fields.Boolean()
    app_normal = fields.Boolean(readonly=True,
                                states={'Start': [('readonly', False)]})
    app_scoliosis = fields.Boolean(readonly=True,
                                   states={'Start': [('readonly', False)]})
    app_khyposis = fields.Boolean(readonly=True,
                                  states={'Start': [('readonly', False)]})
    app_draintube = fields.Boolean(readonly=True,
                                   states={'Start': [('readonly', False)]})
    app_scars = fields.Boolean(readonly=True,
                               states={'Start': [('readonly', False)]})
    app_wound = fields.Boolean(readonly=True,
                               states={'Start': [('readonly', False)]})
    # ==============  Abdomen Assessment =============#
    # Bowel Movement
    abnormal_show = fields.Boolean()
    bowel_movement = fields.Selection([
        ('Normal', 'Normal'),
        ('Abnormal', 'Abnormal'),
        ('Every Other Day', 'Every Other Day'),
    ], default='Normal', readonly=True,
        states={'Start': [('readonly', False)]})
    # bowel sounds
    bowel_sounds = fields.Selection([
        ('Nil', 'Nil'),
        ('Abnormal', 'Abnormal'),
        ('Active', 'Active'),
    ], readonly=True,
        states={'Start': [('readonly', False)]})
    # stoma:(Colostomy/Ileostomy)
    stoma_colostomy = fields.Selection([
        ('NA', 'NA'),
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    ], readonly=True, states={'Start': [('readonly', False)]})
    abdomen_other = fields.Char(readonly=True, states={'Start': [('readonly', False)]})
    # ============== Gastrointestinal Assessment =============#
    # feeding
    feeding_show = fields.Boolean()
    feeding = fields.Selection([
        ('Oral Feeding', 'Oral Feeding'),
        ('Tube Feeding', 'Tube Feeding'),
    ], readonly=True, states={'Start': [('readonly', False)]})

    #  Appetite
    appetite = fields.Selection(APPETITE_STATE, readonly=True, states={'Start': [('readonly', False)]})
    #  Nutritional Status
    nutritional_appetite = fields.Selection(APPETITE_STATE, readonly=True, states={'Start': [('readonly', False)]})
    # Diet
    diet = fields.Selection([
        ('Regular', 'Regular'),
        ('Diabetic', 'Diabetic'),
        ('Low Salt/Fat', 'Low Salt/Fat'),
        ('Low Salt', 'Low Salt'),
        ('Soft', 'Soft'),
        ('Others', 'Others'),
    ], readonly=True, states={'Start': [('readonly', False)]})
    diet_others = fields.Char(readonly=True, states={'Start': [('readonly', False)]})
    # Enteral Feeding
    enteral_feeding = fields.Selection([
        ('NGT', 'NGT'),
        ('NDT', 'NDT'),
        ('JOT', 'JOT'),
        ('GST', 'GST'),
    ], readonly=True, states={'Start': [('readonly', False)]})
    liquid_tube_feeding = fields.Selection([
        ('Mixing Diet', 'Mixing Diet'),
        ('Milk', 'Milk'),
        ('Formola', 'Formola'),
        ('Others', 'Others'),
    ], readonly=True, states={'Start': [('readonly', False)]})
    liquid_feeding_others = fields.Char(readonly=True, states={'Start': [('readonly', False)]})
    ef_amount = fields.Float(readonly=True, states={'Start': [('readonly', False)]})
    ef_frequency = fields.Float(readonly=True, states={'Start': [('readonly', False)]})
    # date and type
    feeding_date_inserted = fields.Date(readonly=True, states={'Start': [('readonly', False)]})
    feeding_tube_type = fields.Selection([
        ('Latex ', 'Latex'),
        ('Rubber', 'Rubber'),
        ('Silicon', 'Silicon'),
    ], readonly=True, states={'Start': [('readonly', False)]})
    feeding_tube_size = fields.Float(readonly=True, states={'Start': [('readonly', False)]})
    feeding_due_date = fields.Date(readonly=True, states={'Start': [('readonly', False)]})
    #      Renal Assessment  #
    renal_show = fields.Boolean()
    renal_voiding = fields.Selection([
        ('Normal ', 'Normal'),
        ('Incontinent', 'Incontinent'),
        ('Urosheath', 'Urosheath'),
        ('Superapubic', 'Superapubic'),
        ('IFC', 'IFC'),
    ], readonly=True, states={'Start': [('readonly', False)]})
    renal_tube_type = fields.Selection([
        ('Latex ', 'Latex'),
        ('Rubber', 'Rubber'),
        ('Silicon', 'Silicon'),
    ], readonly=True, states={'Start': [('readonly', False)]})
    renal_tube_size = fields.Float(readonly=True, states={'Start': [('readonly', False)]})
    renal_date_inserted = fields.Date(readonly=True, states={'Start': [('readonly', False)]})
    renal_due_date = fields.Date(readonly=True, states={'Start': [('readonly', False)]})
    renal_dysuria = fields.Selection(YES_NO, readonly=True, states={'Start': [('readonly', False)]})
    renal_hematuria = fields.Selection(YES_NO, readonly=True, states={'Start': [('readonly', False)]})
    renal_frequency = fields.Selection(YES_NO, readonly=True, states={'Start': [('readonly', False)]})
    renal_urine_color = fields.Selection([
        ('Normal ', 'Normal'),
        ('Abnormal', 'Abnormal'),
    ], readonly=True, states={'Start': [('readonly', False)]})
    renal_urine_clarity = fields.Selection([
        ('Clear ', 'Clear'),
        ('Cloudy', 'Cloudy'),
    ], readonly=True, states={'Start': [('readonly', False)]})
    renal_other = fields.Text(readonly=True, states={'Start': [('readonly', False)]})
    #      9th page tab Musculoskeletal Assessment  #
    musculoskeletal_show = fields.Boolean()
    movement = fields.Selection([
        ('Normal ', 'Normal'),
        ('Impaired', 'Impaired'),
        ('Bedridden', 'Bedridden'),
        ('Wheel chair', 'Wheel chair'),
    ], readonly=True, states={'Start': [('readonly', False)]})

    muscle_power_upper = fields.Selection(MUSCLE_POWER, readonly=True, states={'Start': [('readonly', False)]})
    muscle_power_lower = fields.Selection(MUSCLE_POWER, readonly=True, states={'Start': [('readonly', False)]})
    requires_assistant_ADLS = fields.Selection(YES_NO, readonly=True, states={'Start': [('readonly', False)]})
    requires_assistant_movement = fields.Selection(YES_NO, readonly=True, states={'Start': [('readonly', False)]})
    #   tab Risk Score  #
    fall_risk_score = fields.Selection(RISK_SCORE, readonly=True, states={'Start': [('readonly', False)]})
    braden_risk_score = fields.Selection(RISK_SCORE, readonly=True, states={'Start': [('readonly', False)]})
    actual_risks1 = fields.Text(readonly=True, states={'Start': [('readonly', False)]})
    actual_risks2 = fields.Text(readonly=True, states={'Start': [('readonly', False)]})
    actual_risks3 = fields.Text(readonly=True, states={'Start': [('readonly', False)]})
    actual_risks4 = fields.Text(readonly=True, states={'Start': [('readonly', False)]})
    smart_m_goals1 = fields.Text(readonly=True, states={'Start': [('readonly', False)]})
    smart_m_goals2 = fields.Text(readonly=True, states={'Start': [('readonly', False)]})
    smart_m_goals3 = fields.Text(readonly=True, states={'Start': [('readonly', False)]})
    smart_m_goals4 = fields.Text(readonly=True, states={'Start': [('readonly', False)]})
    care_plan1 = fields.Text(readonly=True, states={'Start': [('readonly', False)]})
    care_plan2 = fields.Text(readonly=True, states={'Start': [('readonly', False)]})
    care_plan3 = fields.Text(readonly=True, states={'Start': [('readonly', False)]})
    care_plan4 = fields.Text(readonly=True, states={'Start': [('readonly', False)]})
    referral_other_speciality = fields.Text(readonly=True, states={'Start': [('readonly', False)]})
    physician = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    physiotherapy = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    social_worker = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    nutritionist = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    respiratory = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})

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
    risk_for_falls_related_to_impaired_mobility = fields.Selection(yes_no_na, readonly=True,
                                                                   states={'Start': [('readonly', False)]})
    fall_risk_assessment_done = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    pressure_ulcer_altered_skin_integrity_related = fields.Selection(yes_no_na, readonly=True,
                                                                     states={'Start': [('readonly', False)]})
    complications_related_to_urinary_bowel_incontinence = fields.Selection(yes_no_na, readonly=True,
                                                                           states={'Start': [('readonly', False)]})

    press_measurable_goals_show = fields.Boolean()
    free_from_injury_related_to_falls = fields.Selection(yes_no_na, readonly=True,
                                                         states={'Start': [('readonly', False)]})
    free_from_skin_redness_blisters_or_discoloration = fields.Selection(yes_no_na, readonly=True,
                                                                        states={'Start': [('readonly', False)]})
    skin_will_be_clean_dry_with_appropriate_and_prompt = fields.Selection(yes_no_na, readonly=True,
                                                                          states={'Start': [('readonly', False)]})

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
    performed_hourly_turning = fields.Selection(competent_yes_no_na, readonly=True,
                                                states={'Start': [('readonly', False)]})
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

    care_follow_up_id = fields.One2many('sm.shifa.care.giver.follow.up', 'care_giver_id',
                                        string='care follow up')
    referral_id = fields.One2many('sm.shifa.referral', 'care_giver_ref_id', string='care referral')
    consent_show = fields.Boolean()
    consent_file1 = fields.Binary()
    consent_file2 = fields.Binary()

    @api.model
    def create(self, vals):
        vals['care_giver_code'] = self.env['ir.sequence'].next_by_code('care.giver')
        return super(CareGiver, self).create(vals)

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

    @api.onchange('systolic', 'temperature', 'bpm', 'respiratory_rate', 'osat', 'diastolic')
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
        if self.osat > 100:
            raise ValidationError("invalid Oxygen Saturation value")


class ShifaReferralInherit(models.Model):
    _inherit = 'sm.shifa.referral'

    care_giver_ref_id = fields.Many2one('sm.shifa.care.giver', string='care giver', ondelete='cascade')
