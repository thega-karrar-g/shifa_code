from odoo import models, fields, api
import datetime
from odoo.exceptions import ValidationError


class ComprehensiveNurseFollowUp(models.Model):
    _name = 'sm.shifa.comprehensive.nurse.follow.up'
    _description = 'Comprehensive Nurse Follow Up'
    _rec_name = 'comprehensive_nurse_follow_up_code'

    ADMISSION_STATES = [
        ('Draft', 'Draft'),
        ('Start', 'Start'),
        ('Done', 'Done'),
    ]
    YES_NO_NA = [
        ('Yes', 'Yes'),
        ('No', 'No'),
        ('NA', 'NA'),
    ]
    YES_NO = [
        ('Yes ', 'Yes'),
        ('No', 'No'),
    ]
    YES_NO_NA_COMPETENT = [
        ('Competent', 'Competent'),
        ('Yes', 'Yes'),
        ('No', 'No'),
        ('NA', 'NA'),
    ]
    COMPETENT_NO_NA = [
        ('Competent', 'Competent'),
        ('No', 'No'),
        ('NA', 'NA'),
    ]
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

    @api.onchange('cna_xx')
    def _onchange_join_cna(self):
        if self.cna_xx:
            self.comprehensive_nurse_id = self.cna_xx

    @api.onchange('hhc_appointment')
    def _onchange_hhc_appointment(self):
        if self.hhc_appointment:
            self.patient = self.hhc_appointment.patient

    def _get_comprehensive(self):
        """Return default comprehensive value"""
        therapist_obj = self.env['oeh.medical.physician']
        domain = [('oeh_user_id', '=', self.env.uid)]
        user_ids = therapist_obj.search(domain, limit=1)
        if user_ids:
            return user_ids.id or False
        else:
            return False

    comprehensive_nurse_follow_up_code = fields.Char('Reference', index=True, copy=False)

    patient = fields.Many2one('oeh.medical.patient', string='Patient', help="Patient Name", required=True,
                              readonly=False, states={'Done': [('readonly', False)]})
    hhc_appointment = fields.Many2one('sm.shifa.hhc.appointment', string='HHC-Appointment',
                                      readonly=False, states={'Done': [('readonly', False)]})
    cna_xx = fields.Many2one('sm.shifa.comprehensive.nurse', string='CNA#', required=True,
                             readonly=False, states={'Done': [('readonly', False)]},
                             domain="[('patient','=',patient), ('state', 'in', ('Admitted', 'Start'))]")
    nurse_name = fields.Many2one('oeh.medical.physician', string='Nurse', required=True,
                                 readonly=False, states={'Done': [('readonly', False)]}, domain=[('role_type', '=', ['HHCN', 'HN'])],
                                 default=_get_comprehensive)
    state = fields.Selection(ADMISSION_STATES, string='State', default=lambda *a: 'Draft', readonly=True)
    weight = fields.Float(string='Weight', related='patient.weight')
    age = fields.Char(string='Age', related='patient.age')
    marital_status = fields.Selection(string='Marital Status', related='patient.marital_status', readonly='1')
    sex = fields.Selection(string='Sex', related='patient.sex')
    blood_type = fields.Selection(string='Blood Type', related='patient.blood_type', readonly='1')
    rh = fields.Selection(string='Rh', related='patient.rh', readonly='1')
    start_date = fields.Datetime(string='Start Date')
    completed_date = fields.Datetime(string='Completed Date')

    conscious_state_show = fields.Boolean()
    conscious_state = fields.Selection([
        ('Alert', 'Alert'),
        ('Response to Voice', 'Response to Voice'),
        ('Response to pain', 'Response to pain'),
        ('Unresponsive', 'Unresponsive'),
    ], readonly=False, states={'Done': [('readonly', False)]})
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
    ], readonly=False, states={'Done': [('readonly', False)]})
    scale_used = fields.Selection([
        ('Numerical', 'Numerical'),
        ('Faces', 'Faces'),
        ('FLACC', 'FLACC'),
        ('ABBEY', 'ABBEY'),
    ], readonly=False, states={'Done': [('readonly', False)]})
    functional_activity_show = fields.Boolean()
    functional_activity = fields.Selection([
        ('No Limitation', 'No Limitation'),
        ('Mild Limitation', 'Mild Limitation'),
        ('Severe Limitation', 'Severe Limitation'),
    ], readonly=False, states={'Done': [('readonly', False)]})

    vital_signs_show = fields.Boolean()
    systolic_bp = fields.Integer(readonly=False, states={'Done': [('readonly', False)]})
    hr_min = fields.Integer(readonly=False, states={'Done': [('readonly', False)]})
    diastolic_br = fields.Integer(readonly=False, states={'Done': [('readonly', False)]})
    rr_min = fields.Integer(readonly=False, states={'Done': [('readonly', False)]})
    temperature_c = fields.Float(readonly=False, states={'Done': [('readonly', False)]})
    # o2_sat = fields.Float(readonly=False, states={'Done': [('readonly', False)]})
    o2_sat = fields.Selection([
        ('at room air', 'at room air'),
        ('with oxygen Support', 'with oxygen Support')
    ], readonly=False, states={'Done': [('readonly', False)]})
    char_other_oxygen = fields.Float(readonly=False, states={'Done': [('readonly', False)]})

    the_following_early_show = fields.Boolean()
    deterioration = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    systolic = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    heart_rate = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    respiratory_rate = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    difficulty_breathing = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    multiple_convulsion = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    chest_pain = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    progress_noted_show = fields.Boolean()
    care_rendered_show = fields.Boolean()
    progress_noted = fields.Text(readonly=False, states={'Done': [('readonly', False)]})
    care_rendered = fields.Text(readonly=False, states={'Done': [('readonly', False)]})

    # link to stoma care
    comprehensive_nurse_id = fields.Many2one('sm.shifa.comprehensive.nurse', string='Comprehensive Nurse',
                                             ondelete='cascade')
    notification_id = fields.One2many('sm.physician.notification', 'comprehensive_nurse_not_id',
                                      string='comprehensive notification')
    consent_show = fields.Boolean()
    consent_file1 = fields.Binary()
    consent_file2 = fields.Binary()

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
    # ++++++++++++++++++ wound Tab ++++++++++++++++++++++++#
    wound_history_show = fields.Boolean()
    wound_history = fields.Text(string='Wound History', readonly=False, states={'Done': [('readonly', False)]})
    # Type of Wound fields
    type_wound_show = fields.Boolean()
    surgical = fields.Boolean(string='Surgical', readonly=False, states={'Done': [('readonly', False)]})
    pressure_ulcer = fields.Boolean(string='Pressure Ulcer', readonly=False, states={'Done': [('readonly', False)]})
    diabetic = fields.Boolean(string='Diabetic', readonly=False, states={'Done': [('readonly', False)]})
    other_types = fields.Boolean(string='Other', readonly=False, states={'Done': [('readonly', False)]})
    other_types_content = fields.Char(readonly=False, states={'Done': [('readonly', False)]})

    # Factors Influencing Wound Healing
    factors_influencing_show = fields.Boolean()
    diabetes = fields.Boolean(string='Diabetes', readonly=False, states={'Done': [('readonly', False)]})
    immobility = fields.Boolean(string='Immobility', readonly=False, states={'Done': [('readonly', False)]})
    tissue_perfusion = fields.Boolean(string='Tissue perfusion', readonly=False, states={'Done': [('readonly', False)]})
    infection = fields.Boolean(string='Infection', readonly=False, states={'Done': [('readonly', False)]})

    incontinence = fields.Boolean(string='Incontinence', readonly=False, states={'Done': [('readonly', False)]})
    malnutrition = fields.Boolean(string='Malnutrition', readonly=False, states={'Done': [('readonly', False)]})
    immnuno_compromised = fields.Boolean(string='Immnuno compromised',  readonly=False, states={'Done': [('readonly', False)]})
    blood_related = fields.Boolean(string='Blood related', readonly=False, states={'Done': [('readonly', False)]})
    blood_related_content = fields.Char(readonly=False, states={'Done': [('readonly', False)]})
    other_factors = fields.Boolean(string='Other', readonly=False, states={'Done': [('readonly', False)]})
    other_factors_content = fields.Char(readonly=False, states={'Done': [('readonly', False)]})

    # Potential Risk
    potential_risk_show = fields.Boolean()
    infection_potential = fields.Boolean(string='Infection', readonly=False, states={'Done': [('readonly', False)]})
    Poor_healing = fields.Boolean(string='Poor healing', readonly=False, states={'Done': [('readonly', False)]})
    other_potential = fields.Boolean(string='Other', readonly=False, states={'Done': [('readonly', False)]})
    other_potential_content = fields.Char(readonly=False, states={'Done': [('readonly', False)]})

    # Measurable Goals
    wound_measurable_goals_show = fields.Boolean()
    free_signs_infection = fields.Boolean(string='Free from signs of infection',  readonly=False, states={'Done': [('readonly', False)]})
    increase_area_granulating_tissue = fields.Boolean(string='Increase in area granulating tissue',  readonly=False, states={'Done': [('readonly', False)]})
    free_skin_excoriation = fields.Boolean(string='Free from skin excoriation',  readonly=False, states={'Done': [('readonly', False)]})
    free_necrosis = fields.Boolean(string='Free from necrosis', readonly=False, states={'Done': [('readonly', False)]})
    # Annotation image
    annotation_image_show = fields.Boolean()
    annotation_image = fields.Binary(readonly=False, states={'Done': [('readonly', False)]})
    # wound assessment and dressing plan
    wound_assessment_dressing_show = fields.Boolean()
    add_new_wound_assessment = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    add_new_wound_assessment_date = fields.Date(string='Date',  readonly=False, states={'Done': [('readonly', False)]})
    add_other_wound_assessment = fields.Boolean()
    add_other_wound_assessment_date = fields.Date(string='Date',  readonly=False, states={'Done': [('readonly', False)]})
    wound_ids = fields.One2many('sm.shifa.wound.assessment.values', 'wound_comp_followup_id', string='Wound Assessment', readonly=False, states={'Done': [('readonly', False)]})

    wound_add = fields.One2many('sm.shifa.wound.assessment.values', 'wound_comp_followup_id', string='Wound Assessment', readonly=False, states={'Done': [('readonly', False)]})
    wound_new_add = fields.One2many('sm.shifa.wound.assessment.values', 'wound_comp_followup_id', string='Wound Assessment', readonly=False, states={'Done': [('readonly', False)]})
    nurse_wound_show = fields.Boolean()
    nurse_note_wound = fields.Text(readonly=False, states={'Done': [('readonly', False)]})

    # ++++++++++++++++++++++++Continence Tab+++++++++++++++++++++++++++++#
    type_continence_show = fields.Boolean()
    bladder = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    bowel = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})

    type_devices_used_show = fields.Boolean()
    indwelling_foley = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    suprapubic_catheter = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    urosheath_condom = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    diaper = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})

    con_potential_actual_risk_show = fields.Boolean()
    impaired_skin_integrity_related_bowel_or_bladder = fields.Selection(YES_NO_NA,  readonly=False, states={'Done': [('readonly', False)]})
    complications_related_indwelling_urinary_catheter = fields.Selection(YES_NO_NA,  readonly=False, states={'Done': [('readonly', False)]})

    con_measurable_goals_show = fields.Boolean()
    will_remain_clean_dry_free_from_urinary_or_faecal = fields.Selection(YES_NO_NA,  readonly=False, states={'Done': [('readonly', False)]})
    will_remain_free_signs_and_symptoms_of_complications = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})

    con_patient_assessment_show = fields.Boolean()
    color_urine = fields.Selection([
        ('Amber', 'Amber'),
        ('Light Yellow', 'Light Yellow'),
        ('Dark Yellow', 'Dark Yellow'),
        ('Cloudy', 'Cloudy'),
        ('Light Hematuria', 'Light Hematuria'),
        ('Gross Hematuria', 'Gross Hematuria'),
    ], readonly=False, states={'Done': [('readonly', False)]})
    con_consistency = fields.Selection([
        ('Clear', 'Clear'),
        ('With Blood Streak', 'With Blood Streak'),
        ('With Blood Clots', 'With Blood Clots'),
        ('With Sediments', 'With Sediments'),
    ], readonly=False, states={'Done': [('readonly', False)]})
    amount_ml = fields.Float(readonly=False, states={'Done': [('readonly', False)]})
    presence_urinary_frequency = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    diaper_changed = fields.Selection([
        ('2-3 times per day', '2-3 times per day'),
        ('3 times per day', '3 times per day'),
        ('3-4 times per day', '3-4 times per day'),
        ('4 times per day', '4 times per day'),
        ('4-5 times per day', '4-5 times per day'),
        ('NA', 'NA'),
    ], readonly=False, states={'Done': [('readonly', False)]})
    presence_burning = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    presence_foul_smelling = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    presence_altered_mental = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    catheter_still_required = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})

    urinaty_catheter_bag_show = fields.Boolean()
    secured_appropriately = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    bag_off_floor = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    bag_below_level = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    tubing_not_taut = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})

    catheter_change_show = fields.Boolean()
    catheter_change_done = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    type_of_catheter = fields.Selection([
        ('Silicone', 'Silicone'),
        ('Rubber/Latex', 'Rubber/Latex'),
        ('Condom', 'Condom'),
        ('Urosheath', 'Urosheath'),
        ('Suprapubic', 'Suprapubic'),
        ('Nephrostomy', 'Nephrostomy'),
    ], readonly=False, states={'Done': [('readonly', False)]})
    size_of_catheter = fields.Text(readonly=False, states={'Done': [('readonly', False)]})
    catheter_change_due_on = fields.Text(readonly=False, states={'Done': [('readonly', False)]})

    bowel_assessment_show = fields.Boolean()
    bowels_opened = fields.Selection([
        ('2 times daily', '2 times daily'),
        ('more than 5 times daily', 'more than 5 times daily'),
        ('more than 10 times daily', 'more than 10 times daily'),
        ('every 2 days', 'every 2 days'),
        ('every other day', 'every other day'),
        ('once a week', 'once a week'),
        ('Bowel not opened', 'Bowel not opened'),
    ], readonly=False, states={'Done': [('readonly', False)]})
    color_of_stool = fields.Selection([
        ('Brown', 'Brown'),
        ('Black', 'Black'),
        ('Reddish Brown', 'Reddish Brown'),
        ('Yellow', 'Yellow'),
        ('Green', 'Green'),
        ('Red', 'Red'),
    ], readonly=False, states={'Done': [('readonly', False)]})
    consistency_of_stool = fields.Selection([
        ('Hard', 'Hard'),
        ('Soft', 'Soft'),
        ('Loose', 'Loose'),
        ('Watery', 'Watery'),
        ('Mucoid', 'Mucoid'),
        ('NA', 'NA'),
    ], readonly=False, states={'Done': [('readonly', False)]})
    perineal_area = fields.Selection([
        ('Dry and intact', 'Dry and intact'),
        ('Excoriation', 'Excoriation'),
        ('Redness', 'Redness'),
        ('Blisters', 'Blisters'),
        ('NA', 'NA'),
    ], readonly=False, states={'Done': [('readonly', False)]})

    con_caregiver_assessment_show = fields.Boolean()
    maintain_patient_hygiene = fields.Selection([
        ('Well', 'Well'),
        ('Very Well', 'Very Well'),
        ('Yes', 'Yes'),
        ('No', 'No'),
        ('NA', 'NA'),
        ('Fair', 'Fair'),
        ('Poor', 'Poor'),
    ], readonly=False, states={'Done': [('readonly', False)]})
    use_incontinence_products = fields.Selection([
        ('Competent', 'Competent'),
        ('Yes', 'Yes'),
        ('No', 'No'),
        ('NA', 'NA'),
    ], readonly=False, states={'Done': [('readonly', False)]})
    keep_patient_odourless = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    ability_cope_care = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})

    con_patient_caregiver_education_show = fields.Boolean()
    patient_caregiver_should = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    maintain_fluids_high_fibre = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    drinking_least_litres_fluid = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    do_not_kink_clamp = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    always_attach_catheter = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    keep_closed_system_drainage = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    carers_should_wash_their = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    con_remarks_show = fields.Boolean()
    con_remarks = fields.Text(readonly=False, states={'Done': [('readonly', False)]})
    # +++++++++++++++++ Enteral Feeding Tab++++++++++++++++++++++++++#
    type_of_enteral_feeding_show = fields.Boolean()
    type_of_enteral_feeding = fields.Selection([
        ('Nasogastric Tube', 'Nasogastric Tube'),
        ('Gastrostomy Tube', 'Gastrostomy Tube'),
        ('Nasojejustomy', 'Nasojejustomy'),
        ('NA', 'NA'),
    ], readonly=False, states={'Done': [('readonly', False)]})
    feeding_regimen_show = fields.Boolean()
    feeding_regimen = fields.Selection([
        ('Bolus', 'Bolus'),
        ('Continuous', 'Continuous'),
    ], readonly=False, states={'Done': [('readonly', False)]})
    potential_actual_risk_show = fields.Boolean()
    potential_actual_complications_related = fields.Selection(YES_NO_NA,
                                                              readonly=False, states={'Done': [('readonly', False)]})
    potential_actual_risk_for_aspiration = fields.Selection(YES_NO_NA,
                                                            readonly=False, states={'Done': [('readonly', False)]})
    potential_actual_nutritional_status_changes = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    measurable_goals_show = fields.Boolean()
    measurable_goals_will_remain_free = fields.Selection(YES_NO_NA,
                                                         readonly=False, states={'Done': [('readonly', False)]})
    measurable_goals_will_maintain_adequate = fields.Selection(YES_NO_NA,
                                                               readonly=False, states={'Done': [('readonly', False)]})
    measurable_goals_will_not_develop = fields.Selection(YES_NO_NA,
                                                         readonly=False, states={'Done': [('readonly', False)]})
    ent_patient_assessment_show = fields.Boolean()
    patient_assessment_signs_of_aspiration = fields.Selection(YES_NO_NA,
                                                              readonly=False, states={'Done': [('readonly', False)]})
    patient_assessment_presence_of_bowel_sounds = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    patient_assessment_presence_of_constipation = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    patient_assessment_presence_of_diarrhoea = fields.Selection(YES_NO_NA,
                                                                readonly=False, states={'Done': [('readonly', False)]})
    patient_assessment_presence_nausea_vomiting = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    # patient_assessment_presence_abdominal_pain = fields.Selection(YES_NO_NA,
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
    ], readonly=False, states={'Done': [('readonly', False)]})
    patient_assessment_facial_skin = fields.Selection([
        ('Dry and Intact', 'Dry and Intact'),
        ('Hypergranulation', 'Hypergranulation'),
        ('NA', 'NA'),
        ('Excoriation', 'Excoriation'),
        ('Redness', 'Redness'),
        ('Blisters', 'Blisters'),
    ], readonly=False, states={'Done': [('readonly', False)]})
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
    ], readonly=False, states={'Done': [('readonly', False)]})
    patient_assessment_frequency_of_feeds = fields.Selection([
        ('Continous', 'Continous'),
        ('4 hourly', '4 hourly'),
        ('Hourly', 'Hourly'),
    ], readonly=False, states={'Done': [('readonly', False)]})
    patient_assessment_daily_nutritional_intake = fields.Selection([
        ('NA', 'NA'),
        ('Adequate', 'Adequate'),
        ('InAdequate', 'InAdequate'),
    ], readonly=False, states={'Done': [('readonly', False)]})
    patient_assessment_weight_change = fields.Selection([
        ('No Change', 'No Change'),
        ('Decrease', 'Decrease'),
        ('Increase', 'Increase'),
        ('NA', 'NA'),
    ], readonly=False, states={'Done': [('readonly', False)]})
    patient_assessment_change_nutritional_status = fields.Selection([
        ('No Change', 'No Change'),
        ('Positive Change', 'Positive Change'),
        ('Negative Change', 'Negative Change'),
    ], readonly=False, states={'Done': [('readonly', False)]})
    patient_assessment_nutritional_status = fields.Selection([
        ('Good', 'Good'),
        ('Fair', 'Fair'),
        ('Poor', 'Poor'),
        ('Cachexic', 'Cachexic'),
        ('Dehydrated', 'Dehydrated'),
        ('Emaciated', 'Emaciated'),
    ], readonly=False, states={'Done': [('readonly', False)]})
    patient_assessment_physical_apearance = fields.Selection([
        ('Adequately Nourished ', 'Adequately Nourished '),
        ('Malnourished', 'Malnourished'),
        ('At Risk of Malnutrition', 'At Risk of Malnutrition'),
        ('Obese', 'Obese'),
        ('NA', 'NA'),
    ], readonly=False, states={'Done': [('readonly', False)]})
    patient_assessment_refer_to_Dietician = fields.Selection(YES_NO_NA,
                                                             readonly=False, states={'Done': [('readonly', False)]})

    tube_change_show = fields.Boolean()
    tube_change_tube_change_done = fields.Selection(YES_NO_NA,
                                                    readonly=False, states={'Done': [('readonly', False)]})
    tube_change_type_of_tube = fields.Selection([
        ('Ryles', 'Ryles'),
        ('Silicone', 'Silicone'),
        ('PEG', 'PEG'),
        ('NA', 'NA'),
    ], readonly=False, states={'Done': [('readonly', False)]})
    tube_change_presence_gastric_residual_volume_checked = fields.Selection([
        ('Yes', 'Yes'),
        ('Nil', 'Nil'),
        ('NA', 'NA'),
    ], readonly=False, states={'Done': [('readonly', False)]})
    tube_change_gastric_ph_result = fields.Selection([
        ('less than 4.5', 'less than 4.5'),
        ('between 4.5 -5.5', 'between 4.5 -5.5'),
        ('Nil', 'Nil'),
        ('NA', 'NA'),
    ], readonly=False, states={'Done': [('readonly', False)]})
    tube_change_gastric_ph_checked = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    tube_change_initiate_feeding = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    tube_change_internal_ngt = fields.Integer(readonly=False, states={'Done': [('readonly', False)]})
    tube_change_external_ngt = fields.Integer(readonly=False, states={'Done': [('readonly', False)]})
    tube_change_ngt_size = fields.Float(readonly=False, states={'Done': [('readonly', False)]})
    tube_change_consent_signed_by = fields.Text(readonly=False, states={'Done': [('readonly', False)]})
    tube_change_next_due = fields.Date(readonly=False, states={'Done': [('readonly', False)]})

    ent_caregiver_assessment_show = fields.Boolean()
    caregiver_assessment_perform_tube_placement = fields.Selection(COMPETENT_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    caregiver_assessment_perform_enteral_feeding = fields.Selection(COMPETENT_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    caregiver_assessment_perform_gastrostomy_site = fields.Selection(YES_NO_NA_COMPETENT, readonly=False, states={'Done': [('readonly', False)]})
    caregiver_assessment_perform_mouth_care = fields.Selection(YES_NO_NA_COMPETENT,
                                                               readonly=False, states={'Done': [('readonly', False)]})
    caregiver_education_show = fields.Boolean()
    caregiver_education_wash_hands_thoroughly = fields.Selection(YES_NO_NA,
                                                                 readonly=False, states={'Done': [('readonly', False)]})
    caregiver_education_check_the_placement = fields.Selection(YES_NO_NA,
                                                               readonly=False, states={'Done': [('readonly', False)]})
    caregiver_education_raise_the_head = fields.Selection(YES_NO_NA,
                                                          readonly=False, states={'Done': [('readonly', False)]})
    caregiver_education_inform_home_care = fields.Selection(YES_NO_NA,
                                                            readonly=False, states={'Done': [('readonly', False)]})
    caregiver_education_reemphasize_education = fields.Selection(YES_NO_NA,
                                                                 readonly=False, states={'Done': [('readonly', False)]})
    ent_remarks_show = fields.Boolean()
    ent_remarks = fields.Text(readonly=False, states={'Done': [('readonly', False)]})

    # ++++++++++++++++++++++++++ Drain Tub Tab+++++++++++++++++++++++ #
    type_of_surgery_procedure_show = fields.Boolean()
    type_of_surgery_procedure = fields.Text(readonly=False, states={'Done': [('readonly', False)]})

    type_of_drain_catheter_show = fields.Boolean()
    drain_catheter_pleurx = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    drain_catheter_pigtail = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    drain_catheter_jackson_pratts = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    drain_catheter_other = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    drain_catheter_other_text = fields.Text(readonly=False, states={'Done': [('readonly', False)]})

    location_show = fields.Boolean()
    location_chest = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    location_abdomen = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    location_other = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    location_other_text = fields.Text(readonly=False, states={'Done': [('readonly', False)]})

    type_of_drainage_show = fields.Boolean()
    type_drainage_free_drainage = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    type_drainage_vacuum = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    type_drainage_other = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    type_drainage_other_text = fields.Text(readonly=False, states={'Done': [('readonly', False)]})

    dra_potential_actual_risk_show = fields.Boolean()
    drain_site_infection_other = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    seroma_formation_other = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    dislodgement_of_drain_tube_other = fields.Selection(YES_NO_NA,  readonly=False, states={'Done': [('readonly', False)]})

    dra_measurable_goals_show = fields.Boolean()
    drain_site_will_remain_free_from_infection = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    drainage_system_will_remain_patent_with = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    drain_tube_will_be_removed_if_less_than_mls = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    drain_remains_insitu_and_drainage_done_as = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})

    dra_patient_assessment_show = fields.Boolean()
    vital_signs_remain_within = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    patient_pain_under_control = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    performing_arm_exercises = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})

    drain_tube_site_assessment_show = fields.Boolean()
    dressing_dry_and_intact = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    presence_drain_site_infection = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    presence_of_leakage = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    nature_of_drainage = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    drainage_amount_last_24hrs = fields.Text(readonly=False, states={'Done': [('readonly', False)]})
    drain_tube_removed = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})

    dra_patient_caregiver_education_show = fields.Boolean()
    patient_understands_importance = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    actions_to_take_if_leaking = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    understands_when_suction = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    taking_analgesia_regularly = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    measuring_and_recording_drainage = fields.Selection(YES_NO_NA,  readonly=False, states={'Done': [('readonly', False)]})
    report_increase_of_temperature_change = fields.Selection(YES_NO_NA,readonly=False, states={'Done': [('readonly', False)]})
    discharge_education_post_removal = fields.Selection(YES_NO_NA,  readonly=False, states={'Done': [('readonly', False)]})
    self_drainage_procedure = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    dra_remarks_show = fields.Boolean()
    dra_remarks = fields.Text(readonly=False, states={'Done': [('readonly', False)]})
    # ++++++++++++++++++++++++ Stoma Tab +++++++++++++++++++++++++#
    type_surgery_show = fields.Boolean()
    type_surgery = fields.Text(readonly=False, states={'Done': [('readonly', False)]})
    sto_patient_assessment_show = fields.Boolean()
    vital_signs_remain = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    coping_with_changing = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    managing_skin = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    stoma_site_assessment_show = fields.Boolean()
    stoma_appliance_intact = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    presence_of_skin = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    nature_of_effluent = fields.Selection([
        ('Stool', 'Stool'),
        ('Urine', 'Urine'),
        ('Blood', 'Blood'),
        ('Bile', 'Bile'),
        ('Nil', 'Nil'),
    ], readonly=False, states={'Done': [('readonly', False)]})
    amount = fields.Integer(readonly=False, states={'Done': [('readonly', False)]})
    sto_consistency = fields.Selection([
        ('Hard', 'Hard'),
        ('Soft', 'Soft'),
        ('Loose', 'Loose'),
    ], readonly=False, states={'Done': [('readonly', False)]})
    follow_up_care_show = fields.Boolean()
    stoma_care_clinic = fields.Text(readonly=False, states={'Done': [('readonly', False)]})
    review_dates = fields.Text(readonly=False, states={'Done': [('readonly', False)]})
    sto_patient_caregiver_education_show = fields.Boolean()
    choose_outfit = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    eating_regular_ = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    drink_reqularly = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    observe_for_stomal = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    sto_remarks_show = fields.Boolean()
    sto_remarks = fields.Text(readonly=False, states={'Done': [('readonly', False)]})
    # +++++++++++++++++++++++++ Palliative Tab +++++++++++++++++++++ #
    palliative_care_type_show = fields.Boolean()
    pall_pain_management = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    symptom_management = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    subcutaneous_infusion = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    palliative_other = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    palliative_other_text = fields.Text(readonly=False, states={'Done': [('readonly', False)]})
    pall_potential_actual_risk_show = fields.Boolean()
    pain_related_to_disease_process = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    ineffective_pain_management = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    nutritional_deficit_related_to_poor_oral = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    nausea_and_or_vomiting_related_to_medication = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    constipation_related_to_medication_immobility_decrease = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    breathlessness_related_to_disease_process = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    psychosocial_issues_related_terminal_prognosis = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    pall_measurable_goals_show = fields.Boolean()
    will_maintain_adequate_level_of_comfort_as_evidenced_no_signs = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    verbalizing_relief_pain_with_ordered_medications = fields.Selection(YES_NO_NA,  readonly=False, states={'Done': [('readonly', False)]})
    will_function_at_optimal_level_within_limitations_imposed = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    verbalizing_satisfaction_with_level_of_comfort = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    will_demonstrate_adjustment_to_of_life_situation_by_verbally = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    expressing_through_words_or_actions_understanding_of_what = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})

    pall_patient_assessment_show = fields.Boolean()
    pall_presence_of_pain = fields.Selection(YES_NO, readonly=False, states={'Done': [('readonly', False)]})
    pain_relieve_with_medication = fields.Selection(YES_NO, readonly=False, states={'Done': [('readonly', False)]})
    presence_of_nausea = fields.Selection(YES_NO, readonly=False, states={'Done': [('readonly', False)]})
    presence_of_vomiting = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    presence_of_constipation = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    frequency = fields.Selection([
        ('Once', 'Once'),
        ('2-3 times per day', '2-3 times per day'),
        ('more than 4 times/dav', 'more than 4 times/dav'),
    ], readonly=False, states={'Done': [('readonly', False)]})

    narcotics_show = fields.Boolean()
    regular_dose = fields.Text(readonly=False, states={'Done': [('readonly', False)]})
    breakthrough_dose = fields.Text(readonly=False, states={'Done': [('readonly', False)]})
    no_of_breakthrough_dose = fields.Text(readonly=False, states={'Done': [('readonly', False)]})
    narcotic_supply_enough_till = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No'),
        ('For refill', 'For refill'),
    ], readonly=False, states={'Done': [('readonly', False)]})

    pall_caregiver_assessment_show = fields.Boolean()
    management_of_patient_pain = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    management_of_patient_nutrition = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    coping_psychologically = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    pall_coping_with_patient_care = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})

    pall_patient_caregiver_education_show = fields.Boolean()
    ensure_that_patient_taking_analgesia = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    ensure_that_there_sufficient_pain = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    advice_activity_movement_hour_after = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    advise_increase_fluids_tolerated = fields.Selection(YES_NO_NA,  readonly=False, states={'Done': [('readonly', False)]})
    advice_take_stool_softeners_for_constipation = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    encourage_mobility_tolerated = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    take_anti_emetics_minutes_before = fields.Selection(YES_NO_NA,  readonly=False, states={'Done': [('readonly', False)]})
    take_small_frequent_meals = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    pall_remarks_show = fields.Boolean()
    pall_remarks = fields.Text(readonly=False, states={'Done': [('readonly', False)]})
    # ++++++++++++++++++++ Anticoagulation Tab ++++++++++++++++++++++++++++++ #
    type_of_anticoagulation_show = fields.Boolean()
    type_warfarin = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    type_other = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    type_other_text = fields.Text(readonly=False, states={'Done': [('readonly', False)]})

    frequency_inr_monitoring_show = fields.Boolean()
    frequency_daily = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    frequency_weekly = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    frequency_as_pre_primary = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    frequency_bimonthly = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    frequency_other = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    frequency_other_text = fields.Text(readonly=False, states={'Done': [('readonly', False)]})

    ant_potential_actual_risk_show = fields.Boolean()
    potential_for_complication_injury_related_anti_coagulation = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    over_or_under_anticoagulation_related_to_non_compliance = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    over_or_under_therapeutic_level_inr_related_to_non_compliance = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    medication_error_related_to_inappropriate_taking_of_warfarin = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})

    ant_measurable_goals_show = fields.Boolean()
    will_be_remain_free_from_complications_bleeding_injury = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    inr_will_be_within_therapeutic_level = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    patient_will_be_compliant_with_taking_warfarin = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    there_will_be_no_medication_error_related_to_taking = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})

    ant_patient_assessment_show = fields.Boolean()
    vital_signs_normal = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    any_change_in_diet = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    develop_any_infection_that = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    presence_of_chest_pain = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    presence_of_short_of_breath = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    presence_of_bleeding = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    presence_of_bruising = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})

    medication_review_show = fields.Boolean()
    taken_warfarin_dose = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    any_new_medication_commenced = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    enough_appropriate_warfarin = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    started_on_antibiotics = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    ensure_that_patient_taking = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})

    ant_caregiver_assessment_show = fields.Boolean()
    administer_correct_warfarin_dose_since = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    understand_dosing_regime = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    medication_storage_appropriately = fields.Selection(YES_NO_NA,  readonly=False, states={'Done': [('readonly', False)]})
    one_reliable_family_member = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    caregiver_name_identified = fields.Text(readonly=False, states={'Done': [('readonly', False)]})

    ant_patient_caregiver_education_show = fields.Boolean()
    warfarin_tablets_to_be_given = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    to_report_missed_dose = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    check_with_home_care_staff_before = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    to_observe_for_any_bleeding = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    correct_technique_in_performing = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    rotate_injection_sites = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    ant_remarks_show = fields.Boolean()
    ant_remarks = fields.Text(readonly=False, states={'Done': [('readonly', False)]})
    # +++++++++++++++++++++++++++++++ Diabetic +++++++++++++++++++++++++ #
    type_hypoglycemic_show = fields.Boolean()
    oral = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    injection = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    oral_medication = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    oral_other = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    oral_other_text = fields.Text(readonly=False, states={'Done': [('readonly', False)]})
    injection_medication = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    injection_units = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    injection_other = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    injection_other_text = fields.Text(readonly=False, states={'Done': [('readonly', False)]})

    dia_potential_actual_risk_show = fields.Boolean()
    hyper_hypoglycemia_related_to_diabetes_mellitus = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    other_complications_related_to_diabetes_mellitus = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})

    dia_measurable_goals_show = fields.Boolean()
    complications_related_to_diabetes_mellitus = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    maintain_blood_sugar_level_within_acceptable = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    blood_sugar_levels_are_monitored_and_recorded = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})

    dia_patient_assessment_show = fields.Boolean()
    dia_vital_signs_within_normal = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    skin_integrity_intact = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    blood_sugar_level = fields.Integer(readonly=False, states={'Done': [('readonly', False)]})
    mmol_mmol_bolin = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    mg_di_bolin = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    mmol_mmol = fields.Selection([
        ('Pre Meal', 'Pre Meal'),
        ('Post Meal', 'Post Meal'),
        ('2 hrs Post Meal', '2 hrs Post Meal'),
        ('4 hrs Post Meal', '4 hrs Post Meal'),
    ], readonly=False, states={'Done': [('readonly', False)]})
    blood_sugar_control = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})

    nutrition_show = fields.Boolean()
    specific_dietary_needs = fields.Selection([
        ('Normal', 'Normal'),
        ('Soft', 'Soft'),
        ('Liquid', 'Liquid'),
        ('Diabetic', 'Diabetic'),
        ('Enteral', 'Enteral'),
    ], readonly=False, states={'Done': [('readonly', False)]})
    observing_dietary_intake = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    physical_appearance = fields.Selection([
        ('Adequately Nourished', 'Adequately Nourished'),
        ('Malnourished', 'Malnourished'),
        ('At Risk of Malnutrition', 'At Risk of Malnutrition'),
        ('NA', 'NA'),
    ], readonly=False, states={'Done': [('readonly', False)]})

    medication_show = fields.Boolean()
    diabetic_medication_discussed = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    compliant_medication_regimen = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    medication_review_done = fields.Text(readonly=False, states={'Done': [('readonly', False)]})

    dia_patient_caregiver_education_show = fields.Boolean()
    ensure_that_patient_monitors = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    patient_taking_appropriate = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    check_feet_daily_any = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    encourages_activities = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    aware_of_managing_hypoglycaemic_event = fields.Selection(YES_NO_NA,readonly=False, states={'Done': [('readonly', False)]})
    dia_remarks_show = fields.Boolean()
    dia_remarks = fields.Text(readonly=False, states={'Done': [('readonly', False)]})
    # ++++++++++++++++++++++++++++++ Parenteral Tab ++++++++++++++++++++++++#
    parenteral_route_show = fields.Boolean()
    peripheral_intravenous_cannula = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    p_i_c_c_line = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    central_catheter = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    subcutaneous = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    intramuscular = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    portacath = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    parenteral_other = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    parenteral_other_text = fields.Text(readonly=False, states={'Done': [('readonly', False)]})

    par_potential_actual_risk_show = fields.Boolean()
    blood_test_done = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})

    complications_related_to_parenteral_therapy = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    complications_related_to_parenteral_medications = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    local_irritation_inflammation_or_infection_related = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    no_complication_of_pulmonary_micro_embolism = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})

    par_measurable_goals_show = fields.Boolean()
    parenteral_device_remains_functional_as_evidence_by = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    no_parenteral_site_infection_as_evidence_by_site_free = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    no_systemic_infection_related_to_parenteral_site = fields.Selection(YES_NO_NA,  readonly=False, states={'Done': [('readonly', False)]})

    par_patient_assessment_show = fields.Boolean()
    par_vital_signs_within_normal = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    general_condition_improved = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    par_presence_of_pain = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    signs_of_phlebitis = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})

    catheter_site_assessment_show = fields.Boolean()
    leakage_from_site = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    site_dressing_attended = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    device_resited = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    p_i_line_exposed_tube_daily = fields.Float(readonly=False, states={'Done': [('readonly', False)]})

    infusion_device_show = fields.Boolean()
    correct_infusion_administered = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    parameters_updated = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    infusion_therapy_started = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    batteries_changed_checked = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})

    par_caregiver_assessment_show = fields.Boolean()
    par_coping_with_patient_care = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    able_to_troubleshoot_device = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    care_of_parenteral_site = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    compliant_to_education = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})

    par_patient_caregiver_education_show = fields.Boolean()
    aware_of_action_and_side_effects = fields.Selection(YES_NO_NA,  readonly=False, states={'Done': [('readonly', False)]})
    care_iv_access_at_home_during = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    par_pain_management = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    advice_on_activity_tolerated = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    trouble_shoot_infusion_device = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    to_inform_home_care_when_parenteral_site = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    par_remarks_show = fields.Boolean()
    par_remarks = fields.Text(readonly=False, states={'Done': [('readonly', False)]})
    apply_warm_compress_to_injection_site = fields.Selection(YES_NO_NA,readonly=False, states={'Done': [('readonly', False)]})

    # +++++++++++++++++++++ Nebulization tab +++++++++++++++++++ #

    potential_acual_risk_show = fields.Boolean()
    risk_for_faster_heartbeat = fields.Selection(YES_NO, readonly=False, states={'Done': [('readonly', False)]})
    risk_for_slightly_shaking_muscles = fields.Selection(YES_NO, readonly=False, states={'Done': [('readonly', False)]})

    measurable_goals_review_date_show = fields.Boolean()
    fast_relief_from_inflammation_and_allowing = fields.Selection(YES_NO, readonly=False, states={'Done': [('readonly', False)]})

    patient_assessment_show = fields.Boolean()
    has_productive_cough = fields.Selection(YES_NO, readonly=False, states={'Done': [('readonly', False)]})
    obvious_nasal_flaring_shortness_breath = fields.Selection(YES_NO, readonly=False, states={'Done': [('readonly', False)]})
    breathing_easier_after_nebulization = fields.Selection(YES_NO, readonly=False, states={'Done': [('readonly', False)]})

    patient_caregiver_education_show = fields.Boolean()
    lifestyle_changes_treat_shortness_breath = fields.Selection(YES_NO, readonly=False, states={'Done': [('readonly', False)]})
    educate_deep_breathing_exercises = fields.Selection(YES_NO,  readonly=False, states={'Done': [('readonly', False)]})
    avoiding_exposure_pollutants_allergens = fields.Selection(YES_NO, readonly=False, states={'Done': [('readonly', False)]})
    comply_medication_prescribed = fields.Selection(YES_NO, readonly=False, states={'Done': [('readonly', False)]})

    remarks_show = fields.Boolean()
    remarks = fields.Text( readonly=False, states={'Done': [('readonly', False)]})

    # +++++++++++++++++++++++++++ newborn tab ++++++++++++++++++++++ #
    clinical_assessments_show = fields.Boolean()
    head_normal = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    head_abnormal = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    head_abnormal_content = fields.Char(readonly=False, states={'Done': [('readonly', False)]})
    skin_normal = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    skin_abnormal = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    skin_abnormal_content = fields.Char(readonly=False, states={'Done': [('readonly', False)]})
    lunge_normal = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    lunge_abnormal = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    lunge_abnormal_content = fields.Char(readonly=False, states={'Done': [('readonly', False)]})
    chest_normal = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    chest_abnormal = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    chest_abnormal_content = fields.Char(readonly=False, states={'Done': [('readonly', False)]})
    abdomen_normal = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    abdomen_abnormal = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    abdomen_abnormal_content = fields.Char(readonly=False, states={'Done': [('readonly', False)]})
    elimination_normal = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    elimination_abnormal = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    elimination_abnormal_content = fields.Char(readonly=False, states={'Done': [('readonly', False)]})
    genitalia_normal = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    genitalia_abnormal = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    genitalia_abnormal_content = fields.Char(readonly=False, states={'Done': [('readonly', False)]})
    extremities_normal = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    extremities_abnormal = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    extremities_abnormal_content = fields.Char(readonly=False, states={'Done': [('readonly', False)]})
    number_of_diaper_per_day = fields.Integer(readonly=False, states={'Done': [('readonly', False)]})
    number_of_stools_per_day = fields.Integer(readonly=False, states={'Done': [('readonly', False)]})
    adequate_amount_diapers_home = fields.Selection(YES_NO, readonly=False, states={'Done': [('readonly', False)]})
    adequate_amount_diapers_home_text = fields.Char(readonly=False, states={'Done': [('readonly', False)]})
    circumcised = fields.Selection(YES_NO, readonly=False, states={'Done': [('readonly', False)]})

    mental_assessments_show = fields.Boolean()
    amount_crying_normal = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    amount_crying_abnormal = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    amount_crying_abnormal_content = fields.Char(readonly=False, states={'Done': [('readonly', False)]})
    makes_eye_contact_normal = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    makes_eye_contact_abnormal = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    makes_eye_contact_abnormal_content = fields.Char(readonly=False, states={'Done': [('readonly', False)]})
    quiet_when_pick_normal = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    quiet_when_pick_abnormal = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    quiet_when_pick_abnormal_content = fields.Char(readonly=False, states={'Done': [('readonly', False)]})

    feeding_type = fields.Selection([
        ('Breast', 'Breast'),
        ('Bottle', 'Bottle'),
        ('Breast and Bottle', 'Breast and Bottle'),
    ], readonly=False, states={'Done': [('readonly', False)]})
    formula_feeding = fields.Text(readonly=False, states={'Done': [('readonly', False)]})
    amount_frequency = fields.Text(readonly=False, states={'Done': [('readonly', False)]})
    adequate_amount_of_formula = fields.Selection(YES_NO, readonly=False, states={'Done': [('readonly', False)]})
    adequate_amount_of_formula_text = fields.Char(readonly=False, states={'Done': [('readonly', False)]})

    other_assessment_show = fields.Boolean()
    other_assessment_show_text = fields.Text(readonly=False, states={'Done': [('readonly', False)]})

    immunization_show = fields.Boolean()
    received_initial_hepatitis = fields.Selection(YES_NO, readonly=False, states={'Done': [('readonly', False)]})
    where_and_when = fields.Text(readonly=False, states={'Done': [('readonly', False)]})
    has_an_appointment_been = fields.Selection(YES_NO, readonly=False, states={'Done': [('readonly', False)]})
    has_an_appointment_been_date = fields.Date(readonly=False, states={'Done': [('readonly', False)]})
    has_an_appointment_been_where = fields.Char(readonly=False, states={'Done': [('readonly', False)]})
    has_an_appointment_been_no_text = fields.Text(readonly=False, states={'Done': [('readonly', False)]})

    safe_sleep_show = fields.Boolean()
    crib = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    bassinet = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    other = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    other_content = fields.Char(readonly=False, states={'Done': [('readonly', False)]})

    mother_caregiver_education_show = fields.Boolean()
    advise_to_refrain_putting_stuffed_animals = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    advise_that_sleep_environment_should = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    advise_not_to_share_sleep = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    advise_on_proper_position = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    advise_to_refrain_from_smoking = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    advise_to_change_clothes_before_holding = fields.Selection(YES_NO_NA,  readonly=False, states={'Done': [('readonly', False)]})
    advise_that_supervision_needed_when = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    # +++++++++++++++++++++++++++++ Oxygen Administration tab ++++++++++++++++++++++++++++++ #
    type_of_oxygen_inhalation_show = fields.Boolean()
    type_of_oxygen_inhalation = fields.Selection([
        ('Nosal', 'Nosal'),
        ('Face Mask', 'Face Mask'),
        ('High Flow', 'High Flow'),
    ], readonly=False, states={'Done': [('readonly', False)]})

    risk_for_dry_or_bloody_nose = fields.Selection(YES_NO, readonly=False, states={'Done': [('readonly', False)]})
    risk_for_oxygen_toxicity = fields.Selection(YES_NO, readonly=False, states={'Done': [('readonly', False)]})

    to_achieve_adequate_tissue_oxygenation = fields.Selection(YES_NO,
                                                              readonly=False, states={'Done': [('readonly', False)]})

    presence_of_shortness_of_breath = fields.Selection(YES_NO,
                                                       readonly=False, states={'Done': [('readonly', False)]})
    presence_of_cough = fields.Selection(YES_NO,
                                         readonly=False, states={'Done': [('readonly', False)]})
    presence_of_chest_pain_due_to_excessive_coughing = fields.Selection(YES_NO,
                                                                         readonly=False, states={'Done': [('readonly', False)]})

    applies_safe_use_equipment_procedure_practice = fields.Selection(YES_NO, readonly=False, states={'Done': [('readonly', False)]})
    never_smoke_and_don_let_others_light_near_you = fields.Selection(YES_NO, readonly=False, states={'Done': [('readonly', False)]})
    keep_oxygen_containers_upright = fields.Selection(YES_NO,
                                                      readonly=False, states={'Done': [('readonly', False)]})

    # ++++++++++++++++++++++++++++ pressure ulcer tab ++++++++++++++++++++++++++ #
    type_impaired_show = fields.Boolean()
    bedridden = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    wheelchair = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    ambulates_assistance = fields.Selection([
        ('Cane', 'Cane'),
        ('Walking Frame', 'Walking Frame'),
        ('Elbow Crutches', 'Elbow Crutches'),
        ('Axillary Crutches', 'Axillary Crutches'),
        ('Patient is Ambulatory', 'Patient is Ambulatory'),
        ('NA', 'NA'),
    ], readonly=False, states={'Done': [('readonly', False)]})

    press_potential_actual_risk_show = fields.Boolean()
    risk_for_falls_related_to_impaired_mobility = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    fall_risk_assessment_done = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    pressure_ulcer_altered_skin_integrity_related = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    complications_related_to_urinary_bowel_incontinence = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})

    press_measurable_goals_show = fields.Boolean()
    free_from_injury_related_to_falls = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    free_from_skin_redness_blisters_or_discoloration = fields.Selection(YES_NO_NA,  readonly=False, states={'Done': [('readonly', False)]})
    skin_will_be_clean_dry_with_appropriate_and_prompt = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})

    skin_clean_dry_odor = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    any_changes_skin = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    use_pressure_relief = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    patient_assessment_other = fields.Text(readonly=False, states={'Done': [('readonly', False)]})

    caregiver_assessment_show = fields.Boolean()
    maintained_patients_general = fields.Selection([
        ('Well', 'Well'),
        ('Very Well', 'Very Well'),
        ('Fair', 'Fair'),
        ('Poor', 'Poor'),
    ], readonly=False, states={'Done': [('readonly', False)]})
    performed_hourly_turning = fields.Selection(YES_NO_NA_COMPETENT,  readonly=False, states={'Done': [('readonly', False)]})
    continence_care = fields.Selection(YES_NO_NA_COMPETENT, readonly=False, states={'Done': [('readonly', False)]})
    skin_care = fields.Selection(YES_NO_NA_COMPETENT, readonly=False, states={'Done': [('readonly', False)]})

    maintain_oral_intake = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})

    Patient_caregiver_education_show = fields.Boolean()
    ensure_that_patient_hygiene = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    turn_change_patient_position = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    apply_moisturiser_skin = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    inform_home_care_nurse = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})

    key_performance_indicator_show = fields.Boolean()
    development_new_pressure = fields.Selection([
        ('No', 'No'),
        ('Yes-Home Acquired', 'Yes-Home Acquired'),
        ('Yes-Hospital Acquired', 'Yes-Hospital Acquired'),
    ], readonly=False, states={'Done': [('readonly', False)]})
    since_last_visit = fields.Selection([
        ('No Event', 'No Event'),
        ('Presented to Emergency Unit', 'Presented to Emergency Unit'),
        ('Readmitted to KFMC Hospital', 'Readmitted to KFMC Hospital'),
        ('Readmitted to Other Hospital', 'Readmitted to Other Hospital'),
        ('Seen by private doctor', 'Seen by private doctor'),
    ], readonly=False, states={'Done': [('readonly', False)]})

    # +++++++++++++++++++++++++ postnatal tab ++++++++++++++++++++++ #
    postnatal_day_show = fields.Boolean()
    postnatal_day = fields.Integer(readonly=False, states={'Done': [('readonly', False)]})

    type_of_delivery_show = fields.Boolean()
    normal_delivery = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    casarean_delivery = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    delivery_other = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    delivery_other_text = fields.Text(readonly=False, states={'Done': [('readonly', False)]})

    pos_potential_actual_risk_show = fields.Boolean()
    risk_for_infection_related_to_episiotomy_post = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    alteration_in_comfort_pain_related_to_episiotomy = fields.Selection(YES_NO_NA,  readonly=False, states={'Done': [('readonly', False)]})
    risk_for_fluid_volume_deficit_related_to_vaginal_bleeding = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    risk_for_maternal_injury_related_to_tissue_oedema_and = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})

    pos_measurable_goals_show = fields.Boolean()
    will_be_able_to_demonstrate_proper_perineal_care = fields.Selection(YES_NO_NA,  readonly=False, states={'Done': [('readonly', False)]})
    will_maintain_adequate_level_of_comfort_as_evidenced_by_pain = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    vital_signs_remain_stable_with_moderate_amount_of_lochia = fields.Selection(YES_NO_NA, readonly=True,
                                                                                states={'Start': [('readonly', False)]})
    free_of_signs_of_cerebral_ischemia_within = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})

    vital_signs_stable = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    presence_of_headache = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    change_in_vision = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    breast = fields.Selection([
        ('Hard', 'Hard'),
        ('Swollen', 'Swollen'),
        ('Painful', 'Painful'),
    ], readonly=False, states={'Done': [('readonly', False)]})
    uterus = fields.Selection([
        ('Fundus Firm', 'Fundus Firm'),
        ('Not palpable', 'Not palpable'),
        ('NA', 'NA'),
    ], readonly=False, states={'Done': [('readonly', False)]})
    bowel_pattem = fields.Selection([
        ('Normal', 'Normal'),
        ('Abnormal', 'Abnormal'),
    ], readonly=False, states={'Done': [('readonly', False)]})
    postnatal_bladder = fields.Selection([
        ('Voiding comfortaness', 'Voiding comfortaness'),
        ('Fullness/with pressure', 'Fullness/with pressure'),
    ], readonly=False, states={'Done': [('readonly', False)]})
    abdominal_incision = fields.Selection([
        ('not inflamed', 'not inflamed'),
        ('no drainage', 'no drainage'),
        ('little drainage', 'little drainage'),
        ('staple present', 'staple present'),
        ('dressing intact', 'dressing intact'),
        ('decrease swelling', 'decrease swelling'),
    ], readonly=False, states={'Done': [('readonly', False)]})
    episiotomy_episiorapphy = fields.Selection([
        ('Intact', 'Intact'),
        ('Small tearing', 'Small tearing'),
        ('with bruising or', 'with bruising or'),
        ('swelling', 'swelling'),
    ], readonly=False, states={'Done': [('readonly', False)]})
    lochia = fields.Selection([
        ('Fleslage smelly', 'Fleslage smelly'),
        ('Rubra serosa', 'Rubra serosa'),
        ('lochia serosa', 'lochia serosa'),
        ('darie red', 'darie red'),
        ('discharges', 'discharges'),
        ('lochia alba', 'lochia alba'),
    ], readonly=False, states={'Done': [('readonly', False)]})
    homan_sign = fields.Selection([
        ('unilateral calf pain', 'unilateral calf pain'),
        ('negative DVT', 'negative DVT'),
        ('Redness', 'Redness'),
        ('Swollen', 'Swollen'),
    ], readonly=False, states={'Done': [('readonly', False)]})

    postnatal_specific_dietary_needs = fields.Selection([
        ('Diabetic', 'Diabetic'),
        ('low salt', 'low salt'),
        ('law fat', 'law fat'),
        ('high fiber', 'high fiber'),
        ('low salt, low fat', 'low salt, low fat'),
        ('Regular diet', 'Regular diet'),
    ], readonly=False, states={'Done': [('readonly', False)]})

    oral_medication_discussed = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    patient_caregiver_able = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    postnatal_medication_review_done = fields.Selection(YES_NO_NA,  readonly=False, states={'Done': [('readonly', False)]})
    next_review_due = fields.Text(readonly=False, states={'Done': [('readonly', False)]})

    advised_on_well_balanced_nutrition_fluids = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    advised_on_ambulation_to_prevent = fields.Selection(YES_NO_NA,  readonly=False, states={'Done': [('readonly', False)]})
    report_to_emergency_department_for_sudden = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    report_to_emergency_department_for_headache = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    report_to_emergency_department_for_unilateral = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    advise_to_take_prescribed_analgesia = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    advise_to_palpate_fundus_and_able_to_demonstrate = fields.Selection(YES_NO_NA,  readonly=False, states={'Done': [('readonly', False)]})
    advise_to_empty_bladder_and_be_aware_of_need = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    encourage_to_splint_abdomen_with_pillow_when = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    observe_for_increased_bleeding_on_post = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    advise_refrain_form_tub_bath_until_dressings = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    advise_to_use_good_body_mechanics_and_avoiding = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    advise_on_frequent_breastfeeding_to_help_prevent = fields.Selection(YES_NO_NA,  readonly=False, states={'Done': [('readonly', False)]})
    advise_on_using_non_restricting_bra = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    advise_on_massaging_breast_gently_and_manually_express_milk = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    advise_application_of_warm_compresses_shower_or_breast = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    advise_on_care_support_and_breastfeeding_technique_for_women = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    advise_on_hand_hygiene = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    advise_on_voiding_comfort_measure = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    advise_on_lochia_and_perineum_comfort = fields.Selection(YES_NO_NA,readonly=False, states={'Done': [('readonly', False)]})
    advise_on_activities_and_rest = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    advise_on_normal_patterns_of_emotional_changes = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})
    advise_on_proper_breastfeeding_technique = fields.Selection(YES_NO_NA, readonly=False, states={'Done': [('readonly', False)]})

    key_performance_indictor_show = fields.Boolean()
    hospital_readmission = fields.Text(readonly=False, states={'Done': [('readonly', False)]})
    since_last_visit_patient_was = fields.Text(readonly=False, states={'Done': [('readonly', False)]})
    # trache tab
    type_tracheostomy_inserted_show = fields.Boolean()
    type_tracheostomy_inserted = fields.Selection([
        ('Cuff Tube', 'Cuff Tube'),
        ('Uncuffed Tube', 'Uncuffed Tube'),
    ])
    type_tracheostomy_inserted_text = fields.Text()

    impaired_skin_integrity_surrounding_stoma = fields.Selection(YES_NO)
    improper_fitting_care_appliance_skin = fields.Selection(YES_NO)

    skin_integrity_around_stoma_will = fields.Selection(YES_NO)
    patient_caregiver_will_demonstrate_behaviours = fields.Selection(YES_NO)

    breathing_effectively = fields.Selection(YES_NO)
    coping_with_presence_of_tracheostomy = fields.Selection(YES_NO)
    managing_skin_integrity_around = fields.Selection(YES_NO)

    presence_of_hypergranulation = fields.Selection(YES_NO)
    presence_of_excoriation = fields.Selection(YES_NO)
    stoma_dressind_done = fields.Selection(YES_NO)

    change_trache_ties_every_other = fields.Selection(YES_NO)
    use_finger_technique_to_determine = fields.Selection(YES_NO)
    observe_for_stomal_complications_and_report = fields.Selection(YES_NO)
    demonstrate_safe_use_of_equipment_and = fields.Selection(YES_NO)

    # +++++++++++++++++++++++++ vaccines tab +++++++++++++++++++++++ #
    check_prior_show = fields.Boolean()
    drug_allergy_yes = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    drug_allergy_no = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    drug_allergy_content = fields.Char(readonly=False, states={'Done': [('readonly', False)]})

    allergic_previous_yes = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    allergic_previous_no = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    allergic_previous_content = fields.Char(readonly=False, states={'Done': [('readonly', False)]})

    allergic_hypersensitivty_yes = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    allergic_hypersensitivty_no = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    allergic_hypersensitivty_content = fields.Char(readonly=False, states={'Done': [('readonly', False)]})

    any_recent_illness_yes = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    any_recent_illness_no = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    any_recent_illness_content = fields.Char(readonly=False, states={'Done': [('readonly', False)]})

    previous_vaccination_yes = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    previous_vaccination_no = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    previous_vaccination_content = fields.Char(readonly=False, states={'Done': [('readonly', False)]})
    previous_vaccination_temp = fields.Float(readonly=False, states={'Done': [('readonly', False)]})
    # ====================================================================
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
    ], readonly=False, states={'Done': [('readonly', False)]})
    ADMINISTERED_OVER = [
        ('Right', 'Right'),
        ('Left', 'Left'),
    ]
    at_birth_hepb = fields.Boolean(string='HepB (0.5 ml)', readonly=False, states={'Done': [('readonly', False)]})
    at_birth_hepb_vaccine_no = fields.Char(string='Vaccine Lot No',  readonly=False, states={'Done': [('readonly', False)]})
    at_birth_hepb_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Done': [('readonly', False)]})
    at_birth_hepb_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over',  readonly=False, states={'Done': [('readonly', False)]})
    add_other_at_birth = fields.Boolean(string='Other', readonly=False, states={'Done': [('readonly', False)]})
    add_other_at_birth_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=False, states={'Done': [('readonly', False)]})
    add_other_at_birth_vaccine_no = fields.Char(string='Vaccine Lot No',  readonly=False, states={'Done': [('readonly', False)]})
    add_other_at_birth_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Done': [('readonly', False)]})
    add_other_at_birth_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Done': [('readonly', False)]})

    add_other_at_birth_comment = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})
    add_other2_at_birth = fields.Boolean(string='Other', readonly=False, states={'Done': [('readonly', False)]})
    add_other2_at_birth_vaccinations = fields.Selection(VACCINATION, string='Vaccination',  readonly=False, states={'Done': [('readonly', False)]})
    add_other2_at_birth_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})
    add_other2_at_birth_expiry_date = fields.Date(string='Expiry Date',  readonly=False, states={'Done': [('readonly', False)]})
    add_other2_at_birth_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over',  readonly=False, states={'Done': [('readonly', False)]})

    add_other2_at_birth_comment = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})

    t_mon_hepb = fields.Boolean(string='HepB (0.5 ml)', readonly=False, states={'Done': [('readonly', False)]})
    t_mon_hepb_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})
    t_mon_hepb_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Done': [('readonly', False)]})
    t_mon_hepb_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Done': [('readonly', False)]})

    t_mon_rv = fields.Boolean(string='RV (1 ml)', readonly=False, states={'Done': [('readonly', False)]})
    t_mon_rv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})
    t_mon_rv_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Done': [('readonly', False)]})
    t_mon_rv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Done': [('readonly', False)]})

    t_mon_dtap = fields.Boolean(string='D TaP (0.5 ml)', readonly=False, states={'Done': [('readonly', False)]})
    t_mon_dtap_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})
    t_mon_dtap_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Done': [('readonly', False)]})
    t_mon_dtap_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Done': [('readonly', False)]})

    t_mon_hib = fields.Boolean(string='Hib (0.5 ml)', readonly=False, states={'Done': [('readonly', False)]})
    t_mon_hib_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})
    t_mon_hib_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Done': [('readonly', False)]})
    t_mon_hib_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Done': [('readonly', False)]})

    t_mon_pcv = fields.Boolean(string='PCV (0.5 ml)', readonly=False, states={'Done': [('readonly', False)]})
    t_mon_pcv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})
    t_mon_pcv_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Done': [('readonly', False)]})
    t_mon_pcv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Done': [('readonly', False)]})

    t_mon_ipv = fields.Boolean(string='IPV (0.5 ml)', readonly=False, states={'Done': [('readonly', False)]})
    t_mon_ipv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})
    t_mon_ipv_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Done': [('readonly', False)]})
    t_mon_ipv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Done': [('readonly', False)]})

    add_other_t_mon = fields.Boolean(string='Other', readonly=False, states={'Done': [('readonly', False)]})
    add_other_t_mon_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=False, states={'Done': [('readonly', False)]})
    add_other_t_mon_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})
    add_other_t_mon_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Done': [('readonly', False)]})
    add_other_t_mon_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Done': [('readonly', False)]})

    add_other_t_mon_comment = fields.Char(string='Vaccine Lot No',  readonly=False, states={'Done': [('readonly', False)]})
    add_other2_t_mon = fields.Boolean(string='Other', readonly=False, states={'Done': [('readonly', False)]})
    add_other2_t_mon_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=False, states={'Done': [('readonly', False)]})
    add_other2_t_mon_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})
    add_other2_t_mon_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Done': [('readonly', False)]})
    add_other2_t_mon_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Done': [('readonly', False)]})

    add_other2_t_mon_comment = fields.Char(string='Vaccine Lot No',  readonly=False, states={'Done': [('readonly', False)]})

    f_mon_hepb = fields.Boolean(string='HepB (0.5 ml)', readonly=False, states={'Done': [('readonly', False)]})
    f_mon_hepb_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})
    f_mon_hepb_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Done': [('readonly', False)]})
    f_mon_hepb_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Done': [('readonly', False)]})

    f_mon_rv = fields.Boolean(string='RV (1 ml)', readonly=False, states={'Done': [('readonly', False)]})
    f_mon_rv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})
    f_mon_rv_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Done': [('readonly', False)]})
    f_mon_rv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Done': [('readonly', False)]})

    f_mon_dtap = fields.Boolean(string='D TaP (0.5 ml)', readonly=False, states={'Done': [('readonly', False)]})
    f_mon_dtap_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})
    f_mon_dtap_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Done': [('readonly', False)]})
    f_mon_dtap_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Done': [('readonly', False)]})

    f_mon_hib = fields.Boolean(string='Hib (0.5 ml)', readonly=False, states={'Done': [('readonly', False)]})
    f_mon_hib_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})
    f_mon_hib_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Done': [('readonly', False)]})
    f_mon_hib_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Done': [('readonly', False)]})

    f_mon_pcv = fields.Boolean(string='PCV (0.5 ml)', readonly=False, states={'Done': [('readonly', False)]})
    f_mon_pcv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})
    f_mon_pcv_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Done': [('readonly', False)]})
    f_mon_pcv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Done': [('readonly', False)]})
    f_mon_ipv = fields.Boolean(string='IPV (0.5 ml)', readonly=False, states={'Done': [('readonly', False)]})
    f_mon_ipv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})
    f_mon_ipv_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Done': [('readonly', False)]})
    f_mon_ipv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Done': [('readonly', False)]})

    add_other_f_mon = fields.Boolean(string='Other', readonly=False, states={'Done': [('readonly', False)]})
    add_other_f_mon_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=False, states={'Done': [('readonly', False)]})
    add_other_f_mon_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})
    add_other_f_mon_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Done': [('readonly', False)]})
    add_other_f_mon_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Done': [('readonly', False)]})

    add_other_f_mon_comment = fields.Char(string='Vaccine Lot No',  readonly=False, states={'Done': [('readonly', False)]})
    add_other2_f_mon = fields.Boolean(string='Other', readonly=False, states={'Done': [('readonly', False)]})
    add_other2_f_mon_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=False, states={'Done': [('readonly', False)]})
    add_other2_f_mon_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})
    add_other2_f_mon_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Done': [('readonly', False)]})
    add_other2_f_mon_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Done': [('readonly', False)]})

    add_other2_f_mon_comment = fields.Char(string='Vaccine Lot No',  readonly=False, states={'Done': [('readonly', False)]})

    s_mon_hepb = fields.Boolean(string='HepB (0.5 ml)', readonly=False, states={'Done': [('readonly', False)]})
    s_mon_hepb_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})
    s_mon_hepb_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Done': [('readonly', False)]})
    s_mon_hepb_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Done': [('readonly', False)]})

    s_mon_rv = fields.Boolean(string='RV (1 ml)', readonly=False, states={'Done': [('readonly', False)]})
    s_mon_rv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})
    s_mon_rv_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Done': [('readonly', False)]})
    s_mon_rv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Done': [('readonly', False)]})

    s_mon_dtap = fields.Boolean(string='D TaP (0.5 ml)', readonly=False, states={'Done': [('readonly', False)]})
    s_mon_dtap_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})
    s_mon_dtap_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Done': [('readonly', False)]})

    s_mon_dtap_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Done': [('readonly', False)]})

    s_mon_hib = fields.Boolean(string='Hib (0.5 ml)', readonly=False, states={'Done': [('readonly', False)]})
    s_mon_hib_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})
    s_mon_hib_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Done': [('readonly', False)]})
    s_mon_hib_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Done': [('readonly', False)]})

    s_mon_pcv = fields.Boolean(string='PCV (0.5 ml)', readonly=False, states={'Done': [('readonly', False)]})
    s_mon_pcv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})
    s_mon_pcv_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Done': [('readonly', False)]})
    s_mon_pcv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Done': [('readonly', False)]})

    s_mon_ipv = fields.Boolean(string='IPV (0.5 ml)', readonly=False, states={'Done': [('readonly', False)]})
    s_mon_ipv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})
    s_mon_ipv_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Done': [('readonly', False)]})
    s_mon_ipv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Done': [('readonly', False)]})

    s_mon_bcg = fields.Boolean(string='BCG (0.5 ml)', readonly=False, states={'Done': [('readonly', False)]})
    s_mon_bcg_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})
    s_mon_bcg_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Done': [('readonly', False)]})
    s_mon_bcg_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Done': [('readonly', False)]})

    s_mon_opv = fields.Boolean(string='OPV (2 gtts)', readonly=False, states={'Done': [('readonly', False)]})
    s_mon_opv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})
    s_mon_opv_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Done': [('readonly', False)]})
    s_mon_opv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Done': [('readonly', False)]})

    add_other_s_mon = fields.Boolean(string='Other', readonly=False, states={'Done': [('readonly', False)]})
    add_other_s_mon_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=False, states={'Done': [('readonly', False)]})
    add_other_s_mon_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})
    add_other_s_mon_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Done': [('readonly', False)]})
    add_other_s_mon_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Done': [('readonly', False)]})

    add_other_s_mon_comment = fields.Char(string='Vaccine Lot No',  readonly=False, states={'Done': [('readonly', False)]})
    add_other2_s_mon = fields.Boolean(string='Other', readonly=False, states={'Done': [('readonly', False)]})
    add_other2_s_mon_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=False, states={'Done': [('readonly', False)]})
    add_other2_s_mon_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})
    add_other2_s_mon_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Done': [('readonly', False)]})
    add_other2_s_mon_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Done': [('readonly', False)]})

    add_other2_s_mon_comment = fields.Char(string='Vaccine Lot No',  readonly=False, states={'Done': [('readonly', False)]})

    n_mon_measels = fields.Boolean(string='Measels (0.5 ml)', readonly=False, states={'Done': [('readonly', False)]})
    n_mon_measels_vaccine_no = fields.Char(string='Vaccine Lot No',  readonly=False, states={'Done': [('readonly', False)]})
    n_mon_measels_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Done': [('readonly', False)]})
    n_mon_measels_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over',  readonly=False, states={'Done': [('readonly', False)]})

    n_mon_mcv = fields.Boolean(string='MCV4 (0.5 ml)', readonly=False, states={'Done': [('readonly', False)]})
    n_mon_mcv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})
    n_mon_mcv_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Done': [('readonly', False)]})
    n_mon_mcv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Done': [('readonly', False)]})
    add_other_n_mon = fields.Boolean(string='Other', readonly=False, states={'Done': [('readonly', False)]})
    add_other_n_mon_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=False, states={'Done': [('readonly', False)]})
    add_other_n_mon_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})
    add_other_n_mon_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Done': [('readonly', False)]})
    add_other_n_mon_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Done': [('readonly', False)]})

    add_other_n_mon_comment = fields.Char(string='Vaccine Lot No',  readonly=False, states={'Done': [('readonly', False)]})
    add_other2_n_mon = fields.Boolean(string='Other', readonly=False, states={'Done': [('readonly', False)]})
    add_other2_n_mon_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=False, states={'Done': [('readonly', False)]})
    add_other2_n_mon_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})
    add_other2_n_mon_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Done': [('readonly', False)]})
    add_other2_n_mon_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Done': [('readonly', False)]})

    add_other2_n_mon_comment = fields.Char(string='Vaccine Lot No',  readonly=False, states={'Done': [('readonly', False)]})

    ot_mon_pcv = fields.Boolean(string='PCV (0.5 ml)', readonly=False, states={'Done': [('readonly', False)]})
    ot_mon_pcv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})
    ot_mon_pcv_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Done': [('readonly', False)]})
    ot_mon_pcv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Done': [('readonly', False)]})

    ot_mon_opv = fields.Boolean(string='OPV (2 gtts)', readonly=False, states={'Done': [('readonly', False)]})
    ot_mon_opv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})
    ot_mon_opv_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Done': [('readonly', False)]})
    ot_mon_opv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Done': [('readonly', False)]})

    ot_mon_mcv = fields.Boolean(string='MCV4 (0.5 ml)', readonly=False, states={'Done': [('readonly', False)]})
    ot_mon_mcv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})
    ot_mon_mcv_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Done': [('readonly', False)]})
    ot_mon_mcv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Done': [('readonly', False)]})

    ot_mon_mmr = fields.Boolean(string='MMR (0.5 ml)', readonly=False, states={'Done': [('readonly', False)]})
    ot_mon_mmr_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})
    ot_mon_mmr_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Done': [('readonly', False)]})
    ot_mon_mmr_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Done': [('readonly', False)]})

    add_other_ot_mon = fields.Boolean(string='Other', readonly=False, states={'Done': [('readonly', False)]})
    add_other_ot_mon_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=False, states={'Done': [('readonly', False)]})
    add_other_ot_mon_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})
    add_other_ot_mon_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Done': [('readonly', False)]})
    add_other_ot_mon_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Done': [('readonly', False)]})

    add_other_ot_mon_comment = fields.Char(string='Vaccine Lot No',  readonly=False, states={'Done': [('readonly', False)]})
    add_other2_ot_mon = fields.Boolean(string='Other', readonly=False, states={'Done': [('readonly', False)]})
    add_other2_ot_mon_vaccinations = fields.Selection(VACCINATION, string='Vaccination',  readonly=False, states={'Done': [('readonly', False)]})
    add_other2_ot_mon_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})
    add_other2_ot_mon_expiry_date = fields.Date(string='Expiry Date',  readonly=False, states={'Done': [('readonly', False)]})
    add_other2_ot_mon_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over',  readonly=False, states={'Done': [('readonly', False)]})

    add_other2_ot_mon_comment = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})

    oe_mon_dtap = fields.Boolean(string='D TaP (0.5 ml)', readonly=False, states={'Done': [('readonly', False)]})
    oe_mon_dtap_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})
    oe_mon_dtap_expiry_date = fields.Date(string='Expiry Date',  readonly=False, states={'Done': [('readonly', False)]})
    oe_mon_dtap_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over',  readonly=False, states={'Done': [('readonly', False)]})

    oe_mon_hib = fields.Boolean(string='Hib (0.5 ml)', readonly=False, states={'Done': [('readonly', False)]})
    oe_mon_hib_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})
    oe_mon_hib_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Done': [('readonly', False)]})
    oe_mon_hib_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Done': [('readonly', False)]})

    oe_mon_hepa = fields.Boolean(string='HepA (0.5 ml)', readonly=False, states={'Done': [('readonly', False)]})
    oe_mon_hepa_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})
    oe_mon_hepa_expiry_date = fields.Date(string='Expiry Date',  readonly=False, states={'Done': [('readonly', False)]})
    oe_mon_hepa_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over',  readonly=False, states={'Done': [('readonly', False)]})

    oe_mon_varicella = fields.Boolean(string='Varicella (0.5 ml)', readonly=False, states={'Done': [('readonly', False)]})
    oe_mon_varicella_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})
    oe_mon_varicella_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Done': [('readonly', False)]})
    oe_mon_varicella_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Done': [('readonly', False)]})

    oe_mon_mmr = fields.Boolean(string='MMR (0.5 ml)', readonly=False, states={'Done': [('readonly', False)]})
    oe_mon_mmr_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})
    oe_mon_mmr_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Done': [('readonly', False)]})
    oe_mon_mmr_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Done': [('readonly', False)]})

    oe_mon_opv = fields.Boolean(string='OPV (2 gtts)', readonly=False, states={'Done': [('readonly', False)]})
    oe_mon_opv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})
    oe_mon_opv_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Done': [('readonly', False)]})
    oe_mon_opv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Done': [('readonly', False)]})

    add_other_oe_mon = fields.Boolean(string='Other', readonly=False, states={'Done': [('readonly', False)]})
    add_other_oe_mon_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=False, states={'Done': [('readonly', False)]})
    add_other_oe_mon_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})
    add_other_oe_mon_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Done': [('readonly', False)]})
    add_other_oe_mon_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Done': [('readonly', False)]})

    add_other_oe_mon_comment = fields.Char(string='Vaccine Lot No',  readonly=False, states={'Done': [('readonly', False)]})
    add_other2_oe_mon = fields.Boolean(string='Other', readonly=False, states={'Done': [('readonly', False)]})
    add_other2_oe_mon_vaccinations = fields.Selection(VACCINATION, string='Vaccination',  readonly=False, states={'Done': [('readonly', False)]})
    add_other2_oe_mon_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})
    add_other2_oe_mon_expiry_date = fields.Date(string='Expiry Date',  readonly=False, states={'Done': [('readonly', False)]})
    add_other2_oe_mon_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over',  readonly=False, states={'Done': [('readonly', False)]})

    add_other2_oe_mon_comment = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})

    tf_mon_hepa = fields.Boolean(string='HepA (0.5 ml)', readonly=False, states={'Done': [('readonly', False)]})

    tf_mon_hepa_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})
    tf_mon_hepa_expiry_date = fields.Date(string='Expiry Date',  readonly=False, states={'Done': [('readonly', False)]})
    tf_mon_hepa_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over',  readonly=False, states={'Done': [('readonly', False)]})

    add_other_tf_mon = fields.Boolean(string='Other', readonly=False, states={'Done': [('readonly', False)]})
    add_other_tf_mon_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=False, states={'Done': [('readonly', False)]})
    add_other_tf_mon_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})
    add_other_tf_mon_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Done': [('readonly', False)]})
    add_other_tf_mon_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Done': [('readonly', False)]})

    add_other_tf_mon_comment = fields.Char(string='Vaccine Lot No',  readonly=False, states={'Done': [('readonly', False)]})
    add_other2_tf_mon = fields.Boolean(string='Other', readonly=False, states={'Done': [('readonly', False)]})
    add_other2_tf_mon_vaccinations = fields.Selection(VACCINATION, string='Vaccination',  readonly=False, states={'Done': [('readonly', False)]})
    add_other2_tf_mon_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})
    add_other2_tf_mon_expiry_date = fields.Date(string='Expiry Date',  readonly=False, states={'Done': [('readonly', False)]})
    add_other2_tf_mon_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over',  readonly=False, states={'Done': [('readonly', False)]})

    add_other2_tf_mon_comment = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})

    fs_yea_dtap = fields.Boolean(string='D Tap (0.5 ml)', readonly=False, states={'Done': [('readonly', False)]})
    fs_yea_dtap_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})
    fs_yea_dtap_expiry_date = fields.Date(string='Expiry Date',  readonly=False, states={'Done': [('readonly', False)]})
    fs_yea_dtap_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over',  readonly=False, states={'Done': [('readonly', False)]})

    fs_yea_opv = fields.Boolean(string='OPV (2 gtts)', readonly=False, states={'Done': [('readonly', False)]})
    fs_yea_opv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})
    fs_yea_opv_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Done': [('readonly', False)]})
    fs_yea_opv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Done': [('readonly', False)]})

    fs_yea_varicella = fields.Boolean(string='Varicella (0.5 ml)', readonly=False, states={'Done': [('readonly', False)]})
    fs_yea_varicella_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})
    fs_yea_varicella_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Done': [('readonly', False)]})
    fs_yea_varicella_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Done': [('readonly', False)]})

    fs_yea_mmr = fields.Boolean(string='MMR (0.5 ml)', readonly=False, states={'Done': [('readonly', False)]})
    fs_yea_mmr_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})
    fs_yea_mmr_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Done': [('readonly', False)]})
    fs_yea_mmr_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Done': [('readonly', False)]})

    add_other_fs_yea = fields.Boolean(string='Other', readonly=False, states={'Done': [('readonly', False)]})
    add_other_fs_yea_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=False, states={'Done': [('readonly', False)]})
    add_other_fs_yea_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})
    add_other_fs_yea_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Done': [('readonly', False)]})
    add_other_fs_yea_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Done': [('readonly', False)]})

    add_other_fs_yea_comment = fields.Char(string='Vaccine Lot No',  readonly=False, states={'Done': [('readonly', False)]})
    add_other2_fs_yea = fields.Boolean(string='Other', readonly=False, states={'Done': [('readonly', False)]})
    add_other2_fs_yea_vaccinations = fields.Selection(VACCINATION, string='Vaccination',  readonly=False, states={'Done': [('readonly', False)]})
    add_other2_fs_yea_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})
    add_other2_fs_yea_expiry_date = fields.Date(string='Expiry Date',  readonly=False, states={'Done': [('readonly', False)]})
    add_other2_fs_yea_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over',  readonly=False, states={'Done': [('readonly', False)]})

    add_other2_fs_yea_comment = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})

    oo_yea_dtap = fields.Boolean(string='Tdap (0.5 ml)', readonly=False, states={'Done': [('readonly', False)]})
    oo_yea_dtap_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})
    oo_yea_dtap_expiry_date = fields.Date(string='Expiry Date',  readonly=False, states={'Done': [('readonly', False)]})
    oo_yea_dtap_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over',  readonly=False, states={'Done': [('readonly', False)]})

    oo_yea_vpv = fields.Boolean(string='HPV (0.5 ml)', readonly=False, states={'Done': [('readonly', False)]})
    oo_yea_vpv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})
    oo_yea_vpv_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Done': [('readonly', False)]})
    oo_yea_vpv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Done': [('readonly', False)]})

    add_other_oo_yea = fields.Boolean(string='Other', readonly=False, states={'Done': [('readonly', False)]})
    add_other_oo_yea_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=False, states={'Done': [('readonly', False)]})
    add_other_oo_yea_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})
    add_other_oo_yea_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Done': [('readonly', False)]})
    add_other_oo_yea_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Done': [('readonly', False)]})

    add_other_oo_yea_comment = fields.Char(string='Vaccine Lot No',  readonly=False, states={'Done': [('readonly', False)]})
    add_other2_oo_yea = fields.Boolean(string='Other', readonly=False, states={'Done': [('readonly', False)]})
    add_other2_oo_yea_vaccinations = fields.Selection(VACCINATION, string='Vaccination',  readonly=False, states={'Done': [('readonly', False)]})
    add_other2_oo_yea_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})
    add_other2_oo_yea_expiry_date = fields.Date(string='Expiry Date',  readonly=False, states={'Done': [('readonly', False)]})
    add_other2_oo_yea_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over',  readonly=False, states={'Done': [('readonly', False)]})
    add_other2_oo_yea_comment = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})

    ot_yea_hpv = fields.Boolean(string='HPV (0.5 ml)', readonly=False, states={'Done': [('readonly', False)]})
    ot_yea_hpv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})
    ot_yea_hpv_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Done': [('readonly', False)]})
    ot_yea_hpv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Done': [('readonly', False)]})

    add_other_ot_yea = fields.Boolean(string='Other', readonly=False, states={'Done': [('readonly', False)]})
    add_other_ot_yea_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=False, states={'Done': [('readonly', False)]})
    add_other_ot_yea_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})
    add_other_ot_yea_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Done': [('readonly', False)]})
    add_other_ot_yea_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Done': [('readonly', False)]})

    add_other_ot_yea_comment = fields.Char(string='Vaccine Lot No',  readonly=False, states={'Done': [('readonly', False)]})
    add_other2_ot_yea = fields.Boolean(string='Other', readonly=False, states={'Done': [('readonly', False)]})
    add_other2_ot_yea_vaccinations = fields.Selection(VACCINATION, string='Vaccination',  readonly=False, states={'Done': [('readonly', False)]})
    add_other2_ot_yea_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})
    add_other2_ot_yea_expiry_date = fields.Date(string='Expiry Date',  readonly=False, states={'Done': [('readonly', False)]})
    add_other2_ot_yea_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over',  readonly=False, states={'Done': [('readonly', False)]})

    add_other2_ot_yea_comment = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})

    oe_yea_mcv = fields.Boolean(string='MCV4 (0.5 ml)', readonly=False, states={'Done': [('readonly', False)]})
    oe_yea_mcv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})
    oe_yea_mcv_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Done': [('readonly', False)]})
    oe_yea_mcv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Done': [('readonly', False)]})

    add_other_oe_yea = fields.Boolean(string='Other', readonly=False, states={'Done': [('readonly', False)]})
    add_other_oe_yea_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=False, states={'Done': [('readonly', False)]})
    add_other_oe_yea_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})
    add_other_oe_yea_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Done': [('readonly', False)]})
    add_other_oe_yea_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Done': [('readonly', False)]})

    add_other_oe_yea_comment = fields.Char(string='Vaccine Lot No',  readonly=False, states={'Done': [('readonly', False)]})
    add_other2_oe_yea = fields.Boolean(string='Other', readonly=False, states={'Done': [('readonly', False)]})
    add_other2_oe_yea_vaccinations = fields.Selection(VACCINATION, string='Vaccination',  readonly=False, states={'Done': [('readonly', False)]})
    add_other2_oe_yea_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})
    add_other2_oe_yea_expiry_date = fields.Date(string='Expiry Date',  readonly=False, states={'Done': [('readonly', False)]})
    add_other2_oe_yea_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over',  readonly=False, states={'Done': [('readonly', False)]})

    add_other2_oe_yea_comment = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})

    oth_influenza = fields.Boolean(string='Influenza (0.25 ml)', readonly=False, states={'Done': [('readonly', False)]})
    oth_influenza_vaccine_no = fields.Char(string='Vaccine Lot No',  readonly=False, states={'Done': [('readonly', False)]})
    oth_influenza_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Done': [('readonly', False)]})
    oth_influenza_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over',  readonly=False, states={'Done': [('readonly', False)]})

    oth_tdap = fields.Boolean(string='Tdap (0.5 ml)', readonly=False, states={'Done': [('readonly', False)]})
    oth_tdap_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})
    oth_tdap_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Done': [('readonly', False)]})
    oth_tdap_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Done': [('readonly', False)]})

    oth_mmr = fields.Boolean(string='MMR (0.5 ml)', readonly=False, states={'Done': [('readonly', False)]})
    oth_mmr_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})
    oth_mmr_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Done': [('readonly', False)]})
    oth_mmr_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Done': [('readonly', False)]})

    oth_varicella = fields.Boolean(string='Varicella (0.5 ml)', readonly=False, states={'Done': [('readonly', False)]})
    oth_varicella_vaccine_no = fields.Char(string='Vaccine Lot No',  readonly=False, states={'Done': [('readonly', False)]})
    oth_varicella_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Done': [('readonly', False)]})
    oth_varicella_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over',  readonly=False, states={'Done': [('readonly', False)]})

    oth_herpes = fields.Boolean(string='Herpes Zoster (0.5 ml)', readonly=False, states={'Done': [('readonly', False)]})
    oth_herpes_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})
    oth_herpes_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Done': [('readonly', False)]})
    oth_herpes_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Done': [('readonly', False)]})

    oth_hpv = fields.Boolean(string='HPV (0.5 ml)', readonly=False, states={'Done': [('readonly', False)]})
    oth_hpv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})
    oth_hpv_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Done': [('readonly', False)]})
    oth_hpv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Done': [('readonly', False)]})

    oth_ppsv = fields.Boolean(string='PPSV23 (0.5 ml)', readonly=False, states={'Done': [('readonly', False)]})
    oth_ppsv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})
    oth_ppsv_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Done': [('readonly', False)]})
    oth_ppsv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Done': [('readonly', False)]})

    oth_pcv = fields.Boolean(string='PCV (0.5 ml)', readonly=False, states={'Done': [('readonly', False)]})
    oth_pcv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})
    oth_pcv_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Done': [('readonly', False)]})
    oth_pcv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Done': [('readonly', False)]})

    oth_hepb = fields.Boolean(string='Hep B (0.5 ml)', readonly=False, states={'Done': [('readonly', False)]})
    oth_hepb_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})
    oth_hepb_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Done': [('readonly', False)]})
    oth_hepb_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Done': [('readonly', False)]})

    oth_mcv = fields.Boolean(string='MCV4 (0.5 ml)', readonly=False, states={'Done': [('readonly', False)]})
    oth_mcv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})
    oth_mcv_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Done': [('readonly', False)]})
    oth_mcv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Done': [('readonly', False)]})

    oth_other = fields.Boolean(string='Other', readonly=False, states={'Done': [('readonly', False)]})
    oth_vaccinations = fields.Char(string='Vaccination', readonly=False, states={'Done': [('readonly', False)]})
    oth_vaccinations_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})
    oth_vaccinations_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Done': [('readonly', False)]})
    oth_vaccinations_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Done': [('readonly', False)]})

    oth_rv = fields.Boolean(string='RV (1 ml)', readonly=False, states={'Done': [('readonly', False)]})
    oth_rv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})
    oth_rv_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Done': [('readonly', False)]})
    oth_rv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over',  readonly=False, states={'Done': [('readonly', False)]})

    oth_dtap = fields.Boolean(string='D TaP (0.5 ml)', readonly=False, states={'Done': [('readonly', False)]})
    oth_dtap_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})
    oth_dtap_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Done': [('readonly', False)]})
    oth_dtap_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Done': [('readonly', False)]})

    oth_hib = fields.Boolean(string='Hib (0.5 ml)', readonly=False, states={'Done': [('readonly', False)]})
    oth_hib_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})
    oth_hib_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Done': [('readonly', False)]})
    oth_hib_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Done': [('readonly', False)]})

    oth_ipv = fields.Boolean(string='IPV (0.5 ml)', readonly=False, states={'Done': [('readonly', False)]})
    oth_ipv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})
    oth_ipv_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Done': [('readonly', False)]})
    oth_ipv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Done': [('readonly', False)]})

    oth_bcg = fields.Boolean(string='BCG (0.5 ml)', readonly=False, states={'Done': [('readonly', False)]})
    oth_bcg_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})
    oth_bcg_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Done': [('readonly', False)]})
    oth_bcg_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Done': [('readonly', False)]})

    oth_opv = fields.Boolean(string='OPV (2 gtts)', readonly=False, states={'Done': [('readonly', False)]})
    oth_opv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})
    oth_opv_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Done': [('readonly', False)]})
    oth_opv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Done': [('readonly', False)]})

    oth_measels = fields.Boolean(string='Measels (0.5 ml)', readonly=False, states={'Done': [('readonly', False)]})
    oth_measels_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})
    oth_measels_expiry_date = fields.Date(string='Expiry Date',  readonly=False, states={'Done': [('readonly', False)]})
    oth_measels_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over',  readonly=False, states={'Done': [('readonly', False)]})

    oth_hepa = fields.Boolean(string='HepA (0.5 ml)', readonly=False, states={'Done': [('readonly', False)]})

    oth_hepa_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=False, states={'Done': [('readonly', False)]})
    oth_hepa_expiry_date = fields.Date(string='Expiry Date', readonly=False, states={'Done': [('readonly', False)]})
    oth_hepa_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=False, states={'Done': [('readonly', False)]})

    mother_caregiver_show = fields.Boolean()
    mother_soreness_redness_swelling = fields.Selection(YES_NO, readonly=False, states={'Done': [('readonly', False)]})
    mother_muscular_pain = fields.Selection(YES_NO, readonly=False, states={'Done': [('readonly', False)]})
    mother_headaches = fields.Selection(YES_NO, readonly=False, states={'Done': [('readonly', False)]})
    mother_fever = fields.Selection(YES_NO, readonly=False, states={'Done': [('readonly', False)]})
    mother_nausea = fields.Selection(YES_NO, readonly=False, states={'Done': [('readonly', False)]})

    mother_difficulty_breathing = fields.Selection(YES_NO, readonly=False, states={'Done': [('readonly', False)]})
    mother_coughing = fields.Selection(YES_NO, readonly=False, states={'Done': [('readonly', False)]})
    mother_hoarse_vice_wheezing = fields.Selection(YES_NO, readonly=False, states={'Done': [('readonly', False)]})
    mother_hives = fields.Selection(YES_NO, readonly=False, states={'Done': [('readonly', False)]})
    mother_paleness = fields.Selection(YES_NO, readonly=False, states={'Done': [('readonly', False)]})
    mother_losing_consciousness = fields.Selection(YES_NO, readonly=False, states={'Done': [('readonly', False)]})
    add_other = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    add_other_text = fields.Text(readonly=False, states={'Done': [('readonly', False)]})

    @api.model
    def create(self, vals):
        vals['comprehensive_nurse_follow_up_code'] = self.env['ir.sequence'].next_by_code(
            'comprehensive.nurse.follow.up')
        return super(ComprehensiveNurseFollowUp, self).create(vals)

    def set_to_done(self):
        return self.write({'state': 'Done', 'completed_date': datetime.datetime.now()})

    def set_to_start(self):
        return self.write({'state': 'Start', 'start_date': datetime.datetime.now()})

    # @api.onchange('cna_xx')
    # def _onchange_cna_xx(self):
    #     if self.cna_xx:
    #         self.patient = self.cna_xx.patient
    #         self.hhc_appointment = self.cna_xx.hhc_appointment

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


class ShifaNotificationInherit(models.Model):
    _inherit = 'sm.physician.notification'

    comprehensive_nurse_not_id = fields.Many2one('sm.shifa.comprehensive.nurse.follow.up',
                                                 string='comprehensive nurse follow up',
                                                 ondelete='cascade')

class ShifaWoundInherit(models.Model):
    _inherit = 'sm.shifa.wound.assessment.values'

    wound_comp_id = fields.Many2one('sm.shifa.comprehensive.nurse', string='Wound Assessment')
    wound_comp_followup_id = fields.Many2one('sm.shifa.comprehensive.nurse.follow.up', string='Wound Assessment')



