from odoo import models, fields, api, _
import datetime
# from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError

import logging

_logger = logging.getLogger(__name__)


class AssessmentNurse(models.Model):
    _name = 'sm.shifa.nurse.assessment'
    _description = 'Nurse Assessment'
    _rec_name = 'assessment_nurse_code'

    ADMISSION_STATES = [
        ('Draft', 'Draft'),
        ('Start', 'Start'),
        ('Admitted', 'Admitted'),
        ('Discharged', 'Discharged'),
        ('Done', 'Done'),
    ]
    YES_NO = [
        ('Yes ', 'Yes'),
        ('No', 'No'),
    ]
    type_visit = [
        ('main_visit', 'Comprehensive Visit'),
        ('follow_up', 'Follow Up'),
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
    DISCHARGE_PLAN = [
        ('provided_explained', 'Provided and explained'),
        ('no_discharge_moment', 'No discharge at the moment'),
        ('not_applicable', 'Not applicable'),
        ('other', 'Others'),
    ]

    def set_to_start(self):
        return self.write({'state': 'Start'})

    def set_to_draft(self):
        return self.write({'state': 'Draft'})

    def set_to_done(self):
        for rec in self:
            rec.followup_date = datetime.datetime.now()
        return self.write({'state': 'Done'})

        #     Clinical Documentation Completed

    def set_to_admitted(self):
        for rec in self:
            if rec.visit_type == 'main_visit':
                rec.admission_date = datetime.datetime.now()
            else:
                rec.followup_date = datetime.datetime.now()
        return self.write({'state': 'Admitted'})

        #     discharge date time method

    def set_to_discharged(self):
        discharged_date = False
        for ina in self:
            if ina.discharge_date:
                discharged_date = ina.discharge_date
            else:
                discharged_date = datetime.datetime.now()

        return self.write({'state': 'Discharged', 'discharge_date': discharged_date})

    def back_to_admitted(self):
        return self.write({'state': 'Admitted', 'discharge_date': None})

    def _get_comprehensive(self):
        """Return default comprehensive value"""
        therapist_obj = self.env['oeh.medical.physician']
        domain = [('oeh_user_id', '=', self.env.uid)]
        user_ids = therapist_obj.search(domain, limit=1)
        if user_ids:
            return user_ids.id or False
        else:
            return False

    # @api.model
    # def create(self, vals):
    #     vals['assessment_nurse_code'] = self.env['ir.sequence'].next_by_code('sm.shifa.nurse.assessment')
    #     return super(AssessmentNurse, self).create(vals)

    @api.model
    def create(self, vals):

        # save sequence depends on selection type
        if vals['visit_type'] == 'main_visit':
            sequence_main = self.env['ir.sequence'].next_by_code('sm.shifa.nurse.assessment.main')
            vals['assessment_nurse_code'] = sequence_main
        elif vals['visit_type'] == 'follow_up':
            sequence_followup = self.env['ir.sequence'].next_by_code('sm.shifa.nurse.assessment.followup')
            vals['assessment_nurse_code'] = sequence_followup
        else:
            vals['assessment_nurse_code'] = ""

        return super(AssessmentNurse, self).create(vals)

    assessment_nurse_code = fields.Char('Reference', index=True, copy=False)
    state = fields.Selection(ADMISSION_STATES, string='State', default=lambda *a: 'Draft', readonly=True)
    patient = fields.Many2one('oeh.medical.patient', string='Patient', help="Patient Name", required=True,
                              readonly=True, states={'Draft': [('readonly', False)]})
    weight = fields.Float(string='Weight', related='patient.weight', readonly=True,
                          states={'Draft': [('readonly', False)]})
    age = fields.Char(string='Age', related='patient.age', readonly=True, states={'Draft': [('readonly', False)]})
    marital_status = fields.Selection(string='Marital Status', related='patient.marital_status')
    sex = fields.Selection(string='Sex', related='patient.sex', readonly=True, states={'Draft': [('readonly', False)]})
    blood_type = fields.Selection(string='Blood Type', related='patient.blood_type', readonly=True,
                                  states={'Draft': [('readonly', False)]})
    rh = fields.Selection(string='Rh', related='patient.rh', readonly=True, states={'Draft': [('readonly', False)]})
    doctor = fields.Many2one('oeh.medical.physician', string='Nurse', help="Current primary care / family doctor",
                             readonly=True, states={'Draft': [('readonly', False)]},
                             domain=[('role_type', '=', ['HHCN', 'HN']), ('active', '=', True)], required=True,
                             default=_get_comprehensive)
    hhc_appointment = fields.Many2one('sm.shifa.hhc.appointment', string='HHC-Appointment',
                                      readonly=True, states={'Draft': [('readonly', False)]},
                                      domain="[('patient', '=', patient)]")
    visit_type = fields.Selection(type_visit, required=True, readonly=True, states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})
    # phy_adm = fields.Many2one('sm.shifa.physician.admission', string='Phy_Adm', readonly=True,
    #                           states={'Draft': [('readonly', False)]},
    #                           domain="[('patient', '=', patient), ('state', 'in', ('Admitted', 'Start','Draft'))]")
    phy_asse = fields.Many2one('sm.shifa.physician.assessment', string="PhA", readonly=True,
                               states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]},
                               domain="[('patient', '=', patient), ('visit_type', '=', 'main_visit'),('state', '=', 'Admitted')]")

    admission_date = fields.Datetime(string='Admission Date', readonly=True,
                                     states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})
    discharge_date = fields.Datetime(string='Discharge Date', readonly='1')
    followup_date = fields.Datetime(string='Follow up Date', readonly='1')

    service_name = fields.Selection(SERVICES, readonly=True,
                                    states={'Draft': [('readonly', False)]}, default='G')
    service = fields.Many2one('sm.shifa.service', string='First Service', required=True,
                              domain=[('show', '=', True), ('service_type', 'in',
                                                            ['HHC', 'FUPH', 'L', 'WBSDFC', 'R', 'LP', 'GCP', 'MH',
                                                             'IVT', 'SM', 'V', 'Car',
                                                             'Diab', 'HVD'])],
                              readonly=True, states={'Draft': [('readonly', False)]})

    service_type = fields.Selection(string='Service type', related='service.service_type', readonly=True, store=False)

    service_2 = fields.Many2one('sm.shifa.service', string='Second Service',
                                domain=[('show', '=', True), ('service_type', 'in',
                                                              ['HHC', 'FUPH', 'L', 'WBSDFC', 'R', 'LP', 'GCP', 'MH',
                                                               'IVT', 'SM', 'V', 'Car',
                                                               'PHY', 'Diab', 'HVD'])],
                                readonly=True, states={'Draft': [('readonly', False)]})

    service_3 = fields.Many2one('sm.shifa.service', string='Third Service',
                                domain=[('show', '=', True), ('service_type', 'in',
                                                              ['HHC', 'FUPH', 'L', 'WBSDFC', 'R', 'LP', 'GCP', 'MH',
                                                               'IVT', 'SM', 'V', 'Car',
                                                               'PHY', 'Diab', 'HVD'])],
                                readonly=True, states={'Draft': [('readonly', False)]})
    consent_show = fields.Boolean()
    consent_file1 = fields.Binary()
    consent_file2 = fields.Binary()
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

    provisional_diagnosis_add_other4 = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    provisional_diagnosis_add4 = fields.Many2one('oeh.medical.pathology', string='Disease', readonly=True,
                                                 states={'Start': [('readonly', False)]})
    provisional_diagnosis_add_other5 = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    provisional_diagnosis_add5 = fields.Many2one('oeh.medical.pathology', string='Disease', readonly=True,
                                                 states={'Start': [('readonly', False)]})
    provisional_diagnosis_add_other6 = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    provisional_diagnosis_add6 = fields.Many2one('oeh.medical.pathology', string='Disease', readonly=True,
                                                 states={'Start': [('readonly', False)]})
    provisional_diagnosis_add_other7 = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    provisional_diagnosis_add7 = fields.Many2one('oeh.medical.pathology', string='Disease', readonly=True,
                                                 states={'Start': [('readonly', False)]})
    provisional_diagnosis_add_other8 = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    provisional_diagnosis_add8 = fields.Many2one('oeh.medical.pathology', string='Disease', readonly=True,
                                                 states={'Start': [('readonly', False)]})
    provisional_diagnosis_add_other9 = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    provisional_diagnosis_add9 = fields.Many2one('oeh.medical.pathology', string='Disease', readonly=True,
                                                 states={'Start': [('readonly', False)]})
    chief_complaint_show = fields.Boolean()
    chief_complaint = fields.Char(string="Chief Complaint", readonly=True, store=True,
                                  states={'Start': [('readonly', False)]})
    care_rendered = fields.Text(readonly=True, states={'Start': [('readonly', False)]})
    care_rendered_show = fields.Boolean()
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
    Observation_show = fields.Boolean()
    conscious_state = fields.Selection([
        ('Alert', 'Alert'),
        ('Response to Voice', 'Response to Voice'),
        ('Response to pain', 'Response to pain'),
        ('Unresponsive', 'Unresponsive'),
    ], readonly=True, states={'Start': [('readonly', False)]})
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
    functional_activity = fields.Selection([
        ('No Limitation', 'No Limitation'),
        ('Mild Limitation', 'Mild Limitation'),
        ('Severe Limitation', 'Severe Limitation'),
    ], readonly=True, states={'Start': [('readonly', False)]})

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
    others_show = fields.Boolean(string="Others")
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
    # Continence # Continence # Continence # Continence # Continence # Continence # Continence # Continence # Continence
    type_continence_show = fields.Boolean()
    bladder = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    bowel = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})

    type_devices_used_show = fields.Boolean()
    indwelling_foley = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    suprapubic_catheter = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    urosheath_condom = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    diaper = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})

    con_potential_actual_risk_show = fields.Boolean()
    impaired_skin_integrity_related_bowel_or_bladder = fields.Selection(yes_no_na, readonly=True,
                                                                        states={'Start': [('readonly', False)]})
    complications_related_indwelling_urinary_catheter = fields.Selection(yes_no_na, readonly=True,
                                                                         states={'Start': [('readonly', False)]})

    con_measurable_goals_show = fields.Boolean()
    will_remain_clean_dry_free_from_urinary_or_faecal = fields.Selection(yes_no_na, readonly=True,
                                                                         states={'Start': [('readonly', False)]})
    will_remain_free_signs_and_symptoms_of_complications = fields.Selection(yes_no_na, readonly=True,
                                                                            states={'Start': [('readonly', False)]})

    con_patient_assessment_show = fields.Boolean()
    color_urine = fields.Selection([
        ('Amber', 'Amber'),
        ('Light Yellow', 'Light Yellow'),
        ('Dark Yellow', 'Dark Yellow'),
        ('Cloudy', 'Cloudy'),
        ('Light Hematuria', 'Light Hematuria'),
        ('Gross Hematuria', 'Gross Hematuria'),
    ], readonly=True, states={'Start': [('readonly', False)]})
    con_consistency = fields.Selection([
        ('Clear', 'Clear'),
        ('With Blood Streak', 'With Blood Streak'),
        ('With Blood Clots', 'With Blood Clots'),
        ('With Sediments', 'With Sediments'),
    ], readonly=True, states={'Start': [('readonly', False)]})
    amount_ml = fields.Float(readonly=True, states={'Start': [('readonly', False)]})
    presence_urinary_frequency = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    diaper_changed = fields.Selection([
        ('2-3 times per day', '2-3 times per day'),
        ('3 times per day', '3 times per day'),
        ('3-4 times per day', '3-4 times per day'),
        ('4 times per day', '4 times per day'),
        ('4-5 times per day', '4-5 times per day'),
        ('NA', 'NA'),
    ], readonly=True, states={'Start': [('readonly', False)]})
    presence_burning = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    presence_foul_smelling = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    presence_altered_mental = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    catheter_still_required = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})

    urinaty_catheter_bag_show = fields.Boolean()
    secured_appropriately = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    bag_off_floor = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    bag_below_level = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    tubing_not_taut = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})

    catheter_change_show = fields.Boolean()
    catheter_change_done = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    type_of_catheter = fields.Selection([
        ('Silicone', 'Silicone'),
        ('Rubber/Latex', 'Rubber/Latex'),
        ('Condom', 'Condom'),
        ('Urosheath', 'Urosheath'),
        ('Suprapubic', 'Suprapubic'),
        ('Nephrostomy', 'Nephrostomy'),
    ], readonly=True, states={'Start': [('readonly', False)]})
    size_of_catheter = fields.Text(readonly=True, states={'Start': [('readonly', False)]})
    catheter_change_due_on = fields.Text(readonly=True, states={'Start': [('readonly', False)]})

    bowel_assessment_show = fields.Boolean()
    bowels_opened = fields.Selection([
        ('2 times daily', '2 times daily'),
        ('more than 5 times daily', 'more than 5 times daily'),
        ('more than 10 times daily', 'more than 10 times daily'),
        ('every 2 days', 'every 2 days'),
        ('every other day', 'every other day'),
        ('once a week', 'once a week'),
        ('Bowel not opened', 'Bowel not opened'),
    ], readonly=True, states={'Start': [('readonly', False)]})
    color_of_stool = fields.Selection([
        ('Brown', 'Brown'),
        ('Black', 'Black'),
        ('Reddish Brown', 'Reddish Brown'),
        ('Yellow', 'Yellow'),
        ('Green', 'Green'),
        ('Red', 'Red'),
    ], readonly=True, states={'Start': [('readonly', False)]})
    consistency_of_stool = fields.Selection([
        ('Hard', 'Hard'),
        ('Soft', 'Soft'),
        ('Loose', 'Loose'),
        ('Watery', 'Watery'),
        ('Mucoid', 'Mucoid'),
        ('NA', 'NA'),
    ], readonly=True, states={'Start': [('readonly', False)]})
    perineal_area = fields.Selection([
        ('Dry and intact', 'Dry and intact'),
        ('Excoriation', 'Excoriation'),
        ('Redness', 'Redness'),
        ('Blisters', 'Blisters'),
        ('NA', 'NA'),
    ], readonly=True, states={'Start': [('readonly', False)]})

    con_caregiver_assessment_show = fields.Boolean()
    maintain_patient_hygiene = fields.Selection([
        ('Well', 'Well'),
        ('Very Well', 'Very Well'),
        ('Yes', 'Yes'),
        ('No', 'No'),
        ('NA', 'NA'),
        ('Fair', 'Fair'),
        ('Poor', 'Poor'),
    ], readonly=True, states={'Start': [('readonly', False)]})
    use_incontinence_products = fields.Selection([
        ('Competent', 'Competent'),
        ('Yes', 'Yes'),
        ('No', 'No'),
        ('NA', 'NA'),
    ], readonly=True, states={'Start': [('readonly', False)]})
    keep_patient_odourless = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    ability_cope_care = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})

    con_patient_caregiver_education_show = fields.Boolean()
    patient_caregiver_should = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    maintain_fluids_high_fibre = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    drinking_least_litres_fluid = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    do_not_kink_clamp = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    always_attach_catheter = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    keep_closed_system_drainage = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    carers_should_wash_their = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    con_remarks_show = fields.Boolean()
    con_remarks = fields.Text(readonly=True, states={'Start': [('readonly', False)]})
    # Enternal Feeding # Enternal Feeding # Enternal Feeding # Enternal Feeding # Enternal Feeding # Enternal Feeding
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
                                                                   readonly=True,
                                                                   states={'Start': [('readonly', False)]})
    measurable_goals_show = fields.Boolean()
    measurable_goals_will_remain_free = fields.Selection(yes_no_na,
                                                         readonly=True, states={'Start': [('readonly', False)]})
    measurable_goals_will_maintain_adequate = fields.Selection(yes_no_na,
                                                               readonly=True, states={'Start': [('readonly', False)]})
    measurable_goals_will_not_develop = fields.Selection(yes_no_na,
                                                         readonly=True, states={'Start': [('readonly', False)]})
    ent_patient_assessment_show = fields.Boolean()
    patient_assessment_signs_of_aspiration = fields.Selection(yes_no_na,
                                                              readonly=True, states={'Start': [('readonly', False)]})
    patient_assessment_presence_of_bowel_sounds = fields.Selection(yes_no_na,
                                                                   readonly=True,
                                                                   states={'Start': [('readonly', False)]})
    patient_assessment_presence_of_constipation = fields.Selection(yes_no_na,
                                                                   readonly=True,
                                                                   states={'Start': [('readonly', False)]})
    patient_assessment_presence_of_diarrhoea = fields.Selection(yes_no_na,
                                                                readonly=True, states={'Start': [('readonly', False)]})
    patient_assessment_presence_nausea_vomiting = fields.Selection(yes_no_na,
                                                                   readonly=True,
                                                                   states={'Start': [('readonly', False)]})
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

    ent_caregiver_assessment_show = fields.Boolean()
    caregiver_assessment_perform_tube_placement = fields.Selection(competent_no_na,
                                                                   readonly=True,
                                                                   states={'Start': [('readonly', False)]})
    caregiver_assessment_perform_enteral_feeding = fields.Selection(competent_no_na,
                                                                    readonly=True,
                                                                    states={'Start': [('readonly', False)]})
    caregiver_assessment_perform_gastrostomy_site = fields.Selection(yes_no_na_competent,
                                                                     readonly=True,
                                                                     states={'Start': [('readonly', False)]})
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
    ent_remarks_show = fields.Boolean()
    ent_remarks = fields.Text(readonly=True, states={'Start': [('readonly', False)]})
    # Drain Tub # Drain Tub # Drain Tub # Drain Tub # Drain Tub # Drain Tub # Drain Tub # Drain Tub # Drain Tub # Drain Tub
    type_of_surgery_procedure_show = fields.Boolean()
    type_of_surgery_procedure = fields.Text(readonly=True, states={'Start': [('readonly', False)]})

    type_of_drain_catheter_show = fields.Boolean()
    drain_catheter_pleurx = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    drain_catheter_pigtail = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    drain_catheter_jackson_pratts = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    drain_catheter_other = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    drain_catheter_other_text = fields.Text(readonly=True, states={'Start': [('readonly', False)]})

    location_show = fields.Boolean()
    location_chest = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    location_abdomen = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    location_other = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    location_other_text = fields.Text(readonly=True, states={'Start': [('readonly', False)]})

    type_of_drainage_show = fields.Boolean()
    type_drainage_free_drainage = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    type_drainage_vacuum = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    type_drainage_other = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    type_drainage_other_text = fields.Text(readonly=True, states={'Start': [('readonly', False)]})

    dra_potential_actual_risk_show = fields.Boolean()
    drain_site_infection_other = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    seroma_formation_other = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    dislodgement_of_drain_tube_other = fields.Selection(yes_no_na, readonly=True,
                                                        states={'Start': [('readonly', False)]})

    dra_measurable_goals_show = fields.Boolean()
    drain_site_will_remain_free_from_infection = fields.Selection(yes_no_na, readonly=True,
                                                                  states={'Start': [('readonly', False)]})
    drainage_system_will_remain_patent_with = fields.Selection(yes_no_na, readonly=True,
                                                               states={'Start': [('readonly', False)]})
    drain_tube_will_be_removed_if_less_than_mls = fields.Selection(yes_no_na, readonly=True,
                                                                   states={'Start': [('readonly', False)]})
    drain_remains_insitu_and_drainage_done_as = fields.Selection(yes_no_na, readonly=True,
                                                                 states={'Start': [('readonly', False)]})

    dra_patient_assessment_show = fields.Boolean()
    vital_signs_remain_within = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    patient_pain_under_control = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    performing_arm_exercises = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})

    drain_tube_site_assessment_show = fields.Boolean()
    dressing_dry_and_intact = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    presence_drain_site_infection = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    presence_of_leakage = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    nature_of_drainage = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    drainage_amount_last_24hrs = fields.Text(readonly=True, states={'Start': [('readonly', False)]})
    drain_tube_removed = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})

    dra_patient_caregiver_education_show = fields.Boolean()
    patient_understands_importance = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    actions_to_take_if_leaking = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    understands_when_suction = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    taking_analgesia_regularly = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    measuring_and_recording_drainage = fields.Selection(yes_no_na, readonly=True,
                                                        states={'Start': [('readonly', False)]})
    report_increase_of_temperature_change = fields.Selection(yes_no_na, readonly=True,
                                                             states={'Start': [('readonly', False)]})
    discharge_education_post_removal = fields.Selection(yes_no_na, readonly=True,
                                                        states={'Start': [('readonly', False)]})
    self_drainage_procedure = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    dra_remarks_show = fields.Boolean()
    dra_remarks = fields.Text(readonly=True, states={'Start': [('readonly', False)]})
    # Stoma # Stoma  # Stoma # Stoma # Stoma # Stoma # Stoma # Stoma # Stoma # Stoma # Stoma # Stoma # Stoma # Stoma # Stoma
    type_surgery_show = fields.Boolean()
    type_surgery = fields.Text(readonly=True, states={'Start': [('readonly', False)]})

    sto_patient_assessment_show = fields.Boolean()
    vital_signs_remain = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    coping_with_changing = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    managing_skin = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})

    stoma_site_assessment_show = fields.Boolean()
    stoma_appliance_intact = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    presence_of_skin = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    nature_of_effluent = fields.Selection([
        ('Stool', 'Stool'),
        ('Urine', 'Urine'),
        ('Blood', 'Blood'),
        ('Bile', 'Bile'),
        ('Nil', 'Nil'),
    ], readonly=True, states={'Start': [('readonly', False)]})
    amount = fields.Integer(readonly=True, states={'Start': [('readonly', False)]})
    sto_consistency = fields.Selection([
        ('Hard', 'Hard'),
        ('Soft', 'Soft'),
        ('Loose', 'Loose'),
    ], readonly=True, states={'Start': [('readonly', False)]})

    follow_up_care_show = fields.Boolean()
    stoma_care_clinic = fields.Text(readonly=True, states={'Start': [('readonly', False)]})
    review_dates = fields.Text(readonly=True, states={'Start': [('readonly', False)]})

    sto_patient_caregiver_education_show = fields.Boolean()
    choose_outfit = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    eating_regular_ = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    drink_reqularly = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    observe_for_stomal = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    sto_remarks_show = fields.Boolean()
    sto_remarks = fields.Text(readonly=True, states={'Start': [('readonly', False)]})
    # Palliative
    palliative_care_type_show = fields.Boolean()
    pall_pain_management = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    symptom_management = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    subcutaneous_infusion = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    palliative_other = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    palliative_other_text = fields.Text(readonly=True, states={'Start': [('readonly', False)]})

    pall_potential_actual_risk_show = fields.Boolean()
    pain_related_to_disease_process = fields.Selection(yes_no_na, readonly=True,
                                                       states={'Start': [('readonly', False)]})
    ineffective_pain_management = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    nutritional_deficit_related_to_poor_oral = fields.Selection(yes_no_na, readonly=True,
                                                                states={'Start': [('readonly', False)]})
    nausea_and_or_vomiting_related_to_medication = fields.Selection(yes_no_na, readonly=True,
                                                                    states={'Start': [('readonly', False)]})
    constipation_related_to_medication_immobility_decrease = fields.Selection(yes_no_na, readonly=True,
                                                                              states={'Start': [('readonly', False)]})
    breathlessness_related_to_disease_process = fields.Selection(yes_no_na, readonly=True,
                                                                 states={'Start': [('readonly', False)]})
    psychosocial_issues_related_terminal_prognosis = fields.Selection(yes_no_na, readonly=True,
                                                                      states={'Start': [('readonly', False)]})

    pall_measurable_goals_show = fields.Boolean()
    will_maintain_adequate_level_of_comfort_as_evidenced_no_signs = fields.Selection(yes_no_na, readonly=True, states={
        'Start': [('readonly', False)]})
    verbalizing_relief_pain_with_ordered_medications = fields.Selection(yes_no_na, readonly=True,
                                                                        states={'Start': [('readonly', False)]})
    will_function_at_optimal_level_within_limitations_imposed = fields.Selection(yes_no_na, readonly=True, states={
        'Start': [('readonly', False)]})
    verbalizing_satisfaction_with_level_of_comfort = fields.Selection(yes_no_na, readonly=True,
                                                                      states={'Start': [('readonly', False)]})
    will_demonstrate_adjustment_to_of_life_situation_by_verbally = fields.Selection(yes_no_na, readonly=True, states={
        'Start': [('readonly', False)]})
    expressing_through_words_or_actions_understanding_of_what = fields.Selection(yes_no_na, readonly=True, states={
        'Start': [('readonly', False)]})

    pall_patient_assessment_show = fields.Boolean()
    pall_presence_of_pain = fields.Selection(yes_no, readonly=True, states={'Start': [('readonly', False)]})
    pain_relieve_with_medication = fields.Selection(yes_no, readonly=True, states={'Start': [('readonly', False)]})
    presence_of_nausea = fields.Selection(yes_no, readonly=True, states={'Start': [('readonly', False)]})
    presence_of_vomiting = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    presence_of_constipation = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    frequency = fields.Selection([
        ('Once', 'Once'),
        ('2-3 times per day', '2-3 times per day'),
        ('more than 4 times/dav', 'more than 4 times/dav'),
    ], readonly=True, states={'Start': [('readonly', False)]})

    narcotics_show = fields.Boolean()
    regular_dose = fields.Text(readonly=True, states={'Start': [('readonly', False)]})
    breakthrough_dose = fields.Text(readonly=True, states={'Start': [('readonly', False)]})
    no_of_breakthrough_dose = fields.Text(readonly=True, states={'Start': [('readonly', False)]})
    narcotic_supply_enough_till = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No'),
        ('For refill', 'For refill'),
    ], readonly=True, states={'Start': [('readonly', False)]})

    pall_caregiver_assessment_show = fields.Boolean()
    management_of_patient_pain = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    management_of_patient_nutrition = fields.Selection(yes_no_na, readonly=True,
                                                       states={'Start': [('readonly', False)]})
    coping_psychologically = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    pall_coping_with_patient_care = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})

    pall_patient_caregiver_education_show = fields.Boolean()
    ensure_that_patient_taking_analgesia = fields.Selection(yes_no_na, readonly=True,
                                                            states={'Start': [('readonly', False)]})
    ensure_that_there_sufficient_pain = fields.Selection(yes_no_na, readonly=True,
                                                         states={'Start': [('readonly', False)]})
    advice_activity_movement_hour_after = fields.Selection(yes_no_na, readonly=True,
                                                           states={'Start': [('readonly', False)]})
    advise_increase_fluids_tolerated = fields.Selection(yes_no_na, readonly=True,
                                                        states={'Start': [('readonly', False)]})
    advice_take_stool_softeners_for_constipation = fields.Selection(yes_no_na, readonly=True,
                                                                    states={'Start': [('readonly', False)]})
    encourage_mobility_tolerated = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    take_anti_emetics_minutes_before = fields.Selection(yes_no_na, readonly=True,
                                                        states={'Start': [('readonly', False)]})
    take_small_frequent_meals = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    pall_remarks_show = fields.Boolean()
    pall_remarks = fields.Text(readonly=True, states={'Start': [('readonly', False)]})
    # Anticoagulation # Anticoagulation # Anticoagulation # Anticoagulation # Anticoagulation # Anticoagulation # Anticoag
    type_of_anticoagulation_show = fields.Boolean()
    type_warfarin = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    type_other = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    type_other_text = fields.Text(readonly=True, states={'Start': [('readonly', False)]})

    frequency_inr_monitoring_show = fields.Boolean()
    frequency_daily = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    frequency_weekly = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    frequency_as_pre_primary = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    frequency_bimonthly = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    frequency_other = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    frequency_other_text = fields.Text(readonly=True, states={'Start': [('readonly', False)]})

    ant_potential_actual_risk_show = fields.Boolean()
    potential_for_complication_injury_related_anti_coagulation = fields.Selection(yes_no_na, readonly=True, states={
        'Start': [('readonly', False)]})
    over_or_under_anticoagulation_related_to_non_compliance = fields.Selection(yes_no_na, readonly=True,
                                                                               states={'Start': [('readonly', False)]})
    over_or_under_therapeutic_level_inr_related_to_non_compliance = fields.Selection(yes_no_na, readonly=True, states={
        'Start': [('readonly', False)]})
    medication_error_related_to_inappropriate_taking_of_warfarin = fields.Selection(yes_no_na, readonly=True, states={
        'Start': [('readonly', False)]})

    ant_measurable_goals_show = fields.Boolean()
    will_be_remain_free_from_complications_bleeding_injury = fields.Selection(yes_no_na, readonly=True, states={
        'Start': [('readonly', False)]})
    inr_will_be_within_therapeutic_level = fields.Selection(yes_no_na, readonly=True,
                                                            states={'Start': [('readonly', False)]})
    patient_will_be_compliant_with_taking_warfarin = fields.Selection(yes_no_na, readonly=True, states={
        'Start': [('readonly', False)]})
    there_will_be_no_medication_error_related_to_taking = fields.Selection(yes_no_na, readonly=True, states={
        'Start': [('readonly', False)]})

    ant_patient_assessment_show = fields.Boolean()
    vital_signs_normal = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    any_change_in_diet = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    develop_any_infection_that = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    presence_of_chest_pain = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    presence_of_short_of_breath = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    presence_of_bleeding = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    presence_of_bruising = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})

    medication_review_show = fields.Boolean()
    taken_warfarin_dose = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    any_new_medication_commenced = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    enough_appropriate_warfarin = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    started_on_antibiotics = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    ensure_that_patient_taking = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})

    ant_caregiver_assessment_show = fields.Boolean()
    administer_correct_warfarin_dose_since = fields.Selection(yes_no_na, readonly=True,
                                                              states={'Start': [('readonly', False)]})
    understand_dosing_regime = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    medication_storage_appropriately = fields.Selection(yes_no_na, readonly=True,
                                                        states={'Start': [('readonly', False)]})
    one_reliable_family_member = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    caregiver_name_identified = fields.Text(readonly=True, states={'Start': [('readonly', False)]})

    ant_patient_caregiver_education_show = fields.Boolean()
    warfarin_tablets_to_be_given = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    to_report_missed_dose = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    check_with_home_care_staff_before = fields.Selection(yes_no_na, readonly=True,
                                                         states={'Start': [('readonly', False)]})
    to_observe_for_any_bleeding = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    correct_technique_in_performing = fields.Selection(yes_no_na, readonly=True,
                                                       states={'Start': [('readonly', False)]})
    rotate_injection_sites = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    ant_remarks_show = fields.Boolean()
    ant_remarks = fields.Text(readonly=True, states={'Start': [('readonly', False)]})
    # Diabetic # Diabetic # Diabetic # Diabetic # Diabetic # Diabetic # Diabetic # Diabetic # Diabetic # Diabetic
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

    dia_patient_assessment_show = fields.Boolean()
    dia_vital_signs_within_normal = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
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

    dia_patient_caregiver_education_show = fields.Boolean()
    ensure_that_patient_monitors = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    patient_taking_appropriate = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    check_feet_daily_any = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    encourages_activities = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    aware_of_managing_hypoglycaemic_event = fields.Selection(yes_no_na, readonly=True,
                                                             states={'Start': [('readonly', False)]})
    dia_remarks_show = fields.Boolean()
    dia_remarks = fields.Text(readonly=True, states={'Start': [('readonly', False)]})
    # Parenteral
    parenteral_route_show = fields.Boolean()
    peripheral_intravenous_cannula = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    p_i_c_c_line = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    central_catheter = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    subcutaneous = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    intramuscular = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    portacath = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    parenteral_other = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    parenteral_other_text = fields.Text(readonly=True, states={'Start': [('readonly', False)]})

    par_potential_actual_risk_show = fields.Boolean()
    complications_related_to_parenteral_therapy = fields.Selection(yes_no_na, readonly=True,
                                                                   states={'Start': [('readonly', False)]})
    complications_related_to_parenteral_medications = fields.Selection(yes_no_na, readonly=True,
                                                                       states={'Start': [('readonly', False)]})
    local_irritation_inflammation_or_infection_related = fields.Selection(yes_no_na, readonly=True,
                                                                          states={'Start': [('readonly', False)]})

    par_measurable_goals_show = fields.Boolean()
    parenteral_device_remains_functional_as_evidence_by = fields.Selection(yes_no_na, readonly=True,
                                                                           states={'Start': [('readonly', False)]})
    no_parenteral_site_infection_as_evidence_by_site_free = fields.Selection(yes_no_na, readonly=True,
                                                                             states={'Start': [('readonly', False)]})
    no_systemic_infection_related_to_parenteral_site = fields.Selection(yes_no_na, readonly=True,
                                                                        states={'Start': [('readonly', False)]})

    par_patient_assessment_show = fields.Boolean()
    par_vital_signs_within_normal = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    general_condition_improved = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    par_presence_of_pain = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    signs_of_phlebitis = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})

    catheter_site_assessment_show = fields.Boolean()
    leakage_from_site = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    site_dressing_attended = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    device_resited = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    p_i_line_exposed_tube_daily = fields.Float(readonly=True, states={'Start': [('readonly', False)]})

    infusion_device_show = fields.Boolean()
    correct_infusion_administered = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    parameters_updated = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    infusion_therapy_started = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    batteries_changed_checked = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})

    par_caregiver_assessment_show = fields.Boolean()
    par_coping_with_patient_care = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    able_to_troubleshoot_device = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    care_of_parenteral_site = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    compliant_to_education = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})

    par_patient_caregiver_education_show = fields.Boolean()
    aware_of_action_and_side_effects = fields.Selection(yes_no_na, readonly=True,
                                                        states={'Start': [('readonly', False)]})
    care_iv_access_at_home_during = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    par_pain_management = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    advice_on_activity_tolerated = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    trouble_shoot_infusion_device = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    to_inform_home_care_when_parenteral_site = fields.Selection(yes_no_na, readonly=True,
                                                                states={'Start': [('readonly', False)]})
    par_remarks_show = fields.Boolean()
    par_remarks = fields.Text(readonly=True, states={'Start': [('readonly', False)]})
    # Wound tab
    wound_history_show = fields.Boolean()
    wound_history = fields.Text(string='Wound History', readonly=True, states={'Start': [('readonly', False)]})
    # Type of Wound fields
    type_wound_show = fields.Boolean()
    surgical = fields.Boolean(string='Surgical', readonly=True, states={'Start': [('readonly', False)]})
    pressure_ulcer = fields.Boolean(string='Pressure Ulcer', readonly=True, states={'Start': [('readonly', False)]})
    diabetic = fields.Boolean(string='Diabetic', readonly=True, states={'Start': [('readonly', False)]})
    other_types = fields.Boolean(string='Other', readonly=True, states={'Start': [('readonly', False)]})
    other_types_content = fields.Char(readonly=True, states={'Start': [('readonly', False)]})

    # Factors Influencing Wound Healing
    factors_influencing_show = fields.Boolean()
    diabetes = fields.Boolean(string='Diabetes', readonly=True, states={'Start': [('readonly', False)]})
    immobility = fields.Boolean(string='Immobility', readonly=True, states={'Start': [('readonly', False)]})
    tissue_perfusion = fields.Boolean(string='Tissue perfusion', readonly=True, states={'Start': [('readonly', False)]})
    infection = fields.Boolean(string='Infection', readonly=True, states={'Start': [('readonly', False)]})

    incontinence = fields.Boolean(string='Incontinence', readonly=True, states={'Start': [('readonly', False)]})
    malnutrition = fields.Boolean(string='Malnutrition', readonly=True, states={'Start': [('readonly', False)]})
    immnuno_compromised = fields.Boolean(string='Immnuno compromised', readonly=True,
                                         states={'Start': [('readonly', False)]})
    blood_related = fields.Boolean(string='Blood related', readonly=True, states={'Start': [('readonly', False)]})
    blood_related_content = fields.Char(readonly=True, states={'Start': [('readonly', False)]})
    other_factors = fields.Boolean(string='Other', readonly=True, states={'Start': [('readonly', False)]})
    other_factors_content = fields.Char(readonly=True, states={'Start': [('readonly', False)]})

    # Potential Risk
    potential_risk_show = fields.Boolean()
    infection_potential = fields.Boolean(string='Infection', readonly=True, states={'Start': [('readonly', False)]})
    Poor_healing = fields.Boolean(string='Poor healing', readonly=True, states={'Start': [('readonly', False)]})
    other_potential = fields.Boolean(string='Other', readonly=True, states={'Start': [('readonly', False)]})
    other_potential_content = fields.Char(readonly=True, states={'Start': [('readonly', False)]})

    # Measurable Goals
    wound_measurable_goals_show = fields.Boolean()
    free_signs_infection = fields.Boolean(string='Free from signs of infection', readonly=True,
                                          states={'Start': [('readonly', False)]})
    increase_area_granulating_tissue = fields.Boolean(string='Increase in area granulating tissue', readonly=True,
                                                      states={'Start': [('readonly', False)]})
    free_skin_excoriation = fields.Boolean(string='Free from skin excoriation', readonly=True,
                                           states={'Start': [('readonly', False)]})
    free_necrosis = fields.Boolean(string='Free from necrosis', readonly=True, states={'Start': [('readonly', False)]})
    # Annotation image
    annotation_image_show = fields.Boolean()
    annotation_image = fields.Binary(readonly=True, states={'Start': [('readonly', False)]})
    # wound assessment and dressing plan
    wound_assessment_dressing_show = fields.Boolean()
    add_new_wound_assessment = fields.Boolean()
    add_new_wound_assessment_date = fields.Date(string='Date', readonly=True,
                                                states={'Admitted': [('readonly', False)]})
    add_other_wound_assessment = fields.Boolean()
    add_other_wound_assessment_date = fields.Date(string='Date', readonly=True,
                                                  states={'Admitted': [('readonly', False)]})

    comprehensive_follow_up_id = fields.One2many('sm.shifa.comprehensive.nurse.follow.up', 'comprehensive_nurse_ass_id',
                                                 string='comprehensive follow up')
    referral_id = fields.One2many('sm.shifa.referral', 'nurse_ass_ref_id', string='comprehensive referral')
    wound_ids = fields.One2many('sm.shifa.wound.assessment.values', 'wound_ass_id', string='Wound Assessment')

    wound_add = fields.One2many('sm.shifa.wound.assessment.values', 'wound_ass_id', string='Wound Assessment')
    wound_new_add = fields.One2many('sm.shifa.wound.assessment.values', 'wound_ass_id', string='Wound Assessment')

    nursing_comprehensive_ids = fields.Many2one('sm.shifa.physician.admission', string='Nurse', ondelete='cascade')
    no_complication_of_pulmonary_micro_embolism = fields.Selection(yes_no_na, readonly=True,
                                                                   states={'Start': [('readonly', False)]})
    apply_warm_compress_to_injection_site = fields.Selection(yes_no_na, readonly=True,
                                                             states={'Start': [('readonly', False)]})
    blood_test_done = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    nurse_assessment_show = fields.Boolean()
    nurse_note_assessment = fields.Text()

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
    diagnosis_show = fields.Boolean()
    conscious_state_show = fields.Boolean()

    assessment_show = fields.Boolean()
    # care_rendered_show = fields.Boolean()
    # care_rendered = fields.Char()
    care_plan_show = fields.Boolean()
    smart_goals_show = fields.Boolean()
    actual_risk_show = fields.Boolean()

    nurse_wound_show = fields.Boolean()
    nurse_note_wound = fields.Text()

    # newborn tab
    clinical_assessments_show = fields.Boolean()
    head_normal = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    head_abnormal = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    head_abnormal_content = fields.Char(readonly=True, states={'Start': [('readonly', False)]})
    skin_normal = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    skin_abnormal = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    skin_abnormal_content = fields.Char(readonly=True, states={'Start': [('readonly', False)]})
    lunge_normal = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    lunge_abnormal = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    lunge_abnormal_content = fields.Char(readonly=True, states={'Start': [('readonly', False)]})
    chest_normal = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    chest_abnormal = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    chest_abnormal_content = fields.Char(readonly=True, states={'Start': [('readonly', False)]})
    abdomen_normal = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    abdomen_abnormal = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    abdomen_abnormal_content = fields.Char(readonly=True, states={'Start': [('readonly', False)]})
    elimination_normal = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    elimination_abnormal = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    elimination_abnormal_content = fields.Char(readonly=True, states={'Start': [('readonly', False)]})
    genitalia_normal = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    genitalia_abnormal = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    genitalia_abnormal_content = fields.Char(readonly=True, states={'Start': [('readonly', False)]})
    extremities_normal = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    extremities_abnormal = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    extremities_abnormal_content = fields.Char(readonly=True, states={'Start': [('readonly', False)]})
    number_of_diaper_per_day = fields.Integer(readonly=True, states={'Start': [('readonly', False)]})
    number_of_stools_per_day = fields.Integer(readonly=True, states={'Start': [('readonly', False)]})
    adequate_amount_diapers_home = fields.Selection(yes_no, readonly=True, states={'Start': [('readonly', False)]})
    adequate_amount_diapers_home_text = fields.Char(readonly=True, states={'Start': [('readonly', False)]})
    circumcised = fields.Selection(yes_no, readonly=True, states={'Start': [('readonly', False)]})

    mental_assessments_show = fields.Boolean()
    amount_crying_normal = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    amount_crying_abnormal = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    amount_crying_abnormal_content = fields.Char(readonly=True, states={'Start': [('readonly', False)]})
    makes_eye_contact_normal = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    makes_eye_contact_abnormal = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    makes_eye_contact_abnormal_content = fields.Char(readonly=True, states={'Start': [('readonly', False)]})
    quiet_when_pick_normal = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    quiet_when_pick_abnormal = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    quiet_when_pick_abnormal_content = fields.Char(readonly=True, states={'Start': [('readonly', False)]})

    feeding_type = fields.Selection([
        ('Breast', 'Breast'),
        ('Bottle', 'Bottle'),
        ('Breast and Bottle', 'Breast and Bottle'),
    ], readonly=True, states={'Start': [('readonly', False)]})
    formula_feeding = fields.Text(readonly=True, states={'Start': [('readonly', False)]})
    amount_frequency = fields.Text(readonly=True, states={'Start': [('readonly', False)]})
    adequate_amount_of_formula = fields.Selection(yes_no, readonly=True, states={'Start': [('readonly', False)]})
    adequate_amount_of_formula_text = fields.Char(readonly=True, states={'Start': [('readonly', False)]})

    other_assessment_show = fields.Boolean()
    other_assessment_show_text = fields.Text(readonly=True, states={'Start': [('readonly', False)]})

    immunization_show = fields.Boolean()
    received_initial_hepatitis = fields.Selection(yes_no, readonly=True, states={'Start': [('readonly', False)]})
    where_and_when = fields.Text(readonly=True, states={'Start': [('readonly', False)]})
    has_an_appointment_been = fields.Selection(yes_no, readonly=True, states={'Start': [('readonly', False)]})
    has_an_appointment_been_date = fields.Date(readonly=True, states={'Start': [('readonly', False)]})
    has_an_appointment_been_where = fields.Char(readonly=True, states={'Start': [('readonly', False)]})
    has_an_appointment_been_no_text = fields.Text(readonly=True, states={'Start': [('readonly', False)]})

    safe_sleep_show = fields.Boolean()
    crib = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    bassinet = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    other = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    other_content = fields.Char(readonly=True, states={'Start': [('readonly', False)]})

    mother_caregiver_education_show = fields.Boolean()
    advise_to_refrain_putting_stuffed_animals = fields.Selection(yes_no_na, readonly=True,
                                                                 states={'Start': [('readonly', False)]})
    advise_that_sleep_environment_should = fields.Selection(yes_no_na, readonly=True,
                                                            states={'Start': [('readonly', False)]})
    advise_not_to_share_sleep = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    advise_on_proper_position = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    advise_to_refrain_from_smoking = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    advise_to_change_clothes_before_holding = fields.Selection(yes_no_na, readonly=True,
                                                               states={'Start': [('readonly', False)]})
    advise_that_supervision_needed_when = fields.Selection(yes_no_na, readonly=True,
                                                           states={'Start': [('readonly', False)]})

    # Oxygen Administration tab
    type_of_oxygen_inhalation_show = fields.Boolean()
    type_of_oxygen_inhalation = fields.Selection([
        ('Nosal', 'Nosal'),
        ('Face Mask', 'Face Mask'),
        ('High Flow', 'High Flow'),
    ], readonly=True, states={'Start': [('readonly', False)]})

    risk_for_dry_or_bloody_nose = fields.Selection(yes_no, readonly=True, states={'Start': [('readonly', False)]})
    risk_for_oxygen_toxicity = fields.Selection(yes_no, readonly=True, states={'Start': [('readonly', False)]})

    to_achieve_adequate_tissue_oxygenation = fields.Selection(yes_no,
                                                              readonly=True, states={'Start': [('readonly', False)]})

    presence_of_shortness_of_breath = fields.Selection(yes_no,
                                                       readonly=True, states={'Start': [('readonly', False)]})
    presence_of_cough = fields.Selection(yes_no,
                                         readonly=True, states={'Start': [('readonly', False)]})
    presence_of_chest_pain_due_to_excessive_coughing = fields.Selection(yes_no,
                                                                        readonly=True,
                                                                        states={'Start': [('readonly', False)]})

    applies_safe_use_equipment_procedure_practice = fields.Selection(yes_no,
                                                                     readonly=True,
                                                                     states={'Start': [('readonly', False)]})
    never_smoke_and_don_let_others_light_near_you = fields.Selection(yes_no,
                                                                     readonly=True,
                                                                     states={'Start': [('readonly', False)]})
    keep_oxygen_containers_upright = fields.Selection(yes_no,
                                                      readonly=True, states={'Start': [('readonly', False)]})
    # pressure ulcer tab
    competent_yes_no_na = [
        ('Competent', 'Competent'),
        ('Yes', 'Yes'),
        ('No', 'No'),
        ('NA', 'NA'),
    ]
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
    # postnatal tab
    postnatal_day_show = fields.Boolean()
    postnatal_day = fields.Integer(readonly=True, states={'Start': [('readonly', False)]})

    type_of_delivery_show = fields.Boolean()
    normal_delivery = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    casarean_delivery = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    delivery_other = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    delivery_other_text = fields.Text(readonly=True, states={'Start': [('readonly', False)]})

    pos_potential_actual_risk_show = fields.Boolean()
    risk_for_infection_related_to_episiotomy_post = fields.Selection(yes_no_na, readonly=True,
                                                                     states={'Start': [('readonly', False)]})
    alteration_in_comfort_pain_related_to_episiotomy = fields.Selection(yes_no_na, readonly=True,
                                                                        states={'Start': [('readonly', False)]})
    risk_for_fluid_volume_deficit_related_to_vaginal_bleeding = fields.Selection(yes_no_na, readonly=True, states={
        'Start': [('readonly', False)]})
    risk_for_maternal_injury_related_to_tissue_oedema_and = fields.Selection(yes_no_na, readonly=True,
                                                                             states={'Start': [('readonly', False)]})

    pos_measurable_goals_show = fields.Boolean()
    will_be_able_to_demonstrate_proper_perineal_care = fields.Selection(yes_no_na, readonly=True,
                                                                        states={'Start': [('readonly', False)]})
    will_maintain_adequate_level_of_comfort_as_evidenced_by_pain = fields.Selection(yes_no_na, readonly=True, states={
        'Start': [('readonly', False)]})
    vital_signs_remain_stable_with_moderate_amount_of_lochia = fields.Selection(yes_no_na, readonly=True,
                                                                                states={'Start': [('readonly', False)]})
    free_of_signs_of_cerebral_ischemia_within = fields.Selection(yes_no_na, readonly=True,
                                                                 states={'Start': [('readonly', False)]})

    vital_signs_stable = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    presence_of_headache = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    change_in_vision = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    breast = fields.Selection([
        ('Hard', 'Hard'),
        ('Swollen', 'Swollen'),
        ('Painful', 'Painful'),
    ], readonly=True, states={'Start': [('readonly', False)]})
    uterus = fields.Selection([
        ('Fundus Firm', 'Fundus Firm'),
        ('Not palpable', 'Not palpable'),
        ('NA', 'NA'),
    ], readonly=True, states={'Start': [('readonly', False)]})
    bowel_pattem = fields.Selection([
        ('Normal', 'Normal'),
        ('Abnormal', 'Abnormal'),
    ], readonly=True, states={'Start': [('readonly', False)]})
    postnatal_bladder = fields.Selection([
        ('Voiding comfortaness', 'Voiding comfortaness'),
        ('Fullness/with pressure', 'Fullness/with pressure'),
    ], readonly=True, states={'Start': [('readonly', False)]})
    abdominal_incision = fields.Selection([
        ('not inflamed', 'not inflamed'),
        ('no drainage', 'no drainage'),
        ('little drainage', 'little drainage'),
        ('staple present', 'staple present'),
        ('dressing intact', 'dressing intact'),
        ('decrease swelling', 'decrease swelling'),
    ], readonly=True, states={'Start': [('readonly', False)]})
    episiotomy_episiorapphy = fields.Selection([
        ('Intact', 'Intact'),
        ('Small tearing', 'Small tearing'),
        ('with bruising or', 'with bruising or'),
        ('swelling', 'swelling'),
    ], readonly=True, states={'Start': [('readonly', False)]})
    lochia = fields.Selection([
        ('Fleslage smelly', 'Fleslage smelly'),
        ('Rubra serosa', 'Rubra serosa'),
        ('lochia serosa', 'lochia serosa'),
        ('darie red', 'darie red'),
        ('discharges', 'discharges'),
        ('lochia alba', 'lochia alba'),
    ], readonly=True, states={'Start': [('readonly', False)]})
    homan_sign = fields.Selection([
        ('unilateral calf pain', 'unilateral calf pain'),
        ('negative DVT', 'negative DVT'),
        ('Redness', 'Redness'),
        ('Swollen', 'Swollen'),
    ], readonly=True, states={'Start': [('readonly', False)]})

    postnatal_specific_dietary_needs = fields.Selection([
        ('Diabetic', 'Diabetic'),
        ('low salt', 'low salt'),
        ('law fat', 'law fat'),
        ('high fiber', 'high fiber'),
        ('low salt, low fat', 'low salt, low fat'),
        ('Regular diet', 'Regular diet'),
    ], readonly=True, states={'Start': [('readonly', False)]})

    oral_medication_discussed = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    patient_caregiver_able = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    postnatal_medication_review_done = fields.Selection(yes_no_na, readonly=True,
                                                        states={'Start': [('readonly', False)]})
    next_review_due = fields.Text(readonly=True, states={'Start': [('readonly', False)]})

    advised_on_well_balanced_nutrition_fluids = fields.Selection(yes_no_na, readonly=True,
                                                                 states={'Start': [('readonly', False)]})
    advised_on_ambulation_to_prevent = fields.Selection(yes_no_na, readonly=True,
                                                        states={'Start': [('readonly', False)]})
    report_to_emergency_department_for_sudden = fields.Selection(yes_no_na, readonly=True,
                                                                 states={'Start': [('readonly', False)]})
    report_to_emergency_department_for_headache = fields.Selection(yes_no_na, readonly=True,
                                                                   states={'Start': [('readonly', False)]})
    report_to_emergency_department_for_unilateral = fields.Selection(yes_no_na, readonly=True,
                                                                     states={'Start': [('readonly', False)]})
    advise_to_take_prescribed_analgesia = fields.Selection(yes_no_na, readonly=True,
                                                           states={'Start': [('readonly', False)]})
    advise_to_palpate_fundus_and_able_to_demonstrate = fields.Selection(yes_no_na, readonly=True,
                                                                        states={'Start': [('readonly', False)]})
    advise_to_empty_bladder_and_be_aware_of_need = fields.Selection(yes_no_na, readonly=True,
                                                                    states={'Start': [('readonly', False)]})
    encourage_to_splint_abdomen_with_pillow_when = fields.Selection(yes_no_na, readonly=True,
                                                                    states={'Start': [('readonly', False)]})
    observe_for_increased_bleeding_on_post = fields.Selection(yes_no_na, readonly=True,
                                                              states={'Start': [('readonly', False)]})
    advise_refrain_form_tub_bath_until_dressings = fields.Selection(yes_no_na, readonly=True,
                                                                    states={'Start': [('readonly', False)]})
    advise_to_use_good_body_mechanics_and_avoiding = fields.Selection(yes_no_na, readonly=True,
                                                                      states={'Start': [('readonly', False)]})
    advise_on_frequent_breastfeeding_to_help_prevent = fields.Selection(yes_no_na, readonly=True,
                                                                        states={'Start': [('readonly', False)]})
    advise_on_using_non_restricting_bra = fields.Selection(yes_no_na, readonly=True,
                                                           states={'Start': [('readonly', False)]})
    advise_on_massaging_breast_gently_and_manually_express_milk = fields.Selection(yes_no_na, readonly=True, states={
        'Start': [('readonly', False)]})
    advise_application_of_warm_compresses_shower_or_breast = fields.Selection(yes_no_na, readonly=True,
                                                                              states={'Start': [('readonly', False)]})
    advise_on_care_support_and_breastfeeding_technique_for_women = fields.Selection(yes_no_na, readonly=True, states={
        'Start': [('readonly', False)]})
    advise_on_hand_hygiene = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    advise_on_voiding_comfort_measure = fields.Selection(yes_no_na, readonly=True,
                                                         states={'Start': [('readonly', False)]})
    advise_on_lochia_and_perineum_comfort = fields.Selection(yes_no_na, readonly=True,
                                                             states={'Start': [('readonly', False)]})
    advise_on_activities_and_rest = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    advise_on_normal_patterns_of_emotional_changes = fields.Selection(yes_no_na, readonly=True,
                                                                      states={'Start': [('readonly', False)]})
    advise_on_proper_breastfeeding_technique = fields.Selection(yes_no_na, readonly=True,
                                                                states={'Start': [('readonly', False)]})

    key_performance_indictor_show = fields.Boolean()
    hospital_readmission = fields.Text(readonly=True, states={'Start': [('readonly', False)]})
    since_last_visit_patient_was = fields.Text(readonly=True, states={'Start': [('readonly', False)]})
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
    drug_allergy_yes = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    drug_allergy_no = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    drug_allergy_content = fields.Char(readonly=True, states={'Start': [('readonly', False)]})

    allergic_previous_yes = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    allergic_previous_no = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    allergic_previous_content = fields.Char(readonly=True, states={'Start': [('readonly', False)]})

    allergic_hypersensitivty_yes = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    allergic_hypersensitivty_no = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    allergic_hypersensitivty_content = fields.Char(readonly=True, states={'Start': [('readonly', False)]})

    any_recent_illness_yes = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    any_recent_illness_no = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    any_recent_illness_content = fields.Char(readonly=True, states={'Start': [('readonly', False)]})

    previous_vaccination_yes = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    previous_vaccination_no = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    previous_vaccination_content = fields.Char(readonly=True, states={'Start': [('readonly', False)]})
    previous_vaccination_temp = fields.Float(readonly=True, states={'Start': [('readonly', False)]})

    pain_present_show = fields.Boolean()

    # Nebulization tab

    potential_acual_risk_show = fields.Boolean()
    risk_for_faster_heartbeat = fields.Selection(yes_no, readonly=True, states={'Start': [('readonly', False)]})
    risk_for_slightly_shaking_muscles = fields.Selection(yes_no, readonly=True, states={'Start': [('readonly', False)]})

    measurable_goals_review_date_show = fields.Boolean()
    fast_relief_from_inflammation_and_allowing = fields.Selection(yes_no, readonly=True,
                                                                  states={'Start': [('readonly', False)]})

    patient_assessment_show = fields.Boolean()
    has_productive_cough = fields.Selection(yes_no, readonly=True,
                                            states={'Start': [('readonly', False)]})
    obvious_nasal_flaring_shortness_breath = fields.Selection(yes_no, readonly=True,
                                                              states={'Start': [('readonly', False)]})
    breathing_easier_after_nebulization = fields.Selection(yes_no, readonly=True,
                                                           states={'Start': [('readonly', False)]})

    patient_caregiver_education_show = fields.Boolean()
    lifestyle_changes_treat_shortness_breath = fields.Selection(yes_no, readonly=True,
                                                                states={'Start': [('readonly', False)]})
    educate_deep_breathing_exercises = fields.Selection(yes_no, readonly=True,
                                                        states={'Start': [('readonly', False)]})
    avoiding_exposure_pollutants_allergens = fields.Selection(yes_no, readonly=True,
                                                              states={'Start': [('readonly', False)]})
    comply_medication_prescribed = fields.Selection(yes_no, readonly=True,
                                                    states={'Start': [('readonly', False)]})

    remarks_show = fields.Boolean()
    remarks = fields.Text(states={'Start': [('readonly', False)]})

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
    ], readonly=True, states={'Start': [('readonly', False)]})
    ADMINISTERED_OVER = [
        ('Right', 'Right'),
        ('Left', 'Left'),
    ]
    at_birth_hepb = fields.Boolean(string='HepB (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    at_birth_hepb_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                           states={'Start': [('readonly', False)]})
    at_birth_hepb_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                            states={'Start': [('readonly', False)]})
    at_birth_hepb_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                                  states={'Start': [('readonly', False)]})
    add_other_at_birth = fields.Boolean(string='Other', readonly=True,
                                        states={'Start': [('readonly', False)]})
    add_other_at_birth_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=True,
                                                       states={'Start': [('readonly', False)]})
    add_other_at_birth_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                                states={'Start': [('readonly', False)]})
    add_other_at_birth_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                                 states={'Start': [('readonly', False)]})
    add_other_at_birth_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                                       states={'Start': [('readonly', False)]})

    add_other_at_birth_comment = fields.Char(string='Vaccine Lot No', readonly=True,
                                             states={'Start': [('readonly', False)]})
    add_other2_at_birth = fields.Boolean(string='Other', readonly=True,
                                         states={'Start': [('readonly', False)]})
    add_other2_at_birth_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=True,
                                                        states={'Start': [('readonly', False)]})
    add_other2_at_birth_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                                 states={'Start': [('readonly', False)]})
    add_other2_at_birth_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                                  states={'Start': [('readonly', False)]})
    add_other2_at_birth_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                                        states={'Start': [('readonly', False)]})

    add_other2_at_birth_comment = fields.Char(string='Vaccine Lot No', readonly=True,
                                              states={'Start': [('readonly', False)]})

    t_mon_hepb = fields.Boolean(string='HepB (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    t_mon_hepb_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                        states={'Start': [('readonly', False)]})
    t_mon_hepb_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                         states={'Start': [('readonly', False)]})
    t_mon_hepb_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                               states={'Start': [('readonly', False)]})

    t_mon_rv = fields.Boolean(string='RV (1 ml)', readonly=True, states={'Start': [('readonly', False)]})
    t_mon_rv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                      states={'Start': [('readonly', False)]})
    t_mon_rv_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                       states={'Start': [('readonly', False)]})
    t_mon_rv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                             states={'Start': [('readonly', False)]})

    t_mon_dtap = fields.Boolean(string='D TaP (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    t_mon_dtap_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                        states={'Start': [('readonly', False)]})
    t_mon_dtap_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                         states={'Start': [('readonly', False)]})
    t_mon_dtap_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                               states={'Start': [('readonly', False)]})

    t_mon_hib = fields.Boolean(string='Hib (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    t_mon_hib_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                       states={'Start': [('readonly', False)]})
    t_mon_hib_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                        states={'Start': [('readonly', False)]})
    t_mon_hib_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                              states={'Start': [('readonly', False)]})

    t_mon_pcv = fields.Boolean(string='PCV (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    t_mon_pcv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                       states={'Start': [('readonly', False)]})
    t_mon_pcv_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                        states={'Start': [('readonly', False)]})
    t_mon_pcv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                              states={'Start': [('readonly', False)]})

    t_mon_ipv = fields.Boolean(string='IPV (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    t_mon_ipv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                       states={'Start': [('readonly', False)]})
    t_mon_ipv_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                        states={'Start': [('readonly', False)]})
    t_mon_ipv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                              states={'Start': [('readonly', False)]})

    add_other_t_mon = fields.Boolean(string='Other', readonly=True,
                                     states={'Start': [('readonly', False)]})
    add_other_t_mon_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=True,
                                                    states={'Start': [('readonly', False)]})
    add_other_t_mon_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                             states={'Start': [('readonly', False)]})
    add_other_t_mon_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                              states={'Start': [('readonly', False)]})
    add_other_t_mon_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                                    states={'Start': [('readonly', False)]})

    add_other_t_mon_comment = fields.Char(string='Vaccine Lot No', readonly=True,
                                          states={'Start': [('readonly', False)]})
    add_other2_t_mon = fields.Boolean(string='Other', readonly=True,
                                      states={'Start': [('readonly', False)]})
    add_other2_t_mon_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=True,
                                                     states={'Start': [('readonly', False)]})
    add_other2_t_mon_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                              states={'Start': [('readonly', False)]})
    add_other2_t_mon_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                               states={'Start': [('readonly', False)]})
    add_other2_t_mon_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                                     states={'Start': [('readonly', False)]})

    add_other2_t_mon_comment = fields.Char(string='Vaccine Lot No', readonly=True,
                                           states={'Start': [('readonly', False)]})

    f_mon_hepb = fields.Boolean(string='HepB (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    f_mon_hepb_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                        states={'Start': [('readonly', False)]})
    f_mon_hepb_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                         states={'Start': [('readonly', False)]})
    f_mon_hepb_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                               states={'Start': [('readonly', False)]})

    f_mon_rv = fields.Boolean(string='RV (1 ml)', readonly=True, states={'Start': [('readonly', False)]})
    f_mon_rv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                      states={'Start': [('readonly', False)]})
    f_mon_rv_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                       states={'Start': [('readonly', False)]})
    f_mon_rv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                             states={'Start': [('readonly', False)]})

    f_mon_dtap = fields.Boolean(string='D TaP (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    f_mon_dtap_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                        states={'Start': [('readonly', False)]})
    f_mon_dtap_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                         states={'Start': [('readonly', False)]})
    f_mon_dtap_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                               states={'Start': [('readonly', False)]})

    f_mon_hib = fields.Boolean(string='Hib (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    f_mon_hib_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                       states={'Start': [('readonly', False)]})
    f_mon_hib_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                        states={'Start': [('readonly', False)]})
    f_mon_hib_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                              states={'Start': [('readonly', False)]})

    f_mon_pcv = fields.Boolean(string='PCV (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    f_mon_pcv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                       states={'Start': [('readonly', False)]})
    f_mon_pcv_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                        states={'Start': [('readonly', False)]})
    f_mon_pcv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                              states={'Start': [('readonly', False)]})
    f_mon_ipv = fields.Boolean(string='IPV (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    f_mon_ipv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                       states={'Start': [('readonly', False)]})
    f_mon_ipv_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                        states={'Start': [('readonly', False)]})
    f_mon_ipv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                              states={'Start': [('readonly', False)]})

    add_other_f_mon = fields.Boolean(string='Other', readonly=True,
                                     states={'Start': [('readonly', False)]})
    add_other_f_mon_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=True,
                                                    states={'Start': [('readonly', False)]})
    add_other_f_mon_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                             states={'Start': [('readonly', False)]})
    add_other_f_mon_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                              states={'Start': [('readonly', False)]})
    add_other_f_mon_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                                    states={'Start': [('readonly', False)]})

    add_other_f_mon_comment = fields.Char(string='Vaccine Lot No', readonly=True,
                                          states={'Start': [('readonly', False)]})
    add_other2_f_mon = fields.Boolean(string='Other', readonly=True,
                                      states={'Start': [('readonly', False)]})
    add_other2_f_mon_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=True,
                                                     states={'Start': [('readonly', False)]})
    add_other2_f_mon_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                              states={'Start': [('readonly', False)]})
    add_other2_f_mon_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                               states={'Start': [('readonly', False)]})
    add_other2_f_mon_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                                     states={'Start': [('readonly', False)]})

    add_other2_f_mon_comment = fields.Char(string='Vaccine Lot No', readonly=True,
                                           states={'Start': [('readonly', False)]})

    s_mon_hepb = fields.Boolean(string='HepB (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    s_mon_hepb_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                        states={'Start': [('readonly', False)]})
    s_mon_hepb_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                         states={'Start': [('readonly', False)]})
    s_mon_hepb_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                               states={'Start': [('readonly', False)]})

    s_mon_rv = fields.Boolean(string='RV (1 ml)', readonly=True, states={'Start': [('readonly', False)]})
    s_mon_rv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                      states={'Start': [('readonly', False)]})
    s_mon_rv_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                       states={'Start': [('readonly', False)]})
    s_mon_rv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                             states={'Start': [('readonly', False)]})

    s_mon_dtap = fields.Boolean(string='D TaP (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    s_mon_dtap_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                        states={'Start': [('readonly', False)]})
    s_mon_dtap_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                         states={'Start': [('readonly', False)]})

    s_mon_dtap_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                               states={'Start': [('readonly', False)]})

    s_mon_hib = fields.Boolean(string='Hib (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    s_mon_hib_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                       states={'Start': [('readonly', False)]})
    s_mon_hib_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                        states={'Start': [('readonly', False)]})
    s_mon_hib_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                              states={'Start': [('readonly', False)]})

    s_mon_pcv = fields.Boolean(string='PCV (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    s_mon_pcv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                       states={'Start': [('readonly', False)]})
    s_mon_pcv_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                        states={'Start': [('readonly', False)]})
    s_mon_pcv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                              states={'Start': [('readonly', False)]})

    s_mon_ipv = fields.Boolean(string='IPV (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    s_mon_ipv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                       states={'Start': [('readonly', False)]})
    s_mon_ipv_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                        states={'Start': [('readonly', False)]})
    s_mon_ipv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                              states={'Start': [('readonly', False)]})

    s_mon_bcg = fields.Boolean(string='BCG (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    s_mon_bcg_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                       states={'Start': [('readonly', False)]})
    s_mon_bcg_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                        states={'Start': [('readonly', False)]})
    s_mon_bcg_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                              states={'Start': [('readonly', False)]})

    s_mon_opv = fields.Boolean(string='OPV (2 gtts)', readonly=True, states={'Start': [('readonly', False)]})
    s_mon_opv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                       states={'Start': [('readonly', False)]})
    s_mon_opv_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                        states={'Start': [('readonly', False)]})
    s_mon_opv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                              states={'Start': [('readonly', False)]})

    add_other_s_mon = fields.Boolean(string='Other', readonly=True,
                                     states={'Start': [('readonly', False)]})
    add_other_s_mon_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=True,
                                                    states={'Start': [('readonly', False)]})
    add_other_s_mon_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                             states={'Start': [('readonly', False)]})
    add_other_s_mon_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                              states={'Start': [('readonly', False)]})
    add_other_s_mon_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                                    states={'Start': [('readonly', False)]})

    add_other_s_mon_comment = fields.Char(string='Vaccine Lot No', readonly=True,
                                          states={'Start': [('readonly', False)]})
    add_other2_s_mon = fields.Boolean(string='Other', readonly=True,
                                      states={'Start': [('readonly', False)]})
    add_other2_s_mon_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=True,
                                                     states={'Start': [('readonly', False)]})
    add_other2_s_mon_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                              states={'Start': [('readonly', False)]})
    add_other2_s_mon_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                               states={'Start': [('readonly', False)]})
    add_other2_s_mon_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                                     states={'Start': [('readonly', False)]})

    add_other2_s_mon_comment = fields.Char(string='Vaccine Lot No', readonly=True,
                                           states={'Start': [('readonly', False)]})

    n_mon_measels = fields.Boolean(string='Measels (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    n_mon_measels_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                           states={'Start': [('readonly', False)]})
    n_mon_measels_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                            states={'Start': [('readonly', False)]})
    n_mon_measels_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                                  states={'Start': [('readonly', False)]})

    n_mon_mcv = fields.Boolean(string='MCV4 (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    n_mon_mcv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                       states={'Start': [('readonly', False)]})
    n_mon_mcv_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                        states={'Start': [('readonly', False)]})
    n_mon_mcv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                              states={'Start': [('readonly', False)]})
    add_other_n_mon = fields.Boolean(string='Other', readonly=True,
                                     states={'Start': [('readonly', False)]})
    add_other_n_mon_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=True,
                                                    states={'Start': [('readonly', False)]})
    add_other_n_mon_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                             states={'Start': [('readonly', False)]})
    add_other_n_mon_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                              states={'Start': [('readonly', False)]})
    add_other_n_mon_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                                    states={'Start': [('readonly', False)]})

    add_other_n_mon_comment = fields.Char(string='Vaccine Lot No', readonly=True,
                                          states={'Start': [('readonly', False)]})
    add_other2_n_mon = fields.Boolean(string='Other', readonly=True,
                                      states={'Start': [('readonly', False)]})
    add_other2_n_mon_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=True,
                                                     states={'Start': [('readonly', False)]})
    add_other2_n_mon_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                              states={'Start': [('readonly', False)]})
    add_other2_n_mon_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                               states={'Start': [('readonly', False)]})
    add_other2_n_mon_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                                     states={'Start': [('readonly', False)]})

    add_other2_n_mon_comment = fields.Char(string='Vaccine Lot No', readonly=True,
                                           states={'Start': [('readonly', False)]})

    ot_mon_pcv = fields.Boolean(string='PCV (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    ot_mon_pcv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                        states={'Start': [('readonly', False)]})
    ot_mon_pcv_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                         states={'Start': [('readonly', False)]})
    ot_mon_pcv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                               states={'Start': [('readonly', False)]})

    ot_mon_opv = fields.Boolean(string='OPV (2 gtts)', readonly=True, states={'Start': [('readonly', False)]})
    ot_mon_opv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                        states={'Start': [('readonly', False)]})
    ot_mon_opv_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                         states={'Start': [('readonly', False)]})
    ot_mon_opv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                               states={'Start': [('readonly', False)]})

    ot_mon_mcv = fields.Boolean(string='MCV4 (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    ot_mon_mcv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                        states={'Start': [('readonly', False)]})
    ot_mon_mcv_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                         states={'Start': [('readonly', False)]})
    ot_mon_mcv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                               states={'Start': [('readonly', False)]})

    ot_mon_mmr = fields.Boolean(string='MMR (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    ot_mon_mmr_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                        states={'Start': [('readonly', False)]})
    ot_mon_mmr_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                         states={'Start': [('readonly', False)]})
    ot_mon_mmr_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                               states={'Start': [('readonly', False)]})

    add_other_ot_mon = fields.Boolean(string='Other', readonly=True,
                                      states={'Start': [('readonly', False)]})
    add_other_ot_mon_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=True,
                                                     states={'Start': [('readonly', False)]})
    add_other_ot_mon_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                              states={'Start': [('readonly', False)]})
    add_other_ot_mon_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                               states={'Start': [('readonly', False)]})
    add_other_ot_mon_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                                     states={'Start': [('readonly', False)]})

    add_other_ot_mon_comment = fields.Char(string='Vaccine Lot No', readonly=True,
                                           states={'Start': [('readonly', False)]})
    add_other2_ot_mon = fields.Boolean(string='Other', readonly=True,
                                       states={'Start': [('readonly', False)]})
    add_other2_ot_mon_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=True,
                                                      states={'Start': [('readonly', False)]})
    add_other2_ot_mon_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                               states={'Start': [('readonly', False)]})
    add_other2_ot_mon_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                                states={'Start': [('readonly', False)]})
    add_other2_ot_mon_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                                      states={'Start': [('readonly', False)]})

    add_other2_ot_mon_comment = fields.Char(string='Vaccine Lot No', readonly=True,
                                            states={'Start': [('readonly', False)]})

    oe_mon_dtap = fields.Boolean(string='D TaP (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    oe_mon_dtap_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                         states={'Start': [('readonly', False)]})
    oe_mon_dtap_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                          states={'Start': [('readonly', False)]})
    oe_mon_dtap_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                                states={'Start': [('readonly', False)]})

    oe_mon_hib = fields.Boolean(string='Hib (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    oe_mon_hib_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                        states={'Start': [('readonly', False)]})
    oe_mon_hib_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                         states={'Start': [('readonly', False)]})
    oe_mon_hib_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                               states={'Start': [('readonly', False)]})

    oe_mon_hepa = fields.Boolean(string='HepA (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    oe_mon_hepa_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                         states={'Start': [('readonly', False)]})
    oe_mon_hepa_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                          states={'Start': [('readonly', False)]})
    oe_mon_hepa_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                                states={'Start': [('readonly', False)]})

    oe_mon_varicella = fields.Boolean(string='Varicella (0.5 ml)', readonly=True,
                                      states={'Start': [('readonly', False)]})
    oe_mon_varicella_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                              states={'Start': [('readonly', False)]})
    oe_mon_varicella_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                               states={'Start': [('readonly', False)]})
    oe_mon_varicella_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                                     states={'Start': [('readonly', False)]})

    oe_mon_mmr = fields.Boolean(string='MMR (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    oe_mon_mmr_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                        states={'Start': [('readonly', False)]})
    oe_mon_mmr_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                         states={'Start': [('readonly', False)]})
    oe_mon_mmr_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                               states={'Start': [('readonly', False)]})

    oe_mon_opv = fields.Boolean(string='OPV (2 gtts)', readonly=True, states={'Start': [('readonly', False)]})
    oe_mon_opv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                        states={'Start': [('readonly', False)]})
    oe_mon_opv_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                         states={'Start': [('readonly', False)]})
    oe_mon_opv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                               states={'Start': [('readonly', False)]})

    add_other_oe_mon = fields.Boolean(string='Other', readonly=True,
                                      states={'Start': [('readonly', False)]})
    add_other_oe_mon_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=True,
                                                     states={'Start': [('readonly', False)]})
    add_other_oe_mon_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                              states={'Start': [('readonly', False)]})
    add_other_oe_mon_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                               states={'Start': [('readonly', False)]})
    add_other_oe_mon_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                                     states={'Start': [('readonly', False)]})

    add_other_oe_mon_comment = fields.Char(string='Vaccine Lot No', readonly=True,
                                           states={'Start': [('readonly', False)]})
    add_other2_oe_mon = fields.Boolean(string='Other', readonly=True,
                                       states={'Start': [('readonly', False)]})
    add_other2_oe_mon_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=True,
                                                      states={'Start': [('readonly', False)]})
    add_other2_oe_mon_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                               states={'Start': [('readonly', False)]})
    add_other2_oe_mon_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                                states={'Start': [('readonly', False)]})
    add_other2_oe_mon_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                                      states={'Start': [('readonly', False)]})

    add_other2_oe_mon_comment = fields.Char(string='Vaccine Lot No', readonly=True,
                                            states={'Start': [('readonly', False)]})

    tf_mon_hepa = fields.Boolean(string='HepA (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})

    tf_mon_hepa_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                         states={'Start': [('readonly', False)]})
    tf_mon_hepa_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                          states={'Start': [('readonly', False)]})
    tf_mon_hepa_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                                states={'Start': [('readonly', False)]})

    add_other_tf_mon = fields.Boolean(string='Other', readonly=True,
                                      states={'Start': [('readonly', False)]})
    add_other_tf_mon_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=True,
                                                     states={'Start': [('readonly', False)]})
    add_other_tf_mon_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                              states={'Start': [('readonly', False)]})
    add_other_tf_mon_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                               states={'Start': [('readonly', False)]})
    add_other_tf_mon_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                                     states={'Start': [('readonly', False)]})

    add_other_tf_mon_comment = fields.Char(string='Vaccine Lot No', readonly=True,
                                           states={'Start': [('readonly', False)]})
    add_other2_tf_mon = fields.Boolean(string='Other', readonly=True,
                                       states={'Start': [('readonly', False)]})
    add_other2_tf_mon_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=True,
                                                      states={'Start': [('readonly', False)]})
    add_other2_tf_mon_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                               states={'Start': [('readonly', False)]})
    add_other2_tf_mon_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                                states={'Start': [('readonly', False)]})
    add_other2_tf_mon_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                                      states={'Start': [('readonly', False)]})

    add_other2_tf_mon_comment = fields.Char(string='Vaccine Lot No', readonly=True,
                                            states={'Start': [('readonly', False)]})

    fs_yea_dtap = fields.Boolean(string='D Tap (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    fs_yea_dtap_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                         states={'Start': [('readonly', False)]})
    fs_yea_dtap_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                          states={'Start': [('readonly', False)]})
    fs_yea_dtap_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                                states={'Start': [('readonly', False)]})

    fs_yea_opv = fields.Boolean(string='OPV (2 gtts)', readonly=True, states={'Start': [('readonly', False)]})
    fs_yea_opv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                        states={'Start': [('readonly', False)]})
    fs_yea_opv_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                         states={'Start': [('readonly', False)]})
    fs_yea_opv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                               states={'Start': [('readonly', False)]})

    fs_yea_varicella = fields.Boolean(string='Varicella (0.5 ml)', readonly=True,
                                      states={'Start': [('readonly', False)]})
    fs_yea_varicella_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                              states={'Start': [('readonly', False)]})
    fs_yea_varicella_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                               states={'Start': [('readonly', False)]})
    fs_yea_varicella_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                                     states={'Start': [('readonly', False)]})

    fs_yea_mmr = fields.Boolean(string='MMR (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    fs_yea_mmr_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                        states={'Start': [('readonly', False)]})
    fs_yea_mmr_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                         states={'Start': [('readonly', False)]})
    fs_yea_mmr_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                               states={'Start': [('readonly', False)]})

    add_other_fs_yea = fields.Boolean(string='Other', readonly=True,
                                      states={'Start': [('readonly', False)]})
    add_other_fs_yea_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=True,
                                                     states={'Start': [('readonly', False)]})
    add_other_fs_yea_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                              states={'Start': [('readonly', False)]})
    add_other_fs_yea_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                               states={'Start': [('readonly', False)]})
    add_other_fs_yea_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                                     states={'Start': [('readonly', False)]})

    add_other_fs_yea_comment = fields.Char(string='Vaccine Lot No', readonly=True,
                                           states={'Start': [('readonly', False)]})
    add_other2_fs_yea = fields.Boolean(string='Other', readonly=True,
                                       states={'Start': [('readonly', False)]})
    add_other2_fs_yea_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=True,
                                                      states={'Start': [('readonly', False)]})
    add_other2_fs_yea_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                               states={'Start': [('readonly', False)]})
    add_other2_fs_yea_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                                states={'Start': [('readonly', False)]})
    add_other2_fs_yea_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                                      states={'Start': [('readonly', False)]})

    add_other2_fs_yea_comment = fields.Char(string='Vaccine Lot No', readonly=True,
                                            states={'Start': [('readonly', False)]})

    oo_yea_dtap = fields.Boolean(string='Tdap (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    oo_yea_dtap_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                         states={'Start': [('readonly', False)]})
    oo_yea_dtap_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                          states={'Start': [('readonly', False)]})
    oo_yea_dtap_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                                states={'Start': [('readonly', False)]})

    # oo_yea_dtap_administered_right = fields.Boolean(string='Right', readonly=True,
    #                                                 states={'Start': [('readonly', False)]})
    # oo_yea_dtap_administered_left = fields.Boolean(string='Left', readonly=True,
    #                                                states={'Start': [('readonly', False)]})

    oo_yea_vpv = fields.Boolean(string='HPV (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    oo_yea_vpv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                        states={'Start': [('readonly', False)]})
    oo_yea_vpv_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                         states={'Start': [('readonly', False)]})
    oo_yea_vpv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                               states={'Start': [('readonly', False)]})

    add_other_oo_yea = fields.Boolean(string='Other', readonly=True,
                                      states={'Start': [('readonly', False)]})
    add_other_oo_yea_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=True,
                                                     states={'Start': [('readonly', False)]})
    add_other_oo_yea_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                              states={'Start': [('readonly', False)]})
    add_other_oo_yea_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                               states={'Start': [('readonly', False)]})
    add_other_oo_yea_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                                     states={'Start': [('readonly', False)]})

    add_other_oo_yea_comment = fields.Char(string='Vaccine Lot No', readonly=True,
                                           states={'Start': [('readonly', False)]})
    add_other2_oo_yea = fields.Boolean(string='Other', readonly=True,
                                       states={'Start': [('readonly', False)]})
    add_other2_oo_yea_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=True,
                                                      states={'Start': [('readonly', False)]})
    add_other2_oo_yea_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                               states={'Start': [('readonly', False)]})
    add_other2_oo_yea_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                                states={'Start': [('readonly', False)]})
    add_other2_oo_yea_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                                      states={'Start': [('readonly', False)]})
    add_other2_oo_yea_comment = fields.Char(string='Vaccine Lot No', readonly=True,
                                            states={'Start': [('readonly', False)]})

    ot_yea_hpv = fields.Boolean(string='HPV (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    ot_yea_hpv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                        states={'Start': [('readonly', False)]})
    ot_yea_hpv_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                         states={'Start': [('readonly', False)]})
    ot_yea_hpv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                               states={'Start': [('readonly', False)]})

    add_other_ot_yea = fields.Boolean(string='Other', readonly=True,
                                      states={'Start': [('readonly', False)]})
    add_other_ot_yea_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=True,
                                                     states={'Start': [('readonly', False)]})
    add_other_ot_yea_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                              states={'Start': [('readonly', False)]})
    add_other_ot_yea_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                               states={'Start': [('readonly', False)]})
    add_other_ot_yea_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                                     states={'Start': [('readonly', False)]})

    add_other_ot_yea_comment = fields.Char(string='Vaccine Lot No', readonly=True,
                                           states={'Start': [('readonly', False)]})
    add_other2_ot_yea = fields.Boolean(string='Other', readonly=True,
                                       states={'Start': [('readonly', False)]})
    add_other2_ot_yea_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=True,
                                                      states={'Start': [('readonly', False)]})
    add_other2_ot_yea_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                               states={'Start': [('readonly', False)]})
    add_other2_ot_yea_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                                states={'Start': [('readonly', False)]})
    add_other2_ot_yea_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                                      states={'Start': [('readonly', False)]})

    add_other2_ot_yea_comment = fields.Char(string='Vaccine Lot No', readonly=True,
                                            states={'Start': [('readonly', False)]})

    oe_yea_mcv = fields.Boolean(string='MCV4 (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    oe_yea_mcv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                        states={'Start': [('readonly', False)]})
    oe_yea_mcv_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                         states={'Start': [('readonly', False)]})
    oe_yea_mcv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                               states={'Start': [('readonly', False)]})

    add_other_oe_yea = fields.Boolean(string='Other', readonly=True,
                                      states={'Start': [('readonly', False)]})
    add_other_oe_yea_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=True,
                                                     states={'Start': [('readonly', False)]})
    add_other_oe_yea_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                              states={'Start': [('readonly', False)]})
    add_other_oe_yea_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                               states={'Start': [('readonly', False)]})
    add_other_oe_yea_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                                     states={'Start': [('readonly', False)]})

    add_other_oe_yea_comment = fields.Char(string='Vaccine Lot No', readonly=True,
                                           states={'Start': [('readonly', False)]})
    add_other2_oe_yea = fields.Boolean(string='Other', readonly=True,
                                       states={'Start': [('readonly', False)]})
    add_other2_oe_yea_vaccinations = fields.Selection(VACCINATION, string='Vaccination', readonly=True,
                                                      states={'Start': [('readonly', False)]})
    add_other2_oe_yea_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                               states={'Start': [('readonly', False)]})
    add_other2_oe_yea_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                                states={'Start': [('readonly', False)]})
    add_other2_oe_yea_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                                      states={'Start': [('readonly', False)]})

    add_other2_oe_yea_comment = fields.Char(string='Vaccine Lot No', readonly=True,
                                            states={'Start': [('readonly', False)]})

    oth_influenza = fields.Boolean(string='Influenza (0.25 ml)', readonly=True, states={'Start': [('readonly', False)]})
    oth_influenza_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                           states={'Start': [('readonly', False)]})
    oth_influenza_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                            states={'Start': [('readonly', False)]})
    oth_influenza_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                                  states={'Start': [('readonly', False)]})

    oth_tdap = fields.Boolean(string='Tdap (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    oth_tdap_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                      states={'Start': [('readonly', False)]})
    oth_tdap_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                       states={'Start': [('readonly', False)]})
    oth_tdap_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                             states={'Start': [('readonly', False)]})

    oth_mmr = fields.Boolean(string='MMR (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    oth_mmr_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                     states={'Start': [('readonly', False)]})
    oth_mmr_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                      states={'Start': [('readonly', False)]})
    oth_mmr_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                            states={'Start': [('readonly', False)]})

    oth_varicella = fields.Boolean(string='Varicella (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    oth_varicella_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                           states={'Start': [('readonly', False)]})
    oth_varicella_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                            states={'Start': [('readonly', False)]})
    oth_varicella_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                                  states={'Start': [('readonly', False)]})

    oth_herpes = fields.Boolean(string='Herpes Zoster (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    oth_herpes_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                        states={'Start': [('readonly', False)]})
    oth_herpes_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                         states={'Start': [('readonly', False)]})
    oth_herpes_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                               states={'Start': [('readonly', False)]})

    oth_hpv = fields.Boolean(string='HPV (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    oth_hpv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                     states={'Start': [('readonly', False)]})
    oth_hpv_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                      states={'Start': [('readonly', False)]})
    oth_hpv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                            states={'Start': [('readonly', False)]})

    oth_ppsv = fields.Boolean(string='PPSV23 (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    oth_ppsv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                      states={'Start': [('readonly', False)]})
    oth_ppsv_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                       states={'Start': [('readonly', False)]})
    oth_ppsv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                             states={'Start': [('readonly', False)]})

    oth_pcv = fields.Boolean(string='PCV (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    oth_pcv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                     states={'Start': [('readonly', False)]})
    oth_pcv_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                      states={'Start': [('readonly', False)]})
    oth_pcv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                            states={'Start': [('readonly', False)]})

    oth_hepb = fields.Boolean(string='Hep B (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    oth_hepb_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                      states={'Start': [('readonly', False)]})
    oth_hepb_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                       states={'Start': [('readonly', False)]})
    oth_hepb_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                             states={'Start': [('readonly', False)]})

    oth_mcv = fields.Boolean(string='MCV4 (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    oth_mcv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                     states={'Start': [('readonly', False)]})
    oth_mcv_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                      states={'Start': [('readonly', False)]})
    oth_mcv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                            states={'Start': [('readonly', False)]})

    oth_other = fields.Boolean(string='Other', readonly=True,
                               states={'Start': [('readonly', False)]})
    oth_vaccinations = fields.Char(string='Vaccination', readonly=True, states={'Start': [('readonly', False)]})
    oth_vaccinations_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                              states={'Start': [('readonly', False)]})
    oth_vaccinations_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                               states={'Start': [('readonly', False)]})
    oth_vaccinations_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                                     states={'Start': [('readonly', False)]})

    oth_rv = fields.Boolean(string='RV (1 ml)', readonly=True, states={'Start': [('readonly', False)]})
    oth_rv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                    states={'Start': [('readonly', False)]})
    oth_rv_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                     states={'Start': [('readonly', False)]})
    oth_rv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                           states={'Start': [('readonly', False)]})

    oth_dtap = fields.Boolean(string='D TaP (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    oth_dtap_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                      states={'Start': [('readonly', False)]})
    oth_dtap_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                       states={'Start': [('readonly', False)]})
    oth_dtap_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                             states={'Start': [('readonly', False)]})

    oth_hib = fields.Boolean(string='Hib (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    oth_hib_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                     states={'Start': [('readonly', False)]})
    oth_hib_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                      states={'Start': [('readonly', False)]})
    oth_hib_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                            states={'Start': [('readonly', False)]})

    oth_ipv = fields.Boolean(string='IPV (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    oth_ipv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                     states={'Start': [('readonly', False)]})
    oth_ipv_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                      states={'Start': [('readonly', False)]})
    oth_ipv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                            states={'Start': [('readonly', False)]})

    oth_bcg = fields.Boolean(string='BCG (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    oth_bcg_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                     states={'Start': [('readonly', False)]})
    oth_bcg_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                      states={'Start': [('readonly', False)]})
    oth_bcg_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                            states={'Start': [('readonly', False)]})

    oth_opv = fields.Boolean(string='OPV (2 gtts)', readonly=True, states={'Start': [('readonly', False)]})
    oth_opv_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                     states={'Start': [('readonly', False)]})
    oth_opv_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                      states={'Start': [('readonly', False)]})
    oth_opv_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                            states={'Start': [('readonly', False)]})

    oth_measels = fields.Boolean(string='Measels (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})
    oth_measels_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                         states={'Start': [('readonly', False)]})
    oth_measels_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                          states={'Start': [('readonly', False)]})
    oth_measels_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                                states={'Start': [('readonly', False)]})

    oth_hepa = fields.Boolean(string='HepA (0.5 ml)', readonly=True, states={'Start': [('readonly', False)]})

    oth_hepa_vaccine_no = fields.Char(string='Vaccine Lot No', readonly=True,
                                      states={'Start': [('readonly', False)]})
    oth_hepa_expiry_date = fields.Date(string='Expiry Date', readonly=True,
                                       states={'Start': [('readonly', False)]})
    oth_hepa_administered = fields.Selection(ADMINISTERED_OVER, string='Administered Over', readonly=True,
                                             states={'Start': [('readonly', False)]})

    mother_caregiver_show = fields.Boolean()
    mother_soreness_redness_swelling = fields.Selection(YES_NO, readonly=True, states={'Start': [('readonly', False)]})
    mother_muscular_pain = fields.Selection(YES_NO, readonly=True, states={'Start': [('readonly', False)]})
    mother_headaches = fields.Selection(YES_NO, readonly=True, states={'Start': [('readonly', False)]})
    mother_fever = fields.Selection(YES_NO, readonly=True, states={'Start': [('readonly', False)]})
    mother_nausea = fields.Selection(YES_NO, readonly=True, states={'Start': [('readonly', False)]})

    mother_difficulty_breathing = fields.Selection(YES_NO, readonly=True, states={'Start': [('readonly', False)]})
    mother_coughing = fields.Selection(YES_NO, readonly=True, states={'Start': [('readonly', False)]})
    mother_hoarse_vice_wheezing = fields.Selection(YES_NO, readonly=True, states={'Start': [('readonly', False)]})
    mother_hives = fields.Selection(YES_NO, readonly=True, states={'Start': [('readonly', False)]})
    mother_paleness = fields.Selection(YES_NO, readonly=True, states={'Start': [('readonly', False)]})
    mother_losing_consciousness = fields.Selection(YES_NO, readonly=True, states={'Start': [('readonly', False)]})
    add_other = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    add_other_text = fields.Text(readonly=True, states={'Start': [('readonly', False)]})

    # follow up
    na = fields.Many2one('sm.shifa.physician.admission', string='NA#', readonly=True,
                         states={'Draft': [('readonly', False)]},
                         domain="[('patient', '=', patient), ('state', 'in', ('Admitted', 'Start','Draft'))]")
    na_id = fields.Many2one('sm.shifa.nurse.assessment', string='NA#',
                            domain="[('patient', '=', patient), ('visit_type', '=', 'main_visit'), ('state', '=', 'Admitted')]")
    na_followup_ids = fields.One2many("sm.shifa.nurse.assessment", 'na_id')
    the_following_early_show = fields.Boolean()
    deterioration = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    systolic = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    heart_rate = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    respiratory_rate = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    difficulty_breathing = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    multiple_convulsion = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    chest_pain = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    progress_noted_show = fields.Boolean()
    care_rendered_show = fields.Boolean()
    progress_noted = fields.Text(readonly=True, states={'Start': [('readonly', False)]})
    care_rendered = fields.Text(readonly=True, states={'Start': [('readonly', False)]})

    notification_id = fields.One2many('sm.physician.notification', 'nurse_assessment_id',
                                      string='comprehensive notification')

    discharge_plan_show = fields.Boolean()
    discharge_plan = fields.Selection(DISCHARGE_PLAN, readonly=False, states={'Start': [('readonly', False)]})
    discharge_plan_other = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    active = fields.Boolean(default=True)

    def action_archive(self):
        for rec in self:
            if rec.state not in ['Discharged', 'Done']:
                raise UserError(_("You can archive only if it discharged assessments or done"))
        return super().action_archive()

    @api.onchange('Wound_show', 'Continence_show', 'Enteral_Feeding_show', 'Drain_Tube_show', 'Stoma_show',
                  'Palliative_show',
                  'Anticoagulation_show', 'Diabetic_show', 'Parenteral_show', 'Nebulization_show', 'Newborn_show',
                  'Oxygen_Administration_show'
        , 'Pressure_Ulcer_show', 'Postnatal_show', 'Trache_show', 'Vaccines_show', 'care_rendered')
    def get_rendered_form(self):
        care = ""
        self.care_rendered = care
        form_list = {
            'wound': self.Wound_show,
            'continence': self.Continence_show,
            'Enteral Feeding': self.Enteral_Feeding_show,
            'Drain Tube': self.Drain_Tube_show,
            'Stoma': self.Stoma_show,
            'Palliative': self.Palliative_show,
            'Anticoagulation': self.Anticoagulation_show,
            'Diabetic': self.Diabetic_show,
            'Parenteral': self.Parenteral_show,
            'Nebulization': self.Nebulization_show,
            'Newborn': self.Newborn_show,
            'Oxygen Administration': self.Oxygen_Administration_show,
            'Pressure Ulcer': self.Pressure_Ulcer_show,
            'Postnatal': self.Postnatal_show,
            'Trache': self.Trache_show,
            'Vaccines': self.Vaccines_show,
        }
        care_list = {
            'wound': "Wound Care Clinical Pathway",
            'continence': "Continence Care  Clinical Pathway",
            'Enteral Feeding': "Enteral Feeding Clinical Pathway",
            'Drain Tube': "Breast Surgery/Drain Tube Care Clinical Pathway",
            'Stoma': "Stoma Care Clinical Pathway",
            'Palliative': "Symptoms Management Clinical Pathway",
            'Anticoagulation': "Anticoagulation Management Clinical pathway",
            'Diabetic': "Diabetic Care Clinical Pathway",
            'Parenteral': "Parenteral Drug/Fluid Care Clinical Pathway",
            'Nebulization': "Nebulization Care Clinical Pathway",
            'Newborn': "Post Natal Care Baby Clinical Pathway",
            'Oxygen Administration': "Oxygen Administration Clinical Pathway",
            'Pressure Ulcer': "Pressure Injury Prevention Clinical Pathway",
            'Postnatal': "Post Natal Care Mother Clinical Pathway",
            'Trache': "Tracheostomy Care Clinical Pathway",
            'Vaccines': "Vaccines Care Clinical Pathway",
        }
        for x, y in form_list.items():
            if y:
                for c, v in care_list.items():
                    if x == c:
                        #print("inner loop " + care)
                        care += v + " , "
        self.care_rendered = care

    space = fields.Char(string="     ", readonly=True)

    @api.model
    def check_and_discharge_patients(self):
        current_date = datetime.datetime.now()
        discharge_date = current_date - datetime.timedelta(days=60)

        # _logger.info(f"Current datetime: {current_date}")
        # _logger.info(f"Discharge datetime: {discharge_date}")

        assessments = self.search([
            ('state', '=', 'Admitted'),
            ('admission_date', '>', discharge_date)
        ])

        # _logger.info(f"Records to be discharged: {assessments}")

        # for record in assessments:
        #     _logger.info(f"Discharging record: {record.id} with admission_date: {record.admission_date}")
        #
        if assessments:
            assessments.write({'state': 'Discharged', 'discharge_date': discharge_date})

        # _logger.info(f"Records after discharge: {self.search([('state', '=', 'Discharged')])}")


class NurseAssessmentNotificationInherit(models.Model):
    _inherit = 'sm.physician.notification'

    nurse_assessment_id = fields.Many2one('sm.shifa.nurse.assessment',
                                          string='comprehensive nurse follow up',
                                          ondelete='cascade')


class NurseAssessmentReferralInherit(models.Model):
    _inherit = 'sm.shifa.referral'

    nurse_ass_ref_id = fields.Many2one('sm.shifa.nurse.assessment', string='nurse assessment',
                                       ondelete='cascade')


class NurseAssessmentWoundInherit(models.Model):
    _inherit = 'sm.shifa.wound.assessment.values'

    wound_ass_id = fields.Many2one('sm.shifa.nurse.assessment', string='Wound Assessment')


class NurseAssessmentComprehensiveFollowUp(models.Model):
    _inherit = 'sm.shifa.comprehensive.nurse.follow.up'

    comprehensive_nurse_ass_id = fields.Many2one('sm.shifa.nurse.assessment', string='Nurse Assessment')


class NurseAssessmentMedicationProfile(models.Model):
    _inherit = "sm.shifa.nurse.assessment"

    @api.onchange('patient')
    def onchange_patient_med_pro(self):
        self.med_pro_id = [(5, 0, 0)]
        if self.patient.med_pro_id:
            lines = self.patient.med_pro_id.filtered(lambda l: l.state_app == 'active')
            if lines:
                self.med_pro_id = [(6, 0, lines.ids)]

    med_pro_id = fields.One2many('sm.shifa.medication.profile', related='patient.med_pro_id',
                                 string='Medication Profile')


class NursePatientFamilyHealthEducation(models.Model):
    _inherit = "sm.shifa.nurse.assessment"

    # education needs assessment
    personal_hygiene = fields.Boolean(string="Personal Hygiene", readonly=True,
                                      states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})
    pain_management = fields.Boolean(string="Pain Management", readonly=True,
                                     states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})
    activity_exercise = fields.Boolean(string="Activity/Exercise", readonly=True,
                                       states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})
    disease_process = fields.Boolean(string="Disease Process", readonly=True,
                                     states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})
    use_medical_equipment = fields.Boolean(string="Use of Medical Equipment", readonly=True,
                                           states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})
    nutrition = fields.Boolean(string="Nutrition", readonly=True,
                               states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})
    wound_care = fields.Boolean(string="Wound care and Dressing", readonly=True,
                                states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})
    diagnostic = fields.Boolean(string="Diagnostic Test/Procedure", readonly=True,
                                states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})
    medication = fields.Boolean(string="Medication", readonly=True,
                                states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})
    post_op = fields.Boolean(string="Post Op Care", readonly=True,
                             states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})
    social_service = fields.Boolean(string="Social Service", readonly=True,
                                    states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})
    home_safety = fields.Boolean(string="Home Safety", readonly=True,
                                 states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})
    informed_consent = fields.Boolean(string="Informed Consent", readonly=True,
                                      states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})
    rights_responsibilities = fields.Boolean(string="Rights & Responsibilities", readonly=True,
                                             states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})
    infection_control = fields.Boolean(string="Infection Control", readonly=True,
                                       states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})
    discharge_transfer = fields.Boolean(string="Discharge/Transfer Instruction", readonly=True,
                                        states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})
    emergency_responds = fields.Boolean(
        string="Emergeny responds for life threatening situations and when to call 997/911", readonly=True,
        states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})
    physiotherapy_exercise = fields.Boolean(string="Physiotherapy Exercise", readonly=True,
                                            states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})
    eduction_other = fields.Boolean(string="other", readonly=True,
                                    states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})
    eduction_other_text = fields.Char(string="other", readonly=True,
                                      states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})

    #     Learning Barriers
    no_learn_barriers = fields.Boolean(readonly=True,
                                       states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})
    impaired_hearing = fields.Boolean(readonly=True,
                                      states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})
    speech_barrier = fields.Boolean(readonly=True,
                                    states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})
    emotional_barrier = fields.Boolean(readonly=True,
                                       states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})
    language_barrier = fields.Boolean(readonly=True,
                                      states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})
    educational_barrier = fields.Boolean(readonly=True,
                                         states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})
    motivation_learn = fields.Boolean(readonly=True,
                                      states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})
    impaired_thought = fields.Boolean(readonly=True,
                                      states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})
    financial_difficulties = fields.Boolean(readonly=True,
                                            states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})
    impaired_vision = fields.Boolean(readonly=True,
                                     states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})
    cultural_beliefs = fields.Boolean(readonly=True,
                                      states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})
    religious_practice = fields.Boolean(readonly=True,
                                        states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})
    learning_other = fields.Boolean(readonly=True,
                                    states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})
    learning_other_text = fields.Char(readonly=True,
                                      states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})

    #     person Taught
    taught_patient = fields.Boolean(readonly=True,
                                    states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})
    son = fields.Boolean(readonly=True, states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})
    daughter = fields.Boolean(readonly=True, states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})
    relatives = fields.Boolean(readonly=True, states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})
    caregiver = fields.Boolean(readonly=True, states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})
    father = fields.Boolean(readonly=True, states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})
    private_nurse = fields.Boolean(readonly=True,
                                   states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})
    mother = fields.Boolean(readonly=True, states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})
    wife = fields.Boolean(readonly=True, states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})
    taught_other = fields.Boolean(readonly=True,
                                  states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})
    taught_other_text = fields.Char(readonly=True,
                                    states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})

    #  Teaching Tools
    audio = fields.Boolean(readonly=True, states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})
    return_demo = fields.Boolean(readonly=True, states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})
    demo = fields.Boolean(readonly=True, states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})
    video = fields.Boolean(readonly=True, states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})
    printed_materials = fields.Boolean(readonly=True,
                                       states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})
    verbal = fields.Boolean(readonly=True, states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})
    role_play = fields.Boolean(readonly=True, states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})
    tool_other = fields.Boolean(readonly=True, states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})
    tool_other_text = fields.Char(readonly=True,
                                  states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})

    #  Responds to teaching
    not_receptive = fields.Boolean(readonly=True,
                                   states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})
    verbalize_understanding = fields.Boolean(readonly=True,
                                             states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})
    demo_ability = fields.Boolean(readonly=True,
                                  states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})
    needs_followup = fields.Boolean(readonly=True,
                                    states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})
    teaching_other = fields.Boolean(readonly=True,
                                    states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})
    teaching_other_text = fields.Char(readonly=True,
                                      states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})


class NursePatientCondition(models.Model):
    _inherit = "sm.shifa.nurse.assessment"

    # morse fall risk
    YES_NO = [
        ('no', 'No'),
        ('yes', 'Yes')
    ]
    MENTAL = [
        ('oriented_own', 'Oriented to own ability'),
        ('overestimates_forgets', 'Overestimates or forgets limitations')
    ]
    AMBULATORY_AID = [
        ('none', 'None'),
        ('bed_rest', 'Bed rest'),
        ('nurse_assists', 'Nurse/Caregiver assist'),
        ('crutches', 'Crutches'),
        ('cane', 'Cane'),
        ('walker', 'Walker'),
        ('furniture', 'Furniture')
    ]
    GAIT = [
        ('normal', 'Normal'),
        ('bed_rest', 'Bed rest'),
        ('wheelchair', 'Wheelchair'),
        ('weak', 'Weak'),
        ('impaired', 'Impaired')
    ]
    SENSORY_PERCEPTION = [
        ('complete_limited', 'Completely limited/ unresponsive to painful or voice'),
        ('very_limited', ' Very limited - Responds only to painful stimuli by moaning and restlessness'),
        ('slightly_limited',
         'Slightly limited - Responds to verbal commands but cannot always communicate discomfort or need to be turned '),
        ('no_impairment', 'No impairment - Responds to verbal commands, can feel, voice pain or discomfort'),
    ]
    # injury_moisture
    BRADEN_MOISTURE = [
        ('skin_constantly_moist', 'Skin constantly moist by perspiration, urine, etc'),
        ('skin_often_moist', 'Skin is often moist and needs to change lines once a day'),
        ('skin_occasionally_moist', 'Skin occasionally moist - requiring an extra linen change once a day'),
        ('rarely_moist', 'Rarely moist - skin is usually dry'),
    ]

    # activity
    ACTIVITY = [
        ('bedfast', 'Bedfast - Confined to bed'),
        ('chairfast', 'Chairfast/Wheelchair'),
        ('walks_occasionally', 'Walks Occasionally'),
        ('walks_frequently', 'Walks Frequently'),
    ]

    # mobility
    MOBILITY = [
        ('completely_immobile', 'Completely Immobile'),
        ('very_limited', 'Very Limited'),
        ('slightly_limited', 'Slightly Limited'),
        ('no_limitations', 'No Limitations'),
    ]
    # nutrition
    NUTRITION = [
        ('very_poor', 'Very Poor or Npo'),
        ('probably_inadequate', 'Probably Inadequate'),
        ('adequate', 'Adequate'),
        ('excellent', 'Excellent'),
    ]
    # friction_shear
    FRICTION_SHEAR = [
        ('problem', 'Problem/full lifting using bedsheet'),
        ('potential_problem', 'Potential Problem Occasionally slides down.'),
        ('no_problem', 'No apparent Problem - moves in bed and in chair independently')
    ]

    @api.depends('history_falling_allegedly', 'ambulatory_aid', 'two_more_diagnosis', 'iv_picc_access', 'gait',
                 'risk_mental_status', 'multiple_medications')
    def _compute_score(self):
        # history, ambulatory, diagnosis, iv, gait_score, medication, mental, morse_fall_scale = 0
        for r in self:
            # check history
            if r.history_falling_allegedly == 'yes':
                history = 25
            else:
                history = 0
            #  check diagnosis
            if r.two_more_diagnosis == 'yes':
                diagnosis = 15
            else:
                diagnosis = 0
            # check ambulatory
            if r.ambulatory_aid == 'furniture':
                ambulatory = 30
            elif r.ambulatory_aid in ['crutches', 'cane', 'walker']:
                ambulatory = 15
            else:
                ambulatory = 0
            if r.iv_picc_access == 'yes':
                iv = 20
            else:
                iv = 0

            if r.gait == 'impaired':
                gait_score = 20
            elif r.gait == 'weak':
                gait_score = 10
            else:
                gait_score = 0
            if r.risk_mental_status == 'overestimates_forgets':
                mental = 15
            else:
                mental = 0
            if r.multiple_medications == 'yes':
                medication = 15
            else:
                medication = 0
            r.morse_fall_scale = history + diagnosis + ambulatory + iv + gait_score + mental + medication

    @api.depends('morse_fall_scale')
    def _compute_risk_level(self):
        for r in self:
            if 0 <= r.morse_fall_scale <= 24:
                r.morse_risk_level = "Low Risk"
            elif 25 <= r.morse_fall_scale <= 44:
                r.morse_risk_level = "Medium Risk"
            elif r.morse_fall_scale >= 45:
                r.morse_risk_level = "High Risk"
            else:
                r.morse_risk_level = " "
            return r.morse_risk_level

    @api.depends('braden_sensory_perception', 'braden_moisture', 'braden_activity', 'braden_mobility',
                 'braden_nutrition',
                 'braden_friction_shear')
    def _compute_braden_score(self):
        for r in self:
            if r.braden_sensory_perception == 'complete_limited':
                sensory = 1
            elif r.braden_sensory_perception == 'very_limited':
                sensory = 2
            elif r.braden_sensory_perception == 'slightly_limited':
                sensory = 3
            elif r.braden_sensory_perception == 'no_impairment':
                sensory = 4
            else:
                sensory = 0

            if r.braden_moisture == 'skin_constantly_moist':
                moisture = 1
            elif r.braden_moisture == 'skin_often_moist':
                moisture = 2
            elif r.braden_moisture == 'skin_occasionally_moist':
                moisture = 3
            elif r.braden_moisture == 'rarely_moist':
                moisture = 4
            else:
                moisture = 0

            if r.braden_activity == 'bedfast':
                activity = 1
            elif r.braden_activity == 'chairfast':
                activity = 2
            elif r.braden_activity == 'walks_occasionally':
                activity = 3
            elif r.braden_activity == 'walks_frequently':
                activity = 4
            else:
                activity = 0

            if r.braden_mobility == 'completely_immobile':
                mobility = 1
            elif r.braden_mobility == 'very_limited':
                mobility = 2
            elif r.braden_mobility == 'slightly_limited':
                mobility = 3
            elif r.braden_mobility == 'no_limitations':
                mobility = 4
            else:
                mobility = 0

            if r.braden_nutrition == 'very_poor':
                nutrition = 1
            elif r.braden_nutrition == 'probably_inadequate':
                nutrition = 2
            elif r.braden_nutrition == 'adequate':
                nutrition = 3
            elif r.braden_nutrition == 'excellent':
                nutrition = 4
            else:
                nutrition = 0

            if r.braden_friction_shear == 'problem':
                friction_shear = 1
            elif r.braden_friction_shear == 'potential_problem':
                friction_shear = 2
            elif r.braden_friction_shear == 'no_problem':
                friction_shear = 3
            else:
                friction_shear = 0
            r.braden_scale = sensory + moisture + mobility + activity + nutrition + friction_shear
            return r.braden_scale

    @api.depends('braden_scale')
    def _compute_branden_risk_level(self):
        for r in self:
            if 0 <= r.braden_scale <= 9:
                r.braden_risk_level = "Severe"
            elif 10 <= r.braden_scale <= 12:
                r.braden_risk_level = "High"
            elif 13 <= r.braden_scale <= 14:
                r.braden_risk_level = "Moderate"
            elif r.braden_scale >= 15:
                r.braden_risk_level = "Mild"
            else:
                r.braden_risk_level = " "
            return r.braden_risk_level

    #  patient conditions
    patient_condition = fields.Boolean(readonly=True,
                                       states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})
    car_accident = fields.Boolean(readonly=True,
                                  states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})
    sport_injuries = fields.Boolean(readonly=True,
                                    states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})
    broken_bones = fields.Boolean(readonly=True,
                                  states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})
    burns = fields.Boolean(readonly=True, states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})
    uncontrolled_bleeding = fields.Boolean(readonly=True,
                                           states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})
    heart_attacks = fields.Boolean(readonly=True,
                                   states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})
    patient_difficulty_breathing = fields.Boolean(readonly=True, states={'Draft': [('readonly', False)],
                                                                         'Start': [('readonly', False)]})
    strokes = fields.Boolean(readonly=True, states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})
    less_vision_hearing = fields.Boolean(readonly=True,
                                         states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})
    unconsciousness = fields.Boolean(readonly=True,
                                     states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})
    confusion = fields.Boolean(readonly=True, states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})
    suicidal = fields.Boolean(readonly=True, states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})
    overdoses = fields.Boolean(readonly=True, states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})
    severe_abdominal = fields.Boolean(readonly=True,
                                      states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})
    food_poisoning = fields.Boolean(readonly=True,
                                    states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})
    blood_vomiting = fields.Boolean(readonly=True,
                                    states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})
    severe_allergic = fields.Boolean(readonly=True,
                                     states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})
    complications = fields.Boolean(readonly=True,
                                   states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})

    morse_fall_risk = fields.Boolean()
    history_falling_allegedly = fields.Selection(YES_NO, string="History of falling or Allegedly Fall within 3 months",
                                                 readonly=True, states={'Draft': [('readonly', False)],
                                                                        'Start': [('readonly', False)]})
    two_more_diagnosis = fields.Selection(YES_NO, string="Two or more diagnosis", readonly=True,
                                          states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})
    ambulatory_aid = fields.Selection(AMBULATORY_AID, string="Ambulation Aid", readonly=True,
                                      states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})
    iv_picc_access = fields.Selection(YES_NO, string="IV, PICC line Access", readonly=True,
                                      states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})
    gait = fields.Selection(GAIT, string="Gait", readonly=True,
                            states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})
    risk_mental_status = fields.Selection(MENTAL, string="Mental status", readonly=True,
                                          states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})
    multiple_medications = fields.Selection(YES_NO, readonly=True,
                                            states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]},
                                            string="Taking multiple Medications for Hypertension, Narcotic/Pain Relief, Sleeping and dizziness")
    morse_fall_scale = fields.Float(compute=_compute_score, string='Morse Fall Scale Score: Total', store=True)
    morse_risk_level = fields.Char(compute=_compute_risk_level, string='Morse risk level', store=True)
    other_condition = fields.Boolean(readonly=True,
                                     states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})
    other_condition_text = fields.Char(readonly=True,
                                       states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})

    # Braden Scale Pressure Injury Score Risk
    braden_fall_risk = fields.Boolean()
    braden_sensory_perception = fields.Selection(SENSORY_PERCEPTION, string="Sensory Perception", readonly=True,
                                                 states={'Draft': [('readonly', False)],
                                                         'Start': [('readonly', False)]})
    braden_moisture = fields.Selection(BRADEN_MOISTURE, string="Moisture", readonly=True,
                                       states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})
    braden_activity = fields.Selection(ACTIVITY, string="Activity", readonly=True,
                                       states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})
    braden_mobility = fields.Selection(MOBILITY, string="Mobility", readonly=True,
                                       states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})
    braden_nutrition = fields.Selection(NUTRITION, string="Nutrition", readonly=True,
                                        states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})
    braden_friction_shear = fields.Selection(FRICTION_SHEAR, string="Friction and Shear", readonly=True,
                                             states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})
    braden_scale = fields.Float(compute=_compute_braden_score, string='Braden Scale Score: Total', store=True)
    braden_risk_level = fields.Char(compute=_compute_branden_risk_level, string='Braden Risk Level', store=True)
