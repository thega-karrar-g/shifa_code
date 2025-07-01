from odoo import models, fields, api
import datetime
from odoo.exceptions import ValidationError
from datetime import date
from psycopg2._psycopg import List


class ComprehensiveNurse(models.Model):
    _name = 'sm.shifa.comprehensive.nurse'
    _description = 'Comprehensive Nurse'
    _rec_name = 'comprehensive_nurse_code'

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
    SERVICES = [
        ('G', 'General'),
        ('W', 'Wound'),
        ('C', 'Continence'),
        ('EF', 'Enteral Feeding'),
        ('DT', 'Drain Tube'),
        ('S', 'Stoma'),
        ('P', 'Palliative'),
        ('A', 'Anticoagulation'),
        ('D', 'Diabetic'),
        ('Pa', 'Parenteral'),

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
    yes_no = [
        ('Yes', 'Yes'),
        ('No', 'No'),
    ]
    form_list = [
        ('Wound', 'Wound'),
        ('Continence', 'Continence'),
        ('Enteral Feeding', 'Enteral Feeding'),
        ('Drain Tube', 'Drain Tube'),
        ('Stoma', 'Stoma'),
        ('Palliative', 'Palliative'),
        ('Anticoagulation', 'Anticoagulation'),
        ('Diabetic', 'Diabetic'),
        ('Parenteral', 'Parenteral'),
        ('Nebulization', 'Nebulization'),
        ('Newborn', 'Newborn'),
        ('Oxygen Administration', 'Oxygen Administration'),
        ('Pressure Ulcer', 'Pressure Ulcer'),
        ('Postnatal', 'Postnatal'),
        ('Trache', 'Trache'),
        ('Vaccines', 'Vaccines'),
    ]

    def _get_comprehensive(self):
        """Return default comprehensive value"""
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

    @api.onchange('phy_adm')
    def _onchange_join_antic(self):
        if self.phy_adm:
            self.nursing_comprehensive_ids = self.phy_adm
            self.physician_admission = self.phy_adm
            self.chief_complaint = self.phy_adm.chief_complaint
            self.provisional_diagnosis = self.phy_adm.provisional_diagnosis
            self.provisional_diagnosis_add_other = self.phy_adm.provisional_diagnosis_add_other
            self.provisional_diagnosis_add = self.phy_adm.provisional_diagnosis_add
            self.provisional_diagnosis_add_other2 = self.phy_adm.provisional_diagnosis_add_other2
            self.provisional_diagnosis_add2 = self.phy_adm.provisional_diagnosis_add2
            self.provisional_diagnosis_add_other3 = self.phy_adm.provisional_diagnosis_add_other3
            self.provisional_diagnosis_add3 = self.phy_adm.provisional_diagnosis_add3
            self.provisional_diagnosis_add_other4 = self.phy_adm.provisional_diagnosis_add_other4
            self.provisional_diagnosis_add4 = self.phy_adm.provisional_diagnosis_add4
            self.provisional_diagnosis_add_other5 = self.phy_adm.provisional_diagnosis_add_other5
            self.provisional_diagnosis_add5 = self.phy_adm.provisional_diagnosis_add5
            self.provisional_diagnosis_add_other6 = self.phy_adm.provisional_diagnosis_add_other6
            self.provisional_diagnosis_add6 = self.phy_adm.provisional_diagnosis_add6
            self.provisional_diagnosis_add_other7 = self.phy_adm.provisional_diagnosis_add_other7
            self.provisional_diagnosis_add7 = self.phy_adm.provisional_diagnosis_add7
            self.provisional_diagnosis_add_other8 = self.phy_adm.provisional_diagnosis_add_other8
            self.provisional_diagnosis_add8 = self.phy_adm.provisional_diagnosis_add8
            self.provisional_diagnosis_add_other9 = self.phy_adm.provisional_diagnosis_add_other9
            self.provisional_diagnosis_add9 = self.phy_adm.provisional_diagnosis_add9

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

    comprehensive_nurse_code = fields.Char('Reference', index=True, copy=False)
    patient = fields.Many2one('oeh.medical.patient', string='Patient', help="Patient Name", required=True,
                              readonly=False, states={'Discharged': [('readonly', False)]})
    hhc_appointment = fields.Many2one('sm.shifa.hhc.appointment', string='HHC-Appointment',
                                      readonly=False, states={'Discharged': [('readonly', False)]})
    doctor = fields.Many2one('oeh.medical.physician', string='Nurse', help="Current primary care / family doctor",
                             readonly=False, states={'Discharged': [('readonly', False)]},
                             domain=[('role_type', '=', ['HHCN', 'HN'])], required=True, default=_get_comprehensive)
    phy_adm = fields.Many2one('sm.shifa.physician.admission', string='Phy_Adm', readonly=False, states={'Discharged': [('readonly', False)]},
                              domain="[('patient', '=', patient), ('state', 'in', ('Admitted', 'Start','Draft'))]")
    state = fields.Selection(ADMISSION_STATES, string='State', default=lambda *a: 'Draft', readonly=True)
    weight = fields.Float(string='Weight', related='patient.weight')
    age = fields.Char(string='Age', related='patient.age')
    marital_status = fields.Selection(string='Marital Status', related='patient.marital_status')
    sex = fields.Selection(string='Sex', related='patient.sex')
    blood_type = fields.Selection(string='Blood Type', related='patient.blood_type')
    rh = fields.Selection(string='Rh', related='patient.rh')
    admission_date = fields.Datetime(string='Admission Date')
    discharge_date = fields.Datetime(string='Discharge Date')

    conscious_state_show = fields.Boolean()
    conscious_state = fields.Selection([
        ('Alert', 'Alert'),
        ('Response to Voice', 'Response to Voice'),
        ('Response to pain', 'Response to pain'),
        ('Unresponsive', 'Unresponsive'),
    ], readonly=False, states={'Discharged': [('readonly', False)]})
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
    ], readonly=False, states={'Discharged': [('readonly', False)]})
    scale_used = fields.Selection([
        ('Numerical', 'Numerical'),
        ('Faces', 'Faces'),
        ('FLACC', 'FLACC'),
        ('ABBEY', 'ABBEY'),
    ], readonly=False, states={'Discharged': [('readonly', False)]})
    functional_activity_show = fields.Boolean()
    functional_activity = fields.Selection([
        ('No Limitation', 'No Limitation'),
        ('Mild Limitation', 'Mild Limitation'),
        ('Severe Limitation', 'Severe Limitation'),
    ], readonly=False, states={'Discharged': [('readonly', False)]})

    vital_signs_show = fields.Boolean()
    systolic_bp = fields.Integer(readonly=False, states={'Discharged': [('readonly', False)]})
    hr_min = fields.Integer(readonly=False, states={'Discharged': [('readonly', False)]})
    diastolic_br = fields.Integer(readonly=False, states={'Discharged': [('readonly', False)]})
    rr_min = fields.Integer(readonly=False, states={'Discharged': [('readonly', False)]})
    temperature_c = fields.Float(readonly=False, states={'Discharged': [('readonly', False)]})
    # o2_sat = fields.Float(readonly=False, states={'Discharged': [('readonly', False)]})
    o2_sat = fields.Selection([
        ('at room air', 'at room air'),
        ('with oxygen Support', 'with oxygen Support')
    ], readonly=False, states={'Discharged': [('readonly', False)]})
    char_other_oxygen = fields.Float(readonly=False, states={'Discharged': [('readonly', False)]})
    # Assessment# Assessment# Assessment # Assessment # Assessment # Assessment # Assessment # Assessment
    diagnosis_show = fields.Boolean()
    # diagnosis = fields.Text(string='Diagnosis', readonly=True,
    #                         states={'Start': [('readonly', False)]})
    chief_complaint_show = fields.Boolean()
    chief_complaint = fields.Char(string="Chief Complaint", store=True, readonly=False, states={'Discharged': [('readonly', False)]})

    respiratory_show = fields.Boolean()
    airway = fields.Selection([
        ('Patent', 'Patent'),
        ('Dyspneic', 'Dyspneic'),
    ], default='Patent', readonly=False, states={'Discharged': [('readonly', False)]})
    # Breath Sounds:
    breath_sound_right_lung = fields.Selection(BREATH_SOUND, default='Clear',readonly=False, states={'Discharged': [('readonly', False)]})
    breath_sound_left_lung = fields.Selection(BREATH_SOUND, default='Clear', readonly=False, states={'Discharged': [('readonly', False)]})
    # Breath Pattern:
    breath_pattern = fields.Selection([
        ('Normal', 'Normal'),
        ('Dyspneic', 'Dyspneic'),
    ], default='Normal', readonly=False, states={'Discharged': [('readonly', False)]})
    # Air Entry:
    air_entry = fields.Selection([
        ('Normal', 'Normal'),
        ('Diminished', 'Diminished'),
    ], default='Normal', readonly=False, states={'Discharged': [('readonly', False)]})
    # ============== Skin/Circulation =============#
    # Skin/Circulation
    skin_circulation_show = fields.Boolean()
    skin_dry = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    skin_intact = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    skin_warm = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    skin_cool = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    # IV Cannula
    iv_size = fields.Float(readonly=False, states={'Discharged': [('readonly', False)]})
    location = fields.Char(readonly=False, states={'Discharged': [('readonly', False)]})
    # color
    skin_color = fields.Selection([
        ('Brown', 'Brown'),
        ('Black', 'Black'),
        ('Pale', 'Pale'),
        ('Red', 'Red'),
    ], default='Brown', readonly=False, states={'Discharged': [('readonly', False)]})
    # wound
    wound = fields.Char(readonly=False, states={'Discharged': [('readonly', False)]})
    # ==============  Pain Score Assessment =============#
    # Pain Score Assessment

    # ==============  Head and Neck Assessment =============#
    # Head and Neck Assessment
    # vision
    head_neck_show = fields.Boolean()
    vision = fields.Selection([
        ('Normal', 'Normal'),
        ('Blind', 'Blind'),
        ('Cataract', 'Cataract'),
    ], default='Normal', readonly=False, states={'Discharged': [('readonly', False)]})
    blind_eye = fields.Selection(EYE, readonly=False, states={'Discharged': [('readonly', False)]})
    cataract_eye = fields.Selection(EYE, readonly=False, states={'Discharged': [('readonly', False)]})
    # nose
    nose = fields.Selection([
        ('Normal', 'Normal'),
        ('Flaring', 'Flaring'),
        ('Discharges', 'Discharges'),
    ], default='Normal', readonly=False, states={'Discharged': [('readonly', False)]})
    # ear hearing
    hearing = fields.Selection([
        ('Normal', 'Normal'),
        ('Diminished', 'Diminished'),
        ('Loss', 'Loss'),
        ('Use of Aid', 'Use of Aid'),
    ], default='Normal', readonly=False, states={'Discharged': [('readonly', False)]})
    # mouth
    mouth = fields.Selection([
        ('Normal', 'Normal'),
        ('Bleeding', 'Bleeding'),
        ('Ulcer', 'Ulcer'),
        ('Odor', 'Odor'),
    ], default='Normal',readonly=False, states={'Discharged': [('readonly', False)]})
    # speech
    speech = fields.Selection([
        ('Normal', 'Normal'),
        ('Slurred', 'Slurred'),
        ('Aphasic', 'Aphasic'),
        ('Incoherent', 'Incoherent'),
    ], default='Normal', readonly=False, states={'Discharged': [('readonly', False)]})
    # Lips
    lips = fields.Selection([
        ('Normal', 'Normal'),
        ('Cracked', 'Cracked'),
        ('Dry', 'Dry'),
    ], default='Normal', readonly=False, states={'Discharged': [('readonly', False)]})
    # swallowing
    swallowing = fields.Selection([
        ('Normal', 'Normal'),
        ('Impaired ', 'Impaired'),
        ('Poor', 'Poor'),
    ], default='Normal', readonly=False, states={'Discharged': [('readonly', False)]})
    # gag reflex
    gag_reflex = fields.Selection([
        ('Normal', 'Normal'),
        ('Poor', 'Poor'),
    ], default='Normal', readonly=False, states={'Discharged': [('readonly', False)]})
    head_others = fields.Text(readonly=False, states={'Discharged': [('readonly', False)]})
    # ============== Chest and Respiratory Assessment =============#
    #      Appearance:
    chest_respiratory_show = fields.Boolean()
    app_normal = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    app_scoliosis = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    app_khyposis = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    app_draintube = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    app_scars = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    app_wound = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    # ==============  Abdomen Assessment =============#
    # Bowel Movement
    abnormal_show = fields.Boolean()
    bowel_movement = fields.Selection([
        ('Normal', 'Normal'),
        ('Abnormal', 'Abnormal'),
        ('Every Other Day', 'Every Other Day'),
    ], default='Normal', readonly=False, states={'Discharged': [('readonly', False)]})
    # bowel sounds
    bowel_sounds = fields.Selection([
        ('Nil', 'Nil'),
        ('Abnormal', 'Abnormal'),
        ('Active', 'Active'),
    ], readonly=False, states={'Discharged': [('readonly', False)]})
    # stoma:(Colostomy/Ileostomy)
    stoma_colostomy = fields.Selection([
        ('NA', 'NA'),
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    ], readonly=False, states={'Discharged': [('readonly', False)]})
    abdomen_other = fields.Char(readonly=False, states={'Discharged': [('readonly', False)]})
    # ============== Gastrointestinal Assessment =============#
    # feeding
    feeding_show = fields.Boolean()
    feeding = fields.Selection([
        ('Oral Feeding', 'Oral Feeding'),
        ('Tube Feeding', 'Tube Feeding'),
    ], readonly=False, states={'Discharged': [('readonly', False)]})

    #  Appetite
    appetite = fields.Selection(APPETITE_STATE, readonly=False, states={'Discharged': [('readonly', False)]})
    #  Nutritional Status
    nutritional_appetite = fields.Selection(APPETITE_STATE, readonly=False, states={'Discharged': [('readonly', False)]})
    # Diet
    diet = fields.Selection([
        ('Regular', 'Regular'),
        ('Diabetic', 'Diabetic'),
        ('Low Salt/Fat', 'Low Salt/Fat'),
        ('Low Salt', 'Low Salt'),
        ('Soft', 'Soft'),
        ('Others', 'Others'),
    ], readonly=False, states={'Discharged': [('readonly', False)]})
    diet_others = fields.Char(readonly=False, states={'Discharged': [('readonly', False)]})
    # Enteral Feeding
    enteral_feeding = fields.Selection([
        ('NGT', 'NGT'),
        ('NDT', 'NDT'),
        ('JOT', 'JOT'),
        ('GST', 'GST'),
    ], readonly=False, states={'Discharged': [('readonly', False)]})
    liquid_tube_feeding = fields.Selection([
        ('Mixing Diet', 'Mixing Diet'),
        ('Milk', 'Milk'),
        ('Formola', 'Formola'),
        ('Others', 'Others'),
    ], readonly=False, states={'Discharged': [('readonly', False)]})
    liquid_feeding_others = fields.Char(readonly=False, states={'Discharged': [('readonly', False)]})
    ef_amount = fields.Float(readonly=False, states={'Discharged': [('readonly', False)]})
    ef_frequency = fields.Float(readonly=False, states={'Discharged': [('readonly', False)]})
    # date and type
    feeding_date_inserted = fields.Date(readonly=False, states={'Discharged': [('readonly', False)]})
    feeding_tube_type = fields.Selection([
        ('Latex ', 'Latex'),
        ('Rubber', 'Rubber'),
        ('Silicon', 'Silicon'),
    ], readonly=False, states={'Discharged': [('readonly', False)]})
    feeding_tube_size = fields.Float(readonly=False, states={'Discharged': [('readonly', False)]})
    feeding_due_date = fields.Date(readonly=False, states={'Discharged': [('readonly', False)]})
    #      Renal Assessment  #
    renal_show = fields.Boolean()
    renal_voiding = fields.Selection([
        ('Normal ', 'Normal'),
        ('Incontinent', 'Incontinent'),
        ('Urosheath', 'Urosheath'),
        ('Superapubic', 'Superapubic'),
        ('IFC', 'IFC'),
    ], readonly=False, states={'Discharged': [('readonly', False)]})
    renal_tube_type = fields.Selection([
        ('Latex ', 'Latex'),
        ('Rubber', 'Rubber'),
        ('Silicon', 'Silicon'),
    ], readonly=False, states={'Discharged': [('readonly', False)]})
    renal_tube_size = fields.Float(readonly=False, states={'Discharged': [('readonly', False)]})
    renal_date_inserted = fields.Date(readonly=False, states={'Discharged': [('readonly', False)]})
    renal_due_date = fields.Date(readonly=False, states={'Discharged': [('readonly', False)]})
    renal_dysuria = fields.Selection(YES_NO, readonly=False, states={'Discharged': [('readonly', False)]})
    renal_hematuria = fields.Selection(YES_NO, readonly=False, states={'Discharged': [('readonly', False)]})
    renal_frequency = fields.Selection(YES_NO, readonly=False, states={'Discharged': [('readonly', False)]})
    renal_urine_color = fields.Selection([
        ('Normal ', 'Normal'),
        ('Abnormal', 'Abnormal'),
    ], readonly=False, states={'Discharged': [('readonly', False)]})
    renal_urine_clarity = fields.Selection([
        ('Clear ', 'Clear'),
        ('Cloudy', 'Cloudy'),
    ], readonly=False, states={'Discharged': [('readonly', False)]})
    renal_other = fields.Text(readonly=False, states={'Discharged': [('readonly', False)]})
    #      9th page tab Musculoskeletal Assessment  #
    musculoskeletal_show = fields.Boolean()
    movement = fields.Selection([
        ('Normal ', 'Normal'),
        ('Impaired', 'Impaired'),
        ('Bedridden', 'Bedridden'),
        ('Wheel chair', 'Wheel chair'),
    ], readonly=False, states={'Discharged': [('readonly', False)]})

    muscle_power_upper = fields.Selection(MUSCLE_POWER, readonly=False, states={'Discharged': [('readonly', False)]})
    muscle_power_lower = fields.Selection(MUSCLE_POWER, readonly=False, states={'Discharged': [('readonly', False)]})
    requires_assistant_ADLS = fields.Selection(YES_NO, readonly=False, states={'Discharged': [('readonly', False)]})
    requires_assistant_movement = fields.Selection(YES_NO, readonly=False, states={'Discharged': [('readonly', False)]})
    #   tab Risk Score  #
    fall_risk_score = fields.Selection(RISK_SCORE, readonly=False, states={'Discharged': [('readonly', False)]})
    braden_risk_score = fields.Selection(RISK_SCORE, readonly=False, states={'Discharged': [('readonly', False)]})
    actual_risks1 = fields.Text(readonly=False, states={'Discharged': [('readonly', False)]})
    actual_risks2 = fields.Text(readonly=False, states={'Discharged': [('readonly', False)]})
    actual_risks3 = fields.Text(readonly=False, states={'Discharged': [('readonly', False)]})
    actual_risks4 = fields.Text(readonly=False, states={'Discharged': [('readonly', False)]})
    smart_m_goals1 = fields.Text(readonly=False, states={'Discharged': [('readonly', False)]})
    smart_m_goals2 = fields.Text(readonly=False, states={'Discharged': [('readonly', False)]})
    smart_m_goals3 = fields.Text(readonly=False, states={'Discharged': [('readonly', False)]})
    smart_m_goals4 = fields.Text(readonly=False, states={'Discharged': [('readonly', False)]})
    care_plan1 = fields.Text(readonly=False, states={'Discharged': [('readonly', False)]})
    care_plan2 = fields.Text(readonly=False, states={'Discharged': [('readonly', False)]})
    care_plan3 = fields.Text(readonly=False, states={'Discharged': [('readonly', False)]})
    care_plan4 = fields.Text(readonly=False, states={'Discharged': [('readonly', False)]})
    referral_other_speciality = fields.Text(readonly=False, states={'Discharged': [('readonly', False)]})
    physician = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    physiotherapy = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    social_worker = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    nutritionist = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    respiratory = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    # Continence # Continence # Continence # Continence # Continence # Continence # Continence # Continence # Continence
    type_continence_show = fields.Boolean()
    bladder = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    bowel = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})

    type_devices_used_show = fields.Boolean()
    indwelling_foley = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    suprapubic_catheter = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    urosheath_condom = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    diaper = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})

    con_potential_actual_risk_show = fields.Boolean()
    impaired_skin_integrity_related_bowel_or_bladder = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    complications_related_indwelling_urinary_catheter = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})

    con_measurable_goals_show = fields.Boolean()
    will_remain_clean_dry_free_from_urinary_or_faecal = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    will_remain_free_signs_and_symptoms_of_complications = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})

    con_patient_assessment_show = fields.Boolean()
    color_urine = fields.Selection([
        ('Amber', 'Amber'),
        ('Light Yellow', 'Light Yellow'),
        ('Dark Yellow', 'Dark Yellow'),
        ('Cloudy', 'Cloudy'),
        ('Light Hematuria', 'Light Hematuria'),
        ('Gross Hematuria', 'Gross Hematuria'),
    ], readonly=False, states={'Discharged': [('readonly', False)]})
    con_consistency = fields.Selection([
        ('Clear', 'Clear'),
        ('With Blood Streak', 'With Blood Streak'),
        ('With Blood Clots', 'With Blood Clots'),
        ('With Sediments', 'With Sediments'),
    ], readonly=False, states={'Discharged': [('readonly', False)]})
    amount_ml = fields.Float(readonly=False, states={'Discharged': [('readonly', False)]})
    presence_urinary_frequency = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    diaper_changed = fields.Selection([
        ('2-3 times per day', '2-3 times per day'),
        ('3 times per day', '3 times per day'),
        ('3-4 times per day', '3-4 times per day'),
        ('4 times per day', '4 times per day'),
        ('4-5 times per day', '4-5 times per day'),
        ('NA', 'NA'),
    ], readonly=False, states={'Discharged': [('readonly', False)]})
    presence_burning = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    presence_foul_smelling = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    presence_altered_mental = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    catheter_still_required = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})

    urinaty_catheter_bag_show = fields.Boolean()
    secured_appropriately = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    bag_off_floor = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    bag_below_level = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    tubing_not_taut = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})

    catheter_change_show = fields.Boolean()
    catheter_change_done = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    type_of_catheter = fields.Selection([
        ('Silicone', 'Silicone'),
        ('Rubber/Latex', 'Rubber/Latex'),
        ('Condom', 'Condom'),
        ('Urosheath', 'Urosheath'),
        ('Suprapubic', 'Suprapubic'),
        ('Nephrostomy', 'Nephrostomy'),
    ], readonly=False, states={'Discharged': [('readonly', False)]})
    size_of_catheter = fields.Text(readonly=False, states={'Discharged': [('readonly', False)]})
    catheter_change_due_on = fields.Text(readonly=False, states={'Discharged': [('readonly', False)]})

    bowel_assessment_show = fields.Boolean()
    bowels_opened = fields.Selection([
        ('2 times daily', '2 times daily'),
        ('more than 5 times daily', 'more than 5 times daily'),
        ('more than 10 times daily', 'more than 10 times daily'),
        ('every 2 days', 'every 2 days'),
        ('every other day', 'every other day'),
        ('once a week', 'once a week'),
        ('Bowel not opened', 'Bowel not opened'),
    ], readonly=False, states={'Discharged': [('readonly', False)]})
    color_of_stool = fields.Selection([
        ('Brown', 'Brown'),
        ('Black', 'Black'),
        ('Reddish Brown', 'Reddish Brown'),
        ('Yellow', 'Yellow'),
        ('Green', 'Green'),
        ('Red', 'Red'),
    ], readonly=False, states={'Discharged': [('readonly', False)]})
    consistency_of_stool = fields.Selection([
        ('Hard', 'Hard'),
        ('Soft', 'Soft'),
        ('Loose', 'Loose'),
        ('Watery', 'Watery'),
        ('Mucoid', 'Mucoid'),
        ('NA', 'NA'),
    ], readonly=False, states={'Discharged': [('readonly', False)]})
    perineal_area = fields.Selection([
        ('Dry and intact', 'Dry and intact'),
        ('Excoriation', 'Excoriation'),
        ('Redness', 'Redness'),
        ('Blisters', 'Blisters'),
        ('NA', 'NA'),
    ], readonly=False, states={'Discharged': [('readonly', False)]})

    con_caregiver_assessment_show = fields.Boolean()
    maintain_patient_hygiene = fields.Selection([
        ('Well', 'Well'),
        ('Very Well', 'Very Well'),
        ('Yes', 'Yes'),
        ('No', 'No'),
        ('NA', 'NA'),
        ('Fair', 'Fair'),
        ('Poor', 'Poor'),
    ], readonly=False, states={'Discharged': [('readonly', False)]})
    use_incontinence_products = fields.Selection([
        ('Competent', 'Competent'),
        ('Yes', 'Yes'),
        ('No', 'No'),
        ('NA', 'NA'),
    ], readonly=False, states={'Discharged': [('readonly', False)]})
    keep_patient_odourless = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    ability_cope_care = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})

    con_patient_caregiver_education_show = fields.Boolean()
    patient_caregiver_should = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    maintain_fluids_high_fibre = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    drinking_least_litres_fluid = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    do_not_kink_clamp = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    always_attach_catheter = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    keep_closed_system_drainage = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    carers_should_wash_their = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    con_remarks_show = fields.Boolean()
    con_remarks = fields.Text(readonly=False, states={'Discharged': [('readonly', False)]})
    # Enternal Feeding # Enternal Feeding # Enternal Feeding # Enternal Feeding # Enternal Feeding # Enternal Feeding
    type_of_enteral_feeding_show = fields.Boolean()
    type_of_enteral_feeding = fields.Selection([
        ('Nasogastric Tube', 'Nasogastric Tube'),
        ('Gastrostomy Tube', 'Gastrostomy Tube'),
        ('Nasojejustomy', 'Nasojejustomy'),
        ('NA', 'NA'),
    ], readonly=False, states={'Discharged': [('readonly', False)]})
    feeding_regimen_show = fields.Boolean()
    feeding_regimen = fields.Selection([
        ('Bolus', 'Bolus'),
        ('Continuous', 'Continuous'),
    ], readonly=False, states={'Discharged': [('readonly', False)]})
    potential_actual_risk_show = fields.Boolean()
    potential_actual_complications_related = fields.Selection(yes_no_na,
                                                              readonly=False, states={'Discharged': [('readonly', False)]})
    potential_actual_risk_for_aspiration = fields.Selection(yes_no_na,
                                                            readonly=False, states={'Discharged': [('readonly', False)]})
    potential_actual_nutritional_status_changes = fields.Selection(yes_no_na,readonly=False, states={'Discharged': [('readonly', False)]})
    measurable_goals_show = fields.Boolean()
    measurable_goals_will_remain_free = fields.Selection(yes_no_na,
                                                         readonly=False, states={'Discharged': [('readonly', False)]})
    measurable_goals_will_maintain_adequate = fields.Selection(yes_no_na,
                                                               readonly=False, states={'Discharged': [('readonly', False)]})
    measurable_goals_will_not_develop = fields.Selection(yes_no_na,
                                                         readonly=False, states={'Discharged': [('readonly', False)]})
    ent_patient_assessment_show = fields.Boolean()
    patient_assessment_signs_of_aspiration = fields.Selection(yes_no_na,
                                                              readonly=False, states={'Discharged': [('readonly', False)]})
    patient_assessment_presence_of_bowel_sounds = fields.Selection(yes_no_na,readonly=False, states={'Discharged': [('readonly', False)]})
    patient_assessment_presence_of_constipation = fields.Selection(yes_no_na,readonly=False, states={'Discharged': [('readonly', False)]})
    patient_assessment_presence_of_diarrhoea = fields.Selection(yes_no_na,
                                                                readonly=False, states={'Discharged': [('readonly', False)]})
    patient_assessment_presence_nausea_vomiting = fields.Selection(yes_no_na,readonly=False, states={'Discharged': [('readonly', False)]})
    # patient_assessment_presence_abdominal_pain = fields.Selection(yes_no_na,
    #                                                               readonly=True,
    #                                                               states={'Start': [('readonly', False)]})
    patient_assessment_peg_tube_site = fields.Selection([
        ('Dry and Intact', 'Dry and Intact'),
        ('Excoriation', 'Excoriation'),
        ('Redness', 'Redness'),
        ('Blisters', 'Blisters'),
        ('Hypergranulation', 'Hypergranulation'),
        ('Leaking', 'Leaking'),
        ('NA', 'NA'),
    ], readonly=False, states={'Discharged': [('readonly', False)]})
    patient_assessment_facial_skin = fields.Selection([
        ('Dry and Intact', 'Dry and Intact'),
        ('Hypergranulation', 'Hypergranulation'),
        ('NA', 'NA'),
        ('Excoriation', 'Excoriation'),
        ('Redness', 'Redness'),
        ('Blisters', 'Blisters'),
    ], readonly=False, states={'Discharged': [('readonly', False)]})
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
    ], readonly=False, states={'Discharged': [('readonly', False)]})
    patient_assessment_frequency_of_feeds = fields.Selection([
        ('Continous', 'Continous'),
        ('4 hourly', '4 hourly'),
        ('Hourly', 'Hourly'),
    ], readonly=False, states={'Discharged': [('readonly', False)]})
    patient_assessment_daily_nutritional_intake = fields.Selection([
        ('NA', 'NA'),
        ('Adequate', 'Adequate'),
        ('InAdequate', 'InAdequate'),
    ], readonly=False, states={'Discharged': [('readonly', False)]})
    patient_assessment_weight_change = fields.Selection([
        ('No Change', 'No Change'),
        ('Decrease', 'Decrease'),
        ('Increase', 'Increase'),
        ('NA', 'NA'),
    ], readonly=False, states={'Discharged': [('readonly', False)]})
    patient_assessment_change_nutritional_status = fields.Selection([
        ('No Change', 'No Change'),
        ('Positive Change', 'Positive Change'),
        ('Negative Change', 'Negative Change'),
    ], readonly=False, states={'Discharged': [('readonly', False)]})
    patient_assessment_nutritional_status = fields.Selection([
        ('Good', 'Good'),
        ('Fair', 'Fair'),
        ('Poor', 'Poor'),
        ('Cachexic', 'Cachexic'),
        ('Dehydrated', 'Dehydrated'),
        ('Emaciated', 'Emaciated'),
    ], readonly=False, states={'Discharged': [('readonly', False)]})
    patient_assessment_physical_apearance = fields.Selection([
        ('Adequately Nourished ', 'Adequately Nourished '),
        ('Malnourished', 'Malnourished'),
        ('At Risk of Malnutrition', 'At Risk of Malnutrition'),
        ('Obese', 'Obese'),
        ('NA', 'NA'),
    ], readonly=False, states={'Discharged': [('readonly', False)]})
    patient_assessment_refer_to_Dietician = fields.Selection(yes_no_na,
                                                             readonly=False, states={'Discharged': [('readonly', False)]})

    tube_change_show = fields.Boolean()
    tube_change_tube_change_done = fields.Selection(yes_no_na,
                                                    readonly=False, states={'Discharged': [('readonly', False)]})
    tube_change_type_of_tube = fields.Selection([
        ('Ryles', 'Ryles'),
        ('Silicone', 'Silicone'),
        ('PEG', 'PEG'),
        ('NA', 'NA'),
    ], readonly=False, states={'Discharged': [('readonly', False)]})
    tube_change_presence_gastric_residual_volume_checked = fields.Selection([
        ('Yes', 'Yes'),
        ('Nil', 'Nil'),
        ('NA', 'NA'),
    ], readonly=False, states={'Discharged': [('readonly', False)]})
    tube_change_gastric_ph_result = fields.Selection([
        ('less than 4.5', 'less than 4.5'),
        ('between 4.5 -5.5', 'between 4.5 -5.5'),
        ('Nil', 'Nil'),
        ('NA', 'NA'),
    ], readonly=False, states={'Discharged': [('readonly', False)]})
    tube_change_gastric_ph_checked = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    tube_change_initiate_feeding = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    tube_change_internal_ngt = fields.Integer(readonly=False, states={'Discharged': [('readonly', False)]})
    tube_change_external_ngt = fields.Integer(readonly=False, states={'Discharged': [('readonly', False)]})
    tube_change_ngt_size = fields.Float(readonly=False, states={'Discharged': [('readonly', False)]})
    tube_change_consent_signed_by = fields.Text(readonly=False, states={'Discharged': [('readonly', False)]})
    tube_change_next_due = fields.Date(readonly=False, states={'Discharged': [('readonly', False)]})

    ent_caregiver_assessment_show = fields.Boolean()
    caregiver_assessment_perform_tube_placement = fields.Selection(competent_no_na,readonly=False, states={'Discharged': [('readonly', False)]})
    caregiver_assessment_perform_enteral_feeding = fields.Selection(competent_no_na,readonly=False, states={'Discharged': [('readonly', False)]})
    caregiver_assessment_perform_gastrostomy_site = fields.Selection(yes_no_na_competent,readonly=False, states={'Discharged': [('readonly', False)]})
    caregiver_assessment_perform_mouth_care = fields.Selection(yes_no_na_competent,readonly=False, states={'Discharged': [('readonly', False)]})

    caregiver_education_show = fields.Boolean()
    caregiver_education_wash_hands_thoroughly = fields.Selection(yes_no_na,
                                                                 readonly=False, states={'Discharged': [('readonly', False)]})
    caregiver_education_check_the_placement = fields.Selection(yes_no_na,
                                                               readonly=False, states={'Discharged': [('readonly', False)]})
    caregiver_education_raise_the_head = fields.Selection(yes_no_na,
                                                          readonly=False, states={'Discharged': [('readonly', False)]})
    caregiver_education_inform_home_care = fields.Selection(yes_no_na,
                                                            readonly=False, states={'Discharged': [('readonly', False)]})
    caregiver_education_reemphasize_education = fields.Selection(yes_no_na,
                                                                 readonly=False, states={'Discharged': [('readonly', False)]})
    ent_remarks_show = fields.Boolean()
    ent_remarks = fields.Text(readonly=False, states={'Discharged': [('readonly', False)]})
    # Drain Tub # Drain Tub # Drain Tub # Drain Tub # Drain Tub # Drain Tub # Drain Tub # Drain Tub # Drain Tub # Drain Tub
    type_of_surgery_procedure_show = fields.Boolean()
    type_of_surgery_procedure = fields.Text(readonly=False, states={'Discharged': [('readonly', False)]})

    type_of_drain_catheter_show = fields.Boolean()
    drain_catheter_pleurx = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    drain_catheter_pigtail = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    drain_catheter_jackson_pratts = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    drain_catheter_other = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    drain_catheter_other_text = fields.Text(readonly=False, states={'Discharged': [('readonly', False)]})

    location_show = fields.Boolean()
    location_chest = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    location_abdomen = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    location_other = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    location_other_text = fields.Text(readonly=False, states={'Discharged': [('readonly', False)]})

    type_of_drainage_show = fields.Boolean()
    type_drainage_free_drainage = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    type_drainage_vacuum = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    type_drainage_other = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    type_drainage_other_text = fields.Text(readonly=False, states={'Discharged': [('readonly', False)]})

    dra_potential_actual_risk_show = fields.Boolean()
    drain_site_infection_other = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    seroma_formation_other = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    dislodgement_of_drain_tube_other = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})

    dra_measurable_goals_show = fields.Boolean()
    drain_site_will_remain_free_from_infection = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    drainage_system_will_remain_patent_with = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    drain_tube_will_be_removed_if_less_than_mls = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    drain_remains_insitu_and_drainage_done_as = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})

    dra_patient_assessment_show = fields.Boolean()
    vital_signs_remain_within = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    patient_pain_under_control = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    performing_arm_exercises = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})

    drain_tube_site_assessment_show = fields.Boolean()
    dressing_dry_and_intact = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    presence_drain_site_infection = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    presence_of_leakage = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    nature_of_drainage = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    drainage_amount_last_24hrs = fields.Text(readonly=False, states={'Discharged': [('readonly', False)]})
    drain_tube_removed = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})

    dra_patient_caregiver_education_show = fields.Boolean()
    patient_understands_importance = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    actions_to_take_if_leaking = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    understands_when_suction = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    taking_analgesia_regularly = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    measuring_and_recording_drainage = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    report_increase_of_temperature_change = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    discharge_education_post_removal = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    self_drainage_procedure = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    dra_remarks_show = fields.Boolean()
    dra_remarks = fields.Text(readonly=False, states={'Discharged': [('readonly', False)]})
    # Stoma # Stoma  # Stoma # Stoma # Stoma # Stoma # Stoma # Stoma # Stoma # Stoma # Stoma # Stoma # Stoma # Stoma # Stoma
    type_surgery_show = fields.Boolean()
    type_surgery = fields.Text(readonly=False, states={'Discharged': [('readonly', False)]})

    sto_patient_assessment_show = fields.Boolean()
    vital_signs_remain = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    coping_with_changing = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    managing_skin = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})

    stoma_site_assessment_show = fields.Boolean()
    stoma_appliance_intact = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    presence_of_skin = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    nature_of_effluent = fields.Selection([
        ('Stool', 'Stool'),
        ('Urine', 'Urine'),
        ('Blood', 'Blood'),
        ('Bile', 'Bile'),
        ('Nil', 'Nil'),
    ], readonly=False, states={'Discharged': [('readonly', False)]})
    amount = fields.Integer(readonly=False, states={'Discharged': [('readonly', False)]})
    sto_consistency = fields.Selection([
        ('Hard', 'Hard'),
        ('Soft', 'Soft'),
        ('Loose', 'Loose'),
    ], readonly=False, states={'Discharged': [('readonly', False)]})

    follow_up_care_show = fields.Boolean()
    stoma_care_clinic = fields.Text(readonly=False, states={'Discharged': [('readonly', False)]})
    review_dates = fields.Text(readonly=False, states={'Discharged': [('readonly', False)]})

    sto_patient_caregiver_education_show = fields.Boolean()
    choose_outfit = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    eating_regular_ = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    drink_reqularly = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    observe_for_stomal = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    sto_remarks_show = fields.Boolean()
    sto_remarks = fields.Text(readonly=False, states={'Discharged': [('readonly', False)]})
    # Palliative
    palliative_care_type_show = fields.Boolean()
    pall_pain_management = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    symptom_management = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    subcutaneous_infusion = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    palliative_other = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    palliative_other_text = fields.Text(readonly=False, states={'Discharged': [('readonly', False)]})

    pall_potential_actual_risk_show = fields.Boolean()
    pain_related_to_disease_process = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    ineffective_pain_management = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    nutritional_deficit_related_to_poor_oral = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    nausea_and_or_vomiting_related_to_medication = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    constipation_related_to_medication_immobility_decrease = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    breathlessness_related_to_disease_process = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    psychosocial_issues_related_terminal_prognosis = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})

    pall_measurable_goals_show = fields.Boolean()
    will_maintain_adequate_level_of_comfort_as_evidenced_no_signs = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    verbalizing_relief_pain_with_ordered_medications = fields.Selection(yes_no_na,readonly=False, states={'Discharged': [('readonly', False)]})
    will_function_at_optimal_level_within_limitations_imposed = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    verbalizing_satisfaction_with_level_of_comfort = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    will_demonstrate_adjustment_to_of_life_situation_by_verbally = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    expressing_through_words_or_actions_understanding_of_what = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})

    pall_patient_assessment_show = fields.Boolean()
    pall_presence_of_pain = fields.Selection(yes_no, readonly=False, states={'Discharged': [('readonly', False)]})
    pain_relieve_with_medication = fields.Selection(yes_no, readonly=False, states={'Discharged': [('readonly', False)]})
    presence_of_nausea = fields.Selection(yes_no, readonly=False, states={'Discharged': [('readonly', False)]})
    presence_of_vomiting = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    presence_of_constipation = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    frequency = fields.Selection([
        ('Once', 'Once'),
        ('2-3 times per day', '2-3 times per day'),
        ('more than 4 times/dav', 'more than 4 times/dav'),
    ], readonly=False, states={'Discharged': [('readonly', False)]})

    narcotics_show = fields.Boolean()
    regular_dose = fields.Text(readonly=False, states={'Discharged': [('readonly', False)]})
    breakthrough_dose = fields.Text(readonly=False, states={'Discharged': [('readonly', False)]})
    no_of_breakthrough_dose = fields.Text(readonly=False, states={'Discharged': [('readonly', False)]})
    narcotic_supply_enough_till = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No'),
        ('For refill', 'For refill'),
    ], readonly=False, states={'Discharged': [('readonly', False)]})

    pall_caregiver_assessment_show = fields.Boolean()
    management_of_patient_pain = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    management_of_patient_nutrition = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    coping_psychologically = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    pall_coping_with_patient_care = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})

    pall_patient_caregiver_education_show = fields.Boolean()
    ensure_that_patient_taking_analgesia = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    ensure_that_there_sufficient_pain = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    advice_activity_movement_hour_after = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    advise_increase_fluids_tolerated = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    advice_take_stool_softeners_for_constipation = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    encourage_mobility_tolerated = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    take_anti_emetics_minutes_before = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    take_small_frequent_meals = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    pall_remarks_show = fields.Boolean()
    pall_remarks = fields.Text(readonly=False, states={'Discharged': [('readonly', False)]})
    # Anticoagulation # Anticoagulation # Anticoagulation # Anticoagulation # Anticoagulation # Anticoagulation # Anticoag
    type_of_anticoagulation_show = fields.Boolean()
    type_warfarin = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    type_other = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    type_other_text = fields.Text(readonly=False, states={'Discharged': [('readonly', False)]})

    frequency_inr_monitoring_show = fields.Boolean()
    frequency_daily = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    frequency_weekly = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    frequency_as_pre_primary = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    frequency_bimonthly = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    frequency_other = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    frequency_other_text = fields.Text(readonly=False, states={'Discharged': [('readonly', False)]})

    ant_potential_actual_risk_show = fields.Boolean()
    potential_for_complication_injury_related_anti_coagulation = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    over_or_under_anticoagulation_related_to_non_compliance = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    over_or_under_therapeutic_level_inr_related_to_non_compliance = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    medication_error_related_to_inappropriate_taking_of_warfarin = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})

    ant_measurable_goals_show = fields.Boolean()
    will_be_remain_free_from_complications_bleeding_injury = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    inr_will_be_within_therapeutic_level = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    patient_will_be_compliant_with_taking_warfarin = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    there_will_be_no_medication_error_related_to_taking = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})

    ant_patient_assessment_show = fields.Boolean()
    vital_signs_normal = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    any_change_in_diet = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    develop_any_infection_that = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    presence_of_chest_pain = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    presence_of_short_of_breath = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    presence_of_bleeding = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    presence_of_bruising = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})

    medication_review_show = fields.Boolean()
    taken_warfarin_dose = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    any_new_medication_commenced = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    enough_appropriate_warfarin = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    started_on_antibiotics = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    ensure_that_patient_taking = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})

    ant_caregiver_assessment_show = fields.Boolean()
    administer_correct_warfarin_dose_since = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    understand_dosing_regime = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    medication_storage_appropriately = fields.Selection(yes_no_na,readonly=False, states={'Discharged': [('readonly', False)]})
    one_reliable_family_member = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    caregiver_name_identified = fields.Text(readonly=False, states={'Discharged': [('readonly', False)]})

    ant_patient_caregiver_education_show = fields.Boolean()
    warfarin_tablets_to_be_given = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    to_report_missed_dose = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    check_with_home_care_staff_before = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    to_observe_for_any_bleeding = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    correct_technique_in_performing = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    rotate_injection_sites = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    ant_remarks_show = fields.Boolean()
    ant_remarks = fields.Text(readonly=False, states={'Discharged': [('readonly', False)]})
    # Diabetic # Diabetic # Diabetic # Diabetic # Diabetic # Diabetic # Diabetic # Diabetic # Diabetic # Diabetic
    type_hypoglycemic_show = fields.Boolean()
    oral = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    injection = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    oral_medication = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    oral_other = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    oral_other_text = fields.Text(readonly=False, states={'Discharged': [('readonly', False)]})
    injection_medication = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    injection_units = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    injection_other = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    injection_other_text = fields.Text(readonly=False, states={'Discharged': [('readonly', False)]})

    dia_potential_actual_risk_show = fields.Boolean()
    hyper_hypoglycemia_related_to_diabetes_mellitus = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    other_complications_related_to_diabetes_mellitus = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})

    dia_measurable_goals_show = fields.Boolean()
    complications_related_to_diabetes_mellitus = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    maintain_blood_sugar_level_within_acceptable = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    blood_sugar_levels_are_monitored_and_recorded = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})

    dia_patient_assessment_show = fields.Boolean()
    dia_vital_signs_within_normal = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    skin_integrity_intact = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    blood_sugar_level = fields.Integer(readonly=False, states={'Discharged': [('readonly', False)]})
    mmol_mmol_bolin = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    mg_di_bolin = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    mmol_mmol = fields.Selection([
        ('Pre Meal', 'Pre Meal'),
        ('Post Meal', 'Post Meal'),
        ('2 hrs Post Meal', '2 hrs Post Meal'),
        ('4 hrs Post Meal', '4 hrs Post Meal'),
    ], readonly=False, states={'Discharged': [('readonly', False)]})
    blood_sugar_control = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})

    nutrition_show = fields.Boolean()
    specific_dietary_needs = fields.Selection([
        ('Normal', 'Normal'),
        ('Soft', 'Soft'),
        ('Liquid', 'Liquid'),
        ('Diabetic', 'Diabetic'),
        ('Enteral', 'Enteral'),
    ], readonly=False, states={'Discharged': [('readonly', False)]})
    observing_dietary_intake = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    physical_appearance = fields.Selection([
        ('Adequately Nourished', 'Adequately Nourished'),
        ('Malnourished', 'Malnourished'),
        ('At Risk of Malnutrition', 'At Risk of Malnutrition'),
        ('NA', 'NA'),
    ], readonly=False, states={'Discharged': [('readonly', False)]})

    medication_show = fields.Boolean()
    diabetic_medication_discussed = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    compliant_medication_regimen = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    medication_review_done = fields.Text(readonly=False, states={'Discharged': [('readonly', False)]})

    dia_patient_caregiver_education_show = fields.Boolean()
    ensure_that_patient_monitors = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    patient_taking_appropriate = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    check_feet_daily_any = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    encourages_activities = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    aware_of_managing_hypoglycaemic_event = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    dia_remarks_show = fields.Boolean()
    dia_remarks = fields.Text(readonly=False, states={'Discharged': [('readonly', False)]})
    # Parenteral
    parenteral_route_show = fields.Boolean()
    peripheral_intravenous_cannula = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    p_i_c_c_line = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    central_catheter = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    subcutaneous = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    intramuscular = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    portacath = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    parenteral_other = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    parenteral_other_text = fields.Text(readonly=False, states={'Discharged': [('readonly', False)]})

    par_potential_actual_risk_show = fields.Boolean()
    complications_related_to_parenteral_therapy = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    complications_related_to_parenteral_medications = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    local_irritation_inflammation_or_infection_related = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})

    par_measurable_goals_show = fields.Boolean()
    parenteral_device_remains_functional_as_evidence_by = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    no_parenteral_site_infection_as_evidence_by_site_free = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    no_systemic_infection_related_to_parenteral_site = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})

    par_patient_assessment_show = fields.Boolean()
    par_vital_signs_within_normal = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    general_condition_improved = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    par_presence_of_pain = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    signs_of_phlebitis = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})

    catheter_site_assessment_show = fields.Boolean()
    leakage_from_site = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    site_dressing_attended = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    device_resited = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    p_i_line_exposed_tube_daily = fields.Float(readonly=False, states={'Discharged': [('readonly', False)]})

    infusion_device_show = fields.Boolean()
    correct_infusion_administered = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    parameters_updated = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    infusion_therapy_started = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    batteries_changed_checked = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})

    par_caregiver_assessment_show = fields.Boolean()
    par_coping_with_patient_care = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    able_to_troubleshoot_device = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    care_of_parenteral_site = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    compliant_to_education = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})

    par_patient_caregiver_education_show = fields.Boolean()
    aware_of_action_and_side_effects = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    care_iv_access_at_home_during = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    par_pain_management = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    advice_on_activity_tolerated = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    trouble_shoot_infusion_device = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    to_inform_home_care_when_parenteral_site = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    par_remarks_show = fields.Boolean()
    par_remarks = fields.Text(readonly=False, states={'Discharged': [('readonly', False)]})
    # Wound tab
    wound_history_show = fields.Boolean()
    wound_history = fields.Text(string='Wound History', readonly=False, states={'Discharged': [('readonly', False)]})
    # Type of Wound fields
    type_wound_show = fields.Boolean()
    surgical = fields.Boolean(string='Surgical', readonly=False, states={'Discharged': [('readonly', False)]})
    pressure_ulcer = fields.Boolean(string='Pressure Ulcer', readonly=False, states={'Discharged': [('readonly', False)]})
    diabetic = fields.Boolean(string='Diabetic', readonly=False, states={'Discharged': [('readonly', False)]})
    other_types = fields.Boolean(string='Other', readonly=False, states={'Discharged': [('readonly', False)]})
    other_types_content = fields.Char(readonly=False, states={'Discharged': [('readonly', False)]})

    # Factors Influencing Wound Healing
    factors_influencing_show = fields.Boolean()
    diabetes = fields.Boolean(string='Diabetes', readonly=False, states={'Discharged': [('readonly', False)]})
    immobility = fields.Boolean(string='Immobility', readonly=False, states={'Discharged': [('readonly', False)]})
    tissue_perfusion = fields.Boolean(string='Tissue perfusion', readonly=False, states={'Discharged': [('readonly', False)]})
    infection = fields.Boolean(string='Infection', readonly=False, states={'Discharged': [('readonly', False)]})

    incontinence = fields.Boolean(string='Incontinence', readonly=False, states={'Discharged': [('readonly', False)]})
    malnutrition = fields.Boolean(string='Malnutrition', readonly=False, states={'Discharged': [('readonly', False)]})
    immnuno_compromised = fields.Boolean(string='Immnuno compromised', readonly=False, states={'Discharged': [('readonly', False)]})
    blood_related = fields.Boolean(string='Blood related', readonly=False, states={'Discharged': [('readonly', False)]})
    blood_related_content = fields.Char(readonly=False, states={'Discharged': [('readonly', False)]})
    other_factors = fields.Boolean(string='Other', readonly=False, states={'Discharged': [('readonly', False)]})
    other_factors_content = fields.Char(readonly=False, states={'Discharged': [('readonly', False)]})

    # Potential Risk
    potential_risk_show = fields.Boolean()
    infection_potential = fields.Boolean(string='Infection', readonly=False, states={'Discharged': [('readonly', False)]})
    Poor_healing = fields.Boolean(string='Poor healing', readonly=False, states={'Discharged': [('readonly', False)]})
    other_potential = fields.Boolean(string='Other', readonly=False, states={'Discharged': [('readonly', False)]})
    other_potential_content = fields.Char(readonly=False, states={'Discharged': [('readonly', False)]})

    # Measurable Goals
    wound_measurable_goals_show = fields.Boolean()
    free_signs_infection = fields.Boolean(string='Free from signs of infection', readonly=False, states={'Discharged': [('readonly', False)]})
    increase_area_granulating_tissue = fields.Boolean(string='Increase in area granulating tissue',readonly=False, states={'Discharged': [('readonly', False)]})
    free_skin_excoriation = fields.Boolean(string='Free from skin excoriation', readonly=False, states={'Discharged': [('readonly', False)]})
    free_necrosis = fields.Boolean(string='Free from necrosis', readonly=False, states={'Discharged': [('readonly', False)]})
    # Annotation image
    annotation_image_show = fields.Boolean()
    annotation_image = fields.Binary(readonly=False, states={'Discharged': [('readonly', False)]})
    # wound assessment and dressing plan
    wound_assessment_dressing_show = fields.Boolean()
    add_new_wound_assessment = fields.Boolean()
    add_new_wound_assessment_date = fields.Date(string='Date', readonly=True,
                                                states={'Admitted': [('readonly', False)]})
    add_other_wound_assessment = fields.Boolean()
    add_other_wound_assessment_date = fields.Date(string='Date', readonly=True,
                                                  states={'Admitted': [('readonly', False)]})

    comprehensive_follow_up_id = fields.One2many('sm.shifa.comprehensive.nurse.follow.up', 'comprehensive_nurse_id',
                                                 string='comprehensive follow up')
    referral_id = fields.One2many('sm.shifa.referral', 'comprehensive_nurse_ref_id', string='comprehensive referral')
    wound_ids = fields.One2many('sm.shifa.wound.assessment.values', 'wound_comp_id', string='Wound Assessment')

    wound_add = fields.One2many('sm.shifa.wound.assessment.values', 'wound_comp_id', string='Wound Assessment')
    wound_new_add = fields.One2many('sm.shifa.wound.assessment.values', 'wound_comp_id', string='Wound Assessment')

    nursing_comprehensive_ids = fields.Many2one('sm.shifa.physician.admission', string='Nurse', ondelete='cascade')
    no_complication_of_pulmonary_micro_embolism = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    apply_warm_compress_to_injection_site = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    blood_test_done = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    nurse_assessment_show = fields.Boolean()
    nurse_note_assessment = fields.Text()
    nurse_wound_show = fields.Boolean()
    nurse_note_wound = fields.Text()
    service_name = fields.Selection(SERVICES, readonly=False, states={'Discharged': [('readonly', False)]}, default='G')
    service = fields.Many2one('sm.shifa.service', string='First Service', required=True,
                              domain=[('show', '=', True), ('service_type', 'in',
                                                            ['HHC', 'FUPH', 'L', 'WBSDFC', 'R', 'LP', 'GCP', 'MH',
                                                             'IVT', 'SM', 'V', 'Car',
                                                              'Diab', 'HVD'])],
                              readonly=False, states={'Discharged': [('readonly', False)]})

    service_type = fields.Selection(string='Service type', related='service.service_type', readonly=True, store=False)

    service_2 = fields.Many2one('sm.shifa.service', string='Second Service',
                                domain=[('show', '=', True), ('service_type', 'in',
                                                              ['HHC', 'FUPH', 'L', 'WBSDFC', 'R', 'LP', 'GCP', 'MH',
                                                               'IVT', 'SM', 'V', 'Car',
                                                               'PHY', 'Diab', 'HVD'])],
                                readonly=False, states={'Discharged': [('readonly', False)]})

    service_3 = fields.Many2one('sm.shifa.service', string='Third Service',
                                domain=[('show', '=', True), ('service_type', 'in',
                                                              ['HHC', 'FUPH', 'L', 'WBSDFC', 'R', 'LP', 'GCP', 'MH',
                                                               'IVT', 'SM', 'V', 'Car',
                                                               'PHY', 'Diab', 'HVD'])],
                                readonly=True, states={'Draft': [('readonly', False)]})
    provisional_diagnosis = fields.Many2one('oeh.medical.pathology', string='Disease', readonly=False, states={'Discharged': [('readonly', False)]})
    provisional_diagnosis_add_other = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    provisional_diagnosis_add = fields.Many2one('oeh.medical.pathology', string='Disease',readonly=False, states={'Discharged': [('readonly', False)]})
    provisional_diagnosis_add_other2 = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    provisional_diagnosis_add2 = fields.Many2one('oeh.medical.pathology', string='Disease', readonly=False, states={'Discharged': [('readonly', False)]})
    provisional_diagnosis_add_other3 = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    provisional_diagnosis_add3 = fields.Many2one('oeh.medical.pathology', string='Disease', readonly=False, states={'Discharged': [('readonly', False)]})

    provisional_diagnosis_add_other4 = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    provisional_diagnosis_add4 = fields.Many2one('oeh.medical.pathology', string='Disease', readonly=False, states={'Discharged': [('readonly', False)]})
    provisional_diagnosis_add_other5 = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    provisional_diagnosis_add5 = fields.Many2one('oeh.medical.pathology', string='Disease', readonly=False, states={'Discharged': [('readonly', False)]})
    provisional_diagnosis_add_other6 = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    provisional_diagnosis_add6 = fields.Many2one('oeh.medical.pathology', string='Disease', readonly=False, states={'Discharged': [('readonly', False)]})
    provisional_diagnosis_add_other7 = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    provisional_diagnosis_add7 = fields.Many2one('oeh.medical.pathology', string='Disease', readonly=False, states={'Discharged': [('readonly', False)]})
    provisional_diagnosis_add_other8 = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    provisional_diagnosis_add8 = fields.Many2one('oeh.medical.pathology', string='Disease', readonly=False, states={'Discharged': [('readonly', False)]})
    provisional_diagnosis_add_other9 = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    provisional_diagnosis_add9 = fields.Many2one('oeh.medical.pathology', string='Disease', readonly=False, states={'Discharged': [('readonly', False)]})
    consent_show = fields.Boolean()
    consent_file1 = fields.Binary()
    consent_file2 = fields.Binary()
    # multidisciplinary_show = fields.Boolean()
    # multidisciplinary_file1 = fields.Binary()
    # multidisciplinary_file2 = fields.Binary()
    # multidisciplinary_file3 = fields.Binary()
    forms_show = fields.Boolean()
    Wound_show = fields.Boolean()
    Continence_show = fields.Boolean()
    Enteral_Feeding_show = fields.Boolean()
    Drain_Tube_show = fields.Boolean()
    Stoma_show = fields.Boolean()
    Palliative_show = fields.Boolean()
    Anticoagulation_show = fields.Boolean()
    Diabetic_show = fields.Boolean()
    Parenteral_show = fields.Boolean()
    Nebulization_show = fields.Boolean()
    Newborn_show = fields.Boolean()
    Oxygen_Administration_show = fields.Boolean()
    Pressure_Ulcer_show = fields.Boolean()
    Postnatal_show = fields.Boolean()
    Trache_show = fields.Boolean()
    Vaccines_show = fields.Boolean()
    Forms = fields.Selection(form_list , string='Forms')
    # Nebulization tab

    potential_acual_risk_show = fields.Boolean()
    risk_for_faster_heartbeat = fields.Selection(yes_no, readonly=False, states={'Discharged': [('readonly', False)]})
    risk_for_slightly_shaking_muscles = fields.Selection(yes_no, readonly=False, states={'Discharged': [('readonly', False)]})

    measurable_goals_review_date_show = fields.Boolean()
    fast_relief_from_inflammation_and_allowing = fields.Selection(yes_no, readonly=False, states={'Discharged': [('readonly', False)]})

    patient_assessment_show = fields.Boolean()
    has_productive_cough = fields.Selection(yes_no, readonly=False, states={'Discharged': [('readonly', False)]})
    obvious_nasal_flaring_shortness_breath = fields.Selection(yes_no, readonly=False, states={'Discharged': [('readonly', False)]})
    breathing_easier_after_nebulization = fields.Selection(yes_no, readonly=False, states={'Discharged': [('readonly', False)]})

    patient_caregiver_education_show = fields.Boolean()
    lifestyle_changes_treat_shortness_breath = fields.Selection(yes_no, readonly=False, states={'Discharged': [('readonly', False)]})
    educate_deep_breathing_exercises = fields.Selection(yes_no, readonly=False, states={'Discharged': [('readonly', False)]})
    avoiding_exposure_pollutants_allergens = fields.Selection(yes_no, readonly=False, states={'Discharged': [('readonly', False)]})
    comply_medication_prescribed = fields.Selection(yes_no, readonly=False, states={'Discharged': [('readonly', False)]})

    remarks_show = fields.Boolean()
    remarks = fields.Text(states={'Start': [('readonly', False)]})

    # newborn tab
    clinical_assessments_show = fields.Boolean()
    head_normal = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    head_abnormal = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    head_abnormal_content = fields.Char(readonly=False, states={'Discharged': [('readonly', False)]})
    skin_normal = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    skin_abnormal = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    skin_abnormal_content = fields.Char(readonly=False, states={'Discharged': [('readonly', False)]})
    lunge_normal = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    lunge_abnormal = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    lunge_abnormal_content = fields.Char(readonly=False, states={'Discharged': [('readonly', False)]})
    chest_normal = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    chest_abnormal = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    chest_abnormal_content = fields.Char(readonly=False, states={'Discharged': [('readonly', False)]})
    abdomen_normal = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    abdomen_abnormal = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    abdomen_abnormal_content = fields.Char(readonly=False, states={'Discharged': [('readonly', False)]})
    elimination_normal = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    elimination_abnormal = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    elimination_abnormal_content = fields.Char(readonly=False, states={'Discharged': [('readonly', False)]})
    genitalia_normal = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    genitalia_abnormal = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    genitalia_abnormal_content = fields.Char(readonly=False, states={'Discharged': [('readonly', False)]})
    extremities_normal = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    extremities_abnormal = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    extremities_abnormal_content = fields.Char(readonly=False, states={'Discharged': [('readonly', False)]})
    number_of_diaper_per_day = fields.Integer(readonly=False, states={'Discharged': [('readonly', False)]})
    number_of_stools_per_day = fields.Integer(readonly=False, states={'Discharged': [('readonly', False)]})
    adequate_amount_diapers_home = fields.Selection(yes_no, readonly=False, states={'Discharged': [('readonly', False)]})
    adequate_amount_diapers_home_text = fields.Char(readonly=False, states={'Discharged': [('readonly', False)]})
    circumcised = fields.Selection(yes_no, readonly=False, states={'Discharged': [('readonly', False)]})

    mental_assessments_show = fields.Boolean()
    amount_crying_normal = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    amount_crying_abnormal = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    amount_crying_abnormal_content = fields.Char(readonly=False, states={'Discharged': [('readonly', False)]})
    makes_eye_contact_normal = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    makes_eye_contact_abnormal = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    makes_eye_contact_abnormal_content = fields.Char(readonly=False, states={'Discharged': [('readonly', False)]})
    quiet_when_pick_normal = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    quiet_when_pick_abnormal = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    quiet_when_pick_abnormal_content = fields.Char(readonly=False, states={'Discharged': [('readonly', False)]})

    feeding_type = fields.Selection([
        ('Breast', 'Breast'),
        ('Bottle', 'Bottle'),
        ('Breast and Bottle', 'Breast and Bottle'),
    ], readonly=False, states={'Discharged': [('readonly', False)]})
    formula_feeding = fields.Text(readonly=False, states={'Discharged': [('readonly', False)]})
    amount_frequency = fields.Text(readonly=False, states={'Discharged': [('readonly', False)]})
    adequate_amount_of_formula = fields.Selection(yes_no, readonly=False, states={'Discharged': [('readonly', False)]})
    adequate_amount_of_formula_text = fields.Char(readonly=False, states={'Discharged': [('readonly', False)]})

    other_assessment_show = fields.Boolean()
    other_assessment_show_text = fields.Text(readonly=False, states={'Discharged': [('readonly', False)]})

    immunization_show = fields.Boolean()
    received_initial_hepatitis = fields.Selection(yes_no, readonly=False, states={'Discharged': [('readonly', False)]})
    where_and_when = fields.Text(readonly=False, states={'Discharged': [('readonly', False)]})
    has_an_appointment_been = fields.Selection(yes_no, readonly=False, states={'Discharged': [('readonly', False)]})
    has_an_appointment_been_date = fields.Date(readonly=False, states={'Discharged': [('readonly', False)]})
    has_an_appointment_been_where = fields.Char(readonly=False, states={'Discharged': [('readonly', False)]})
    has_an_appointment_been_no_text = fields.Text(readonly=False, states={'Discharged': [('readonly', False)]})

    safe_sleep_show = fields.Boolean()
    crib = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    bassinet = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    other = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    other_content = fields.Char(readonly=False, states={'Discharged': [('readonly', False)]})

    mother_caregiver_education_show = fields.Boolean()
    advise_to_refrain_putting_stuffed_animals = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    advise_that_sleep_environment_should = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    advise_not_to_share_sleep = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    advise_on_proper_position = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    advise_to_refrain_from_smoking = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    advise_to_change_clothes_before_holding = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    advise_that_supervision_needed_when = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    # Oxygen Administration tab
    type_of_oxygen_inhalation_show = fields.Boolean()
    type_of_oxygen_inhalation = fields.Selection([
        ('Nosal', 'Nosal'),
        ('Face Mask', 'Face Mask'),
        ('High Flow', 'High Flow'),
    ], readonly=False, states={'Discharged': [('readonly', False)]})


    risk_for_dry_or_bloody_nose = fields.Selection(yes_no, readonly=False, states={'Discharged': [('readonly', False)]})
    risk_for_oxygen_toxicity = fields.Selection(yes_no, readonly=False, states={'Discharged': [('readonly', False)]})

    to_achieve_adequate_tissue_oxygenation = fields.Selection(yes_no,
                                                              readonly=False, states={'Discharged': [('readonly', False)]})

    presence_of_shortness_of_breath = fields.Selection(yes_no,
                                                       readonly=False, states={'Discharged': [('readonly', False)]})
    presence_of_cough = fields.Selection(yes_no,
                                         readonly=False, states={'Discharged': [('readonly', False)]})
    presence_of_chest_pain_due_to_excessive_coughing = fields.Selection(yes_no, readonly=False, states={'Discharged': [('readonly', False)]})


    applies_safe_use_equipment_procedure_practice = fields.Selection(yes_no, readonly=False, states={'Discharged': [('readonly', False)]})
    never_smoke_and_don_let_others_light_near_you = fields.Selection(yes_no, readonly=False, states={'Discharged': [('readonly', False)]})
    keep_oxygen_containers_upright = fields.Selection(yes_no,
                                                      readonly=False, states={'Discharged': [('readonly', False)]})
    # pressure ulcer tab
    competent_yes_no_na = [
        ('Competent', 'Competent'),
        ('Yes', 'Yes'),
        ('No', 'No'),
        ('NA', 'NA'),
    ]
    type_impaired_show = fields.Boolean()
    bedridden = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    wheelchair = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    ambulates_assistance = fields.Selection([
        ('Cane', 'Cane'),
        ('Walking Frame', 'Walking Frame'),
        ('Elbow Crutches', 'Elbow Crutches'),
        ('Axillary Crutches', 'Axillary Crutches'),
        ('Patient is Ambulatory', 'Patient is Ambulatory'),
        ('NA', 'NA'),
    ], readonly=False, states={'Discharged': [('readonly', False)]})

    press_potential_actual_risk_show = fields.Boolean()
    risk_for_falls_related_to_impaired_mobility = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    fall_risk_assessment_done = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    pressure_ulcer_altered_skin_integrity_related = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    complications_related_to_urinary_bowel_incontinence = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})

    press_measurable_goals_show = fields.Boolean()
    free_from_injury_related_to_falls = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    free_from_skin_redness_blisters_or_discoloration = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    skin_will_be_clean_dry_with_appropriate_and_prompt = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})

    skin_clean_dry_odor = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    any_changes_skin = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    use_pressure_relief = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    patient_assessment_other = fields.Text(readonly=False, states={'Discharged': [('readonly', False)]})

    caregiver_assessment_show = fields.Boolean()
    maintained_patients_general = fields.Selection([
        ('Well', 'Well'),
        ('Very Well', 'Very Well'),
        ('Fair', 'Fair'),
        ('Poor', 'Poor'),
    ], readonly=False, states={'Discharged': [('readonly', False)]})
    performed_hourly_turning = fields.Selection(competent_yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    continence_care = fields.Selection(competent_yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    skin_care = fields.Selection(competent_yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})


    maintain_oral_intake = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})

    Patient_caregiver_education_show = fields.Boolean()
    ensure_that_patient_hygiene = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    turn_change_patient_position = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    apply_moisturiser_skin = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    inform_home_care_nurse = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})

    key_performance_indicator_show = fields.Boolean()
    development_new_pressure = fields.Selection([
        ('No', 'No'),
        ('Yes-Home Acquired', 'Yes-Home Acquired'),
        ('Yes-Hospital Acquired', 'Yes-Hospital Acquired'),
    ], readonly=False, states={'Discharged': [('readonly', False)]})
    since_last_visit = fields.Selection([
        ('No Event', 'No Event'),
        ('Presented to Emergency Unit', 'Presented to Emergency Unit'),
        ('Readmitted to KFMC Hospital', 'Readmitted to KFMC Hospital'),
        ('Readmitted to Other Hospital', 'Readmitted to Other Hospital'),
        ('Seen by private doctor', 'Seen by private doctor'),
    ], readonly=False, states={'Discharged': [('readonly', False)]})
    # postnatal tab
    postnatal_day_show = fields.Boolean()
    postnatal_day = fields.Integer(readonly=False, states={'Discharged': [('readonly', False)]})

    type_of_delivery_show = fields.Boolean()
    normal_delivery = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    casarean_delivery = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    delivery_other = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    delivery_other_text = fields.Text(readonly=False, states={'Discharged': [('readonly', False)]})

    pos_potential_actual_risk_show = fields.Boolean()
    risk_for_infection_related_to_episiotomy_post = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    alteration_in_comfort_pain_related_to_episiotomy = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    risk_for_fluid_volume_deficit_related_to_vaginal_bleeding = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    risk_for_maternal_injury_related_to_tissue_oedema_and = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})

    pos_measurable_goals_show = fields.Boolean()
    will_be_able_to_demonstrate_proper_perineal_care = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    will_maintain_adequate_level_of_comfort_as_evidenced_by_pain = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    vital_signs_remain_stable_with_moderate_amount_of_lochia = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    free_of_signs_of_cerebral_ischemia_within = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})

    vital_signs_stable = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    presence_of_headache = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    change_in_vision = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    breast = fields.Selection([
        ('Hard', 'Hard'),
        ('Swollen', 'Swollen'),
        ('Painful', 'Painful'),
    ], readonly=False, states={'Discharged': [('readonly', False)]})
    uterus = fields.Selection([
        ('Fundus Firm', 'Fundus Firm'),
        ('Not palpable', 'Not palpable'),
        ('NA', 'NA'),
    ], readonly=False, states={'Discharged': [('readonly', False)]})
    bowel_pattem = fields.Selection([
        ('Normal', 'Normal'),
        ('Abnormal', 'Abnormal'),
    ], readonly=False, states={'Discharged': [('readonly', False)]})
    postnatal_bladder = fields.Selection([
        ('Voiding comfortaness', 'Voiding comfortaness'),
        ('Fullness/with pressure', 'Fullness/with pressure'),
    ], readonly=False, states={'Discharged': [('readonly', False)]})
    abdominal_incision = fields.Selection([
        ('not inflamed', 'not inflamed'),
        ('no drainage', 'no drainage'),
        ('little drainage', 'little drainage'),
        ('staple present', 'staple present'),
        ('dressing intact', 'dressing intact'),
        ('decrease swelling', 'decrease swelling'),
    ], readonly=False, states={'Discharged': [('readonly', False)]})
    episiotomy_episiorapphy = fields.Selection([
        ('Intact', 'Intact'),
        ('Small tearing', 'Small tearing'),
        ('with bruising or', 'with bruising or'),
        ('swelling', 'swelling'),
    ], readonly=False, states={'Discharged': [('readonly', False)]})
    lochia = fields.Selection([
        ('Fleslage smelly', 'Fleslage smelly'),
        ('Rubra serosa', 'Rubra serosa'),
        ('lochia serosa', 'lochia serosa'),
        ('darie red', 'darie red'),
        ('discharges', 'discharges'),
        ('lochia alba', 'lochia alba'),
    ], readonly=False, states={'Discharged': [('readonly', False)]})
    homan_sign = fields.Selection([
        ('unilateral calf pain', 'unilateral calf pain'),
        ('negative DVT', 'negative DVT'),
        ('Redness', 'Redness'),
        ('Swollen', 'Swollen'),
    ], readonly=False, states={'Discharged': [('readonly', False)]})


    postnatal_specific_dietary_needs = fields.Selection([
        ('Diabetic', 'Diabetic'),
        ('low salt', 'low salt'),
        ('law fat', 'law fat'),
        ('high fiber', 'high fiber'),
        ('low salt, low fat', 'low salt, low fat'),
        ('Regular diet', 'Regular diet'),
    ], readonly=False, states={'Discharged': [('readonly', False)]})
    oral_medication_discussed = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    patient_caregiver_able = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    postnatal_medication_review_done = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    next_review_due = fields.Text(readonly=False, states={'Discharged': [('readonly', False)]})

    advised_on_well_balanced_nutrition_fluids = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    advised_on_ambulation_to_prevent = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    report_to_emergency_department_for_sudden = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    report_to_emergency_department_for_headache = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    report_to_emergency_department_for_unilateral = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    advise_to_take_prescribed_analgesia = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    advise_to_palpate_fundus_and_able_to_demonstrate = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    advise_to_empty_bladder_and_be_aware_of_need = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    encourage_to_splint_abdomen_with_pillow_when = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    observe_for_increased_bleeding_on_post = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    advise_refrain_form_tub_bath_until_dressings = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    advise_to_use_good_body_mechanics_and_avoiding = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    advise_on_frequent_breastfeeding_to_help_prevent = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    advise_on_using_non_restricting_bra = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    advise_on_massaging_breast_gently_and_manually_express_milk = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    advise_application_of_warm_compresses_shower_or_breast = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    advise_on_care_support_and_breastfeeding_technique_for_women = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    advise_on_hand_hygiene = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    advise_on_voiding_comfort_measure = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    advise_on_lochia_and_perineum_comfort = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    advise_on_activities_and_rest = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    advise_on_normal_patterns_of_emotional_changes = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})
    advise_on_proper_breastfeeding_technique = fields.Selection(yes_no_na, readonly=False, states={'Discharged': [('readonly', False)]})

    key_performance_indictor_show = fields.Boolean()
    hospital_readmission = fields.Text(readonly=False, states={'Discharged': [('readonly', False)]})
    since_last_visit_patient_was = fields.Text(readonly=False, states={'Discharged': [('readonly', False)]})
    # trache tab
    type_tracheostomy_inserted_show = fields.Boolean()
    type_tracheostomy_inserted = fields.Selection([
        ('Cuff Tube', 'Cuff Tube'),
        ('Uncuffed Tube', 'Uncuffed Tube'),
    ])
    type_tracheostomy_inserted_text = fields.Text()


    impaired_skin_integrity_surrounding_stoma = fields.Selection(yes_no)
    improper_fitting_care_appliance_skin = fields.Selection(yes_no)

    skin_integrity_around_stoma_will = fields.Selection(yes_no)
    patient_caregiver_will_demonstrate_behaviours = fields.Selection(yes_no)



    breathing_effectively = fields.Selection(yes_no)
    coping_with_presence_of_tracheostomy = fields.Selection(yes_no)
    managing_skin_integrity_around = fields.Selection(yes_no)

    presence_of_hypergranulation = fields.Selection(yes_no)
    presence_of_excoriation = fields.Selection(yes_no)
    stoma_dressind_done = fields.Selection(yes_no)

    change_trache_ties_every_other = fields.Selection(yes_no)
    use_finger_technique_to_determine = fields.Selection(yes_no)
    observe_for_stomal_complications_and_report = fields.Selection(yes_no)
    demonstrate_safe_use_of_equipment_and = fields.Selection(yes_no)

    # vaccines tab
    VACCINATION = [
        ('Influenza (0.25 ml)', 'Influenza (0.25 ml)'),
        ('Tdap (0.5 ml)', 'Tdap (0.5 ml)'),
        ('MMR (0.5 ml)', 'MMR (0.5 ml)'),
        ('Varicella (0.5 ml)', 'Varicella (0.5 ml)'),
        ('Herpes Zoster (0.5 ml)', 'Herpes Zoster (0.5 ml)'),
        ('HPV (0.5 ml)', 'HPV (0.5 ml)'),
        ('PPSV23 (0.5 ml)', 'PPSV23 (0.5 ml)'),
        ('PCV (0.5 ml)', 'PCV (0.5 ml)'),
        ('Hep B (0.5 ml)', 'Hep B (0.5 ml)'),
        ('MCV4 (0.5 ml)', 'MCV4 (0.5 ml)'),
        ('RV (1 ml)', 'RV (1 ml)'),
        ('D TaP (0.5 ml)', 'D TaP (0.5 ml)'),
        ('Hib (0.5 ml)', 'Hib (0.5 ml)'),
        ('IPV (0.5 ml)', 'IPV (0.5 ml)'),
        ('BCG (0.5 ml)', 'BCG (0.5 ml)'),
        ('OPV (2 gtts)', 'OPV (2 gtts)'),
        ('Measels (0.5 ml)', 'Measels (0.5 ml)'),
        ('HepA (0.5 ml)', 'HepA (0.5 ml)'),
    ]
    check_prior_show = fields.Boolean()
    drug_allergy_yes = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    drug_allergy_no = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    drug_allergy_content = fields.Char(readonly=False, states={'Discharged': [('readonly', False)]})

    allergic_previous_yes = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    allergic_previous_no = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    allergic_previous_content = fields.Char(readonly=False, states={'Discharged': [('readonly', False)]})

    allergic_hypersensitivty_yes = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    allergic_hypersensitivty_no = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    allergic_hypersensitivty_content = fields.Char(readonly=False, states={'Discharged': [('readonly', False)]})

    any_recent_illness_yes = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    any_recent_illness_no = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    any_recent_illness_content = fields.Char(readonly=False, states={'Discharged': [('readonly', False)]})

    previous_vaccination_yes = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    previous_vaccination_no = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    previous_vaccination_content = fields.Char(readonly=False, states={'Discharged': [('readonly', False)]})
    previous_vaccination_temp = fields.Float(readonly=False, states={'Discharged': [('readonly', False)]})

    # vaccination schedule
    vaccination_schedule_show = fields.Boolean()
    vaccination_schedule = fields.Selection([
        ('At Birth', 'At Birth'),
        ('2 Months', '2 Months'),
        ('4 Months', '4 Months'),
        ('6 Months', '6 Months'),
        ('9 Months', '9 Months'),
        ('12 Months', '12 Months'),
        ('18 Months', '18 Months'),
        ('24 Months', '24 Months'),
        ('4-6 Years old', '4-6 Years old'),
        ('11 Years', '11 Years'),
        ('12 Years', '12 Years'),
        ('18 Years', '18 Years'),
        ('Other', 'Other'),
    ], readonly=False, states={'Discharged': [('readonly', False)]})
    ADMINISTERED_OVER = [
        ('Right', 'Right'),
        ('Left', 'Left'),
    ]
    at_birth_hepb = fields.Boolean(string='HepB (0.5 ml)', readonly=False, states={'Discharged': [('readonly', False)]})
    at_birth_hepb_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    at_birth_hepb_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Discharged': [('readonly', False)]})
    at_birth_hepb_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other_at_birth = fields.Boolean(string='Other', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other_at_birth_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other_at_birth_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other_at_birth_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other_at_birth_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Discharged': [('readonly', False)]})

    add_other_at_birth_comment = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other2_at_birth = fields.Boolean(string='Other', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other2_at_birth_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other2_at_birth_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other2_at_birth_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other2_at_birth_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Discharged': [('readonly', False)]})

    add_other2_at_birth_comment = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})

    t_mon_hepb = fields.Boolean(string='HepB (0.5 ml)', readonly=False, states={'Discharged': [('readonly', False)]})
    t_mon_hepb_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    t_mon_hepb_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Discharged': [('readonly', False)]})
    t_mon_hepb_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Discharged': [('readonly', False)]})

    t_mon_rv = fields.Boolean(string='RV (1 ml)', readonly=False, states={'Discharged': [('readonly', False)]})
    t_mon_rv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    t_mon_rv_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Discharged': [('readonly', False)]})
    t_mon_rv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Discharged': [('readonly', False)]})

    t_mon_dtap = fields.Boolean(string='D TaP (0.5 ml)', readonly=False, states={'Discharged': [('readonly', False)]})
    t_mon_dtap_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    t_mon_dtap_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Discharged': [('readonly', False)]})
    t_mon_dtap_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Discharged': [('readonly', False)]})

    t_mon_hib = fields.Boolean(string='Hib (0.5 ml)', readonly=False, states={'Discharged': [('readonly', False)]})
    t_mon_hib_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    t_mon_hib_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Discharged': [('readonly', False)]})
    t_mon_hib_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Discharged': [('readonly', False)]})

    t_mon_pcv = fields.Boolean(string='PCV (0.5 ml)', readonly=False, states={'Discharged': [('readonly', False)]})
    t_mon_pcv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    t_mon_pcv_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Discharged': [('readonly', False)]})
    t_mon_pcv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Discharged': [('readonly', False)]})

    t_mon_ipv = fields.Boolean(string='IPV (0.5 ml)', readonly=False, states={'Discharged': [('readonly', False)]})
    t_mon_ipv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    t_mon_ipv_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Discharged': [('readonly', False)]})
    t_mon_ipv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Discharged': [('readonly', False)]})

    add_other_t_mon = fields.Boolean(string='Other', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other_t_mon_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other_t_mon_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other_t_mon_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other_t_mon_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Discharged': [('readonly', False)]})

    add_other_t_mon_comment = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other2_t_mon = fields.Boolean(string='Other', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other2_t_mon_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other2_t_mon_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other2_t_mon_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other2_t_mon_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Discharged': [('readonly', False)]})

    add_other2_t_mon_comment = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})

    f_mon_hepb = fields.Boolean(string='HepB (0.5 ml)', readonly=False, states={'Discharged': [('readonly', False)]})
    f_mon_hepb_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    f_mon_hepb_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Discharged': [('readonly', False)]})
    f_mon_hepb_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Discharged': [('readonly', False)]})

    f_mon_rv = fields.Boolean(string='RV (1 ml)', readonly=False, states={'Discharged': [('readonly', False)]})
    f_mon_rv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    f_mon_rv_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Discharged': [('readonly', False)]})
    f_mon_rv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Discharged': [('readonly', False)]})

    f_mon_dtap = fields.Boolean(string='D TaP (0.5 ml)', readonly=False, states={'Discharged': [('readonly', False)]})
    f_mon_dtap_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    f_mon_dtap_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Discharged': [('readonly', False)]})
    f_mon_dtap_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Discharged': [('readonly', False)]})

    f_mon_hib = fields.Boolean(string='Hib (0.5 ml)', readonly=False, states={'Discharged': [('readonly', False)]})
    f_mon_hib_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    f_mon_hib_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Discharged': [('readonly', False)]})
    f_mon_hib_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Discharged': [('readonly', False)]})

    f_mon_pcv = fields.Boolean(string='PCV (0.5 ml)', readonly=False, states={'Discharged': [('readonly', False)]})
    f_mon_pcv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    f_mon_pcv_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Discharged': [('readonly', False)]})
    f_mon_pcv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Discharged': [('readonly', False)]})
    f_mon_ipv = fields.Boolean(string='IPV (0.5 ml)', readonly=False, states={'Discharged': [('readonly', False)]})
    f_mon_ipv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    f_mon_ipv_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Discharged': [('readonly', False)]})
    f_mon_ipv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Discharged': [('readonly', False)]})

    add_other_f_mon = fields.Boolean(string='Other', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other_f_mon_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other_f_mon_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other_f_mon_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other_f_mon_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Discharged': [('readonly', False)]})

    add_other_f_mon_comment = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other2_f_mon = fields.Boolean(string='Other', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other2_f_mon_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other2_f_mon_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other2_f_mon_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other2_f_mon_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Discharged': [('readonly', False)]})

    add_other2_f_mon_comment = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})

    s_mon_hepb = fields.Boolean(string='HepB (0.5 ml)', readonly=False, states={'Discharged': [('readonly', False)]})
    s_mon_hepb_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    s_mon_hepb_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Discharged': [('readonly', False)]})
    s_mon_hepb_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Discharged': [('readonly', False)]})

    s_mon_rv = fields.Boolean(string='RV (1 ml)', readonly=False, states={'Discharged': [('readonly', False)]})
    s_mon_rv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    s_mon_rv_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Discharged': [('readonly', False)]})
    s_mon_rv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Discharged': [('readonly', False)]})

    s_mon_dtap = fields.Boolean(string='D TaP (0.5 ml)', readonly=False, states={'Discharged': [('readonly', False)]})
    s_mon_dtap_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    s_mon_dtap_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Discharged': [('readonly', False)]})

    s_mon_dtap_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Discharged': [('readonly', False)]})

    s_mon_hib = fields.Boolean(string='Hib (0.5 ml)', readonly=False, states={'Discharged': [('readonly', False)]})
    s_mon_hib_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    s_mon_hib_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Discharged': [('readonly', False)]})
    s_mon_hib_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Discharged': [('readonly', False)]})

    s_mon_pcv = fields.Boolean(string='PCV (0.5 ml)', readonly=False, states={'Discharged': [('readonly', False)]})
    s_mon_pcv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    s_mon_pcv_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Discharged': [('readonly', False)]})
    s_mon_pcv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Discharged': [('readonly', False)]})

    s_mon_ipv = fields.Boolean(string='IPV (0.5 ml)', readonly=False, states={'Discharged': [('readonly', False)]})
    s_mon_ipv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    s_mon_ipv_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Discharged': [('readonly', False)]})
    s_mon_ipv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Discharged': [('readonly', False)]})

    s_mon_bcg = fields.Boolean(string='BCG (0.5 ml)', readonly=False, states={'Discharged': [('readonly', False)]})
    s_mon_bcg_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    s_mon_bcg_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Discharged': [('readonly', False)]})
    s_mon_bcg_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Discharged': [('readonly', False)]})

    s_mon_opv = fields.Boolean(string='OPV (2 gtts)', readonly=False, states={'Discharged': [('readonly', False)]})
    s_mon_opv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    s_mon_opv_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Discharged': [('readonly', False)]})
    s_mon_opv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Discharged': [('readonly', False)]})

    add_other_s_mon = fields.Boolean(string='Other', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other_s_mon_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other_s_mon_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other_s_mon_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other_s_mon_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Discharged': [('readonly', False)]})

    add_other_s_mon_comment = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other2_s_mon = fields.Boolean(string='Other', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other2_s_mon_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other2_s_mon_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other2_s_mon_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other2_s_mon_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Discharged': [('readonly', False)]})

    add_other2_s_mon_comment = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})

    n_mon_measels = fields.Boolean(string='Measels (0.5 ml)', readonly=False, states={'Discharged': [('readonly', False)]})
    n_mon_measels_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    n_mon_measels_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Discharged': [('readonly', False)]})
    n_mon_measels_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Discharged': [('readonly', False)]})

    n_mon_mcv = fields.Boolean(string='MCV4 (0.5 ml)', readonly=False, states={'Discharged': [('readonly', False)]})
    n_mon_mcv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    n_mon_mcv_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Discharged': [('readonly', False)]})
    n_mon_mcv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other_n_mon = fields.Boolean(string='Other', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other_n_mon_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other_n_mon_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other_n_mon_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other_n_mon_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Discharged': [('readonly', False)]})

    add_other_n_mon_comment = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other2_n_mon = fields.Boolean(string='Other', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other2_n_mon_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other2_n_mon_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other2_n_mon_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other2_n_mon_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Discharged': [('readonly', False)]})

    add_other2_n_mon_comment = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})

    ot_mon_pcv = fields.Boolean(string='PCV (0.5 ml)', readonly=False, states={'Discharged': [('readonly', False)]})
    ot_mon_pcv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    ot_mon_pcv_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Discharged': [('readonly', False)]})
    ot_mon_pcv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Discharged': [('readonly', False)]})

    ot_mon_opv = fields.Boolean(string='OPV (2 gtts)', readonly=False, states={'Discharged': [('readonly', False)]})
    ot_mon_opv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    ot_mon_opv_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Discharged': [('readonly', False)]})
    ot_mon_opv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Discharged': [('readonly', False)]})

    ot_mon_mcv = fields.Boolean(string='MCV4 (0.5 ml)', readonly=False, states={'Discharged': [('readonly', False)]})
    ot_mon_mcv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    ot_mon_mcv_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Discharged': [('readonly', False)]})
    ot_mon_mcv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Discharged': [('readonly', False)]})

    ot_mon_mmr = fields.Boolean(string='MMR (0.5 ml)', readonly=False, states={'Discharged': [('readonly', False)]})
    ot_mon_mmr_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    ot_mon_mmr_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Discharged': [('readonly', False)]})
    ot_mon_mmr_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Discharged': [('readonly', False)]})

    add_other_ot_mon = fields.Boolean(string='Other', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other_ot_mon_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other_ot_mon_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other_ot_mon_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other_ot_mon_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Discharged': [('readonly', False)]})

    add_other_ot_mon_comment = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other2_ot_mon = fields.Boolean(string='Other', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other2_ot_mon_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other2_ot_mon_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other2_ot_mon_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other2_ot_mon_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Discharged': [('readonly', False)]})

    add_other2_ot_mon_comment = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})

    oe_mon_dtap = fields.Boolean(string='D TaP (0.5 ml)', readonly=False, states={'Discharged': [('readonly', False)]})
    oe_mon_dtap_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    oe_mon_dtap_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Discharged': [('readonly', False)]})
    oe_mon_dtap_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Discharged': [('readonly', False)]})

    oe_mon_hib = fields.Boolean(string='Hib (0.5 ml)', readonly=False, states={'Discharged': [('readonly', False)]})
    oe_mon_hib_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    oe_mon_hib_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Discharged': [('readonly', False)]})
    oe_mon_hib_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Discharged': [('readonly', False)]})

    oe_mon_hepa = fields.Boolean(string='HepA (0.5 ml)', readonly=False, states={'Discharged': [('readonly', False)]})
    oe_mon_hepa_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    oe_mon_hepa_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Discharged': [('readonly', False)]})
    oe_mon_hepa_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Discharged': [('readonly', False)]})

    oe_mon_varicella = fields.Boolean(string='Varicella (0.5 ml)', readonly=False, states={'Discharged': [('readonly', False)]})
    oe_mon_varicella_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    oe_mon_varicella_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Discharged': [('readonly', False)]})
    oe_mon_varicella_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Discharged': [('readonly', False)]})

    oe_mon_mmr = fields.Boolean(string='MMR (0.5 ml)', readonly=False, states={'Discharged': [('readonly', False)]})
    oe_mon_mmr_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    oe_mon_mmr_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Discharged': [('readonly', False)]})
    oe_mon_mmr_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Discharged': [('readonly', False)]})

    oe_mon_opv = fields.Boolean(string='OPV (2 gtts)', readonly=False, states={'Discharged': [('readonly', False)]})
    oe_mon_opv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    oe_mon_opv_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Discharged': [('readonly', False)]})
    oe_mon_opv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Discharged': [('readonly', False)]})

    add_other_oe_mon = fields.Boolean(string='Other', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other_oe_mon_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other_oe_mon_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other_oe_mon_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other_oe_mon_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Discharged': [('readonly', False)]})

    add_other_oe_mon_comment = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other2_oe_mon = fields.Boolean(string='Other', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other2_oe_mon_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other2_oe_mon_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other2_oe_mon_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other2_oe_mon_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Discharged': [('readonly', False)]})

    add_other2_oe_mon_comment = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})

    tf_mon_hepa = fields.Boolean(string='HepA (0.5 ml)', readonly=False, states={'Discharged': [('readonly', False)]})

    tf_mon_hepa_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    tf_mon_hepa_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Discharged': [('readonly', False)]})
    tf_mon_hepa_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Discharged': [('readonly', False)]})

    add_other_tf_mon = fields.Boolean(string='Other', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other_tf_mon_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other_tf_mon_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other_tf_mon_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other_tf_mon_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Discharged': [('readonly', False)]})

    add_other_tf_mon_comment = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other2_tf_mon = fields.Boolean(string='Other', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other2_tf_mon_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other2_tf_mon_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other2_tf_mon_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other2_tf_mon_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Discharged': [('readonly', False)]})

    add_other2_tf_mon_comment = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})

    fs_yea_dtap = fields.Boolean(string='D Tap (0.5 ml)', readonly=False, states={'Discharged': [('readonly', False)]})
    fs_yea_dtap_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    fs_yea_dtap_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Discharged': [('readonly', False)]})
    fs_yea_dtap_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Discharged': [('readonly', False)]})

    fs_yea_opv = fields.Boolean(string='OPV (2 gtts)', readonly=False, states={'Discharged': [('readonly', False)]})
    fs_yea_opv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    fs_yea_opv_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Discharged': [('readonly', False)]})
    fs_yea_opv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Discharged': [('readonly', False)]})

    fs_yea_varicella = fields.Boolean(string='Varicella (0.5 ml)', readonly=False, states={'Discharged': [('readonly', False)]})
    fs_yea_varicella_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    fs_yea_varicella_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Discharged': [('readonly', False)]})
    fs_yea_varicella_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Discharged': [('readonly', False)]})

    fs_yea_mmr = fields.Boolean(string='MMR (0.5 ml)', readonly=False, states={'Discharged': [('readonly', False)]})
    fs_yea_mmr_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    fs_yea_mmr_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Discharged': [('readonly', False)]})
    fs_yea_mmr_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Discharged': [('readonly', False)]})

    add_other_fs_yea = fields.Boolean(string='Other', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other_fs_yea_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other_fs_yea_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other_fs_yea_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other_fs_yea_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Discharged': [('readonly', False)]})

    add_other_fs_yea_comment = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other2_fs_yea = fields.Boolean(string='Other', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other2_fs_yea_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other2_fs_yea_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other2_fs_yea_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other2_fs_yea_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Discharged': [('readonly', False)]})

    add_other2_fs_yea_comment = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})

    oo_yea_dtap = fields.Boolean(string='Tdap (0.5 ml)', readonly=False, states={'Discharged': [('readonly', False)]})
    oo_yea_dtap_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    oo_yea_dtap_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Discharged': [('readonly', False)]})
    oo_yea_dtap_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Discharged': [('readonly', False)]})

    # oo_yea_dtap_administered_right = fields.Boolean(string='Right', readonly=True,
    #                                                 states={'Start': [('readonly', False)]})
    # oo_yea_dtap_administered_left = fields.Boolean(string='Left', readonly=True,
    #                                                states={'Start': [('readonly', False)]})

    oo_yea_vpv = fields.Boolean(string='HPV (0.5 ml)', readonly=False, states={'Discharged': [('readonly', False)]})
    oo_yea_vpv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    oo_yea_vpv_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Discharged': [('readonly', False)]})
    oo_yea_vpv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Discharged': [('readonly', False)]})

    add_other_oo_yea = fields.Boolean(string='Other', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other_oo_yea_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other_oo_yea_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other_oo_yea_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other_oo_yea_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Discharged': [('readonly', False)]})

    add_other_oo_yea_comment = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other2_oo_yea = fields.Boolean(string='Other', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other2_oo_yea_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other2_oo_yea_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other2_oo_yea_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other2_oo_yea_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other2_oo_yea_comment = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})

    ot_yea_hpv = fields.Boolean(string='HPV (0.5 ml)', readonly=False, states={'Discharged': [('readonly', False)]})
    ot_yea_hpv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    ot_yea_hpv_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Discharged': [('readonly', False)]})
    ot_yea_hpv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Discharged': [('readonly', False)]})

    add_other_ot_yea = fields.Boolean(string='Other', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other_ot_yea_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other_ot_yea_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other_ot_yea_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other_ot_yea_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Discharged': [('readonly', False)]})

    add_other_ot_yea_comment = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other2_ot_yea = fields.Boolean(string='Other', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other2_ot_yea_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other2_ot_yea_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other2_ot_yea_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other2_ot_yea_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Discharged': [('readonly', False)]})

    add_other2_ot_yea_comment = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})

    oe_yea_mcv = fields.Boolean(string='MCV4 (0.5 ml)', readonly=False, states={'Discharged': [('readonly', False)]})
    oe_yea_mcv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    oe_yea_mcv_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Discharged': [('readonly', False)]})
    oe_yea_mcv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Discharged': [('readonly', False)]})

    add_other_oe_yea = fields.Boolean(string='Other', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other_oe_yea_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other_oe_yea_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other_oe_yea_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other_oe_yea_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Discharged': [('readonly', False)]})

    add_other_oe_yea_comment = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other2_oe_yea = fields.Boolean(string='Other', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other2_oe_yea_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other2_oe_yea_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other2_oe_yea_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Discharged': [('readonly', False)]})
    add_other2_oe_yea_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Discharged': [('readonly', False)]})

    add_other2_oe_yea_comment = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})

    oth_influenza = fields.Boolean(string='Influenza (0.25 ml)', readonly=False, states={'Discharged': [('readonly', False)]})
    oth_influenza_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    oth_influenza_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Discharged': [('readonly', False)]})
    oth_influenza_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Discharged': [('readonly', False)]})

    oth_tdap = fields.Boolean(string='Tdap (0.5 ml)', readonly=False, states={'Discharged': [('readonly', False)]})
    oth_tdap_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    oth_tdap_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Discharged': [('readonly', False)]})
    oth_tdap_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Discharged': [('readonly', False)]})

    oth_mmr = fields.Boolean(string='MMR (0.5 ml)', readonly=False, states={'Discharged': [('readonly', False)]})
    oth_mmr_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    oth_mmr_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Discharged': [('readonly', False)]})
    oth_mmr_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Discharged': [('readonly', False)]})

    oth_varicella = fields.Boolean(string='Varicella (0.5 ml)', readonly=False, states={'Discharged': [('readonly', False)]})
    oth_varicella_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    oth_varicella_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Discharged': [('readonly', False)]})
    oth_varicella_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Discharged': [('readonly', False)]})

    oth_herpes = fields.Boolean(string='Herpes Zoster (0.5 ml)', readonly=False, states={'Discharged': [('readonly', False)]})
    oth_herpes_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    oth_herpes_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Discharged': [('readonly', False)]})
    oth_herpes_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Discharged': [('readonly', False)]})

    oth_hpv = fields.Boolean(string='HPV (0.5 ml)', readonly=False, states={'Discharged': [('readonly', False)]})
    oth_hpv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    oth_hpv_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Discharged': [('readonly', False)]})
    oth_hpv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Discharged': [('readonly', False)]})

    oth_ppsv = fields.Boolean(string='PPSV23 (0.5 ml)', readonly=False, states={'Discharged': [('readonly', False)]})
    oth_ppsv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    oth_ppsv_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Discharged': [('readonly', False)]})
    oth_ppsv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Discharged': [('readonly', False)]})

    oth_pcv = fields.Boolean(string='PCV (0.5 ml)', readonly=False, states={'Discharged': [('readonly', False)]})
    oth_pcv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    oth_pcv_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Discharged': [('readonly', False)]})
    oth_pcv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Discharged': [('readonly', False)]})

    oth_hepb = fields.Boolean(string='Hep B (0.5 ml)', readonly=False, states={'Discharged': [('readonly', False)]})
    oth_hepb_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    oth_hepb_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Discharged': [('readonly', False)]})
    oth_hepb_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Discharged': [('readonly', False)]})

    oth_mcv = fields.Boolean(string='MCV4 (0.5 ml)', readonly=False, states={'Discharged': [('readonly', False)]})
    oth_mcv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    oth_mcv_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Discharged': [('readonly', False)]})
    oth_mcv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Discharged': [('readonly', False)]})

    oth_other = fields.Boolean(string='Other', readonly=False, states={'Discharged': [('readonly', False)]})
    oth_vaccinations = fields.Char(string='Vaccination', readonly=False, states={'Discharged': [('readonly', False)]})
    oth_vaccinations_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    oth_vaccinations_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Discharged': [('readonly', False)]})
    oth_vaccinations_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Discharged': [('readonly', False)]})

    oth_rv = fields.Boolean(string='RV (1 ml)', readonly=False, states={'Discharged': [('readonly', False)]})
    oth_rv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    oth_rv_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Discharged': [('readonly', False)]})
    oth_rv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Discharged': [('readonly', False)]})

    oth_dtap = fields.Boolean(string='D TaP (0.5 ml)', readonly=False, states={'Discharged': [('readonly', False)]})
    oth_dtap_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    oth_dtap_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Discharged': [('readonly', False)]})
    oth_dtap_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Discharged': [('readonly', False)]})

    oth_hib = fields.Boolean(string='Hib (0.5 ml)', readonly=False, states={'Discharged': [('readonly', False)]})
    oth_hib_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    oth_hib_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Discharged': [('readonly', False)]})
    oth_hib_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Discharged': [('readonly', False)]})

    oth_ipv = fields.Boolean(string='IPV (0.5 ml)', readonly=False, states={'Discharged': [('readonly', False)]})
    oth_ipv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    oth_ipv_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Discharged': [('readonly', False)]})
    oth_ipv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Discharged': [('readonly', False)]})

    oth_bcg = fields.Boolean(string='BCG (0.5 ml)', readonly=False, states={'Discharged': [('readonly', False)]})
    oth_bcg_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    oth_bcg_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Discharged': [('readonly', False)]})
    oth_bcg_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Discharged': [('readonly', False)]})

    oth_opv = fields.Boolean(string='OPV (2 gtts)', readonly=False, states={'Discharged': [('readonly', False)]})
    oth_opv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    oth_opv_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Discharged': [('readonly', False)]})
    oth_opv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Discharged': [('readonly', False)]})

    oth_measels = fields.Boolean(string='Measels (0.5 ml)', readonly=False, states={'Discharged': [('readonly', False)]})
    oth_measels_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    oth_measels_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Discharged': [('readonly', False)]})
    oth_measels_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Discharged': [('readonly', False)]})

    oth_hepa = fields.Boolean(string='HepA (0.5 ml)', readonly=False, states={'Discharged': [('readonly', False)]})

    oth_hepa_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Discharged': [('readonly', False)]})
    oth_hepa_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Discharged': [('readonly', False)]})
    oth_hepa_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Discharged': [('readonly', False)]})

    mother_caregiver_show = fields.Boolean()
    mother_soreness_redness_swelling = fields.Selection(YES_NO, readonly=False, states={'Discharged': [('readonly', False)]})
    mother_muscular_pain = fields.Selection(YES_NO, readonly=False, states={'Discharged': [('readonly', False)]})
    mother_headaches = fields.Selection(YES_NO, readonly=False, states={'Discharged': [('readonly', False)]})
    mother_fever = fields.Selection(YES_NO, readonly=False, states={'Discharged': [('readonly', False)]})
    mother_nausea = fields.Selection(YES_NO, readonly=False, states={'Discharged': [('readonly', False)]})

    mother_difficulty_breathing = fields.Selection(YES_NO, readonly=False, states={'Discharged': [('readonly', False)]})
    mother_coughing = fields.Selection(YES_NO, readonly=False, states={'Discharged': [('readonly', False)]})
    mother_hoarse_vice_wheezing = fields.Selection(YES_NO, readonly=False, states={'Discharged': [('readonly', False)]})
    mother_hives = fields.Selection(YES_NO, readonly=False, states={'Discharged': [('readonly', False)]})
    mother_paleness = fields.Selection(YES_NO, readonly=False, states={'Discharged': [('readonly', False)]})
    mother_losing_consciousness = fields.Selection(YES_NO, readonly=False, states={'Discharged': [('readonly', False)]})
    add_other = fields.Boolean(readonly=False, states={'Discharged': [('readonly', False)]})
    add_other_text = fields.Text(readonly=False, states={'Discharged': [('readonly', False)]})

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
        vals['comprehensive_nurse_code'] = self.env['ir.sequence'].next_by_code('comprehensive.nurse')
        return super(ComprehensiveNurse, self).create(vals)

    @api.onchange('number_foam')
    def _check_vital_signs(self):
        if self.number_foam > 100:
            raise ValidationError("invalid Number of Foam")


class ShifaReferralInherit(models.Model):
    _inherit = 'sm.shifa.referral'

    comprehensive_nurse_ref_id = fields.Many2one('sm.shifa.comprehensive.nurse', string='comprehensive nurse',
                                                 ondelete='cascade')


class ShifaWoundInherit(models.Model):
    _inherit = 'sm.shifa.wound.assessment.values'

    wound_comp_id = fields.Many2one('sm.shifa.comprehensive.nurse', string='Wound Assessment')
