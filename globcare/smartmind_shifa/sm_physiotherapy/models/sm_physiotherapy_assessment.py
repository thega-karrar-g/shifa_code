from odoo import models, fields, api, _
import datetime
from odoo.exceptions import ValidationError, UserError


class ShifaPhysiotherapyAssessment(models.Model):
    _name = "sm.shifa.physiotherapy.assessment"
    _description = "Physiotherapy Assessment"
    _rec_name = 'physiotherapy_assessment_code'

    skin_tissues_state = [
        ('Minor', 'Minor'),
        ('Important', 'Important'),
    ]
    
    muscle_test = [
        ('0', '0'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
    ]
    muscle_tone = [
        ('0', '0'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
    ]
    sensitivity_state = [
        ('Right', 'Right'),
        ('Left', 'Left'),
    ]
    reflex_state = [
        ('+ Hyper', '+ Hyper'),
        ('- Hypo', '- Hypo'),
        ('normal', 'normal'),
    ]
    balance_disorders = [
        ('Normal', 'Normal'),
        ('Good', 'Good'),
        ('Poor', 'Poor'),
        ('Not possible', 'Not possible'),
    ]
    coordination_state = [
        ('Good', 'Good'),
        ('Poor', 'Poor'),
        ('Not possible', 'Not possible')
    ]
    activity_state = [
        ('Independent', 'Independent'),
        ('Assisted', 'Assisted'),
        ('Impossible', 'Impossible')
    ]
    functional_quality_state = [
        ('Normal', 'Normal'),
        ('Good', 'Good'),
        ('Poor', 'Poor'),
    ]
    ADMISSION_STATES = [
        ('Draft', 'Draft'),
        ('Start', 'Start'),
        ('Admitted', 'Admitted'),
        ('Discharged', 'Discharged'),
    ]

    def _get_physiotherapy(self):
        """Return default physiotherapy value"""
        therapist_obj = self.env['oeh.medical.physician']
        domain = [('oeh_user_id', '=', self.env.uid)]
        user_ids = therapist_obj.search(domain, limit=1)
        if user_ids:
            return user_ids.id or False
        else:
            return False

    def set_to_start(self):
        return self.write({'state': 'Start'})

    #     admitted date method
    def set_to_admitted(self):
        admission_date = False
        for ina in self:
            if ina.admission_date:
                admission_date = ina.admission_date
            else:
                admission_date = datetime.datetime.now()
        return self.write(
            {'state': 'Admitted', 'admission_date': admission_date, 'date_assessment_range_of_motion': admission_date,
             'date_assessment_muscle_test': admission_date, 'date_assessment_muscle_tone': admission_date})

    #     discharge date time method
    def set_to_discharged(self):
        discharged_date = False
        for ina in self:
            if ina.discharge_date:
                discharged_date = ina.discharge_date
            else:
                discharged_date = datetime.datetime.now()
        return self.write({'state': 'Discharged', 'discharge_date': discharged_date})

    @api.onchange('phys_appointment')
    def _onchange_hhc_appointment(self):
        if self.phys_appointment:
            self.patient = self.phys_appointment.patient

    @api.onchange('phy_adm')
    def _onchange_join_phy_adm(self):
        if self.phy_adm:
            self.physician_admission = self.phy_adm

    physiotherapy_assessment_code = fields.Char('Reference', index=True, copy=False)
    patient = fields.Many2one('oeh.medical.patient', string='Patient', help="Patient Name", required=True,
                              readonly=False, states={'Draft': [('readonly', False)]})

    # hhc_appointment = fields.Many2one('sm.shifa.hhc.appointment', string='HHC-Appointment',
    #                                   readonly=False, states={'Draft': [('readonly', False)]}, )
    phys_appointment = fields.Many2one('sm.shifa.physiotherapy.appointment', string='Physiotherapy appointment',
                                       readonly=False, states={'Draft': [('readonly', False)]})
    doctor = fields.Many2one('oeh.medical.physician', string='Physiotherapist',
                             readonly=False, states={'Draft': [('readonly', False)]},
                             domain=[('role_type', 'in', ['HHCP', 'HP']), ('active', '=', True)], required=True, default=_get_physiotherapy)
    state = fields.Selection(ADMISSION_STATES, string='State', default=lambda *a: 'Draft', readonly=False)
    dob = fields.Date(string='Date of Birth', related='patient.dob')
    weight = fields.Float(string='Weight', related='patient.weight')
    age = fields.Char(string='Age', related='patient.age')
    marital_status = fields.Selection(string='Marital Status', related='patient.marital_status')
    sex = fields.Selection(string='Sex', related='patient.sex')
    blood_type = fields.Selection(string='Blood Type', related='patient.blood_type')
    rh = fields.Selection(string='Rh', related='patient.rh')
    ssn = fields.Char(size=256, string='National ID', related='patient.ssn')
    phone = fields.Char(string='Mobile', related='patient.mobile')
    admission_date = fields.Datetime(string='Admission Date', readonly=False, states={'Admitted': [('readonly', False)]})
    discharge_date = fields.Datetime(string='Discharge Date')
    phy_adm = fields.Many2one('sm.shifa.physician.admission', string='Phy_Adm', readonly=False,
                              states={'Discharged': [('readonly', True)]},
                              domain="[('patient', '=', patient), ('state', 'in', ('Admitted', 'Start','Draft'))]")
    service_name = fields.Char(string='Service', related='service.abbreviation', readonly=False, store=False)

    service = fields.Many2one('sm.shifa.service', string='Service Name',
                              required=True,
                              domain="[('service_type', '=', 'PHY')]",
                              readonly=False, states={'Draft': [('readonly', False)]})

    chief_complaint_show = fields.Boolean()
    chief_complaint = fields.Text(readonly=False, states={'Start': [('readonly', False)]})
    diagnosis_show = fields.Boolean()
    diagnosis = fields.Text(readonly=False, states={'Start': [('readonly', False)]})

    # Vital Signs
    vital_signs_show = fields.Boolean()
    temperature = fields.Float(string="Temperature (c)", readonly=False, states={'Start': [('readonly', False)]})
    systolic = fields.Integer(string="Systolic BP(mmHg)", readonly=False, states={'Start': [('readonly', False)]})
    respiratory_rate = fields.Integer(string="RR (/min)", readonly=False,
                                      states={'Start': [('readonly', False)]})
    # osat = fields.Float(string="O2 Sat(%)", readonly=False, states={'Start': [('readonly', False)]})
    o2_sat = fields.Selection([
        ('at room air', 'at room air'),
        ('with oxygen Support', 'with oxygen Support')
    ], readonly=False, states={'Start': [('readonly', False)]})
    char_other_oxygen = fields.Float(readonly=False, states={'Start': [('readonly', False)]})
    diastolic = fields.Integer(string="Diastolic BR(mmHg)", readonly=False,
                               states={'Start': [('readonly', False)]})
    bpm = fields.Integer(string="HR (/min)", readonly=False, states={'Start': [('readonly', False)]})

    # Medical History / Treatment
    medical_history_show = fields.Boolean()
    medical_history_medication = fields.Many2one('oeh.medical.medicines', string='Medication', readonly=False,
                                                 states={'Start': [('readonly', False)]})
    medical_hospital = fields.Char(string='Hospital', readonly=False, states={'Start': [('readonly', False)]})
    medical_care = fields.Char(string='Care', readonly=False, states={'Start': [('readonly', False)]})
    medical_evaluation_since_beginning = fields.Selection([
        ('Improved', 'Improved'),
        ('Worse', 'Worse'),
    ], string='Evaluation Since Beginning', readonly=False, states={'Start': [('readonly', False)]})
    medical_remarks = fields.Char(string='Remarks', readonly=False, states={'Start': [('readonly', False)]})

    xray_other = fields.Boolean(string='X-ray/Other ex', readonly=False, states={'Start': [('readonly', False)]})
    xray_other_text = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    xray_other_bin = fields.Binary(readonly=False, states={'Start': [('readonly', False)]})
    xray_other_add_other = fields.Boolean(string='add other', readonly=False, states={'Start': [('readonly', False)]})
    xray_other_add_other_text = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    xray_other_add_bin = fields.Binary(readonly=False, states={'Start': [('readonly', False)]})

    main_patient_concerns = fields.Char(string="Main Patient's concerns", readonly=False,
                                        states={'Start': [('readonly', False)]})
    main_patient_expectations = fields.Char(string="Main Patient's expectations", readonly=False,
                                            states={'Start': [('readonly', False)]})
    medical_current_treatment = fields.Selection([
        ('1st', '1st'),
        ('2nd', '2nd'),
        ('3rd', '3rd'),
    ], string='Current Treatment', readonly=False, states={'Start': [('readonly', False)]})

    physiotherapy_remark = fields.Text(string='Remark', readonly=False, states={'Start': [('readonly', False)]})

    # Physical Examination
    physical_examination_image_show = fields.Boolean()
    physical_examination_image = fields.Binary(readonly=False, states={'Start': [('readonly', False)]})
    physical_examination_remark = fields.Text(string='Remark', readonly=False, states={'Start': [('readonly', False)]})

    skin_soft_tissues_problem_show = fields.Boolean()
    skin_tissues_problem_swelling = fields.Selection(skin_tissues_state, string='Swelling',
                                                     readonly=False, states={'Start': [('readonly', False)]})
    skin_tissues_problem_callus = fields.Selection(skin_tissues_state, string='Callus ',
                                                   readonly=False, states={'Start': [('readonly', False)]})
    skin_tissues_problem_scar = fields.Selection(skin_tissues_state, string='Scar',
                                                 readonly=False, states={'Start': [('readonly', False)]})
    skin_tissues_problem_wound = fields.Selection(skin_tissues_state, string='Wound',
                                                  readonly=False, states={'Start': [('readonly', False)]})
    skin_tissues_problem_temperature = fields.Selection(skin_tissues_state, string='Temperature',
                                                        readonly=False, states={'Start': [('readonly', False)]})
    skin_tissues_problem_infection = fields.Selection(skin_tissues_state, string='Infection',
                                                      readonly=False, states={'Start': [('readonly', False)]})
    skin_tissues_problem_pain = fields.Selection(skin_tissues_state, string='Pain',
                                                 readonly=False, states={'Start': [('readonly', False)]})
    skin_tissues_problem_abnormal_sensation = fields.Selection(skin_tissues_state, string='Abnormal Sensation',
                                                               readonly=False, states={'Start': [('readonly', False)]})

    sensation_show = fields.Boolean()
    sensitivity_superficial = fields.Selection(sensitivity_state, string='Superficial',
                                               readonly=False, states={'Start': [('readonly', False)]})
    sensitivity_superficial_specification = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    sensitivity_deep = fields.Selection(sensitivity_state, string='Deep',
                                        readonly=False, states={'Start': [('readonly', False)]})
    sensitivity_deep_specification = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    sensitivity_numbness = fields.Selection(sensitivity_state, string='Numbness',
                                            readonly=False, states={'Start': [('readonly', False)]})
    sensitivity_numbness_specification = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    sensitivity_paresthesia = fields.Selection(sensitivity_state, string='Paresthesia',
                                               readonly=False, states={'Start': [('readonly', False)]})
    sensitivity_paresthesia_specification = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    sensitivity_other = fields.Selection(sensitivity_state, string='Other',
                                         readonly=False, states={'Start': [('readonly', False)]})
    sensitivity_other_specification = fields.Char(readonly=False, states={'Start': [('readonly', False)]})

    reflexes_show = fields.Boolean()
    reflex_BTR = fields.Selection(reflex_state, string='BTR',
                                  readonly=False, states={'Start': [('readonly', False)]})
    reflex_BTR_comments = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    reflex_TTR = fields.Selection(reflex_state, string='TTR',
                                  readonly=False, states={'Start': [('readonly', False)]})
    reflex_TTR_comments = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    reflex_KTR = fields.Selection(reflex_state, string='KTR',
                                  readonly=False, states={'Start': [('readonly', False)]})
    reflex_KTR_comments = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    reflex_ATR = fields.Selection(reflex_state, string='ATR',
                                  readonly=False, states={'Start': [('readonly', False)]})
    reflex_ATR_comments = fields.Char(readonly=False, states={'Start': [('readonly', False)]})

    # Body chard of pain
    body_chard_of_pain_show = fields.Boolean()
    body_chard_image = fields.Binary(readonly=False, states={'Start': [('readonly', False)]})
    date_first_complains = fields.Date(string='Date of first complains',
                                       readonly=False, states={'Start': [('readonly', False)]})
    evolution_since_begin_pain = fields.Char(string='Evolution since the beginning of pain',
                                             readonly=False, states={'Start': [('readonly', False)]})
    evolution_in24h = fields.Selection([
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
    ], string='Evolution in 24h & scale', readonly=False, states={'Start': [('readonly', False)]})
    body_pain_increase = fields.Char(string='Pain increase with', readonly=False,
                                     states={'Start': [('readonly', False)]})
    body_pain_decrease = fields.Char(string='Pain decrease with', readonly=False,
                                     states={'Start': [('readonly', False)]})
    patient_category = fields.Selection([
        ('SIN', 'SIN'),
        ('ROM', 'ROM'),
        ('MOMP', 'MOMP'),
        ('EOR', 'EOR'),
    ], string="Patient's category", readonly=False, states={'Start': [('readonly', False)]})

    # motion

    date_assessment_range_of_motion = fields.Date(readonly=False, states={'Start': [('readonly', False)]})
    start_discharge_assessment = fields.Boolean()
    assessment_discharge_date = fields.Date()
    # date_follow_up_range_of_motion = fields.Date(readonly=False, states={'Start': [('readonly', False)]})
    lower_limb_hip_flexion_assessment_l = fields.Float(readonly=False, states={'Start': [('readonly', False)]})
    lower_limb_hip_flexion_assessment_n = fields.Float(readonly=False, states={'Start': [('readonly', False)]})
    lower_limb_hip_flexion_follow_l = fields.Float()
    lower_limb_hip_flexion_follow_n = fields.Float()
    lower_limb_hip_extension_assessment_l = fields.Float(readonly=False, states={'Start': [('readonly', False)]})
    lower_limb_hip_extension_assessment_n = fields.Float(readonly=False, states={'Start': [('readonly', False)]})
    lower_limb_hip_extension_follow_l = fields.Float()
    lower_limb_hip_extension_follow_n = fields.Float()
    lower_limb_hip_abduction_assessment_l = fields.Float(readonly=False, states={'Start': [('readonly', False)]})
    lower_limb_hip_abduction_assessment_n = fields.Float(readonly=False, states={'Start': [('readonly', False)]})
    lower_limb_hip_abduction_follow_l = fields.Float()
    lower_limb_hip_abduction_follow_n = fields.Float()
    lower_limb_hip_adduction_assessment_l = fields.Float(readonly=False, states={'Start': [('readonly', False)]})
    lower_limb_hip_adduction_assessment_n = fields.Float(readonly=False, states={'Start': [('readonly', False)]})
    lower_limb_hip_adduction_follow_l = fields.Float()
    lower_limb_hip_adduction_follow_n = fields.Float()
    lower_limb_hip_medial_rotation_assessment_l = fields.Float(readonly=False, states={'Start': [('readonly', False)]})
    lower_limb_hip_medial_rotation_assessment_n = fields.Float(readonly=False, states={'Start': [('readonly', False)]})
    lower_limb_hip_medial_rotation_follow_l = fields.Float()
    lower_limb_hip_medial_rotation_follow_n = fields.Float()
    lower_limb_hip_lateral_rotation_assessment_l = fields.Float(readonly=False, states={'Start': [('readonly', False)]})
    lower_limb_hip_lateral_rotation_assessment_n = fields.Float(readonly=False, states={'Start': [('readonly', False)]})
    lower_limb_hip_lateral_rotation_follow_l = fields.Float()
    lower_limb_hip_lateral_rotation_follow_n = fields.Float()

    lower_limb_knee_flexion_assessment_l = fields.Float(readonly=False, states={'Start': [('readonly', False)]})
    lower_limb_knee_flexion_assessment_n = fields.Float(readonly=False, states={'Start': [('readonly', False)]})
    lower_limb_knee_flexion_follow_l = fields.Float()
    lower_limb_knee_flexion_follow_n = fields.Float()
    lower_limb_knee_extension_assessment_l = fields.Float(readonly=False, states={'Start': [('readonly', False)]})
    lower_limb_knee_extension_assessment_n = fields.Float(readonly=False, states={'Start': [('readonly', False)]})
    lower_limb_knee_extension_follow_l = fields.Float()
    lower_limb_knee_extension_follow_n = fields.Float()

    lower_limb_ankle_foot_dorsi_flexion_assessment_l = fields.Float(readonly=False,
                                                                    states={'Start': [('readonly', False)]})
    lower_limb_ankle_foot_dorsi_flexion_assessment_n = fields.Float(readonly=False,
                                                                    states={'Start': [('readonly', False)]})
    lower_limb_ankle_foot_dorsi_flexion_follow_l = fields.Float()
    lower_limb_ankle_foot_dorsi_flexion_follow_n = fields.Float()
    lower_limb_ankle_foot_plantar_flexion_assessment_l = fields.Float(readonly=False,
                                                                      states={'Start': [('readonly', False)]})
    lower_limb_ankle_foot_plantar_flexion_assessment_n = fields.Float(readonly=False,
                                                                      states={'Start': [('readonly', False)]})
    lower_limb_ankle_foot_plantar_flexion_follow_l = fields.Float()
    lower_limb_ankle_foot_plantar_flexion_follow_n = fields.Float()
    lower_limb_ankle_foot_inversion_assessment_l = fields.Float(readonly=False, states={'Start': [('readonly', False)]})
    lower_limb_ankle_foot_inversion_assessment_n = fields.Float(readonly=False, states={'Start': [('readonly', False)]})
    lower_limb_ankle_foot_inversion_follow_l = fields.Float()
    lower_limb_ankle_foot_inversion_follow_n = fields.Float()
    lower_limb_ankle_foot_eversion_assessment_l = fields.Float(readonly=False, states={'Start': [('readonly', False)]})
    lower_limb_ankle_foot_eversion_assessment_n = fields.Float(readonly=False, states={'Start': [('readonly', False)]})
    lower_limb_ankle_foot_eversion_follow_l = fields.Float()
    lower_limb_ankle_foot_eversion_follow_n = fields.Float()

    lower_limb_neck_flexion_assessment_l = fields.Float(readonly=False, states={'Start': [('readonly', False)]})
    lower_limb_neck_flexion_assessment_n = fields.Float(readonly=False, states={'Start': [('readonly', False)]})
    lower_limb_neck_flexion_follow_l = fields.Float()
    lower_limb_neck_flexion_follow_n = fields.Float()
    lower_limb_neck_extension_assessment_l = fields.Float(readonly=False, states={'Start': [('readonly', False)]})
    lower_limb_neck_extension_assessment_n = fields.Float(readonly=False, states={'Start': [('readonly', False)]})
    lower_limb_neck_extension_follow_l = fields.Float()
    lower_limb_neck_extension_follow_n = fields.Float()
    lower_limb_neck_latero_flexion_r_assessment_l = fields.Float(readonly=False, states={'Start': [('readonly', False)]})
    lower_limb_neck_latero_flexion_r_assessment_n = fields.Float(readonly=False, states={'Start': [('readonly', False)]})
    lower_limb_neck_latero_flexion_r_follow_l = fields.Float()
    lower_limb_neck_latero_flexion_r_follow_n = fields.Float()
    lower_limb_neck_latero_flexion_l_assessment_l = fields.Float(readonly=False, states={'Start': [('readonly', False)]})
    lower_limb_neck_latero_flexion_l_assessment_n = fields.Float(readonly=False, states={'Start': [('readonly', False)]})
    lower_limb_neck_latero_flexion_l_follow_l = fields.Float()
    lower_limb_neck_latero_flexion_l_follow_n = fields.Float()
    lower_limb_neck_rotation_r_assessment_l = fields.Float(readonly=False, states={'Start': [('readonly', False)]})
    lower_limb_neck_rotation_r_assessment_n = fields.Float(readonly=False, states={'Start': [('readonly', False)]})
    lower_limb_neck_rotation_r_follow_l = fields.Float()
    lower_limb_neck_rotation_r_follow_n = fields.Float()
    lower_limb_neck_rotation_l_assessment_l = fields.Float(readonly=False, states={'Start': [('readonly', False)]})
    lower_limb_neck_rotation_l_assessment_n = fields.Float(readonly=False, states={'Start': [('readonly', False)]})
    lower_limb_neck_rotation_l_follow_l = fields.Float()
    lower_limb_neck_rotation_l_follow_n = fields.Float()

    lower_limb_trunk_global_flexion_assessment_l = fields.Float(readonly=False, states={'Start': [('readonly', False)]})
    lower_limb_trunk_global_flexion_assessment_n = fields.Float(readonly=False, states={'Start': [('readonly', False)]})
    lower_limb_trunk_global_flexion_follow_l = fields.Float()
    lower_limb_trunk_global_flexion_follow_n = fields.Float()
    lower_limb_trunk_thoracic_flexion_assessment_l = fields.Float(readonly=False,
                                                                  states={'Start': [('readonly', False)]})
    lower_limb_trunk_thoracic_flexion_assessment_n = fields.Float(readonly=False,
                                                                  states={'Start': [('readonly', False)]})
    lower_limb_trunk_thoracic_flexion_follow_l = fields.Float()
    lower_limb_trunk_thoracic_flexion_follow_n = fields.Float()
    lower_limb_trunk_lumbar_flexion_assessment_l = fields.Float(readonly=False, states={'Start': [('readonly', False)]})
    lower_limb_trunk_lumbar_flexion_assessment_n = fields.Float(readonly=False, states={'Start': [('readonly', False)]})
    lower_limb_trunk_lumbar_flexion_follow_l = fields.Float()
    lower_limb_trunk_lumbar_flexion_follow_n = fields.Float()
    lower_limb_trunk_global_extension_assessment_l = fields.Float(readonly=False,
                                                                  states={'Start': [('readonly', False)]})
    lower_limb_trunk_global_extension_assessment_n = fields.Float(readonly=False,
                                                                  states={'Start': [('readonly', False)]})
    lower_limb_trunk_global_extension_follow_l = fields.Float()
    lower_limb_trunk_global_extension_follow_n = fields.Float()
    lower_limb_trunk_latero_flexion_r_assessment_l = fields.Float(readonly=False,
                                                                  states={'Start': [('readonly', False)]})
    lower_limb_trunk_latero_flexion_r_assessment_n = fields.Float(readonly=False,
                                                                  states={'Start': [('readonly', False)]})
    lower_limb_trunk_latero_flexion_r_follow_l = fields.Float()
    lower_limb_trunk_latero_flexion_r_follow_n = fields.Float()
    lower_limb_trunk_latero_flexion_l_assessment_l = fields.Float(readonly=False,
                                                                  states={'Start': [('readonly', False)]})
    lower_limb_trunk_latero_flexion_l_assessment_n = fields.Float(readonly=False,
                                                                  states={'Start': [('readonly', False)]})
    lower_limb_trunk_latero_flexion_l_follow_l = fields.Float()
    lower_limb_trunk_latero_flexion_l_follow_n = fields.Float()
    lower_limb_trunk_rotation_r_assessment_l = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    lower_limb_trunk_rotation_r_assessment_n = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    lower_limb_trunk_rotation_r_follow_l = fields.Char()
    lower_limb_trunk_rotation_r_follow_n = fields.Char()
    lower_limb_trunk_rotation_l_assessment_l = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    lower_limb_trunk_rotation_l_assessment_n = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    lower_limb_trunk_rotation_l_follow_l = fields.Char()
    lower_limb_trunk_rotation_l_follow_n = fields.Char()

    lower_limb_remarks = fields.Text(readonly=False, states={'Start': [('readonly', False)]})

    upper_limb_shoulder_flexion_assessment_l = fields.Float(readonly=False, states={'Start': [('readonly', False)]})
    upper_limb_shoulder_flexion_assessment_n = fields.Float(readonly=False, states={'Start': [('readonly', False)]})
    upper_limb_shoulder_flexion_follow_l = fields.Float()
    upper_limb_shoulder_flexion_follow_n = fields.Float()
    upper_limb_shoulder_extension_assessment_l = fields.Float(readonly=False, states={'Start': [('readonly', False)]})
    upper_limb_shoulder_extension_assessment_n = fields.Float(readonly=False, states={'Start': [('readonly', False)]})
    upper_limb_shoulder_extension_follow_l = fields.Float()
    upper_limb_shoulder_extension_follow_n = fields.Float()
    upper_limb_shoulder_abduction_assessment_l = fields.Float(readonly=False, states={'Start': [('readonly', False)]})
    upper_limb_shoulder_abduction_assessment_n = fields.Float(readonly=False, states={'Start': [('readonly', False)]})
    upper_limb_shoulder_abduction_follow_l = fields.Float()
    upper_limb_shoulder_abduction_follow_n = fields.Float()
    upper_limb_shoulder_adduction_assessment_l = fields.Float(readonly=False, states={'Start': [('readonly', False)]})
    upper_limb_shoulder_adduction_assessment_n = fields.Float(readonly=False, states={'Start': [('readonly', False)]})
    upper_limb_shoulder_adduction_follow_l = fields.Float()
    upper_limb_shoulder_adduction_follow_n = fields.Float()
    upper_limb_shoulder_medial_rotation_assessment_l = fields.Float(readonly=False,
                                                                    states={'Start': [('readonly', False)]})
    upper_limb_shoulder_medial_rotation_assessment_n = fields.Float(readonly=False,
                                                                    states={'Start': [('readonly', False)]})
    upper_limb_shoulder_medial_rotation_follow_l = fields.Float()
    upper_limb_shoulder_medial_rotation_follow_n = fields.Float()
    upper_limb_shoulder_lateral_rotation_assessment_l = fields.Float(readonly=False,
                                                                     states={'Start': [('readonly', False)]})
    upper_limb_shoulder_lateral_rotation_assessment_n = fields.Float(readonly=False,
                                                                     states={'Start': [('readonly', False)]})
    upper_limb_shoulder_lateral_rotation_follow_l = fields.Float()
    upper_limb_shoulder_lateral_rotation_follow_n = fields.Float()

    upper_limb_elbow_flexion_assessment_l = fields.Float(readonly=False, states={'Start': [('readonly', False)]})
    upper_limb_elbow_flexion_assessment_n = fields.Float(readonly=False, states={'Start': [('readonly', False)]})
    upper_limb_elbow_flexion_follow_l = fields.Float()
    upper_limb_elbow_flexion_follow_n = fields.Float()
    upper_limb_elbow_extension_assessment_l = fields.Float(readonly=False, states={'Start': [('readonly', False)]})
    upper_limb_elbow_extension_assessment_n = fields.Float(readonly=False, states={'Start': [('readonly', False)]})
    upper_limb_elbow_extension_follow_l = fields.Float()
    upper_limb_elbow_extension_follow_n = fields.Float()

    upper_limb_forearm_pronation_assessment_l = fields.Float(readonly=False, states={'Start': [('readonly', False)]})
    upper_limb_forearm_pronation_assessment_n = fields.Float(readonly=False, states={'Start': [('readonly', False)]})
    upper_limb_forearm_pronation_follow_l = fields.Float()
    upper_limb_forearm_pronation_follow_n = fields.Float()
    upper_limb_forearm_supination_assessment_l = fields.Float(readonly=False, states={'Start': [('readonly', False)]})
    upper_limb_forearm_supination_assessment_n = fields.Float(readonly=False, states={'Start': [('readonly', False)]})
    upper_limb_forearm_supination_follow_l = fields.Float()
    upper_limb_forearm_supination_follow_n = fields.Float()

    upper_limb_wrist_flexion_assessment_l = fields.Float(readonly=False, states={'Start': [('readonly', False)]})
    upper_limb_wrist_flexion_assessment_n = fields.Float(readonly=False, states={'Start': [('readonly', False)]})
    upper_limb_wrist_flexion_follow_l = fields.Float()
    upper_limb_wrist_flexion_follow_n = fields.Float()
    upper_limb_wrist_extension_assessment_l = fields.Float(readonly=False, states={'Start': [('readonly', False)]})
    upper_limb_wrist_extension_assessment_n = fields.Float(readonly=False, states={'Start': [('readonly', False)]})
    upper_limb_wrist_extension_follow_l = fields.Float()
    upper_limb_wrist_extension_follow_n = fields.Float()
    upper_limb_wrist_abduction_assessment_l = fields.Float(readonly=False, states={'Start': [('readonly', False)]})
    upper_limb_wrist_abduction_assessment_n = fields.Float(readonly=False, states={'Start': [('readonly', False)]})
    upper_limb_wrist_abduction_follow_l = fields.Float()
    upper_limb_wrist_abduction_follow_n = fields.Float()
    upper_limb_wrist_adduction_assessment_l = fields.Float(readonly=False, states={'Start': [('readonly', False)]})
    upper_limb_wrist_adduction_assessment_n = fields.Float(readonly=False, states={'Start': [('readonly', False)]})
    upper_limb_wrist_adduction_follow_l = fields.Float()
    upper_limb_wrist_adduction_follow_n = fields.Float()

    upper_limb_fingers_thumb_opposition_assessment_l = fields.Float(readonly=False,
                                                                    states={'Start': [('readonly', False)]})
    upper_limb_fingers_thumb_opposition_assessment_n = fields.Float(readonly=False,
                                                                    states={'Start': [('readonly', False)]})
    upper_limb_fingers_thumb_opposition_follow_l = fields.Float()
    upper_limb_fingers_thumb_opposition_follow_n = fields.Float()
    upper_limb_fingers_mp_flexion_assessment_l = fields.Float(readonly=False, states={'Start': [('readonly', False)]})
    upper_limb_fingers_mp_flexion_assessment_n = fields.Float(readonly=False, states={'Start': [('readonly', False)]})
    upper_limb_fingers_mp_flexion_follow_l = fields.Float()
    upper_limb_fingers_mp_flexion_follow_n = fields.Float()
    upper_limb_fingers_mp_extension_assessment_l = fields.Float(readonly=False, states={'Start': [('readonly', False)]})
    upper_limb_fingers_mp_extension_assessment_n = fields.Float(readonly=False, states={'Start': [('readonly', False)]})
    upper_limb_fingers_mp_extension_follow_l = fields.Float()
    upper_limb_fingers_mp_extension_follow_n = fields.Float()
    upper_limb_fingers_ip_flexion_assessment_l = fields.Float(readonly=False, states={'Start': [('readonly', False)]})
    upper_limb_fingers_ip_flexion_assessment_n = fields.Float(readonly=False, states={'Start': [('readonly', False)]})
    upper_limb_fingers_ip_flexion_follow_l = fields.Float()
    upper_limb_fingers_ip_flexion_follow_n = fields.Float()

    upper_limb_remarks = fields.Text(readonly=False, states={'Start': [('readonly', False)]})

    # muscles test

    date_assessment_muscle_test = fields.Date(readonly=False, states={'Start': [('readonly', False)]})
    start_discharge_assessment_muscle = fields.Boolean()
    assessment_discharge_date_muscle = fields.Date()
    # date_follow_up_muscle_test = fields.Date(readonly=False, states={'Start': [('readonly', False)]})

    muscle_test_lower_hip_flex_assessment_left = fields.Selection(muscle_test, readonly=False,
                                                                  states={'Start': [('readonly', False)]})
    muscle_test_lower_hip_flex_assessment_right = fields.Selection(muscle_test, readonly=False,
                                                                   states={'Start': [('readonly', False)]})
    muscle_test_lower_hip_flex_followup_left = fields.Selection(muscle_test)
    muscle_test_lower_hip_flex_followup_right = fields.Selection(muscle_test)
    muscle_test_lower_hip_flex_comment = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    muscle_test_lower_hip_flex_comment_followup = fields.Char()
    muscle_test_lower_hip_extensors_assessment_left = fields.Selection(muscle_test, readonly=False,
                                                                       states={'Start': [('readonly', False)]})
    muscle_test_lower_hip_extensors_assessment_right = fields.Selection(muscle_test, readonly=False,
                                                                        states={'Start': [('readonly', False)]})
    muscle_test_lower_hip_extensors_followup_left = fields.Selection(muscle_test)
    muscle_test_lower_hip_extensors_followup_right = fields.Selection(muscle_test)
    muscle_test_lower_hip_extensors_comment = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    muscle_test_lower_hip_extensors_comment_followup = fields.Char()
    muscle_test_lower_hip_abductors_assessment_left = fields.Selection(muscle_test, readonly=False,
                                                                       states={'Start': [('readonly', False)]})
    muscle_test_lower_hip_abductors_assessment_right = fields.Selection(muscle_test, readonly=False,
                                                                        states={'Start': [('readonly', False)]})
    muscle_test_lower_hip_abductors_followup_left = fields.Selection(muscle_test)
    muscle_test_lower_hip_abductors_followup_right = fields.Selection(muscle_test)
    muscle_test_lower_hip_abductors_comment = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    muscle_test_lower_hip_abductors_comment_followup = fields.Char()
    muscle_test_lower_hip_adductors_assessment_left = fields.Selection(muscle_test, readonly=False,
                                                                       states={'Start': [('readonly', False)]})
    muscle_test_lower_hip_adductors_assessment_right = fields.Selection(muscle_test, readonly=False,
                                                                        states={'Start': [('readonly', False)]})
    muscle_test_lower_hip_adductors_followup_left = fields.Selection(muscle_test)
    muscle_test_lower_hip_adductors_followup_right = fields.Selection(muscle_test)
    muscle_test_lower_hip_adductors_comment = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    muscle_test_lower_hip_adductors_comment_followup = fields.Char()
    muscle_test_lower_hip_lateral_rot_assessment_left = fields.Selection(muscle_test, readonly=False,
                                                                         states={'Start': [('readonly', False)]})
    muscle_test_lower_hip_lateral_rot_assessment_right = fields.Selection(muscle_test, readonly=False,
                                                                          states={'Start': [('readonly', False)]})
    muscle_test_lower_hip_lateral_rot_followup_left = fields.Selection(muscle_test)
    muscle_test_lower_hip_lateral_rot_followup_right = fields.Selection(muscle_test)
    muscle_test_lower_hip_lateral_rot_comment = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    muscle_test_lower_hip_lateral_rot_comment_followup = fields.Char()
    muscle_test_lower_hip_medial_rot_assessment_left = fields.Selection(muscle_test, readonly=False,
                                                                        states={'Start': [('readonly', False)]})
    muscle_test_lower_hip_medial_rot_assessment_right = fields.Selection(muscle_test, readonly=False,
                                                                         states={'Start': [('readonly', False)]})
    muscle_test_lower_hip_medial_rot_followup_left = fields.Selection(muscle_test)
    muscle_test_lower_hip_medial_rot_followup_right = fields.Selection(muscle_test)
    muscle_test_lower_hip_medial_rot_comment = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    muscle_test_lower_hip_medial_rot_comment_followup = fields.Char()

    muscle_test_lower_knee_flexors_assessment_left = fields.Selection(muscle_test, readonly=False,
                                                                      states={'Start': [('readonly', False)]})
    muscle_test_lower_knee_flexors_assessment_right = fields.Selection(muscle_test, readonly=False,
                                                                       states={'Start': [('readonly', False)]})
    muscle_test_lower_knee_flexors_followup_left = fields.Selection(muscle_test)
    muscle_test_lower_knee_flexors_followup_right = fields.Selection(muscle_test)
    muscle_test_lower_knee_flexors_comment = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    muscle_test_lower_knee_flexors_comment_followup = fields.Char()
    muscle_test_lower_knee_extensors_assessment_left = fields.Selection(muscle_test, readonly=False,
                                                                        states={'Start': [('readonly', False)]})
    muscle_test_lower_knee_extensors_assessment_right = fields.Selection(muscle_test, readonly=False,
                                                                         states={'Start': [('readonly', False)]})
    muscle_test_lower_knee_extensors_followup_left = fields.Selection(muscle_test)
    muscle_test_lower_knee_extensors_followup_right = fields.Selection(muscle_test)
    muscle_test_lower_knee_extensors_comment = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    muscle_test_lower_knee_extensors_comment_followup = fields.Char()

    muscle_test_lower_ankle_dorsi_flex_assessment_left = fields.Selection(muscle_test, readonly=False,
                                                                          states={'Start': [('readonly', False)]})
    muscle_test_lower_ankle_dorsi_flex_assessment_right = fields.Selection(muscle_test, readonly=False,
                                                                           states={'Start': [('readonly', False)]})
    muscle_test_lower_ankle_dorsi_flex_followup_left = fields.Selection(muscle_test)
    muscle_test_lower_ankle_dorsi_flex_followup_right = fields.Selection(muscle_test)
    muscle_test_lower_ankle_dorsi_flex_comment = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    muscle_test_lower_ankle_dorsi_flex_comment_followup = fields.Char()
    muscle_test_lower_ankle_plantar_flex_assessment_left = fields.Selection(muscle_test, readonly=False,
                                                                            states={'Start': [('readonly', False)]})
    muscle_test_lower_ankle_plantar_flex_assessment_right = fields.Selection(muscle_test, readonly=False,
                                                                             states={'Start': [('readonly', False)]})
    muscle_test_lower_ankle_plantar_flex_followup_left = fields.Selection(muscle_test)
    muscle_test_lower_ankle_plantar_flex_followup_right = fields.Selection(muscle_test)
    muscle_test_lower_ankle_plantar_flex_comment = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    muscle_test_lower_ankle_plantar_flex_comment_followup = fields.Char()
    muscle_test_lower_ankle_inversors_assessment_left = fields.Selection(muscle_test, readonly=False,
                                                                         states={'Start': [('readonly', False)]})
    muscle_test_lower_ankle_inversors_assessment_right = fields.Selection(muscle_test, readonly=False,
                                                                          states={'Start': [('readonly', False)]})
    muscle_test_lower_ankle_inversors_followup_left = fields.Selection(muscle_test)
    muscle_test_lower_ankle_inversors_followup_right = fields.Selection(muscle_test)
    muscle_test_lower_ankle_inversors_comment = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    muscle_test_lower_ankle_inversors_comment_followup = fields.Char()
    muscle_test_lower_ankle_eversors_assessment_left = fields.Selection(muscle_test, readonly=False,
                                                                        states={'Start': [('readonly', False)]})
    muscle_test_lower_ankle_eversors_assessment_right = fields.Selection(muscle_test, readonly=False,
                                                                         states={'Start': [('readonly', False)]})
    muscle_test_lower_ankle_eversors_followup_left = fields.Selection(muscle_test)
    muscle_test_lower_ankle_eversors_followup_right = fields.Selection(muscle_test)
    muscle_test_lower_ankle_eversors_comment = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    muscle_test_lower_ankle_eversors_comment_followup = fields.Char()

    muscle_test_lower_foot_flexors_assessment_left = fields.Selection(muscle_test, readonly=False,
                                                                      states={'Start': [('readonly', False)]})
    muscle_test_lower_foot_flexors_assessment_right = fields.Selection(muscle_test, readonly=False,
                                                                       states={'Start': [('readonly', False)]})
    muscle_test_lower_foot_flexors_followup_left = fields.Selection(muscle_test)
    muscle_test_lower_foot_flexors_followup_right = fields.Selection(muscle_test)
    muscle_test_lower_foot_flexors_comment = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    muscle_test_lower_foot_flexors_comment_followup = fields.Char()
    muscle_test_lower_foot_extensors_assessment_left = fields.Selection(muscle_test, readonly=False,
                                                                        states={'Start': [('readonly', False)]})
    muscle_test_lower_foot_extensors_assessment_right = fields.Selection(muscle_test, readonly=False,
                                                                         states={'Start': [('readonly', False)]})
    muscle_test_lower_foot_extensors_followup_left = fields.Selection(muscle_test)
    muscle_test_lower_foot_extensors_followup_right = fields.Selection(muscle_test)
    muscle_test_lower_foot_extensors_comment = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    muscle_test_lower_foot_extensors_comment_followup = fields.Char()

    muscle_test_lower_trunk_flexors_assessment_left = fields.Selection(muscle_test, readonly=False,
                                                                       states={'Start': [('readonly', False)]})
    muscle_test_lower_trunk_flexors_assessment_right = fields.Selection(muscle_test, readonly=False,
                                                                        states={'Start': [('readonly', False)]})
    muscle_test_lower_trunk_flexors_followup_left = fields.Selection(muscle_test)
    muscle_test_lower_trunk_flexors_followup_right = fields.Selection(muscle_test)
    muscle_test_lower_trunk_flexors_comment = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    muscle_test_lower_trunk_flexors_comment_followup = fields.Char()
    muscle_test_lower_trunk_extensor_assessment_left = fields.Selection(muscle_test, readonly=False,
                                                                        states={'Start': [('readonly', False)]})
    muscle_test_lower_trunk_extensor_assessment_right = fields.Selection(muscle_test, readonly=False,
                                                                         states={'Start': [('readonly', False)]})
    muscle_test_lower_trunk_extensor_followup_left = fields.Selection(muscle_test)
    muscle_test_lower_trunk_extensor_followup_right = fields.Selection(muscle_test)
    muscle_test_lower_trunk_extensor_comment = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    muscle_test_lower_trunk_extensor_comment_followup = fields.Char()
    muscle_test_lower_trunk_r_bending_assessment_left = fields.Selection(muscle_test, readonly=False,
                                                                         states={'Start': [('readonly', False)]})
    muscle_test_lower_trunk_r_bending_assessment_right = fields.Selection(muscle_test, readonly=False,
                                                                          states={'Start': [('readonly', False)]})
    muscle_test_lower_trunk_r_bending_followup_left = fields.Selection(muscle_test)
    muscle_test_lower_trunk_r_bending_followup_right = fields.Selection(muscle_test)
    muscle_test_lower_trunk_r_bending_comment = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    muscle_test_lower_trunk_r_bending_comment_followup = fields.Char()
    muscle_test_lower_trunk_l_bending_assessment_left = fields.Selection(muscle_test, readonly=False,
                                                                         states={'Start': [('readonly', False)]})
    muscle_test_lower_trunk_l_bending_assessment_right = fields.Selection(muscle_test, readonly=False,
                                                                          states={'Start': [('readonly', False)]})
    muscle_test_lower_trunk_l_bending_followup_left = fields.Selection(muscle_test)
    muscle_test_lower_trunk_l_bending_followup_right = fields.Selection(muscle_test)
    muscle_test_lower_trunk_l_bending_comment = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    muscle_test_lower_trunk_l_bending_comment_followup = fields.Char()
    muscle_test_lower_trunk_r_rotation_assessment_left = fields.Selection(muscle_test, readonly=False,
                                                                          states={'Start': [('readonly', False)]})
    muscle_test_lower_trunk_r_rotation_assessment_right = fields.Selection(muscle_test, readonly=False,
                                                                           states={'Start': [('readonly', False)]})
    muscle_test_lower_trunk_r_rotation_followup_left = fields.Selection(muscle_test)
    muscle_test_lower_trunk_r_rotation_followup_right = fields.Selection(muscle_test)
    muscle_test_lower_trunk_r_rotation_comment = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    muscle_test_lower_trunk_r_rotation_comment_followup = fields.Char()
    muscle_test_lower_trunk_l_rotation_assessment_left = fields.Selection(muscle_test, readonly=False,
                                                                          states={'Start': [('readonly', False)]})
    muscle_test_lower_trunk_l_rotation_assessment_right = fields.Selection(muscle_test, readonly=False,
                                                                           states={'Start': [('readonly', False)]})
    muscle_test_lower_trunk_l_rotation_followup_left = fields.Selection(muscle_test)
    muscle_test_lower_trunk_l_rotation_followup_right = fields.Selection(muscle_test)
    muscle_test_lower_trunk_l_rotation_comment = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    muscle_test_lower_trunk_l_rotation_comment_followup = fields.Char()

    muscle_test_upper_shoulder_flex_assessment_left = fields.Selection(muscle_test, readonly=False,
                                                                       states={'Start': [('readonly', False)]})
    muscle_test_upper_shoulder_flex_assessment_right = fields.Selection(muscle_test, readonly=False,
                                                                        states={'Start': [('readonly', False)]})
    muscle_test_upper_shoulder_flex_followup_left = fields.Selection(muscle_test)
    muscle_test_upper_shoulder_flex_followup_right = fields.Selection(muscle_test)
    muscle_test_upper_shoulder_flex_comment = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    muscle_test_upper_shoulder_flex_comment_followup = fields.Char()
    muscle_test_upper_shoulder_extensors_assessment_left = fields.Selection(muscle_test, readonly=False,
                                                                            states={'Start': [('readonly', False)]})
    muscle_test_upper_shoulder_extensors_assessment_right = fields.Selection(muscle_test, readonly=False,
                                                                             states={'Start': [('readonly', False)]})
    muscle_test_upper_shoulder_extensors_followup_left = fields.Selection(muscle_test)
    muscle_test_upper_shoulder_extensors_followup_right = fields.Selection(muscle_test)
    muscle_test_upper_shoulder_extensors_comment = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    muscle_test_upper_shoulder_extensors_comment_followup = fields.Char()
    muscle_test_upper_shoulder_abductors_assessment_left = fields.Selection(muscle_test, readonly=False,
                                                                            states={'Start': [('readonly', False)]})
    muscle_test_upper_shoulder_abductors_assessment_right = fields.Selection(muscle_test, readonly=False,
                                                                             states={'Start': [('readonly', False)]})
    muscle_test_upper_shoulder_abductors_followup_left = fields.Selection(muscle_test)
    muscle_test_upper_shoulder_abductors_followup_right = fields.Selection(muscle_test)
    muscle_test_upper_shoulder_abductors_comment = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    muscle_test_upper_shoulder_abductors_comment_followup = fields.Char()
    muscle_test_upper_shoulder_adductors_assessment_left = fields.Selection(muscle_test, readonly=False,
                                                                            states={'Start': [('readonly', False)]})
    muscle_test_upper_shoulder_adductors_assessment_right = fields.Selection(muscle_test, readonly=False,
                                                                             states={'Start': [('readonly', False)]})
    muscle_test_upper_shoulder_adductors_followup_left = fields.Selection(muscle_test)
    muscle_test_upper_shoulder_adductors_followup_right = fields.Selection(muscle_test)
    muscle_test_upper_shoulder_adductors_comment = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    muscle_test_upper_shoulder_adductors_comment_followup = fields.Char()
    muscle_test_upper_shoulder_lateral_rot_assessment_left = fields.Selection(muscle_test, readonly=False,
                                                                              states={'Start': [('readonly', False)]})
    muscle_test_upper_shoulder_lateral_rot_assessment_right = fields.Selection(muscle_test, readonly=False,
                                                                               states={'Start': [('readonly', False)]})
    muscle_test_upper_shoulder_lateral_rot_followup_left = fields.Selection(muscle_test)
    muscle_test_upper_shoulder_lateral_rot_followup_right = fields.Selection(muscle_test)
    muscle_test_upper_shoulder_lateral_rot_comment = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    muscle_test_upper_shoulder_lateral_rot_comment_followup = fields.Char()
    muscle_test_upper_shoulder_medial_rot_assessment_left = fields.Selection(muscle_test, readonly=False,
                                                                             states={'Start': [('readonly', False)]})
    muscle_test_upper_shoulder_medial_rot_assessment_right = fields.Selection(muscle_test, readonly=False,
                                                                              states={'Start': [('readonly', False)]})
    muscle_test_upper_shoulder_medial_rot_followup_left = fields.Selection(muscle_test)
    muscle_test_upper_shoulder_medial_rot_followup_right = fields.Selection(muscle_test)
    muscle_test_upper_shoulder_medial_rot_comment = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    muscle_test_upper_shoulder_medial_rot_comment_followup = fields.Char()
    muscle_test_upper_shoulder_elevators_assessment_left = fields.Selection(muscle_test, readonly=False,
                                                                            states={'Start': [('readonly', False)]})
    muscle_test_upper_shoulder_elevators_assessment_right = fields.Selection(muscle_test, readonly=False,
                                                                             states={'Start': [('readonly', False)]})
    muscle_test_upper_shoulder_elevators_followup_left = fields.Selection(muscle_test)
    muscle_test_upper_shoulder_elevators_followup_right = fields.Selection(muscle_test)
    muscle_test_upper_shoulder_elevators_comment = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    muscle_test_upper_shoulder_elevators_comment_followup = fields.Char()
    muscle_test_upper_shoulder_depressors_assessment_left = fields.Selection(muscle_test, readonly=False,
                                                                             states={'Start': [('readonly', False)]})
    muscle_test_upper_shoulder_depressors_assessment_right = fields.Selection(muscle_test, readonly=False,
                                                                              states={'Start': [('readonly', False)]})
    muscle_test_upper_shoulder_depressors_followup_left = fields.Selection(muscle_test)
    muscle_test_upper_shoulder_depressors_followup_right = fields.Selection(muscle_test)
    muscle_test_upper_shoulder_depressors_comment = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    muscle_test_upper_shoulder_depressors_comment_followup = fields.Char()
    muscle_test_upper_shoulder_antepulsors_assessment_left = fields.Selection(muscle_test, readonly=False,
                                                                              states={'Start': [('readonly', False)]})
    muscle_test_upper_shoulder_antepulsors_assessment_right = fields.Selection(muscle_test, readonly=False,
                                                                               states={'Start': [('readonly', False)]})
    muscle_test_upper_shoulder_antepulsors_followup_left = fields.Selection(muscle_test)
    muscle_test_upper_shoulder_antepulsors_followup_right = fields.Selection(muscle_test)
    muscle_test_upper_shoulder_antepulsors_comment = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    muscle_test_upper_shoulder_antepulsors_comment_followup = fields.Char()
    muscle_test_upper_shoulder_retropulsors_assessment_left = fields.Selection(muscle_test, readonly=False,
                                                                               states={'Start': [('readonly', False)]})
    muscle_test_upper_shoulder_retropulsors_assessment_right = fields.Selection(muscle_test, readonly=False,
                                                                                states={'Start': [('readonly', False)]})
    muscle_test_upper_shoulder_retropulsors_followup_left = fields.Selection(muscle_test)
    muscle_test_upper_shoulder_retropulsors_followup_right = fields.Selection(muscle_test)
    muscle_test_upper_shoulder_retropulsors_comment = fields.Char(readonly=False,
                                                                  states={'Start': [('readonly', False)]})
    muscle_test_upper_shoulder_retropulsors_comment_followup = fields.Char()

    muscle_test_upper_elbow_flexors_assessment_left = fields.Selection(muscle_test, readonly=False,
                                                                       states={'Start': [('readonly', False)]})
    muscle_test_upper_elbow_flexors_assessment_right = fields.Selection(muscle_test, readonly=False,
                                                                        states={'Start': [('readonly', False)]})
    muscle_test_upper_elbow_flexors_followup_left = fields.Selection(muscle_test)
    muscle_test_upper_elbow_flexors_followup_right = fields.Selection(muscle_test)
    muscle_test_upper_elbow_flexors_comment = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    muscle_test_upper_elbow_flexors_comment_followup = fields.Char()
    muscle_test_upper_elbow_extensors_assessment_left = fields.Selection(muscle_test, readonly=False,
                                                                         states={'Start': [('readonly', False)]})
    muscle_test_upper_elbow_extensors_assessment_right = fields.Selection(muscle_test, readonly=False,
                                                                          states={'Start': [('readonly', False)]})
    muscle_test_upper_elbow_extensors_followup_left = fields.Selection(muscle_test)
    muscle_test_upper_elbow_extensors_followup_right = fields.Selection(muscle_test)
    muscle_test_upper_elbow_extensors_comment = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    muscle_test_upper_elbow_extensors_comment_followup = fields.Char()

    muscle_test_upper_forearm_supinators_assessment_left = fields.Selection(muscle_test, readonly=False,
                                                                            states={'Start': [('readonly', False)]})
    muscle_test_upper_forearm_supinators_assessment_right = fields.Selection(muscle_test, readonly=False,
                                                                             states={'Start': [('readonly', False)]})
    muscle_test_upper_forearm_supinators_followup_left = fields.Selection(muscle_test)
    muscle_test_upper_forearm_supinators_followup_right = fields.Selection(muscle_test)
    muscle_test_upper_forearm_supinators_comment = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    muscle_test_upper_forearm_supinators_comment_followup = fields.Char()
    muscle_test_upper_forearm_pronators_assessment_left = fields.Selection(muscle_test, readonly=False,
                                                                           states={'Start': [('readonly', False)]})
    muscle_test_upper_forearm_pronators_assessment_right = fields.Selection(muscle_test, readonly=False,
                                                                            states={'Start': [('readonly', False)]})
    muscle_test_upper_forearm_pronators_followup_left = fields.Selection(muscle_test)
    muscle_test_upper_forearm_pronators_followup_right = fields.Selection(muscle_test)
    muscle_test_upper_forearm_pronators_comment = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    muscle_test_upper_forearm_pronators_comment_followup = fields.Char()

    muscle_test_upper_wrist_flexors_assessment_left = fields.Selection(muscle_test, readonly=False,
                                                                       states={'Start': [('readonly', False)]})
    muscle_test_upper_wrist_flexors_assessment_right = fields.Selection(muscle_test, readonly=False,
                                                                        states={'Start': [('readonly', False)]})
    muscle_test_upper_wrist_flexors_followup_left = fields.Selection(muscle_test)
    muscle_test_upper_wrist_flexors_followup_right = fields.Selection(muscle_test)
    muscle_test_upper_wrist_flexors_comment = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    muscle_test_upper_wrist_flexors_comment_followup = fields.Char()
    muscle_test_upper_wrist_extensors_assessment_left = fields.Selection(muscle_test, readonly=False,
                                                                         states={'Start': [('readonly', False)]})
    muscle_test_upper_wrist_extensors_assessment_right = fields.Selection(muscle_test, readonly=False,
                                                                          states={'Start': [('readonly', False)]})
    muscle_test_upper_wrist_extensors_followup_left = fields.Selection(muscle_test)
    muscle_test_upper_wrist_extensors_followup_right = fields.Selection(muscle_test)
    muscle_test_upper_wrist_extensors_comment = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    muscle_test_upper_wrist_extensors_comment_followup = fields.Char()

    muscle_test_upper_fingers_flexors_assessment_left = fields.Selection(muscle_test, readonly=False,
                                                                         states={'Start': [('readonly', False)]})
    muscle_test_upper_fingers_flexors_assessment_right = fields.Selection(muscle_test, readonly=False,
                                                                          states={'Start': [('readonly', False)]})
    muscle_test_upper_fingers_flexors_followup_left = fields.Selection(muscle_test)
    muscle_test_upper_fingers_flexors_followup_right = fields.Selection(muscle_test)
    muscle_test_upper_fingers_flexors_comment = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    muscle_test_upper_fingers_flexors_comment_followup = fields.Char()
    muscle_test_upper_fingers_extensors_assessment_left = fields.Selection(muscle_test, readonly=False,
                                                                           states={'Start': [('readonly', False)]})
    muscle_test_upper_fingers_extensors_assessment_right = fields.Selection(muscle_test, readonly=False,
                                                                            states={'Start': [('readonly', False)]})
    muscle_test_upper_fingers_extensors_followup_left = fields.Selection(muscle_test)
    muscle_test_upper_fingers_extensors_followup_right = fields.Selection(muscle_test)
    muscle_test_upper_fingers_extensors_comment = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    muscle_test_upper_fingers_extensors_comment_followup = fields.Char()
    muscle_test_upper_fingers_abductors_assessment_left = fields.Selection(muscle_test, readonly=False,
                                                                           states={'Start': [('readonly', False)]})
    muscle_test_upper_fingers_abductors_assessment_right = fields.Selection(muscle_test, readonly=False,
                                                                            states={'Start': [('readonly', False)]})
    muscle_test_upper_fingers_abductors_followup_left = fields.Selection(muscle_test)
    muscle_test_upper_fingers_abductors_followup_right = fields.Selection(muscle_test)
    muscle_test_upper_fingers_abductors_comment = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    muscle_test_upper_fingers_abductors_comment_followup = fields.Char()
    muscle_test_upper_fingers_opposition_assessment_left = fields.Selection(muscle_test, readonly=False,
                                                                            states={'Start': [('readonly', False)]})
    muscle_test_upper_fingers_opposition_assessment_right = fields.Selection(muscle_test, readonly=False,
                                                                             states={'Start': [('readonly', False)]})
    muscle_test_upper_fingers_opposition_followup_left = fields.Selection(muscle_test)
    muscle_test_upper_fingers_opposition_followup_right = fields.Selection(muscle_test)
    muscle_test_upper_fingers_opposition_comment = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    muscle_test_upper_fingers_opposition_comment_followup = fields.Char()

    # muscle tone
    date_assessment_muscle_tone = fields.Date(readonly=False, states={'Start': [('readonly', False)]})
    start_discharge_assessment_muscle_tone = fields.Boolean()
    assessment_discharge_date_muscle_tone = fields.Date()
    # date_follow_up_muscle_tone = fields.Date(readonly=False, states={'Start': [('readonly', False)]})
    # lower limb
    muscle_tone_lower_hip_flex_assessment_left = fields.Selection(muscle_tone, readonly=False,
                                                                  states={'Start': [('readonly', False)]})
    muscle_tone_lower_hip_flex_assessment_right = fields.Selection(muscle_tone, readonly=False,
                                                                   states={'Start': [('readonly', False)]})
    muscle_tone_lower_hip_flex_followup_left = fields.Selection(muscle_tone)
    muscle_tone_lower_hip_flex_followup_right = fields.Selection(muscle_tone)
    muscle_tone_lower_hip_flex_comment = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    muscle_tone_lower_hip_flex_comment_followup = fields.Char()

    muscle_tone_lower_hip_extensors_assessment_left = fields.Selection(muscle_tone, readonly=False,
                                                                       states={'Start': [('readonly', False)]})
    muscle_tone_lower_hip_extensors_assessment_right = fields.Selection(muscle_tone, readonly=False,
                                                                        states={'Start': [('readonly', False)]})
    muscle_tone_lower_hip_extensors_followup_left = fields.Selection(muscle_tone)
    muscle_tone_lower_hip_extensors_followup_right = fields.Selection(muscle_tone)
    muscle_tone_lower_hip_extensors_comment = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    muscle_tone_lower_hip_extensors_comment_followup = fields.Char()

    muscle_tone_lower_hip_abductors_assessment_left = fields.Selection(muscle_tone, readonly=False,
                                                                       states={'Start': [('readonly', False)]})
    muscle_tone_lower_hip_abductors_assessment_right = fields.Selection(muscle_tone, readonly=False,
                                                                        states={'Start': [('readonly', False)]})
    muscle_tone_lower_hip_abductors_followup_left = fields.Selection(muscle_tone)
    muscle_tone_lower_hip_abductors_followup_right = fields.Selection(muscle_tone)
    muscle_tone_lower_hip_abductors_comment = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    muscle_tone_lower_hip_abductors_comment_followup = fields.Char()

    muscle_tone_lower_hip_adductors_assessment_left = fields.Selection(muscle_tone, readonly=False,
                                                                       states={'Start': [('readonly', False)]})
    muscle_tone_lower_hip_adductors_assessment_right = fields.Selection(muscle_tone, readonly=False,
                                                                        states={'Start': [('readonly', False)]})
    muscle_tone_lower_hip_adductors_followup_left = fields.Selection(muscle_tone)
    muscle_tone_lower_hip_adductors_followup_right = fields.Selection(muscle_tone)
    muscle_tone_lower_hip_adductors_comment = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    muscle_tone_lower_hip_adductors_comment_followup = fields.Char()

    muscle_tone_lower_hip_lateral_rot_assessment_left = fields.Selection(muscle_tone, readonly=False,
                                                                         states={'Start': [('readonly', False)]})
    muscle_tone_lower_hip_lateral_rot_assessment_right = fields.Selection(muscle_tone, readonly=False,
                                                                          states={'Start': [('readonly', False)]})
    muscle_tone_lower_hip_lateral_rot_followup_left = fields.Selection(muscle_tone)
    muscle_tone_lower_hip_lateral_rot_followup_right = fields.Selection(muscle_tone)
    muscle_tone_lower_hip_lateral_rot_comment = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    muscle_tone_lower_hip_lateral_rot_comment_followup = fields.Char()

    muscle_tone_lower_hip_medial_rot_assessment_left = fields.Selection(muscle_tone, readonly=False,
                                                                        states={'Start': [('readonly', False)]})
    muscle_tone_lower_hip_medial_rot_assessment_right = fields.Selection(muscle_tone, readonly=False,
                                                                         states={'Start': [('readonly', False)]})
    muscle_tone_lower_hip_medial_rot_followup_left = fields.Selection(muscle_tone)
    muscle_tone_lower_hip_medial_rot_followup_right = fields.Selection(muscle_tone)
    muscle_tone_lower_hip_medial_rot_comment = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    muscle_tone_lower_hip_medial_rot_comment_followup = fields.Char()
    # KNEE
    muscle_tone_lower_knee_flex_assessment_left = fields.Selection(muscle_tone, readonly=False,
                                                                   states={'Start': [('readonly', False)]})
    muscle_tone_lower_knee_flex_assessment_right = fields.Selection(muscle_tone, readonly=False,
                                                                    states={'Start': [('readonly', False)]})
    muscle_tone_lower_knee_flex_followup_left = fields.Selection(muscle_tone)
    muscle_tone_lower_knee_flex_followup_right = fields.Selection(muscle_tone)
    muscle_tone_lower_knee_flex_comment = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    muscle_tone_lower_knee_flex_comment_followup = fields.Char()

    muscle_tone_lower_knee_extensors_assessment_left = fields.Selection(muscle_tone, readonly=False,
                                                                        states={'Start': [('readonly', False)]})
    muscle_tone_lower_knee_extensors_assessment_right = fields.Selection(muscle_tone, readonly=False,
                                                                         states={'Start': [('readonly', False)]})
    muscle_tone_lower_knee_extensors_followup_left = fields.Selection(muscle_tone)
    muscle_tone_lower_knee_extensors_followup_right = fields.Selection(muscle_tone)
    muscle_tone_lower_knee_extensors_comment = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    muscle_tone_lower_knee_extensors_comment_followup = fields.Char()

    muscle_tone_lower_ankle_dorsi_flex_assessment_left = fields.Selection(muscle_tone, readonly=False,
                                                                          states={'Start': [('readonly', False)]})
    muscle_tone_lower_ankle_dorsi_flex_assessment_right = fields.Selection(muscle_tone, readonly=False,
                                                                           states={'Start': [('readonly', False)]})
    muscle_tone_lower_ankle_dorsi_flex_followup_left = fields.Selection(muscle_tone)
    muscle_tone_lower_ankle_dorsi_flex_followup_right = fields.Selection(muscle_tone)
    muscle_tone_lower_ankle_dorsi_flex_comment = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    muscle_tone_lower_ankle_dorsi_flex_comment_followup = fields.Char()

    muscle_tone_lower_ankle_plantar_flex_assessment_left = fields.Selection(muscle_tone, readonly=False,
                                                                            states={'Start': [('readonly', False)]})
    muscle_tone_lower_ankle_plantar_flex_assessment_right = fields.Selection(muscle_tone, readonly=False,
                                                                             states={'Start': [('readonly', False)]})
    muscle_tone_lower_ankle_plantar_flex_followup_left = fields.Selection(muscle_tone)
    muscle_tone_lower_ankle_plantar_flex_followup_right = fields.Selection(muscle_tone)
    muscle_tone_lower_ankle_plantar_flex_comment = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    muscle_tone_lower_ankle_plantar_flex_comment_followup = fields.Char()

    muscle_tone_lower_ankle_inversors_assessment_left = fields.Selection(muscle_tone, readonly=False,
                                                                         states={'Start': [('readonly', False)]})
    muscle_tone_lower_ankle_inversors_assessment_right = fields.Selection(muscle_tone, readonly=False,
                                                                          states={'Start': [('readonly', False)]})
    muscle_tone_lower_ankle_inversors_followup_left = fields.Selection(muscle_tone)
    muscle_tone_lower_ankle_inversors_followup_right = fields.Selection(muscle_tone)
    muscle_tone_lower_ankle_inversors_comment = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    muscle_tone_lower_ankle_inversors_comment_followup = fields.Char()

    muscle_tone_lower_ankle_eversors_assessment_left = fields.Selection(muscle_tone, readonly=False,
                                                                        states={'Start': [('readonly', False)]})
    muscle_tone_lower_ankle_eversors_assessment_right = fields.Selection(muscle_tone, readonly=False,
                                                                         states={'Start': [('readonly', False)]})
    muscle_tone_lower_ankle_eversors_followup_left = fields.Selection(muscle_tone)
    muscle_tone_lower_ankle_eversors_followup_right = fields.Selection(muscle_tone)
    muscle_tone_lower_ankle_eversors_comment = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    muscle_tone_lower_ankle_eversors_comment_followup = fields.Char()
    # foot
    muscle_tone_lower_foot_flex_assessment_left = fields.Selection(muscle_tone, readonly=False,
                                                                   states={'Start': [('readonly', False)]})
    muscle_tone_lower_foot_flex_assessment_right = fields.Selection(muscle_tone, readonly=False,
                                                                    states={'Start': [('readonly', False)]})
    muscle_tone_lower_foot_flex_followup_left = fields.Selection(muscle_tone)
    muscle_tone_lower_foot_flex_followup_right = fields.Selection(muscle_tone)
    muscle_tone_lower_foot_flex_comment = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    muscle_tone_lower_foot_flex_comment_followup = fields.Char()

    muscle_tone_lower_foot_extensors_assessment_left = fields.Selection(muscle_tone, readonly=False,
                                                                        states={'Start': [('readonly', False)]})
    muscle_tone_lower_foot_extensors_assessment_right = fields.Selection(muscle_tone, readonly=False,
                                                                         states={'Start': [('readonly', False)]})
    muscle_tone_lower_foot_extensors_followup_left = fields.Selection(muscle_tone)
    muscle_tone_lower_foot_extensors_followup_right = fields.Selection(muscle_tone)
    muscle_tone_lower_foot_extensors_comment = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    muscle_tone_lower_foot_extensors_comment_followup = fields.Char()
    # trunk
    muscle_tone_lower_trunk_flex_assessment_left = fields.Selection(muscle_tone, readonly=False,
                                                                    states={'Start': [('readonly', False)]})
    muscle_tone_lower_trunk_flex_assessment_right = fields.Selection(muscle_tone, readonly=False,
                                                                     states={'Start': [('readonly', False)]})
    muscle_tone_lower_trunk_flex_followup_left = fields.Selection(muscle_tone)
    muscle_tone_lower_trunk_flex_followup_right = fields.Selection(muscle_tone)
    muscle_tone_lower_trunk_flex_comment = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    muscle_tone_lower_trunk_flex_comment_followup = fields.Char()

    muscle_tone_lower_trunk_extensors_assessment_left = fields.Selection(muscle_tone, readonly=False,
                                                                         states={'Start': [('readonly', False)]})
    muscle_tone_lower_trunk_extensors_assessment_right = fields.Selection(muscle_tone, readonly=False,
                                                                          states={'Start': [('readonly', False)]})
    muscle_tone_lower_trunk_extensors_followup_left = fields.Selection(muscle_tone)
    muscle_tone_lower_trunk_extensors_followup_right = fields.Selection(muscle_tone)
    muscle_tone_lower_trunk_extensors_comment = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    muscle_tone_lower_trunk_extensors_comment_followup = fields.Char()
    # R.Bending
    muscle_tone_lower_trunk_r_bending_assessment_left = fields.Selection(muscle_tone, readonly=False,
                                                                         states={'Start': [('readonly', False)]})
    muscle_tone_lower_trunk_r_bending_assessment_right = fields.Selection(muscle_tone, readonly=False,
                                                                          states={'Start': [('readonly', False)]})
    muscle_tone_lower_trunk_r_bending_followup_left = fields.Selection(muscle_tone)
    muscle_tone_lower_trunk_r_bending_followup_right = fields.Selection(muscle_tone)
    muscle_tone_lower_trunk_r_bending_comment = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    muscle_tone_lower_trunk_r_bending_comment_followup = fields.Char()

    muscle_tone_lower_trunk_l_bending_assessment_left = fields.Selection(muscle_tone, readonly=False,
                                                                         states={'Start': [('readonly', False)]})
    muscle_tone_lower_trunk_l_bending_assessment_right = fields.Selection(muscle_tone, readonly=False,
                                                                          states={'Start': [('readonly', False)]})
    muscle_tone_lower_trunk_l_bending_followup_left = fields.Selection(muscle_tone)
    muscle_tone_lower_trunk_l_bending_followup_right = fields.Selection(muscle_tone)
    muscle_tone_lower_trunk_l_bending_comment = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    muscle_tone_lower_trunk_l_bending_comment_followup = fields.Char()
    # R.Rotation
    muscle_tone_lower_trunk_r_rotation_assessment_left = fields.Selection(muscle_tone, readonly=False,
                                                                          states={'Start': [('readonly', False)]})
    muscle_tone_lower_trunk_r_rotation_assessment_right = fields.Selection(muscle_tone, readonly=False,
                                                                           states={'Start': [('readonly', False)]})
    muscle_tone_lower_trunk_r_rotation_followup_left = fields.Selection(muscle_tone)
    muscle_tone_lower_trunk_r_rotation_followup_right = fields.Selection(muscle_tone)
    muscle_tone_lower_trunk_r_rotation_comment = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    muscle_tone_lower_trunk_r_rotation_comment_followup = fields.Char()

    muscle_tone_lower_trunk_l_rotation_assessment_left = fields.Selection(muscle_tone, readonly=False,
                                                                          states={'Start': [('readonly', False)]})
    muscle_tone_lower_trunk_l_rotation_assessment_right = fields.Selection(muscle_tone, readonly=False,
                                                                           states={'Start': [('readonly', False)]})
    muscle_tone_lower_trunk_l_rotation_followup_left = fields.Selection(muscle_tone)
    muscle_tone_lower_trunk_l_rotation_followup_right = fields.Selection(muscle_tone)
    muscle_tone_lower_trunk_l_rotation_comment = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    muscle_tone_lower_trunk_l_rotation_comment_followup = fields.Char()
    # Upper limb
    # shoulder
    muscle_tone_upper_shoulder_flex_assessment_left = fields.Selection(muscle_tone, readonly=False,
                                                                       states={'Start': [('readonly', False)]})
    muscle_tone_upper_shoulder_flex_assessment_right = fields.Selection(muscle_tone, readonly=False,
                                                                        states={'Start': [('readonly', False)]})
    muscle_tone_upper_shoulder_flex_followup_left = fields.Selection(muscle_tone)
    muscle_tone_upper_shoulder_flex_followup_right = fields.Selection(muscle_tone)
    muscle_tone_upper_shoulder_flex_comment = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    muscle_tone_upper_shoulder_flex_comment_followup = fields.Char()

    muscle_tone_upper_shoulder_extensors_assessment_left = fields.Selection(muscle_tone, readonly=False,
                                                                            states={'Start': [('readonly', False)]})
    muscle_tone_upper_shoulder_extensors_assessment_right = fields.Selection(muscle_tone, readonly=False,
                                                                             states={'Start': [('readonly', False)]})
    muscle_tone_upper_shoulder_extensors_followup_left = fields.Selection(muscle_tone)
    muscle_tone_upper_shoulder_extensors_followup_right = fields.Selection(muscle_tone)
    muscle_tone_upper_shoulder_extensors_comment = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    muscle_tone_upper_shoulder_extensors_comment_followup = fields.Char()

    muscle_tone_upper_shoulder_abductors_assessment_left = fields.Selection(muscle_tone, readonly=False,
                                                                            states={'Start': [('readonly', False)]})
    muscle_tone_upper_shoulder_abductors_assessment_right = fields.Selection(muscle_tone, readonly=False,
                                                                             states={'Start': [('readonly', False)]})
    muscle_tone_upper_shoulder_abductors_followup_left = fields.Selection(muscle_tone)
    muscle_tone_upper_shoulder_abductors_followup_right = fields.Selection(muscle_tone)
    muscle_tone_upper_shoulder_abductors_comment = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    muscle_tone_upper_shoulder_abductors_comment_followup = fields.Char()

    muscle_tone_upper_shoulder_adductors_assessment_left = fields.Selection(muscle_tone, readonly=False,
                                                                            states={'Start': [('readonly', False)]})
    muscle_tone_upper_shoulder_adductors_assessment_right = fields.Selection(muscle_tone, readonly=False,
                                                                             states={'Start': [('readonly', False)]})
    muscle_tone_upper_shoulder_adductors_followup_left = fields.Selection(muscle_tone)
    muscle_tone_upper_shoulder_adductors_followup_right = fields.Selection(muscle_tone)
    muscle_tone_upper_shoulder_adductors_comment = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    muscle_tone_upper_shoulder_adductors_comment_followup = fields.Char()

    muscle_tone_upper_shoulder_lateral_rot_assessment_left = fields.Selection(muscle_tone, readonly=False,
                                                                              states={'Start': [('readonly', False)]})
    muscle_tone_upper_shoulder_lateral_rot_assessment_right = fields.Selection(muscle_tone, readonly=False,
                                                                               states={'Start': [('readonly', False)]})
    muscle_tone_upper_shoulder_lateral_rot_followup_left = fields.Selection(muscle_tone)
    muscle_tone_upper_shoulder_lateral_rot_followup_right = fields.Selection(muscle_tone)
    muscle_tone_upper_shoulder_lateral_rot_comment = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    muscle_tone_upper_shoulder_lateral_rot_comment_followup = fields.Char()

    muscle_tone_upper_shoulder_medial_rot_assessment_left = fields.Selection(muscle_tone, readonly=False,
                                                                             states={'Start': [('readonly', False)]})
    muscle_tone_upper_shoulder_medial_rot_assessment_right = fields.Selection(muscle_tone, readonly=False,
                                                                              states={'Start': [('readonly', False)]})
    muscle_tone_upper_shoulder_medial_rot_followup_left = fields.Selection(muscle_tone)
    muscle_tone_upper_shoulder_medial_rot_followup_right = fields.Selection(muscle_tone)
    muscle_tone_upper_shoulder_medial_rot_comment = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    muscle_tone_upper_shoulder_medial_rot_comment_followup = fields.Char()

    muscle_tone_upper_shoulder_elevators_assessment_left = fields.Selection(muscle_tone, readonly=False,
                                                                            states={'Start': [('readonly', False)]})
    muscle_tone_upper_shoulder_elevators_assessment_right = fields.Selection(muscle_tone, readonly=False,
                                                                             states={'Start': [('readonly', False)]})
    muscle_tone_upper_shoulder_elevators_followup_left = fields.Selection(muscle_tone)
    muscle_tone_upper_shoulder_elevators_followup_right = fields.Selection(muscle_tone)
    muscle_tone_upper_shoulder_elevators_comment = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    muscle_tone_upper_shoulder_elevators_comment_followup = fields.Char()

    muscle_tone_upper_shoulder_depressors_assessment_left = fields.Selection(muscle_tone, readonly=False,
                                                                             states={'Start': [('readonly', False)]})
    muscle_tone_upper_shoulder_depressors_assessment_right = fields.Selection(muscle_tone, readonly=False,
                                                                              states={'Start': [('readonly', False)]})
    muscle_tone_upper_shoulder_depressors_followup_left = fields.Selection(muscle_tone)
    muscle_tone_upper_shoulder_depressors_followup_right = fields.Selection(muscle_tone)
    muscle_tone_upper_shoulder_depressors_comment = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    muscle_tone_upper_shoulder_depressors_comment_followup = fields.Char()

    muscle_tone_upper_shoulder_antropulsors_assessment_left = fields.Selection(muscle_tone, readonly=False,
                                                                               states={'Start': [('readonly', False)]})
    muscle_tone_upper_shoulder_antropulsors_assessment_right = fields.Selection(muscle_tone, readonly=False,
                                                                                states={'Start': [('readonly', False)]})
    muscle_tone_upper_shoulder_antepulsors_followup_left = fields.Selection(muscle_tone)
    muscle_tone_upper_shoulder_antepulsors_followup_right = fields.Selection(muscle_tone)
    muscle_tone_upper_shoulder_antepulsors_comment = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    muscle_tone_upper_shoulder_antepulsors_comment_followup = fields.Char()

    muscle_tone_upper_shoulder_retropulsors_assessment_left = fields.Selection(muscle_tone, readonly=False,
                                                                               states={'Start': [('readonly', False)]})
    muscle_tone_upper_shoulder_retropulsors_assessment_right = fields.Selection(muscle_tone, readonly=False,
                                                                                states={'Start': [('readonly', False)]})
    muscle_tone_upper_shoulder_retropulsors_followup_left = fields.Selection(muscle_tone)
    muscle_tone_upper_shoulder_retropulsors_followup_right = fields.Selection(muscle_tone)
    muscle_tone_upper_shoulder_retropulsors_comment = fields.Char(readonly=False,
                                                                  states={'Start': [('readonly', False)]})
    muscle_tone_upper_shoulder_retropulsors_comment_followup = fields.Char()
    # ELBOW
    muscle_tone_upper_elbow_flex_assessment_left = fields.Selection(muscle_tone, readonly=False,
                                                                    states={'Start': [('readonly', False)]})
    muscle_tone_upper_elbow_flex_assessment_right = fields.Selection(muscle_tone, readonly=False,
                                                                     states={'Start': [('readonly', False)]})
    muscle_tone_upper_elbow_flex_followup_left = fields.Selection(muscle_tone)
    muscle_tone_upper_elbow_flex_followup_right = fields.Selection(muscle_tone)
    muscle_tone_upper_elbow_flex_comment = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    muscle_tone_upper_elbow_flex_comment_followup = fields.Char()

    muscle_tone_upper_elbow_extensors_assessment_left = fields.Selection(muscle_tone, readonly=False,
                                                                         states={'Start': [('readonly', False)]})
    muscle_tone_upper_elbow_extensors_assessment_right = fields.Selection(muscle_tone, readonly=False,
                                                                          states={'Start': [('readonly', False)]})
    muscle_tone_upper_elbow_extensors_followup_left = fields.Selection(muscle_tone)
    muscle_tone_upper_elbow_extensors_followup_right = fields.Selection(muscle_tone)
    muscle_tone_upper_elbow_extensors_comment = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    muscle_tone_upper_elbow_extensors_comment_followup = fields.Char()

    # FOREARM
    muscle_tone_upper_forearm_supinators_assessment_left = fields.Selection(muscle_tone, readonly=False,
                                                                            states={'Start': [('readonly', False)]})
    muscle_tone_upper_forearm_supinators_assessment_right = fields.Selection(muscle_tone, readonly=False,
                                                                             states={'Start': [('readonly', False)]})
    muscle_tone_upper_forearm_supinators_followup_left = fields.Selection(muscle_tone)
    muscle_tone_upper_forearm_supinators_followup_right = fields.Selection(muscle_tone)
    muscle_tone_upper_forearm_supinators_comment = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    muscle_tone_upper_forearm_supinators_comment_followup = fields.Char()

    muscle_tone_upper_forearm_pronators_assessment_left = fields.Selection(muscle_tone, readonly=False,
                                                                           states={'Start': [('readonly', False)]})
    muscle_tone_upper_forearm_pronators_assessment_right = fields.Selection(muscle_tone, readonly=False,
                                                                            states={'Start': [('readonly', False)]})
    muscle_tone_upper_forearm_pronators_followup_left = fields.Selection(muscle_tone)
    muscle_tone_upper_forearm_pronators_followup_right = fields.Selection(muscle_tone)
    muscle_tone_upper_forearm_pronators_comment = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    muscle_tone_upper_forearm_pronators_comment_followup = fields.Char()

    # wrist
    muscle_tone_upper_wrist_flex_assessment_left = fields.Selection(muscle_tone, readonly=False,
                                                                    states={'Start': [('readonly', False)]})
    muscle_tone_upper_wrist_flex_assessment_right = fields.Selection(muscle_tone, readonly=False,
                                                                     states={'Start': [('readonly', False)]})
    muscle_tone_upper_wrist_flex_followup_left = fields.Selection(muscle_tone)
    muscle_tone_upper_wrist_flex_followup_right = fields.Selection(muscle_tone)
    muscle_tone_upper_wrist_flex_comment = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    muscle_tone_upper_wrist_flex_comment_followup = fields.Char()

    muscle_tone_upper_wrist_extensors_assessment_left = fields.Selection(muscle_tone, readonly=False,
                                                                         states={'Start': [('readonly', False)]})
    muscle_tone_upper_wrist_extensors_assessment_right = fields.Selection(muscle_tone, readonly=False,
                                                                          states={'Start': [('readonly', False)]})
    muscle_tone_upper_wrist_extensors_followup_left = fields.Selection(muscle_tone)
    muscle_tone_upper_wrist_extensors_followup_right = fields.Selection(muscle_tone)
    muscle_tone_upper_wrist_extensors_comment = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    muscle_tone_upper_wrist_extensors_comment_followup = fields.Char()

    # fingers
    muscle_tone_upper_fingers_flex_assessment_left = fields.Selection(muscle_tone, readonly=False,
                                                                      states={'Start': [('readonly', False)]})
    muscle_tone_upper_fingers_flex_assessment_right = fields.Selection(muscle_tone, readonly=False,
                                                                       states={'Start': [('readonly', False)]})
    muscle_tone_upper_fingers_flex_followup_left = fields.Selection(muscle_tone)
    muscle_tone_upper_fingers_flex_followup_right = fields.Selection(muscle_tone)
    muscle_tone_upper_fingers_flex_comment = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    muscle_tone_upper_fingers_flex_comment_followup = fields.Char()

    muscle_tone_upper_fingers_extensors_assessment_left = fields.Selection(muscle_tone, readonly=False,
                                                                           states={'Start': [('readonly', False)]})
    muscle_tone_upper_fingers_extensors_assessment_right = fields.Selection(muscle_tone, readonly=False,
                                                                            states={'Start': [('readonly', False)]})
    muscle_tone_upper_fingers_extensors_followup_left = fields.Selection(muscle_tone)
    muscle_tone_upper_fingers_extensors_followup_right = fields.Selection(muscle_tone)
    muscle_tone_upper_fingers_extensors_comment = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    muscle_tone_upper_fingers_extensors_comment_followup = fields.Char()

    muscle_tone_upper_fingers_abductors_assessment_left = fields.Selection(muscle_tone, readonly=False,
                                                                           states={'Start': [('readonly', False)]})
    muscle_tone_upper_fingers_abductors_assessment_right = fields.Selection(muscle_tone, readonly=False,
                                                                            states={'Start': [('readonly', False)]})
    muscle_tone_upper_fingers_abductors_followup_left = fields.Selection(muscle_tone)
    muscle_tone_upper_fingers_abductors_followup_right = fields.Selection(muscle_tone)
    muscle_tone_upper_fingers_abductors_comment = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    muscle_tone_upper_fingers_abductors_comment_followup = fields.Char()

    muscle_tone_upper_fingers_opposition_assessment_left = fields.Selection(muscle_tone, readonly=False,
                                                                            states={'Start': [('readonly', False)]})
    muscle_tone_upper_fingers_opposition_assessment_right = fields.Selection(muscle_tone, readonly=False,
                                                                             states={'Start': [('readonly', False)]})
    muscle_tone_upper_fingers_opposition_followup_left = fields.Selection(muscle_tone)
    muscle_tone_upper_fingers_opposition_followup_right = fields.Selection(muscle_tone)
    muscle_tone_upper_fingers_opposition_comment = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    muscle_tone_upper_fingers_opposition_comment_followup = fields.Char()

    # Functional Evaluation
    balance_disorders_show = fields.Boolean()
    balance_disorders_sitting = fields.Selection(balance_disorders, string='Sitting',
                                                 readonly=False, states={'Start': [('readonly', False)]})
    balance_disorders_standing = fields.Selection(balance_disorders, string='Standing',
                                                  readonly=False, states={'Start': [('readonly', False)]})

    coordination_show = fields.Boolean()
    coordination_upper_limbs_left = fields.Selection(coordination_state, string='Left',
                                                     readonly=False, states={'Start': [('readonly', False)]})
    coordination_upper_limbs_right = fields.Selection(coordination_state, string='Right',
                                                      readonly=False, states={'Start': [('readonly', False)]})
    coordination_lower_limbs_left = fields.Selection(coordination_state, string='Left',
                                                     readonly=False, states={'Start': [('readonly', False)]})
    coordination_lower_limbs_right = fields.Selection(coordination_state, string='Right',
                                                      readonly=False, states={'Start': [('readonly', False)]})
    coordination_comments = fields.Text(string='Comments',
                                        readonly=False, states={'Start': [('readonly', False)]})

    gait_analysis_show = fields.Boolean()
    frontal_plane_observation = fields.Text(string='Observations',
                                            readonly=False, states={'Start': [('readonly', False)]})
    sagittal_plane_observation = fields.Text(string='Observations',
                                             readonly=False, states={'Start': [('readonly', False)]})

    functional_quality_of_the_gait_show = fields.Boolean()
    functional_quality_safety = fields.Selection(functional_quality_state, string='Safety',
                                                 readonly=False, states={'Start': [('readonly', False)]})
    functional_quality_safety_comments = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    functional_quality_cadence = fields.Selection(functional_quality_state, string='Cadence',
                                                  readonly=False, states={'Start': [('readonly', False)]})
    functional_quality_cadence_comments = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    functional_quality_speed = fields.Selection(functional_quality_state, string='Speed',
                                                readonly=False, states={'Start': [('readonly', False)]})
    functional_quality_speed_comments = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    functional_quality_fatigue = fields.Selection(functional_quality_state, string='Fatigue',
                                                  readonly=False, states={'Start': [('readonly', False)]})
    functional_quality_fatigue_comments = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    functional_quality_remarks = fields.Text(string='Other Remarks',
                                             readonly=False, states={'Start': [('readonly', False)]})

    # Activity Limitations & Participation Restrictions
    # Mobility
    mobility_show = fields.Boolean()
    activity_mobility_crawling = fields.Selection(activity_state, string='Crawling',
                                                  readonly=False, states={'Start': [('readonly', False)]})
    activity_mobility_crawling_comments = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    activity_mobility_crouching_gait = fields.Selection(activity_state, string='Crouching gait',
                                                        readonly=False, states={'Start': [('readonly', False)]})
    activity_mobility_crouching_gait_comments = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    activity_mobility_walking = fields.Selection(activity_state, string='Walking',
                                                 readonly=False, states={'Start': [('readonly', False)]})
    activity_mobility_walking_comments = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    activity_mobility_squatting = fields.Selection(activity_state, string='Squatting',
                                                   readonly=False, states={'Start': [('readonly', False)]})
    activity_mobility_squatting_comments = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    activity_mobility_stairs = fields.Selection(activity_state, string='Stairs',
                                                readonly=False, states={'Start': [('readonly', False)]})
    activity_mobility_stairs_comments = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    activity_mobility_running = fields.Selection(activity_state, string='Running',
                                                 readonly=False, states={'Start': [('readonly', False)]})
    activity_mobility_running_comments = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    # Transfers
    transfers_show = fields.Boolean()
    activity_transfers_lie_sit = fields.Selection(activity_state, string='Lie to Sit (& opposite)',
                                                  readonly=False, states={'Start': [('readonly', False)]})
    activity_transfers_lie_sit_comments = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    activity_transfers_sit_stand = fields.Selection(activity_state, string='Sit to Stand (& opposite)',
                                                    readonly=False, states={'Start': [('readonly', False)]})
    activity_transfers_sit_stand_comments = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    activity_transfers_stand_floor = fields.Selection(activity_state, string='Stand to Floor (& opposite)',
                                                      readonly=False, states={'Start': [('readonly', False)]})
    activity_transfers_stand_floor_comments = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    activity_transfers_sit_sit = fields.Selection(activity_state, string='Sit to Sit',
                                                  readonly=False, states={'Start': [('readonly', False)]})
    activity_transfers_sit_sit_comments = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    # Balance
    balance_show = fields.Boolean()
    activity_balance_sitting = fields.Selection(activity_state, string='Sitting',
                                                readonly=False, states={'Start': [('readonly', False)]})
    activity_balance_sitting_comments = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    activity_balance_standing = fields.Selection(activity_state, string='Standing',
                                                 readonly=False, states={'Start': [('readonly', False)]})
    activity_balance_standing_comments = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    activity_balance_on_one_leg = fields.Selection(activity_state, string='On One Leg',
                                                   readonly=False, states={'Start': [('readonly', False)]})
    activity_balance_on_one_leg_comments = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    # upper limb functions
    upper_limb_functions_show = fields.Boolean()
    activity_upperlimb_grasp_right = fields.Selection(activity_state, string='Right',
                                                      readonly=False, states={'Start': [('readonly', False)]})
    activity_upperlimb_grasp_right_comments = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    activity_upperlimb_grasp_left = fields.Selection(activity_state, string='Left',
                                                     readonly=False, states={'Start': [('readonly', False)]})
    activity_upperlimb_grasp_left_comments = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    activity_upperlimb_release_right = fields.Selection(activity_state, string='Right',
                                                        readonly=False, states={'Start': [('readonly', False)]})
    activity_upperlimb_release_right_comments = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    activity_upperlimb_release_left = fields.Selection(activity_state, string='Left',
                                                       readonly=False, states={'Start': [('readonly', False)]})
    activity_upperlimb_release_left_comments = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    activity_upperlimb_fine_manipulation_right = fields.Selection(activity_state, string='Right',
                                                                  readonly=False,
                                                                  states={'Start': [('readonly', False)]})
    activity_upperlimb_fine_manipulation_right_comments = fields.Char(readonly=False,
                                                                      states={'Start': [('readonly', False)]})
    activity_upperlimb_fine_manipulation_left = fields.Selection(activity_state, string='Left',
                                                                 readonly=False, states={'Start': [('readonly', False)]})
    activity_upperlimb_fine_manipulation_left_comments = fields.Char(readonly=False,
                                                                     states={'Start': [('readonly', False)]})
    activity_upperlimb_holding_right = fields.Selection(activity_state, string='Right',
                                                        readonly=False, states={'Start': [('readonly', False)]})
    activity_upperlimb_holding_right_comments = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    activity_upperlimb_holding_left = fields.Selection(activity_state, string='Left',
                                                       readonly=False, states={'Start': [('readonly', False)]})
    activity_upperlimb_holding_left_comments = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    # Daily Life Activities
    daily_life_activities_show = fields.Boolean()
    activity_daily_life_dressing_upper = fields.Selection(activity_state, string='Dressing-Upper body',
                                                          readonly=False, states={'Start': [('readonly', False)]})
    activity_daily_life_dressing_upper_comments = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    activity_daily_life_dressing_lower = fields.Selection(activity_state, string='Dressing-Lower body',
                                                          readonly=False, states={'Start': [('readonly', False)]})
    activity_daily_life_dressing_lower_comments = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    activity_daily_life_toileting = fields.Selection(activity_state, string='Toileting',
                                                     readonly=False, states={'Start': [('readonly', False)]})
    activity_daily_life_toileting_comments = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    activity_daily_life_bathing = fields.Selection(activity_state, string='Bathing',
                                                   readonly=False, states={'Start': [('readonly', False)]})
    activity_daily_life_bathing_comments = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    activity_daily_life_washing_oneself = fields.Selection(activity_state, string='Washing oneself',
                                                           readonly=False, states={'Start': [('readonly', False)]})
    activity_daily_life_washing_oneself_comments = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    activity_daily_life_eating = fields.Selection(activity_state, string='Eating',
                                                  readonly=False, states={'Start': [('readonly', False)]})
    activity_daily_life_eating_comments = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    activity_daily_life_drinking = fields.Selection(activity_state, string='Drinking',
                                                    readonly=False, states={'Start': [('readonly', False)]})
    activity_daily_life_drinking_comments = fields.Char(readonly=False, states={'Start': [('readonly', False)]})

    # Conclusion of patient assessment & main findings
    environmental_personal_factors_show = fields.Boolean()
    environmental_current_treatment = fields.Text(string='Current Treatment',
                                                  readonly=False, states={'Start': [('readonly', False)]})
    environmental_remarks = fields.Text(string='Remarks',
                                        readonly=False, states={'Start': [('readonly', False)]})
    body_structure_function_impairments_show = fields.Boolean()
    body_structure_ass_trauma = fields.Text(string='Ass.trauma & diseases',
                                            readonly=False, states={'Start': [('readonly', False)]})
    body_structure_rom_status = fields.Text(string='R.O.M status',
                                            readonly=False, states={'Start': [('readonly', False)]})
    body_structure_muscle_status = fields.Text(string='Muscle status',
                                               readonly=False, states={'Start': [('readonly', False)]})
    body_structure_skin_tissues = fields.Text(string='Skin & soft tissues/ Pain',
                                              readonly=False, states={'Start': [('readonly', False)]})
    activity_limitations_participation_restriction_show = fields.Boolean()
    activities_limitation_general_mobility = fields.Text(string='General Mobility(gait)',
                                                         readonly=False, states={'Start': [('readonly', False)]})
    activities_limitation_transfers = fields.Text(string='Transfers',
                                                  readonly=False, states={'Start': [('readonly', False)]})
    activities_limitation_balance = fields.Text(string='Balance',
                                                readonly=False, states={'Start': [('readonly', False)]})
    activities_limitation_daily_life = fields.Text(string='Daily life activities',
                                                   readonly=False, states={'Start': [('readonly', False)]})
    activities_limitation_upper_limb_functions = fields.Text(string='Upper limb functions',
                                                             readonly=False, states={'Start': [('readonly', False)]})

    # Treatment plan
    treatment_plan_show = fields.Boolean()
    treatment_plane = fields.Selection([
        ('Standing Frame', 'Standing Frame'),
        ('Baby walker', 'Baby walker'),
        ('Other', 'Other'),
    ], string="Treatment Plane", readonly=False, states={'Start': [('readonly', False)]})
    treatment_plane_other_content = fields.Char(string='specify', readonly=False,
                                                states={'Start': [('readonly', False)]})
    technical_specification_show = fields.Boolean()
    technical_specifications = fields.Text(string="Technical Specifications", readonly=False,
                                           states={'Start': [('readonly', False)]})
    physiotherapy_treatment_plan_show = fields.Boolean()
    treatment_objectives_short_term = fields.Text(string="Short Term", readonly=False,
                                                  states={'Start': [('readonly', False)]})
    treatment_objectives_mid_term = fields.Text(string="Mid Term", readonly=False,
                                                states={'Start': [('readonly', False)]})
    treatment_objectives_long_term = fields.Text(string="Long Term", readonly=False,
                                                 states={'Start': [('readonly', False)]})

    # followup_ids = fields.One2many('sm.shifa.physiotherapy.followup', 'physiotherapy_number_id', string='Follow up')
    physiotherapy_follow_up_id = fields.One2many('sm.shifa.physiotherapy.followup', 'phyio_as',
                                                 string='physiotherapy follow up')
    consent_show = fields.Boolean()
    consent_file1 = fields.Binary()
    consent_file2 = fields.Binary()
    active = fields.Boolean(default=True)

    """def action_archive(self):
        for rec in self:
            if rec.state != 'Discharged':
                raise UserError(_("You can archive only if it discharged assessments"))
        return super().action_archive()"""
    @api.onchange('treatment_plane')
    def _onchange_vision(self):
        if not self.treatment_plane == 'Other':
            self.treatment_plane_other_content = ''

    # @api.onchange('admission_date', 'date_assessment_range_of_motion')
    # def _onchange_assessment_date(self):
    #     if self.admission_date:
    #         self.date_assessment_range_of_motion = self.admission_date
    #         print(1)
    @api.model
    def create(self, vals):
        vals['physiotherapy_assessment_code'] = self.env['ir.sequence'].next_by_code(
            'sm.shifa.physiotherapy.assessment')
        return super(ShifaPhysiotherapyAssessment, self).create(vals)

    @api.onchange('systolic', 'bpm', 'diastolic', 'respiratory_rate', 'temperature', 'char_other_oxygen')
    def _check_vital_signs(self):
        if self.systolic > 1000:
            raise ValidationError("invalid systolic BP(mmHg)")
        if self.bpm > 1000:
            raise ValidationError("invalid HR(/min)")
        if self.temperature > 100:
            raise ValidationError("invalid Temperature(C)")
        if self.diastolic > 1000:
            raise ValidationError("invalid Diastolic BR(mmHg)")
        if self.respiratory_rate > 100:
            raise ValidationError("invalid RR(/min)")
        if self.char_other_oxygen > 1000:
            raise ValidationError("invalid O2 Sat(%)")

    def back_to_admitted(self):
        return self.write({'state': 'Admitted', 'discharge_date': None})

    @api.model
    def check_and_discharge_patients(self):
        current_date = datetime.datetime.now()
        discharge_date = current_date - datetime.timedelta(days=60)

        assessments = self.search([
            ('state', '=', 'Admitted'),
            ('admission_date', '>', discharge_date)
        ])

        if assessments:
            assessments.write({'state': 'Discharged', 'discharge_date': discharge_date})

