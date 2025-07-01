from odoo import models, fields, api
import datetime
from odoo.exceptions import ValidationError


class ShifaPhysicianAdmissionFollowUp(models.Model):
    _name = 'sm.physician.admission.followup'
    _description = 'Physician Admission Follow Up'
    _rec_name = 'name'

    ADMISSION_STATES = [
        ('Draft', 'Draft'),
        ('Start', 'Start'),
        ('Done', 'Done'),
    ]
    pain_score_number = [
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
    ]

    @api.onchange('hhc_appointment')
    def _onchange_hhc_appointment(self):
        if self.hhc_appointment:
            self.patient = self.hhc_appointment.patient

    @api.onchange('phy_adm')
    def _onchange_join_phy_adm(self):
        if self.phy_adm:
            self.physician_admission = self.phy_adm

    def _get_physician(self):
        """Return default physician value"""
        therapist_obj = self.env['oeh.medical.physician']
        domain = [('oeh_user_id', '=', self.env.uid)]
        user_ids = therapist_obj.search(domain, limit=1)
        if user_ids:
            return user_ids.id or False
        else:
            return False

    name = fields.Char('Physician Admission Follow up Reference', index=True, copy=False)
    # appointment register link
    hhc_appointment = fields.Many2one('sm.shifa.hhc.appointment', string='HHC-Appointment',
                                      readonly=False, states={'Done': [('readonly', False)]})
    # appointment register link
    phy_adm = fields.Many2one('sm.shifa.physician.admission', string='Phy_Adm #', required=True, readonly=False, states={'Done': [('readonly', False)]},
                              domain="[('patient', '=', patient), ('state', 'in', ('Admitted', 'Start'))]")
    doctor = fields.Many2one('oeh.medical.physician', string='Doctor', help="Current primary care / family doctor",
                             domain=[('role_type', 'in', ['HD', 'HHCD', 'HVD']), ('active', '=', True)],
                             readonly=False, states={'Done': [('readonly', False)]}, required=True,
                             default=_get_physician)
    state = fields.Selection(ADMISSION_STATES, string='State', default=lambda *a: 'Draft', readonly=True)
    start_date = fields.Datetime(string='Start Date')
    completed_date = fields.Datetime(string='Completed Date')

    # patient details
    patient = fields.Many2one('oeh.medical.patient', string='Patient', help="Patient Name", required=True,
                              readonly=False, states={'Done': [('readonly', False)]})
    dob = fields.Date(string='Date of Birth', related='patient.dob', readonly='1')
    marital_status = fields.Selection(string='Marital Status', related='patient.marital_status', readonly='1')
    sex = fields.Selection(string='Sex', related='patient.sex')
    blood_type = fields.Selection(string='Blood Type', related='patient.blood_type', readonly='1')
    rh = fields.Selection(string='Rh', related='patient.rh', readonly='1')
    patient_weight = fields.Float(string='Weight(kg)', related='patient.weight')
    age = fields.Char(string='Age', related='patient.age')

    # relate prescription to physician
    notification_ids = fields.One2many('sm.physician.notification', 'physician_admission_followup',
                                       string='physician follow up notification')
    investigation_ids = fields.One2many('sm.shifa.investigation', 'physician_followup', string='Investigation')
    labtest_line = fields.One2many('sm.shifa.lab.request', 'physician_followup', string='Lab Request')
    image_test_ids = fields.One2many('sm.shifa.imaging.request', 'physician_followup')
    # relate prescription to physician
    prescription_ids = fields.One2many('oeh.medical.prescription', 'physician_followup')
    lab_request_test_line = fields.One2many('sm.shifa.lab.request.line', 'phy_adm_fu', string='Lab Request',
                                            readonly=False, states={'Done': [('readonly', False)]})
    image_request_test_ids = fields.One2many('sm.shifa.imaging.request.line', 'phy_adm_fu', string='Image Request',
                                             readonly=False, states={'Done': [('readonly', False)]})

    # sequence number method
    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('sm.physician.admission.followup')
        return super(ShifaPhysicianAdmissionFollowUp, self).create(vals)

    def set_to_done(self):
        for rec in self:
            if not rec.lab_request_test_line:
                pass
            else:
                # print("Lab")
                rec.env['sm.shifa.lab.request'].create({
                    'patient': rec.patient.id,
                    'doctor': rec.doctor.id,
                    'hhc_appointment': rec.hhc_appointment.id,
                    'lab_request_ids': rec.lab_request_test_line,
                })

            if not rec.image_request_test_ids:
                pass
            else:
                # print("Image")
                rec.env['sm.shifa.imaging.request'].create({
                    'patient': rec.patient.id,
                    'doctor': rec.doctor.id,
                    'hhc_appointment': rec.hhc_appointment.id,
                    'image_req_test_ids': rec.image_request_test_ids,
                })
        return self.write({'state': 'Done', 'completed_date': datetime.datetime.now()})

    def set_to_start(self):
        return self.write({'state': 'Start', 'start_date': datetime.datetime.now()})


class ShifaPhysicianExaminationTab(models.Model):
    _inherit = 'sm.physician.admission.followup'
    pain_score = [
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
    ]
    yes_no = [
        ('Yes', 'Yes'),
        ('No', 'No'),
    ]
    musculoskeletal_extremity = [
        ('Active Against Gravity and Resistance', 'Active Against Gravity and Resistance'),
        ('Active with Gravity Eliminated', 'Active with Gravity Eliminated'),
        ('Contracture', 'Contracture'),
        ('Deformity', 'Deformity'),
        ('Dislocation', 'Dislocation'),
        ('Fracture', 'Fracture'),
        ('Paralysis', 'Paralysis'),
        ('Prosthesis', 'Prosthesis'),
        ('Stiffness', 'Stiffness'),
        ('Weak', 'Weak'),
        ('Other', 'Other'),
    ]
    number_neuralogical = [
        ('0.5', '0.5'),
        ('1', '1'),
        ('1.5', '1.5'),
        ('2', '2'),
        ('2.5', '2.5'),
        ('3', '3'),
        ('3.5', '3.5'),
        ('4', '4'),
        ('4.5', '4.5'),
        ('5', '5'),
        ('5.5', '5.5'),
        ('6', '6'),
        ('6.5', '6.5'),
        ('7', '7'),
        ('7.5', '7.5'),
        ('8', '8'),
        ('8.5', '8.5'),
        ('9', '9'),
        ('9.5', '9.5'),
    ]
    level_consciousness = [
        ('Alert', 'Alert'),
        ('Awake', 'Awake'),
        ('Decrease response to environment', 'Decrease response to environment'),
        ('Delirious', 'Delirious'),
        ('Drowsiness', 'Drowsiness'),
        ('Irritable', 'Irritable'),
        ('Lathargy', 'Lathargy'),
        ('Obtunded', 'Obtunded'),
        ('Restless', 'Restless'),
        ('Stuper', 'Stuper'),
        ('Unresponsnsive', 'Unresponsnsive'),
    ]
    eye_momement = [
        ('Spontaneous', 'Spontaneous'),
        ('To speech', 'To speech'),
        ('To pain', 'To pain'),
        ('No respond', 'No respond'),
    ]

    cal_score_eye = {
        'Spontaneous': 4,
        'To speech': 3,
        'To pain': 2,
        'No respond': 1,
    }
    cal_score_motor = {
        'Spontaneous movements': 6,
        'Localizes pain': 5,
        'Flexion withdrawal': 4,
        'Abnormal flexion': 3,
        'Abnormal extension': 2,
        'No response': 1,
    }
    cal_score_verbal = {
        'Coos and smiles appropriate': 5,
        'Cries': 4,
        'Inappropriate crying/screaming': 3,
        'Grunts': 2,
        'No response': 1,
    }
    cal_score_verbal_2_5 = {
        'Appropriate Words': 5,
        'Inappropriate Word': 4,
        'Cries/Screams': 3,
        'Grunts': 2,
        'No response': 1,
    }
    cal_score_verbal_5 = {
        'Orient': 5,
        'Confused': 4,
        'Inappropriate': 3,
        'Incompratensive': 2,
        'No verable response': 1,
    }
    motor_response = [
        ('Obeys command', 'Obeys command'),
        ('Localizes pain', 'Localizes pain'),
        ('Withdraws from pain', 'Withdraws from pain'),
        ('Flexion response to pain', 'Flexion response to pain'),
        ('Extension response to pain', 'Extension response to pain'),
        ('No motor response', 'No motor response'),
    ]
    motor_response_dec = {
        'Obeys command': 6,
        'Localizes pain': 5,
        'Withdraws from pain': 4,
        'Flexion response to pain': 3,
        'Extension response to pain': 2,
        'No motor response': 1,
    }

    @api.depends("neuralogical_less_than_2_eye", "neuralogical_less_than_2_motor", "neuralogical_less_than_2_verbal")
    def _compute_less_2(self):
        sum_1, sum_2, sum_3 = 0, 0, 0
        for key, value in self.cal_score_eye.items():
            if self.neuralogical_less_than_2_eye == key:
                sum_1 = value
        for key, value in self.cal_score_motor.items():
            if self.neuralogical_less_than_2_motor == key:
                sum_2 = value
        for key, value in self.cal_score_verbal.items():
            if self.neuralogical_less_than_2_verbal == key:
                sum_3 = value
        for record in self:
            record.neuralogical_less_than_2_glascow = sum_1 + sum_2 + sum_3

    @api.depends("neuralogical_2_to_5_eye", "neuralogical_2_to_5_motor", "neuralogical_2_to_5_verbal")
    def _compute_2_5_old(self):
        sum_1, sum_2, sum_3 = 0, 0, 0
        for key, value in self.cal_score_eye.items():
            if self.neuralogical_2_to_5_eye == key:
                sum_1 = value
        for key, value in self.motor_response_dec.items():
            if self.neuralogical_2_to_5_motor == key:
                sum_2 = value
        for key, value in self.cal_score_verbal_2_5.items():
            if self.neuralogical_2_to_5_verbal == key:
                sum_3 = value
        for record in self:
            record.neuralogical_2_to_5_glascow = sum_1 + sum_2 + sum_3

    @api.depends("neuralogical_greater_than_5_years_eye", "neuralogical_greater_than_5_years_motor",
                 "neuralogical_greater_than_5_years_verbal")
    def _compute_greater_5_old(self):
        sum_1, sum_2, sum_3 = 0, 0, 0
        for key, value in self.cal_score_eye.items():
            if self.neuralogical_greater_than_5_years_eye == key:
                sum_1 = value
        for key, value in self.motor_response_dec.items():
            if self.neuralogical_greater_than_5_years_motor == key:
                sum_2 = value
        for key, value in self.cal_score_verbal_5.items():
            if self.neuralogical_greater_than_5_years_verbal == key:
                sum_3 = value
        for record in self:
            record.neuralogical_greater_than_5_years_glascow = sum_1 + sum_2 + sum_3

        # constrains on vital signs

    @api.onchange('systolic', 'temperature', 'bpm', 'respiratory_rate', 'diastolic')
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

    # calculate bmi
    @api.depends('height', 'weight')
    def _compute_bmi(self):
        for r in self:
            if not r.height:
                return 0
            else:
                r.bmi = r.weight / (r.height * r.height) * 10000
                print(r.bmi)
                return r.bmi

    # Examination tab
    vital_signs_show = fields.Boolean()
    temperature = fields.Float(string="Temperature (c)", readonly=False, states={'Done': [('readonly', False)]})
    systolic = fields.Integer(string="Systolic BP(mmHg)", readonly=False, states={'Done': [('readonly', False)]})
    respiratory_rate = fields.Integer(string="RR (/min)", readonly=True,
                                      states={'Start': [('readonly', False)]})
    at_room_air = fields.Boolean(string="at room air", readonly=False, states={'Done': [('readonly', False)]})
    with_oxygen_support = fields.Boolean(string="with oxygen Support", readonly=False, states={'Done': [('readonly', False)]})
    char_other_oxygen = fields.Char(readonly=False, states={'Done': [('readonly', False)]})
    diastolic = fields.Integer(string="Diastolic BR(mmHg)", readonly=False, states={'Done': [('readonly', False)]})
    bpm = fields.Integer(string="HR (/min)", readonly=False, states={'Done': [('readonly', False)]})

    # Pain Assessment
    pain_present_show = fields.Boolean()
    admission_pain_score = fields.Selection([
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
    admission_scale_used = fields.Selection([
        ('Numerical', 'Numerical'),
        ('Faces', 'Faces'),
        ('FLACC', 'FLACC'),
        ('ABBEY', 'ABBEY'),
    ], readonly=False, states={'Done': [('readonly', False)]})
    # metabolic
    metabolic_show = fields.Boolean()
    weight = fields.Float(string='Weight (kg)', readonly=False, states={'Done': [('readonly', False)]})
    waist_circ = fields.Float(string='Waist Circumference (cm)', readonly=False, states={'Done': [('readonly', False)]})
    bmi = fields.Float(compute=_compute_bmi, string='Body Mass Index (BMI)', store=True)
    height = fields.Float(string='Height (cm)', readonly=False, states={'Done': [('readonly', False)]})
    head_circumference = fields.Float(string='Head Circumference(cm)', help="Head circumference", readonly=False, states={'Done': [('readonly', False)]})

    location_head = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    location_face = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    location_limbs = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    location_chest = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    location_abdomen = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    location_back = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    location_of_pain = fields.Text(readonly=False, states={'Done': [('readonly', False)]})

    Characteristics_dull = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    Characteristics_sharp = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    Characteristics_burning = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    Characteristics_throbbing = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    Characteristics_other = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    Characteristics_patient_own_words = fields.Text(readonly=False, states={'Done': [('readonly', False)]})

    onset_time_sudden = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    onset_time_gradual = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    onset_time_constant = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    onset_time_intermittent = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    onset_time_other = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    onset_time_fdv = fields.Text(readonly=False, states={'Done': [('readonly', False)]})

    provoking_factors_food = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    provoking_factors_rest = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    provoking_factors_movement = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    provoking_factors_palpation = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    provoking_factors_other = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    provoking_factors_patient_words = fields.Text(readonly=False, states={'Done': [('readonly', False)]})

    relieving_factors_rest = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    relieving_factors_medication = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    relieving_factors_heat = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    relieving_factors_distraction = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    relieving_factors_other = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    relieving_factors_patient_words = fields.Text(readonly=False, states={'Done': [('readonly', False)]})

    expressing_pain_verbal = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    expressing_pain_facial = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    expressing_pain_body = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    expressing_pain_other = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    expressing_pain_when_pain = fields.Text(readonly=False, states={'Done': [('readonly', False)]})

    effect_of_pain_nausea = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    effect_of_pain_vomiting = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    effect_of_pain_appetite = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    effect_of_pain_activity = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    effect_of_pain_relationship = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    effect_of_pain_emotions = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    effect_of_pain_concentration = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    effect_of_pain_sleep = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    effect_of_pain_other = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    effect_of_pain_other_text = fields.Text(readonly=False, states={'Done': [('readonly', False)]})

    pain_management_advice_analgesia = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    pain_management_change_of = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    pain_management_refer_physician = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    pain_management_refer_physician_home = fields.Boolean(string="Home Care", readonly=False, states={'Done': [('readonly', False)]})
    pain_management_refer_physician_palliative = fields.Boolean(string="palliative", readonly=False, states={'Done': [('readonly', False)]})
    pain_management_refer_physician_primary = fields.Boolean(string="primary", readonly=False, states={'Done': [('readonly', False)]})
    pain_management_refer_hospital = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    pain_management_other = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    pain_management_other_text = fields.Text(readonly=False, states={'Done': [('readonly', False)]})
    pain_management_comment = fields.Text(readonly=False, states={'Done': [('readonly', False)]})

    # General Condition
    general_condition_show = fields.Boolean()
    general_condition = fields.Text(string='General Condition', readonly=False, states={'Done': [('readonly', False)]})

    # EENT
    EENT_show = fields.Boolean()
    eent_eye = fields.Boolean(default=True, readonly=False, states={'Done': [('readonly', False)]})
    eent_eye_condition = fields.Char(readonly=False, states={'Done': [('readonly', False)]})
    eent_eye_vision = fields.Char(readonly=False, states={'Done': [('readonly', False)]})
    eent_ear = fields.Boolean(default=True, readonly=False, states={'Done': [('readonly', False)]})
    eent_ear_content = fields.Char(readonly=False, states={'Done': [('readonly', False)]})
    eent_nose = fields.Boolean(default=True, readonly=False, states={'Done': [('readonly', False)]})
    eent_nose_content = fields.Char(readonly=False, states={'Done': [('readonly', False)]})
    eent_throut = fields.Boolean(default=True, readonly=False, states={'Done': [('readonly', False)]})
    eent_throut_content = fields.Char(readonly=False, states={'Done': [('readonly', False)]})
    eent_neck = fields.Boolean(default=True, readonly=False, states={'Done': [('readonly', False)]})
    eent_neck_content = fields.Char(readonly=False, states={'Done': [('readonly', False)]})
    eent_remarks = fields.Text(readonly=False, states={'Done': [('readonly', False)]})

    # csv
    csv_show = fields.Boolean()
    cvs_h_sound_1_2 = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    cvs_h_sound_3 = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    cvs_h_sound_4 = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    cvs_h_sound_click = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    cvs_h_sound_murmurs = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    cvs_h_sound_other = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    cvs_h_sound_other_text = fields.Char(readonly=False, states={'Done': [('readonly', False)]})

    cvs_rhythm = fields.Selection([
        ('Regular', 'Regular'),
        ('Irregular', 'Irregular'),
        ('Regular Irregular', 'Regular Irregular'),
        ('Irregular Irregular', 'Irregular Irregular'),
    ], default='Regular', readonly=False, states={'Done': [('readonly', False)]})
    cvs_peripherial_pulse = fields.Selection([
        ('Normal Palpable', 'Normal Palpable'),
        ('Absent Without Pulse', 'Absent Without Pulse'),
        ('Diminished', 'Diminished'),
        ('Bounding', 'Bounding'),
        ('Full and brisk', 'Full and brisk'),
    ], default='Normal Palpable', readonly=False, states={'Done': [('readonly', False)]})

    cvs_edema_yes_no = fields.Selection(yes_no, readonly=False, states={'Done': [('readonly', False)]})
    cvs_edema_yes_type = fields.Selection([
        ('Pitting', 'Pitting'),
        ('Non-Pitting', 'Non-Pitting'),
    ], readonly=False, states={'Done': [('readonly', False)]})
    cvs_edema_yes_location = fields.Text(readonly=False, states={'Done': [('readonly', False)]})
    cvs_edema_yes_grade = fields.Selection([
        ('I- 2mm Depth', 'I- 2mm Depth'),
        ('II- 4mm Depth', 'II- 4mm Depth'),
        ('III- 6mm Depth', 'III- 6mm Depth'),
        ('IV- 8mm Depth', 'IV- 8mm Depth'),
    ], readonly=False, states={'Done': [('readonly', False)]})
    cvs_edema_yes_capillary = fields.Selection([
        ('Less than', 'Less than'),
        ('2-3', '2-3'),
        ('3-4', '3-4'),
        ('4-5', '4-5'),
        ('More than 5', 'More than 5'),
    ], readonly=False, states={'Done': [('readonly', False)]})

    cvs_parenteral_devices_yes_no = fields.Selection(yes_no, readonly=False, states={'Done': [('readonly', False)]})
    cvs_parenteral_devices_yes_sel = fields.Selection([
        ('Central Line', 'Central Line'),
        ('TPN', 'TPN'),
        ('IV Therapy', 'IV Therapy'),
        ('PICC Line', 'PICC Line'),
        ('Other', 'Other'),
    ], readonly=False, states={'Done': [('readonly', False)]})
    cvs_remarks = fields.Text(readonly=False, states={'Done': [('readonly', False)]})
    # Respiratory
    respiratory_show = fields.Boolean()
    lung_sounds_clear = fields.Boolean(default=True, readonly=False, states={'Done': [('readonly', False)]})
    lung_sounds_diminished = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    lung_sounds_absent = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    lung_sounds_fine_crackles = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    lung_sounds_rhonchi = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    lung_sounds_stridor = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    lung_sounds_wheeze = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    lung_sounds_coarse_crackles = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})

    Location_bilateral = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    Location_left_lower = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    Location_left_middle = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    Location_left_upper = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    Location_lower = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    Location_upper = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    Location_right_lower = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    Location_right_middle = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    Location_right_upper = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})

    type_regular = fields.Boolean(default=True, readonly=False, states={'Done': [('readonly', False)]})
    type_irregular = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    type_rapid = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    type_dyspnea = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    type_apnea = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    type_tachypnea = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    type_orthopnea = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    type_accessory_muscles = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    type_snoring_mechanical = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    Cough_yes_no = fields.Selection(yes_no, readonly=False, states={'Done': [('readonly', False)]})
    cough_yes_type = fields.Selection([
        ('Productive', 'Productive'),
        ('none-productive', 'none-productive'),
        ('Spontaneous', 'Spontaneous'),
    ], readonly=False, states={'Done': [('readonly', False)]})
    cough_yes_frequency = fields.Selection([
        ('Spontaneous', 'Spontaneous'),
        ('Occassional', 'Occassional'),
        ('Persistent', 'Persistent'),
    ], readonly=False, states={'Done': [('readonly', False)]})
    cough_yes_amount = fields.Selection([
        ('Scanty', 'Scanty'),
        ('Moderate', 'Moderate'),
        ('Large', 'Large'),
    ], readonly=False, states={'Done': [('readonly', False)]})
    cough_yes_characteristic = fields.Selection([
        ('Clear', 'Clear'),
        ('Yellow', 'Yellow'),
        ('Mucoid', 'Mucoid'),
        ('Mucopurulent', 'Mucopurulent'),
        ('Purulent', 'Purulent'),
        ('Pink Frothy', 'Pink Frothy'),
        ('Blood streaked', 'Blood streaked'),
        ('Bloody', 'Bloody'),
    ], readonly=False, states={'Done': [('readonly', False)]})

    respiratory_support_yes_no = fields.Selection(yes_no, readonly=False, states={'Done': [('readonly', False)]})
    respiratory_support_yes_oxygen = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    respiratory_support_yes_oxygen_text = fields.Text(readonly=False, states={'Done': [('readonly', False)]})
    respiratory_support_yes_trachestory = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    respiratory_support_yes_trachestory_text = fields.Text(readonly=False, states={'Done': [('readonly', False)]})
    respiratory_support_yes_ventilator = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    respiratory_support_yes_ventilator_text = fields.Text(readonly=False, states={'Done': [('readonly', False)]})

    suction_yes_no = fields.Selection(yes_no, readonly=False, states={'Done': [('readonly', False)]})
    suction_yes_type = fields.Selection([
        ('Nasal', 'Nasal'),
        ('Oral', 'Oral'),
        ('Trachestory', 'Trachestory'),
    ], readonly=False, states={'Done': [('readonly', False)]})
    suction_yes_frequency = fields.Integer(readonly=False, states={'Done': [('readonly', False)]})

    nebulization_yes_no = fields.Selection(yes_no, readonly=False, states={'Done': [('readonly', False)]})
    nebulization_yes_frequency = fields.Integer(readonly=False, states={'Done': [('readonly', False)]})
    nebulization_yes_medication = fields.Many2one('oeh.medical.medicines', string='Medicines', readonly=True,
                                                  states={'Start': [('readonly', False)]})
    respiratory_remarks = fields.Text(readonly=False, states={'Done': [('readonly', False)]})

    # Neuralogical

    neuralogical_show = fields.Boolean()
    neuralogical_left_eye = fields.Selection(number_neuralogical, readonly=False, states={'Done': [('readonly', False)]})
    neuralogical_right_eye = fields.Selection(number_neuralogical, readonly=False, states={'Done': [('readonly', False)]})
    neuralogical_pupil_reaction = fields.Selection([
        ('Equal round, reactive', 'Equal round, reactive'),
        ('Equal round, none reactive', 'Equal round, none reactive'),
        ('Miosis', 'Miosis'),
        ('Mydriasis', 'Mydriasis'),
        ('Sluggish', 'Sluggish'),
        ('Brisk', 'Brisk'),
        ('Elliptical', 'Elliptical'),
        ('Anisocoria', 'Anisocoria'),
    ], default='Equal round, reactive', readonly=False, states={'Done': [('readonly', False)]})
    neuralogical_old = fields.Selection([
        ('Greater Than 5 years Old', 'Greater Than 5 years Old'),
        ('2 to 5 Years Old', '2 to 5 Years Old'),
        ('Less than 2 Years Old', 'Less than 2 Years Old'),
    ], readonly=False, states={'Done': [('readonly', False)]})
    neuralogical_greater_than_5_years_mental = fields.Selection([
        ('Alert', 'Alert'),
        ('Disoriented', 'Disoriented'),
        ('Lethargy', 'Lethargy'),
        ('Minimally responsive', 'Minimally responsive'),
        ('No response', 'No response'),
        ('Obtunded', 'Obtunded'),
        ('Orient to person', 'Orient to person'),
        ('Orient to place', 'Orient to place'),
        ('Orient to situation', 'Orient to situation'),
        ('Orient to time', 'Orient to time'),
        ('Stupor', 'Stupor'),
    ], readonly=False, states={'Done': [('readonly', False)]})
    neuralogical_greater_than_5_years_facial = fields.Selection([
        ('Symmetric', 'Symmetric'),
        ('Unequal facial movement', 'Unequal facial movement'),
        ('Drooping left side of face', 'Drooping left side of face'),
        ('Drooping left side of mouth', 'Drooping left side of mouth'),
        ('Drooping right side of face', 'Drooping right side of face'),
        ('Drooping right side of mouth', 'Drooping right side of mouth'),
    ], readonly=False, states={'Done': [('readonly', False)]})
    neuralogical_greater_than_5_years_glascow = fields.Float(compute=_compute_greater_5_old)
    neuralogical_greater_than_5_years_eye = fields.Selection(eye_momement, readonly=False, states={'Done': [('readonly', False)]})
    neuralogical_greater_than_5_years_motor = fields.Selection(motor_response, readonly=False, states={'Done': [('readonly', False)]})
    neuralogical_greater_than_5_years_verbal = fields.Selection([
        ('Orient', 'Orient'),
        ('Confused', 'Confused'),
        ('Inappropriate', 'Inappropriate'),
        ('Incompratensive', 'Incompratensive'),
        ('No verable response', 'No verable response'),
    ], readonly=False, states={'Done': [('readonly', False)]})
    neuralogical_2_to_5_level = fields.Selection(level_consciousness, readonly=False, states={'Done': [('readonly', False)]})
    neuralogical_2_to_5_glascow = fields.Float(compute=_compute_2_5_old)
    neuralogical_2_to_5_eye = fields.Selection(eye_momement, readonly=False, states={'Done': [('readonly', False)]})
    neuralogical_2_to_5_motor = fields.Selection(motor_response, readonly=False, states={'Done': [('readonly', False)]})
    neuralogical_2_to_5_verbal = fields.Selection([
        ('Appropriate Words', 'Appropriate Words'),
        ('Inappropriate Word', 'Inappropriate Word'),
        ('Cries/Screams', 'Cries/Screams'),
        ('Grunts', 'Grunts'),
        ('No response', 'No response'),
    ], readonly=False, states={'Done': [('readonly', False)]})
    neuralogical_less_than_2_level = fields.Selection(level_consciousness, readonly=False, states={'Done': [('readonly', False)]})
    neuralogical_less_than_2_glascow = fields.Float(compute=_compute_less_2)
    neuralogical_less_than_2_eye = fields.Selection(eye_momement, readonly=False, states={'Done': [('readonly', False)]})
    neuralogical_less_than_2_motor = fields.Selection([
        ('Spontaneous movements', 'Spontaneous movements'),
        ('Localizes pain', 'Localizes pain'),
        ('Flexion withdrawal', 'Flexion withdrawal'),
        ('Abnormal flexion', 'Abnormal flexion'),
        ('Abnormal extension', 'Abnormal extension'),
        ('No response', 'No response'),
    ], readonly=False, states={'Done': [('readonly', False)]})
    neuralogical_less_than_2_verbal = fields.Selection([
        ('Coos and smiles appropriate', 'Coos and smiles appropriate'),
        ('Cries', 'Cries'),
        ('Inappropriate crying/screaming', 'Inappropriate crying/screaming'),
        ('Grunts', 'Grunts'),
        ('No response', 'No response'),
    ], readonly=False, states={'Done': [('readonly', False)]})
    neuralogical_remarks = fields.Text(readonly=False, states={'Done': [('readonly', False)]})
    # Gastrointestinal
    gastrointestinal_show = fields.Boolean()
    gastrointestinal_bowel_sound = fields.Selection([
        ('Active', 'Active'),
        ('Absent', 'Absent'),
        ('Hypoactive', 'Hypoactive'),
        ('Hyperactive', 'Hyperactive'),
    ], default='Active', readonly=False, states={'Done': [('readonly', False)]})
    gastrointestinal_abdomen_lax = fields.Boolean(default=True, readonly=False, states={'Done': [('readonly', False)]})
    gastrointestinal_abdomen_soft = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    gastrointestinal_abdomen_firm = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    gastrointestinal_abdomen_distended = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    gastrointestinal_abdomen_tender = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    gastrointestinal_stool_color = fields.Selection([
        ('Brown', 'Brown'),
        ('Yellow', 'Yellow'),
        ('Black', 'Black'),
        ('Bright Red', 'Bright Red'),
        ('Dark Red', 'Dark Red'),
        ('Clay', 'Clay'),
    ], default='Brown', readonly=False, states={'Done': [('readonly', False)]})
    gastrointestinal_stool_loose = fields.Boolean(default=True, readonly=False, states={'Done': [('readonly', False)]})
    gastrointestinal_stool_hard = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    gastrointestinal_stool_mucoid = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    gastrointestinal_stool_soft = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    gastrointestinal_stool_tarry = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    gastrointestinal_stool_formed = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    gastrointestinal_stool_semi_formed = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    gastrointestinal_stool_bloody = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    gastrointestinal_stoma_none = fields.Boolean(default=True, readonly=False, states={'Done': [('readonly', False)]})
    gastrointestinal_stoma_colostory = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    gastrointestinal_stoma_ileostomy = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    gastrointestinal_stoma_peg = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    gastrointestinal_stoma_pej = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    gastrointestinal_stoma_urostomy = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    gastrointestinal_problem_none = fields.Boolean(default=True, readonly=False, states={'Done': [('readonly', False)]})
    gastrointestinal_problem_nausea = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    gastrointestinal_problem_vomiting = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    gastrointestinal_problem_colic = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    gastrointestinal_problem_diarrhea = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    gastrointestinal_problem_constipation = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    gastrointestinal_problem_dysphagia = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    gastrointestinal_problem_hemorrhoids = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    gastrointestinal_problem_anal_fissure = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    gastrointestinal_problem_anal_fistula = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    gastrointestinal_problem_other = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    gastrointestinal_problem_other_text = fields.Text(readonly=False, states={'Done': [('readonly', False)]})
    gastrointestinal_bowel_movement_none = fields.Boolean(default=True, readonly=False, states={'Done': [('readonly', False)]})
    gastrointestinal_bowel_movement_laxative = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    gastrointestinal_bowel_movement_enema = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    gastrointestinal_bowel_movement_stoma = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    gastrointestinal_bowel_movement_stool_softener = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    gastrointestinal_bowel_movement_suppository = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    gastrointestinal_bowel_movement_digital = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    gastrointestinal_bowel_movement_other = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    gastrointestinal_bowel_movement_other_text = fields.Text(readonly=False, states={'Done': [('readonly', False)]})
    gastrointestinal_enteral_device_none = fields.Boolean(default=True, readonly=False, states={'Done': [('readonly', False)]})
    gastrointestinal_enteral_device_nasogastric_tube = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    gastrointestinal_enteral_device_orogastric_tube = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    gastrointestinal_enteral_device_gastro_jejunal = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    gastrointestinal_enteral_device_peg = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    gastrointestinal_enteral_device_pej = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    gastrointestinal_enteral_device_pd = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    gastrointestinal_enteral_device_other = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    gastrointestinal_enteral_device_other_text = fields.Text(readonly=False, states={'Done': [('readonly', False)]})
    gastrointestinal_remarks = fields.Text(readonly=False, states={'Done': [('readonly', False)]})

    # Genitourinary
    genitourinary_show = fields.Boolean()
    genitourinary_urine_color = fields.Selection([
        ('Pale Yellow', 'Pale Yellow'),
        ('Dark Yellow', 'Dark Yellow'),
        ('Yellow', 'Yellow'),
        ('Tea-Colored', 'Tea-Colored'),
        ('Red', 'Red'),
        ('Blood Tinged', 'Blood Tinged'),
        ('Green', 'Green'),
    ], default='Pale Yellow', readonly=False, states={'Done': [('readonly', False)]})
    genitourinary_urine_appearance = fields.Selection([
        ('Clear', 'Clear'),
        ('Cloudy', 'Cloudy'),
        ('With Sediment', 'With Sediment'),
    ], default='Clear', readonly=False, states={'Done': [('readonly', False)]})
    genitourinary_urine_amount = fields.Selection([
        ('Adequate', 'Adequate'),
        ('Scanty', 'Scanty'),
        ('Large', 'Large'),
    ], default='Adequate', readonly=False, states={'Done': [('readonly', False)]})
    genitourinary_urination_none = fields.Boolean(default=True, readonly=False, states={'Done': [('readonly', False)]})
    genitourinary_urination_dysuria = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    genitourinary_urination_frequency = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    genitourinary_urination_urgency = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    genitourinary_urination_hesitancy = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    genitourinary_urination_incontinence = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    genitourinary_urination_inability_to_void = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    genitourinary_urination_nocturia = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    genitourinary_urination_retention = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    genitourinary_urination_suprapubic_pain = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    genitourinary_urination_loin_pain = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    genitourinary_urination_colicky_pain = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    genitourinary_urination_difficult_control = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    genitourinary_urination_other = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    genitourinary_urination_other_text = fields.Text(readonly=False, states={'Done': [('readonly', False)]})
    genitourinary_urination_assistance = fields.Selection([
        ('None', 'None'),
        ('Indwelling Catheter', 'Indwelling Catheter'),
        ('Condom Catheter', 'Condom Catheter'),
        ('Intermittent bladder Wash', 'Intermittent bladder Wash'),
        ('Urostomy', 'Urostomy'),
        ('Suprapubic Catheter', 'Suprapubic Catheter'),
    ], default='None', readonly=False, states={'Done': [('readonly', False)]})
    genitourinary_remarks = fields.Text(readonly=False, states={'Done': [('readonly', False)]})
    # Integumentary
    integumentary_show = fields.Boolean()
    appearance_normal = fields.Boolean(string='Normal', default=True, readonly=False, states={'Done': [('readonly', False)]})
    appearance_dry = fields.Boolean(string='Dry', readonly=False, states={'Done': [('readonly', False)]})
    appearance_edema = fields.Boolean(string='Edema', readonly=False, states={'Done': [('readonly', False)]})
    appearance_flushed = fields.Boolean(string='Flushed', readonly=False, states={'Done': [('readonly', False)]})
    appearance_pale = fields.Boolean(string='clay', readonly=False, states={'Done': [('readonly', False)]})
    appearance_rash = fields.Boolean(string='Rash', readonly=False, states={'Done': [('readonly', False)]})
    appearance_jundiced = fields.Boolean(string='Jandiced', readonly=False, states={'Done': [('readonly', False)]})
    appearance_eczema = fields.Boolean(string='Eczema', readonly=False, states={'Done': [('readonly', False)]})
    appearance_hemayome = fields.Boolean(string='Hemayome', readonly=False, states={'Done': [('readonly', False)]})
    appearance_rusty = fields.Boolean(string='Rusty', readonly=False, states={'Done': [('readonly', False)]})
    appearance_cyanotic = fields.Boolean(string='Cyanotic', readonly=False, states={'Done': [('readonly', False)]})
    appearance_bruises = fields.Boolean(string='Bruises', readonly=False, states={'Done': [('readonly', False)]})
    appearance_abrasion = fields.Boolean(string='Abrasion', readonly=False, states={'Done': [('readonly', False)]})
    appearance_sores = fields.Boolean(string='Sores', readonly=False, states={'Done': [('readonly', False)]})
    integumentary_turgor = fields.Selection([
        ('Elastic', 'Elastic'),
        ('Normal for age', 'Normal for age'),
        ('Poor', 'Poor'),
    ], default='Elastic', readonly=False, states={'Done': [('readonly', False)]})
    integumentary_temperature = fields.Selection([
        ('Normal', 'Normal'),
        ('Cool', 'Cool'),
        ('Cold', 'Cold'),
        ('Warm', 'Warm'),
        ('Hot', 'Hot'),
    ], default='Normal', readonly=False, states={'Done': [('readonly', False)]})
    integumentary_remarks = fields.Text(readonly=False, states={'Done': [('readonly', False)]})

    # Infections
    infection_show = fields.Boolean()
    infection_nad = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    infection_content = fields.Char(readonly=False, states={'Done': [('readonly', False)]})

    # psychological
    psychological_show = fields.Boolean()
    psychological_nad = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    psychological_content = fields.Char(readonly=False, states={'Done': [('readonly', False)]})
    # reproductive
    reproductive_show = fields.Boolean()
    reproductive_nad = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    reproductive_content = fields.Char(readonly=False, states={'Done': [('readonly', False)]})
    # musculoskeletal
    musculoskeletal_show = fields.Boolean()
    musculoskeletal_left_upper_extremity = fields.Selection(musculoskeletal_extremity,
                                                            default='Active Against Gravity and Resistance',
                                                            readonly=False, states={'Done': [('readonly', False)]})
    musculoskeletal_right_upper_extremity = fields.Selection(musculoskeletal_extremity,
                                                             default='Active Against Gravity and Resistance',
                                                             readonly=False, states={'Done': [('readonly', False)]})
    musculoskeletal_left_lower_extremity = fields.Selection(musculoskeletal_extremity,
                                                            default='Active Against Gravity and Resistance',
                                                            readonly=False, states={'Done': [('readonly', False)]})
    musculoskeletal_right_lower_extremity = fields.Selection(musculoskeletal_extremity,
                                                             default='Active Against Gravity and Resistance',
                                                             readonly=False, states={'Done': [('readonly', False)]})
    musculoskeletal_gait = fields.Selection([
        ('Normal', 'Normal'),
        ('Asymmetrical', 'Asymmetrical'),
        ('Dragging', 'Dragging'),
        ('Impaired', 'Impaired'),
        ('Jerky', 'Jerky'),
        ('Shuffling', 'Shuffling'),
        ('Spastic', 'Spastic'),
        ('Steady', 'Steady'),
        ('Unsteady', 'Unsteady'),
        ('Wide Based', 'Wide Based'),
        ('Other', 'Other'),
    ], default='Normal', readonly=False, states={'Done': [('readonly', False)]})
    musculoskeletal_remarks = fields.Text(readonly=False, states={'Done': [('readonly', False)]})

    # sensory
    sensory_show = fields.Boolean()
    sensory_nad = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    sensory_content = fields.Char(readonly=False, states={'Done': [('readonly', False)]})
    consent_show = fields.Boolean()
    consent_file1 = fields.Binary()
    consent_file2 = fields.Binary()

    @api.onchange('specify', 'effect_of_pain_other_text', 'pain_management_other_text',
                  'pain_management_refer_physician_home', 'pain_management_refer_physician_palliative',
                  'pain_management_refer_physician_primary')
    def _check(self):
        # if self.pain_assessment_elicited_form == 'Other':
        #     self.specify = ''
        if self.effect_of_pain_other:
            self.effect_of_pain_other_text = ''
        if self.pain_management_other:
            self.pain_management_other_text = ''
        if self.pain_management_refer_physician == 'False':
            self.pain_management_refer_physician_home = ''
        if self.pain_management_refer_physician == 'False':
            self.pain_management_refer_physician_palliative = ''
        if self.pain_management_refer_physician == 'False':
            self.pain_management_refer_physician_primary = ''

    @api.onchange('weight', 'waist_circ', 'height', 'head_circumference')
    def _check_metabolic(self):
        if self.weight > 1000:
            raise ValidationError("invalid weight value")
        if self.height > 1000:
            raise ValidationError("invalid height value")
        if self.waist_circ > 1000:
            raise ValidationError("invalid Waist Circumference value")
        if self.head_circumference > 100:
            raise ValidationError("invalid head circumference value")


class ShifaInvestigationInherit(models.Model):
    _inherit = 'sm.shifa.investigation'

    physician_followup = fields.Many2one('sm.physician.admission.followup', string='physician', ondelete='cascade')


class ShifaLabTestInherit(models.Model):
    _inherit = 'sm.shifa.lab.request'

    physician_followup = fields.Many2one('sm.physician.admission.followup', string='physician',
                                         ondelete='cascade')


class ShifaImageTestInherit(models.Model):
    _inherit = 'sm.shifa.imaging.request'

    physician_followup = fields.Many2one('sm.physician.admission.followup', string='physician',
                                         ondelete='cascade')


class ShifaPhysicianDiagnosisTab(models.Model):
    _inherit = 'sm.physician.admission.followup'

    # diagnosis tab
    provisional_diagnosis = fields.Many2one('oeh.medical.pathology', string='Disease', readonly=False, states={'Done': [('readonly', False)]})
    provisional_diagnosis_add_other = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    provisional_diagnosis_add = fields.Many2one('oeh.medical.pathology', string='Disease', readonly=False, states={'Done': [('readonly', False)]})

    differential_diagnosis = fields.Many2one('oeh.medical.pathology', string='Disease', readonly=False, states={'Done': [('readonly', False)]})

    differential_diagnosis_add = fields.Many2one('oeh.medical.pathology', string='Disease', readonly=False, states={'Done': [('readonly', False)]})
    differential_diagnosis_add_other = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})


class ShifaPhysicianMedicalCareTab(models.Model):
    _inherit = 'sm.physician.admission.followup'
    # medical care plan tab
    medical_care_plan = fields.Text(string='Medical Care Plan', readonly=False, states={'Done': [('readonly', False)]})
    program_chronic_anticoagulation = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    program_general_nursing_care = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    program_wound_care = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    program_palliative_care = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    program_acute_anticoagulation = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    program_home_infusion = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    program_other = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    program_other_text = fields.Text(readonly=False, states={'Done': [('readonly', False)]})
    services_provided_oxygen_dependent = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    services_provided_tracheostomy = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    services_provided_wound_care = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    services_provided_pain_management = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    services_provided_hydration_therapy = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    services_provided_o2_via_nasal_cannula = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    services_provided_hypodermoclysis = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    services_provided_tpn = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    services_provided_stoma_care = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    services_provided_peg_tube = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    services_provided_inr_monitoring = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    services_provided_prevention_pressure = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    services_provided_vac_therapy = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    services_provided_drain_tube = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    services_provided_medication_management = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    services_provided_warfarin_stabilization = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    services_provided_parenteral_antimicrobial = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    services_provided_indwelling_foley_catheter = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    services_provided_ngt = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    services_provided_other = fields.Boolean(readonly=False, states={'Done': [('readonly', False)]})
    services_provided_other_text = fields.Text(readonly=False, states={'Done': [('readonly', False)]})
    patient_condition = fields.Selection([
        ('Declined', 'Declined'),
        ('Unstable', 'Unstable'),
        ('Unchanged', 'Unchanged'),
        ('Improved', 'Improved'),
        ('Stable', 'Stable'),
    ], readonly=False, states={'Done': [('readonly', False)]})
    prognosis = fields.Selection([
        ('Poor', 'Poor'),
        ('Guarded', 'Guarded'),
        ('Fair', 'Fair'),
        ('Good', 'Good'),
        ('Excellent', 'Excellent'),
    ], readonly=False, states={'Done': [('readonly', False)]})
    potential_risk = fields.Text(readonly=False, states={'Done': [('readonly', False)]})
    admission_goal = fields.Text(readonly=False, states={'Done': [('readonly', False)]})
    final_plan = fields.Text(readonly=False, states={'Done': [('readonly', False)]})


class ShifaPrescriptionInherit(models.Model):
    _inherit = 'oeh.medical.prescription'

    physician_followup = fields.Many2one('sm.physician.admission.followup', string='physician Follow up',
                                         ondelete='cascade')


class ShifaLabRequestTestPhyAdmFu(models.Model):
    _inherit = 'sm.shifa.lab.request.line'

    phy_adm_fu = fields.Many2one("sm.physician.admission.followup", string='phy_adm')


class ShifaImagingRequestTestPhyAdmFu(models.Model):
    _inherit = 'sm.shifa.imaging.request.line'

    phy_adm_fu = fields.Many2one("sm.physician.admission.followup", string='phy_adm')
