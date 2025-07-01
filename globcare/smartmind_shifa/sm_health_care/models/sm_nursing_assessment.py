from odoo import models, fields, api
import datetime
from odoo.exceptions import ValidationError


class ShifaNursingAssessment(models.Model):
    _name = 'sm.shifa.nursing.assessment'
    _description = "Nursing Assessment"
    _rec_name = "nursing_assessment_code"

    STATES = [
        ('Draft', 'Draft'),
        ('Start', 'Start'),
        ('Done', 'Done'),
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
    MUSCLE_POWER= [
        ('Right ', 'Right'),
        ('Left', 'Left'),
        ('Both', 'Both'),
        ('Normal', 'Normal'),
        ('Mild Weakness', 'Mild Weakness'),
        ('Moderate Weakness', 'Moderate Weakness'),
        ('Severe Weakness', 'Severe Weakness'),
    ]
    state = fields.Selection(STATES, string='State', default=lambda *a: 'Draft', readonly=True,
                             states={'Draft': [('readonly', False)]})
    nurse = fields.Many2one('oeh.medical.physician', string='Nurse',  required=True, readonly=True, domain=[('role_type', '=', ['HP', 'HHCP']), ('active', '=', True)],
                              states={'Draft': [('readonly', False)]})
    phy_adm = fields.Many2one('sm.shifa.physician.admission', string='Phy_Adm #', domain="[('patient', '=', patient)]", readonly=True,
                              states={'Draft': [('readonly', False)]})
    hvd_appointment = fields.Many2one('sm.shifa.hvd.appointment', string='HVD Appointment', readonly=True,
                                      states={'Draft': [('readonly', False)]})
    hhc_appointment = fields.Many2one('sm.shifa.hhc.appointment', string='HHC-Appointment',
                                      readonly=True, states={'Draft': [('readonly', False)]})
    nursing_assessment_code = fields.Char('Reference', index=True, copy=False)
    patient = fields.Many2one('oeh.medical.patient', string='Patient', help="Patient Name", required=True,
                              readonly=True,
                              states={'Draft': [('readonly', False)]})
    dob = fields.Date(string='Date of Birth', related='patient.dob')
    marital_status = fields.Selection(string='Marital Status', related='patient.marital_status')
    sex = fields.Selection(string='Sex', related='patient.sex')
    blood_type = fields.Selection(string='Blood Type', related='patient.blood_type')
    rh = fields.Selection(string='Rh', related='patient.rh')
    # ssn = fields.Char(size=256, string='National ID', related='patient.ssn')
    # phone = fields.Char(string='Phone', related='patient.phone')
    icu_admission_id = fields.Many2one('oeh.medical.icu.admission', string='Home Admission', index=True)
    start_date = fields.Datetime(string='Start Date', readonly='1')
    completed_date = fields.Datetime(string='Completed Date', readonly='1')
    diagnosis_show = fields.Boolean()
    diagnosis = fields.Text(string='Diagnosis', readonly=True,
                            states={'Start': [('readonly', False)]})
    chief_complaint_show = fields.Boolean()
    chief_complaint = fields.Char(string="Chief Complaint", readonly=True,
                                  states={'Start': [('readonly', False)]})
    # Vital Signs
    vital_signs_show = fields.Boolean()
    temperature = fields.Float(string="Temperature (celsius)", readonly=True,
                               states={'Start': [('readonly', False)]})
    systolic = fields.Integer(string="Systolic Pressure", readonly=True,
                              states={'Start': [('readonly', False)]})
    respiratory_rate = fields.Integer(string="Respiratory Rate", readonly=True,
                                      states={'Start': [('readonly', False)]})
    osat = fields.Integer(string="Oxygen Saturation", readonly=True,
                          states={'Start': [('readonly', False)]})
    diastolic = fields.Integer(string="Diastolic Pressure", readonly=True,
                               states={'Start': [('readonly', False)]})
    bpm = fields.Integer(string="Heart Rate", readonly=True,
                         states={'Start': [('readonly', False)]})
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

    @api.onchange('hhc_appointment')
    def _onchange_hhc_appointment(self):
        if self.hhc_appointment:
            self.patient = self.hhc_appointment.patient
            self.hvd_appointment = None

    @api.onchange('hvd_appointment')
    def _onchange_hvd_appointment(self):
        if self.hvd_appointment:
            self.patient = self.hvd_appointment.patient
            self.hhc_appointment = None
    @api.model
    def create(self, vals):
        vals['nursing_assessment_code'] = self.env['ir.sequence'].next_by_code('sm.shifa.nursing.assessment')
        return super(ShifaNursingAssessment, self).create(vals)

    def set_to_done(self):
        return self.write({'state': 'Done', 'completed_date': datetime.datetime.now()})

    def set_to_start(self):
        return self.write({'state': 'Start', 'start_date': datetime.datetime.now()})

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
