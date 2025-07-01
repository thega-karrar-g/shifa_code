from odoo import models, fields, api, _
import datetime
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError, ValidationError
from datetime import date
from psycopg2._psycopg import List


class PhysicianAssessment(models.Model):
    _name = 'sm.shifa.physician.assessment'
    _description = 'Physician Assessment'
    _rec_name = 'assessment_physician_code'

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
    type_visit = [
        ('main_visit', 'Comprehensive Visit'),
        ('follow_up', 'Follow Up'),
    ]
    draft = {'Draft': [('readonly', False)]}
    start = {'Start': [('readonly', False)]}
    draft_start = {'Draft': [('readonly', False)], 'Start': [('readonly', False)]}
    complete = {
        'Draft': [('readonly', True)],
        'Admitted': [('readonly', True)],
        'Discharged': [('readonly', True)]
    }

    def set_to_start(self):
        return self.write({'state': 'Start'})

        #     Clinical Documentation Completed

    def set_to_draft(self):
        return self.write({'state': 'Draft'})

    def set_to_admitted(self):
        for rec in self:
            if not rec.pres_phA_line:
                pass
            else:
                pres_obj = rec.env['oeh.medical.prescription'].create({
                    'patient': rec.patient.id,
                    'doctor': rec.doctor.id,
                    'phy_assessment': rec.id,
                    'provisional_diagnosis': rec.provisional_diagnosis.id,
                    'provisional_diagnosis_add_other': rec.provisional_diagnosis_add_other,
                    'provisional_diagnosis_add': rec.provisional_diagnosis_add.id,
                    'provisional_diagnosis_add_other2': rec.provisional_diagnosis_add_other2,
                    'provisional_diagnosis_add2': rec.provisional_diagnosis_add2.id,
                    'provisional_diagnosis_add_other3': rec.provisional_diagnosis_add_other3,
                    'provisional_diagnosis_add3': rec.provisional_diagnosis_add3.id,
                    'allergies_show': rec.allergies_show,
                    'has_drug_allergy': rec.has_drug_allergy,
                    'drug_allergy': rec.drug_allergy,
                    'drug_allergy_content': rec.drug_allergy_content,
                    'has_food_allergy': rec.has_food_allergy,
                    'food_allergy': rec.food_allergy,
                    'food_allergy_content': rec.food_allergy_content,
                    'has_other_allergy': rec.has_other_allergy,
                    'other_allergy': rec.other_allergy,
                    'other_allergy_content': rec.other_allergy_content,
                    'prescription_line': rec.pres_phA_line,
                })
                rec.prescription_id = pres_obj.id
            if not rec.lab_request_test_line:
                pass
            else:
                # print("Lab")
                lab_req = rec.env['sm.shifa.lab.request'].create({
                    'patient': rec.patient.id,
                    'doctor': rec.doctor.id,
                    'hhc_appointment': rec.hhc_appointment.id,
                    'lab_request_ids': rec.lab_request_test_line,
                })
                rec.lab_req_id = lab_req.id

            if not rec.image_request_test_ids:
                pass
            else:
                # print("Image")
                image_req = rec.env['sm.shifa.imaging.request'].create({
                    'patient': rec.patient.id,
                    'doctor': rec.doctor.id,
                    'hhc_appointment': rec.hhc_appointment.id,
                    'image_req_test_ids': rec.image_request_test_ids,
                })
                rec.image_req_id = image_req.id
        rec.create_report()
        if self.visit_type == 'main_visit':
            return self.write({'state': 'Admitted', 'admission_date': datetime.datetime.now()})
        else:
            return self.write({'state': 'Done', 'followup_date': datetime.datetime.now()})

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
    # download prescription pdf
    def download_pdf(self):
        for rec in self:
            if not rec.pres_phA_line:
                raise ValidationError(_("No Prescription to print"))
            else:
                return self.env.ref('smartmind_shifa.sm_shifa_report_patient_prescriptions').report_action(rec.prescription_id.id)
    # download report
    def report_pdf(self):
        for rec in self:
            if not rec.move_id:
                raise ValidationError(_("No Report to print first click on create report"))
            else:
                return self.env.ref('smartmind_shifa_more.sm_medical_report').report_action(rec.move_id)

    # download lab request pdf
    def lab_request_pdf(self):
        for rec in self:
            if not rec.lab_req_id:
                raise ValidationError(_("No Lab request to print"))
            else:
                return self.env.ref('smartmind_shifa.sm_shifa_report_lab_request_action').report_action(rec.lab_req_id)
    # download imaging request pdf
    def image_request_pdf(self):
        for rec in self:
            if not rec.image_req_id:
                raise ValidationError(_("No image request to print"))
            else:
                return self.env.ref('smartmind_shifa.sm_shifa_report_imaging_request_action').report_action(rec.image_req_id)

    def download_pdf_followup(self):
        self.write({'state': 'Done'})
        for rec in self:
            if not rec.pres_phA_line:
                raise ValidationError(_("No Prescription to print"))
            else:
                therapist_obj = self.env['oeh.medical.prescription']
                domain = [('phy_assessment', '=', self.id)]
                pres_id = therapist_obj.search(domain)
                return self.env.ref('smartmind_shifa.sm_shifa_report_patient_prescriptions').report_action(pres_id)

    @api.model
    def create(self, vals):

        # save sequence depends on selection type
        if vals['visit_type'] == 'main_visit':
            sequence_main = self.env['ir.sequence'].next_by_code('sm.shifa.physician.assessment.main')
            vals['assessment_physician_code'] = sequence_main
        elif vals['visit_type'] == 'follow_up':
            sequence_followup = self.env['ir.sequence'].next_by_code('sm.shifa.physician.assessment.followup')
            vals['assessment_physician_code'] = sequence_followup
        else:
            vals['assessment_physician_code'] = ""

        return super(PhysicianAssessment, self).create(vals)

    @api.depends('height', 'weight')
    def _compute_bmi(self):
        for r in self:
            if not r.height:
                return 0
            else:
                r.bmi = r.weight / (r.height * r.height) * 10000
                print(r.bmi)
                return r.bmi

    def create_report(self):
        report_obj = self.env["sm.medical.report"]
        for rec in self:
            o2_sat = ''
            if rec.at_room_air:
                o2_sat = 'at room air'
            if rec.with_oxygen_support:
                o2_sat = 'with oxygen Support'
            report = report_obj.sudo().create({
                'name': rec.assessment_physician_code,
                'patient': rec.patient.id,
                'date': datetime.datetime.now(),
                'language': 'English',
                'report': 'Physician_home_visit',
                'patient_weight': rec.weight,
                'doctor': rec.doctor.id,
                'chief_complaint': rec.chief_complaint,
                'systolic_bp': rec.systolic,
                'hr_min': rec.bpm,
                'diastolic_br': rec.diastolic,
                'rr_min': rec.respiratory_rate,
                'temperature_c': rec.temperature,
                'o2_sat': o2_sat,
                'plan_care': rec.medical_care_plan,
                'history_illness': rec.history_present_illness,
                'char_other_oxygen': rec.char_other_oxygen,
                'provisional_diagnosis': rec.provisional_diagnosis.id,
                'provisional_diagnosis_add': rec.provisional_diagnosis_add.id,
                'provisional_diagnosis_add_other': rec.provisional_diagnosis_add_other,
                'provisional_diagnosis_add_other2': rec.provisional_diagnosis_add_other2,
                'provisional_diagnosis_add2': rec.provisional_diagnosis_add2.id,
                'provisional_diagnosis_add_other3': rec.provisional_diagnosis_add_other3,
                'provisional_diagnosis_add3': rec.provisional_diagnosis_add3.id,
                'provisional_diagnosis_add_other4': rec.provisional_diagnosis_add_other4,
                'provisional_diagnosis_add4': rec.provisional_diagnosis_add4.id,
                'provisional_diagnosis_add_other5': rec.provisional_diagnosis_add_other5,
                'provisional_diagnosis_add5': rec.provisional_diagnosis_add5.id,
                'provisional_diagnosis_add_other6': rec.provisional_diagnosis_add_other6,
                'provisional_diagnosis_add6': rec.provisional_diagnosis_add6.id,
                'provisional_diagnosis_add_other7': rec.provisional_diagnosis_add_other7,
                'provisional_diagnosis_add7': rec.provisional_diagnosis_add7.id,
                'provisional_diagnosis_add_other8': rec.provisional_diagnosis_add_other8,
                'provisional_diagnosis_add8': rec.provisional_diagnosis_add8.id,
                'provisional_diagnosis_add_other9': rec.provisional_diagnosis_add_other9,
                'provisional_diagnosis_add9': rec.provisional_diagnosis_add9.id,
            })
        self.write(
            {'move_id': report.id})
    def open_lab_request_view(self):
        action = self.env['ir.actions.act_window']._for_xml_id('smartmind_shifa.sm_shifa_lab_request_action')
        action['domain'] = [('id', '=', self.lab_req_id.id)]
        return action
    def open_image_request_view(self):
        action = self.env['ir.actions.act_window']._for_xml_id('smartmind_shifa.sm_shifa_imaging_request_action')
        action['domain'] = [('id', '=', self.image_req_id.id)]
        return action
    def open_report_view(self):
        action = self.env['ir.actions.act_window']._for_xml_id('smartmind_shifa_more.sm_medical_report_action_tree')
        action['domain'] = [('id', '=', self.move_id.id)]
        return action


    # Get active medication profile for patient
    @api.onchange('patient')
    def onchange_patient_med_pro(self):
        self.med_pro_id = [(5, 0, 0)]
        if self.patient.med_pro_id:
            lines = self.patient.med_pro_id.filtered(lambda l: l.state_app == 'active')
            if lines:
                self.med_pro_id = [(6, 0, lines.ids)]


    assessment_physician_code = fields.Char('Reference', index=True, copy=False)
    state = fields.Selection(ADMISSION_STATES, string='State', default=lambda *a: 'Draft', readonly=True)
    patient = fields.Many2one('oeh.medical.patient', string='Patient', help="Patient Name", required=True,
                              readonly=True, states=draft)
    patient_weight = fields.Float(string='Weight', related='patient.weight', readonly=True, states=draft)
    age = fields.Char(string='Age', related='patient.age', readonly=True, states=draft)
    marital_status = fields.Selection(string='Marital Status', related='patient.marital_status', readonly=True,
                                      states=draft)
    sex = fields.Selection(string='Sex', related='patient.sex', readonly=True, states=draft)
    blood_type = fields.Selection(string='Blood Type', related='patient.blood_type', readonly=True, states=draft)
    rh = fields.Selection(string='Rh', related='patient.rh', readonly=True, states=draft)
    doctor = fields.Many2one('oeh.medical.physician', string='Doctor', help="Current primary care / family doctor",
                             readonly=True, states=draft,
                             domain=[('role_type', '=', ['HVD', 'HHCD', 'HD']),('active', '=', True)], required=True,
                             default=_get_comprehensive)

    hhc_appointment = fields.Many2one('sm.shifa.hhc.appointment', string='HHC-Appointment',
                                      readonly=True, states=draft, domain="[('patient', '=', patient)]")
    visit_type = fields.Selection(type_visit, required=True, readonly=True, states={'Draft': [('readonly', False)], 'Start': [('readonly', False)]})
    phy_adm = fields.Many2one('sm.shifa.physician.admission', readonly=True, states=draft,
                              domain="[('patient', '=', patient), ('state', 'in', ('Admitted', 'Start','Draft'))]")
    # ,('state','in',['Draft','Start','Admitted'])
    pha_id = fields.Many2one('sm.shifa.physician.assessment', string='PhA', readonly=True, states=draft_start,
                             domain="[('patient', '=', patient), ('visit_type', '=', 'main_visit'), ('state', '=', 'Admitted')]")
    phy_followup_ids = fields.One2many("sm.shifa.physician.assessment", 'pha_id', readonly=False, states=complete)
    # medication_pro_id = fields.One2many('sm.shifa.medication.profile', 'physician_assessment',
    #                                     string='Medication Profile')

    med_pro_id = fields.Many2many('sm.shifa.medication.profile', string='Medication Profile')

    admission_date = fields.Datetime(string='Admission Date')
    discharge_date = fields.Datetime(string='Discharge Date')
    followup_date = fields.Datetime(string='Follow up Date')
    service_name = fields.Selection(SERVICES, readonly=True, states=draft, default='G')
    service = fields.Many2one('sm.shifa.service', string='First Service', required=True,
                              domain=[('show', '=', True), ('service_type', 'in',
                                                            ['HHC', 'FUPH', 'L', 'WBSDFC', 'R', 'LP', 'GCP', 'MH',
                                                             'IVT', 'SM', 'V', 'Car',
                                                             'Diab', 'HVD'])],
                              readonly=True, states=draft)

    service_type = fields.Selection(string='Service type', related='service.service_type', readonly=True, store=False)

    service_2 = fields.Many2one('sm.shifa.service', string='Second Service',
                                domain=[('show', '=', True), ('service_type', 'in',
                                                              ['HHC', 'FUPH', 'L', 'WBSDFC', 'R', 'LP', 'GCP', 'MH',
                                                               'IVT', 'SM', 'V', 'Car',
                                                               'PHY', 'Diab', 'HVD'])],
                                readonly=True, states=draft)

    service_3 = fields.Many2one('sm.shifa.service', string='Third Service',
                                domain=[('show', '=', True), ('service_type', 'in',
                                                              ['HHC', 'FUPH', 'L', 'WBSDFC', 'R', 'LP', 'GCP', 'MH',
                                                               'IVT', 'SM', 'V', 'Car',
                                                               'PHY', 'Diab', 'HVD'])],
                                readonly=True, states=draft)
    consent_show = fields.Boolean()
    consent_file1 = fields.Binary(readonly=False, states=complete)
    consent_file2 = fields.Binary(readonly=False, states=complete)
    chief_complaint_show = fields.Boolean()
    chief_complaint = fields.Char(string="Chief Complaint", readonly=True,
                                  states=draft_start)
    vital_signs_show = fields.Boolean()
    temperature = fields.Float(string="Temperature (c)", readonly=True, states=start)
    systolic = fields.Integer(string="Systolic BP(mmHg)", readonly=True, states=start)
    respiratory_rate = fields.Integer(string="RR (/min)", readonly=True,
                                      states=start)
    at_room_air = fields.Boolean(string="at room air", readonly=True, states=start)
    with_oxygen_support = fields.Boolean(string="with oxygen Support", readonly=True,
                                         states=start)
    char_other_oxygen = fields.Char(readonly=True, states=start)
    diastolic = fields.Integer(string="Diastolic BR(mmHg)", readonly=True,
                               states=start)
    bpm = fields.Integer(string="HR (/min)", readonly=True, states=start)

    # metabolic
    metabolic_show = fields.Boolean()
    weight = fields.Float(string='Weight (kg)', readonly=True, states=start)
    waist_circ = fields.Float(string='Waist Circumference (cm)', readonly=True, states=start)
    bmi = fields.Float(compute=_compute_bmi, string='Body Mass Index (BMI)', store=True)
    height = fields.Float(string='Height (cm)', readonly=True, states=start)
    head_circumference = fields.Float(string='Head Circumference(cm)', help="Head circumference", readonly=True,
                                      states=start)

    lab_request_test_line = fields.One2many('sm.shifa.lab.request.line', 'phy_ass', string='Lab Request',
                                            readonly=False, states=complete)
    image_request_test_ids = fields.One2many('sm.shifa.imaging.request.line', 'phy_ass', string='Image Request',
                                             readonly=False, states=complete)

    # relate prescription to physician
    prescription_ids = fields.One2many('oeh.medical.prescription', 'physician_assessment')
    prescription_id = fields.Many2one('oeh.medical.prescription')

    # relate prescription to investigation
    investigation_ids = fields.One2many('sm.shifa.investigation', 'physician_assessment', string='Investigation',
                                        readonly=False, states=complete)

    followup_ids = fields.One2many('sm.physician.admission.followup', 'physician_assessment', string='Follow Up',
                                   readonly=False, states=complete)
    referral_ids = fields.One2many('sm.shifa.referral', 'physician_assessment', readonly=False, states=complete)
    nurse_assessment_line = fields.One2many('sm.shifa.nurse.assessment', 'phy_asse', readonly=False, states=complete)

    move_id = fields.Many2one('sm.medical.report', string='Report #', readonly=True)
    lab_req_id = fields.Many2one('sm.shifa.lab.request', string='lab req #', readonly=True)
    image_req_id = fields.Many2one('sm.shifa.imaging.request', string='image req #', readonly=True)

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


class PhysicianPatientFamilyHealthEducation(models.Model):
    _inherit = "sm.shifa.physician.assessment"
    draft_start = {'Draft': [('readonly', False)], 'Start': [('readonly', False)]}
    # education needs assessment
    personal_hygiene = fields.Boolean(string="Personal Hygiene", readonly=True, states=draft_start)
    pain_management = fields.Boolean(string="Pain Management", readonly=True, states=draft_start)
    activity_exercise = fields.Boolean(string="Activity/Exercise", readonly=True, states=draft_start)
    disease_process = fields.Boolean(string="Disease Process", readonly=True, states=draft_start)
    use_medical_equipment = fields.Boolean(string="Use of Medical Equipment", readonly=True, states=draft_start)
    nutrition = fields.Boolean(string="Nutrition", readonly=True, states=draft_start)
    wound_care = fields.Boolean(string="Wound care and Dressing", readonly=True, states=draft_start)
    diagnostic = fields.Boolean(string="Diagnostic Test/Procedure", readonly=True, states=draft_start)
    medication = fields.Boolean(string="Medication", readonly=True, states=draft_start)
    post_op = fields.Boolean(string="Post Op Care", readonly=True, states=draft_start)
    social_service = fields.Boolean(string="Social Service", readonly=True, states=draft_start)
    home_safety = fields.Boolean(string="Home Safety", readonly=True, states=draft_start)
    informed_consent = fields.Boolean(string="Informed Consent", readonly=True, states=draft_start)
    rights_responsibilities = fields.Boolean(string="Rights & Responsibilities", readonly=True, states=draft_start)
    infection_control = fields.Boolean(string="Infection Control", readonly=True, states=draft_start)
    discharge_transfer = fields.Boolean(string="Discharge/Transfer Instruction", readonly=True, states=draft_start)
    emergency_responds = fields.Boolean(
        string="Emergeny responds for life threatening situations and when to call 997/911", readonly=True,
        states=draft_start)
    physiotherapy_exercise = fields.Boolean(string="Physiotherapy Exercise", readonly=True, states=draft_start)
    eduction_other = fields.Boolean(string="other", readonly=True, states=draft_start)
    eduction_other_text = fields.Char(string="other", readonly=True, states=draft_start)

    #     Learning Barriers
    no_learn_barriers = fields.Boolean(readonly=True, states=draft_start)
    impaired_hearing = fields.Boolean(readonly=True, states=draft_start)
    speech_barrier = fields.Boolean(readonly=True, states=draft_start)
    emotional_barrier = fields.Boolean(readonly=True, states=draft_start)
    language_barrier = fields.Boolean(readonly=True, states=draft_start)
    educational_barrier = fields.Boolean(readonly=True, states=draft_start)
    motivation_learn = fields.Boolean(readonly=True, states=draft_start)
    impaired_thought = fields.Boolean(readonly=True, states=draft_start)
    financial_difficulties = fields.Boolean(readonly=True, states=draft_start)
    impaired_vision = fields.Boolean(readonly=True, states=draft_start)
    cultural_beliefs = fields.Boolean(readonly=True, states=draft_start)
    religious_practice = fields.Boolean(readonly=True, states=draft_start)
    learning_other = fields.Boolean(readonly=True, states=draft_start)
    learning_other_text = fields.Char(readonly=True, states=draft_start)

    #     person Taught
    taught_patient = fields.Boolean(readonly=True, states=draft_start)
    son = fields.Boolean(readonly=True, states=draft_start)
    daughter = fields.Boolean(readonly=True, states=draft_start)
    relatives = fields.Boolean(readonly=True, states=draft_start)
    caregiver = fields.Boolean(readonly=True, states=draft_start)
    father = fields.Boolean(readonly=True, states=draft_start)
    private_nurse = fields.Boolean(readonly=True, states=draft_start)
    mother = fields.Boolean(readonly=True, states=draft_start)
    wife = fields.Boolean(readonly=True, states=draft_start)
    taught_other = fields.Boolean(readonly=True, states=draft_start)
    taught_other_text = fields.Char(readonly=True, states=draft_start)

    #  Teaching Tools
    audio = fields.Boolean(readonly=True, states=draft_start)
    return_demo = fields.Boolean(readonly=True, states=draft_start)
    demo = fields.Boolean(readonly=True, states=draft_start)
    video = fields.Boolean(readonly=True, states=draft_start)
    printed_materials = fields.Boolean(readonly=True, states=draft_start)
    verbal = fields.Boolean(readonly=True, states=draft_start)
    role_play = fields.Boolean(readonly=True, states=draft_start)
    tool_other = fields.Boolean(readonly=True, states=draft_start)
    tool_other_text = fields.Char(readonly=True, states=draft_start)

    #  Responds to teaching
    not_receptive = fields.Boolean(readonly=True, states=draft_start)
    verbalize_understanding = fields.Boolean(readonly=True, states=draft_start)
    demo_ability = fields.Boolean(readonly=True, states=draft_start)
    needs_followup = fields.Boolean(readonly=True, states=draft_start)
    teaching_other = fields.Boolean(readonly=True, states=draft_start)
    teaching_other_text = fields.Char(readonly=True, states=draft_start)


class PhysicianAssessmentInReport(models.Model):
    _inherit = 'sm.medical.report'

    phy_ass = fields.Many2one('sm.shifa.physician.assessment', string="Physician Assessment #")


class PhysicianAssessmentPrescription(models.Model):
    _inherit = 'oeh.medical.prescription'

    physician_assessment = fields.Many2one('sm.shifa.physician.assessment', string='physician_assessment',
                                           ondelete='cascade')


class PhysicianAssessmentFollowup(models.Model):
    _inherit = 'sm.physician.admission.followup'

    physician_assessment = fields.Many2one('sm.shifa.physician.assessment', string='physician_assessment',
                                           ondelete='cascade')


class PhysicianAssessmentReferral(models.Model):
    _inherit = 'sm.shifa.referral'

    physician_assessment = fields.Many2one('sm.shifa.physician.assessment', string='physician_assessment',
                                           ondelete='cascade')


class PhysicianAssessmentInvestigation(models.Model):
    _inherit = 'sm.shifa.investigation'

    physician_assessment = fields.Many2one('sm.shifa.physician.assessment', string='physician_assessment',
                                           ondelete='cascade')


class PhysicianAssessmentExaminationTab(models.Model):
    _inherit = 'sm.shifa.physician.assessment'
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

    start = {'Start': [('readonly', False)]}

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

    # Examination tab
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
    ], readonly=True, states=start)
    admission_scale_used = fields.Selection([
        ('Numerical', 'Numerical'),
        ('Faces', 'Faces'),
        ('FLACC', 'FLACC'),
        ('ABBEY', 'ABBEY'),
    ], readonly=True, states=start)

    location_head = fields.Boolean(readonly=True, states=start)
    location_face = fields.Boolean(readonly=True, states=start)
    location_limbs = fields.Boolean(readonly=True, states=start)
    location_chest = fields.Boolean(readonly=True, states=start)
    location_abdomen = fields.Boolean(readonly=True, states=start)
    location_back = fields.Boolean(readonly=True, states=start)
    location_of_pain = fields.Text(readonly=True, states=start)

    Characteristics_dull = fields.Boolean(readonly=True, states=start)
    Characteristics_sharp = fields.Boolean(readonly=True, states=start)
    Characteristics_burning = fields.Boolean(readonly=True, states=start)
    Characteristics_throbbing = fields.Boolean(readonly=True, states=start)
    Characteristics_other = fields.Boolean(readonly=True, states=start)
    Characteristics_patient_own_words = fields.Text(readonly=True, states=start)

    onset_time_sudden = fields.Boolean(readonly=True, states=start)
    onset_time_gradual = fields.Boolean(readonly=True, states=start)
    onset_time_constant = fields.Boolean(readonly=True, states=start)
    onset_time_intermittent = fields.Boolean(readonly=True, states=start)
    onset_time_other = fields.Boolean(readonly=True, states=start)
    onset_time_fdv = fields.Text(readonly=True, states=start)

    provoking_factors_food = fields.Boolean(readonly=True, states=start)
    provoking_factors_rest = fields.Boolean(readonly=True, states=start)
    provoking_factors_movement = fields.Boolean(readonly=True, states=start)
    provoking_factors_palpation = fields.Boolean(readonly=True, states=start)
    provoking_factors_other = fields.Boolean(readonly=True, states=start)
    provoking_factors_patient_words = fields.Text(readonly=True, states=start)

    relieving_factors_rest = fields.Boolean(readonly=True, states=start)
    relieving_factors_medication = fields.Boolean(readonly=True, states=start)
    relieving_factors_heat = fields.Boolean(readonly=True, states=start)
    relieving_factors_distraction = fields.Boolean(readonly=True, states=start)
    relieving_factors_other = fields.Boolean(readonly=True, states=start)
    relieving_factors_patient_words = fields.Text(readonly=True, states=start)

    expressing_pain_verbal = fields.Boolean(readonly=True, states=start)
    expressing_pain_facial = fields.Boolean(readonly=True, states=start)
    expressing_pain_body = fields.Boolean(readonly=True, states=start)
    expressing_pain_other = fields.Boolean(readonly=True, states=start)
    expressing_pain_when_pain = fields.Text(readonly=True, states=start)

    effect_of_pain_nausea = fields.Boolean(readonly=True, states=start)
    effect_of_pain_vomiting = fields.Boolean(readonly=True, states=start)
    effect_of_pain_appetite = fields.Boolean(readonly=True, states=start)
    effect_of_pain_activity = fields.Boolean(readonly=True, states=start)
    effect_of_pain_relationship = fields.Boolean(readonly=True, states=start)
    effect_of_pain_emotions = fields.Boolean(readonly=True, states=start)
    effect_of_pain_concentration = fields.Boolean(readonly=True, states=start)
    effect_of_pain_sleep = fields.Boolean(readonly=True, states=start)
    effect_of_pain_other = fields.Boolean(readonly=True, states=start)
    effect_of_pain_other_text = fields.Text(readonly=True, states=start)

    # previous_methods_pain = fields.Text(readonly=True, states=start)
    # previous_methods_pain_not = fields.Text(readonly=True, states=start)

    pain_management_advice_analgesia = fields.Boolean(readonly=True, states=start)
    pain_management_change_of = fields.Boolean(readonly=True, states=start)
    pain_management_refer_physician = fields.Boolean(readonly=True, states=start)
    pain_management_refer_physician_home = fields.Boolean(string="Home Care", readonly=True,
                                                          states=start)
    pain_management_refer_physician_palliative = fields.Boolean(string="palliative", readonly=True,
                                                                states=start)
    pain_management_refer_physician_primary = fields.Boolean(string="primary", readonly=True,
                                                             states=start)
    pain_management_refer_hospital = fields.Boolean(readonly=True, states=start)
    pain_management_other = fields.Boolean(readonly=True, states=start)
    pain_management_other_text = fields.Text(readonly=True, states=start)
    pain_management_comment = fields.Text(readonly=True, states=start)

    # General Condition
    general_condition_show = fields.Boolean()
    general_condition = fields.Text(string='General Condition', readonly=True, states=start)

    # EENT
    EENT_show = fields.Boolean()
    eent_eye = fields.Boolean(default=True, readonly=True, states=start)
    eent_eye_condition = fields.Char(readonly=True, states=start)
    eent_eye_vision = fields.Char(readonly=True, states=start)
    eent_ear = fields.Boolean(default=True, readonly=True, states=start)
    eent_ear_content = fields.Char(readonly=True, states=start)
    eent_nose = fields.Boolean(default=True, readonly=True, states=start)
    eent_nose_content = fields.Char(readonly=True, states=start)
    eent_throut = fields.Boolean(default=True, readonly=True, states=start)
    eent_throut_content = fields.Char(readonly=True, states=start)
    eent_neck = fields.Boolean(default=True, readonly=True, states=start)
    eent_neck_content = fields.Char(readonly=True, states=start)
    eent_remarks = fields.Text(readonly=True, states=start)

    # csv
    csv_show = fields.Boolean()
    cvs_h_sound_1_2 = fields.Boolean(readonly=True, states=start)
    cvs_h_sound_3 = fields.Boolean(readonly=True, states=start)
    cvs_h_sound_4 = fields.Boolean(readonly=True, states=start)
    cvs_h_sound_click = fields.Boolean(readonly=True, states=start)
    cvs_h_sound_murmurs = fields.Boolean(readonly=True, states=start)
    cvs_h_sound_other = fields.Boolean(readonly=True, states=start)
    cvs_h_sound_other_text = fields.Char(readonly=True, states=start)

    cvs_rhythm = fields.Selection([
        ('Regular', 'Regular'),
        ('Irregular', 'Irregular'),
        ('Regular Irregular', 'Regular Irregular'),
        ('Irregular Irregular', 'Irregular Irregular'),
    ], default='Regular', readonly=True, states=start)
    cvs_peripherial_pulse = fields.Selection([
        ('Normal Palpable', 'Normal Palpable'),
        ('Absent Without Pulse', 'Absent Without Pulse'),
        ('Diminished', 'Diminished'),
        ('Bounding', 'Bounding'),
        ('Full and brisk', 'Full and brisk'),
    ], default='Normal Palpable', readonly=True, states=start)

    cvs_edema_yes_no = fields.Selection(yes_no, readonly=True, states=start)
    cvs_edema_yes_type = fields.Selection([
        ('Pitting', 'Pitting'),
        ('Non-Pitting', 'Non-Pitting'),
    ], readonly=True, states=start)
    cvs_edema_yes_location = fields.Text(readonly=True, states=start)
    cvs_edema_yes_grade = fields.Selection([
        ('I- 2mm Depth', 'I- 2mm Depth'),
        ('II- 4mm Depth', 'II- 4mm Depth'),
        ('III- 6mm Depth', 'III- 6mm Depth'),
        ('IV- 8mm Depth', 'IV- 8mm Depth'),
    ], readonly=True, states=start)
    cvs_edema_yes_capillary = fields.Selection([
        ('Less than', 'Less than'),
        ('2-3', '2-3'),
        ('3-4', '3-4'),
        ('4-5', '4-5'),
        ('More than 5', 'More than 5'),
    ], readonly=True, states=start)

    cvs_parenteral_devices_yes_no = fields.Selection(yes_no, readonly=True, states=start)
    cvs_parenteral_devices_yes_sel = fields.Selection([
        ('Central Line', 'Central Line'),
        ('TPN', 'TPN'),
        ('IV Therapy', 'IV Therapy'),
        ('PICC Line', 'PICC Line'),
        ('Other', 'Other'),
    ], readonly=True, states=start)
    cvs_remarks = fields.Text(readonly=True, states=start)
    # Respiratory
    respiratory_show = fields.Boolean()
    lung_sounds_clear = fields.Boolean(default=True, readonly=True, states=start)
    lung_sounds_diminished = fields.Boolean(readonly=True, states=start)
    lung_sounds_absent = fields.Boolean(readonly=True, states=start)
    lung_sounds_fine_crackles = fields.Boolean(readonly=True, states=start)
    lung_sounds_rhonchi = fields.Boolean(readonly=True, states=start)
    lung_sounds_stridor = fields.Boolean(readonly=True, states=start)
    lung_sounds_wheeze = fields.Boolean(readonly=True, states=start)
    lung_sounds_coarse_crackles = fields.Boolean(readonly=True, states=start)

    Location_bilateral = fields.Boolean(readonly=True, states=start)
    Location_left_lower = fields.Boolean(readonly=True, states=start)
    Location_left_middle = fields.Boolean(readonly=True, states=start)
    Location_left_upper = fields.Boolean(readonly=True, states=start)
    Location_lower = fields.Boolean(readonly=True, states=start)
    Location_upper = fields.Boolean(readonly=True, states=start)
    Location_right_lower = fields.Boolean(readonly=True, states=start)
    Location_right_middle = fields.Boolean(readonly=True, states=start)
    Location_right_upper = fields.Boolean(readonly=True, states=start)

    type_regular = fields.Boolean(default=True, readonly=True, states=start)
    type_irregular = fields.Boolean(readonly=True, states=start)
    type_rapid = fields.Boolean(readonly=True, states=start)
    type_dyspnea = fields.Boolean(readonly=True, states=start)
    type_apnea = fields.Boolean(readonly=True, states=start)
    type_tachypnea = fields.Boolean(readonly=True, states=start)
    type_orthopnea = fields.Boolean(readonly=True, states=start)
    type_accessory_muscles = fields.Boolean(readonly=True, states=start)
    type_snoring_mechanical = fields.Boolean(readonly=True, states=start)
    Cough_yes_no = fields.Selection(yes_no, readonly=True, states=start)
    cough_yes_type = fields.Selection([
        ('Productive', 'Productive'),
        ('none-productive', 'none-productive'),
        ('Spontaneous', 'Spontaneous'),
    ], readonly=True, states=start)
    cough_yes_frequency = fields.Selection([
        ('Spontaneous', 'Spontaneous'),
        ('Occassional', 'Occassional'),
        ('Persistent', 'Persistent'),
    ], readonly=True, states=start)
    cough_yes_amount = fields.Selection([
        ('Scanty', 'Scanty'),
        ('Moderate', 'Moderate'),
        ('Large', 'Large'),
    ], readonly=True, states=start)
    cough_yes_characteristic = fields.Selection([
        ('Clear', 'Clear'),
        ('Yellow', 'Yellow'),
        ('Mucoid', 'Mucoid'),
        ('Mucopurulent', 'Mucopurulent'),
        ('Purulent', 'Purulent'),
        ('Pink Frothy', 'Pink Frothy'),
        ('Blood streaked', 'Blood streaked'),
        ('Bloody', 'Bloody'),
    ], readonly=True, states=start)

    respiratory_support_yes_no = fields.Selection(yes_no, readonly=True, states=start)
    respiratory_support_yes_oxygen = fields.Boolean(readonly=True, states=start)
    respiratory_support_yes_oxygen_text = fields.Text(readonly=True, states=start)
    respiratory_support_yes_trachestory = fields.Boolean(readonly=True, states=start)
    respiratory_support_yes_trachestory_text = fields.Text(readonly=True, states=start)
    respiratory_support_yes_ventilator = fields.Boolean(readonly=True, states=start)
    respiratory_support_yes_ventilator_text = fields.Text(readonly=True, states=start)

    suction_yes_no = fields.Selection(yes_no, readonly=True, states=start)
    suction_yes_type = fields.Selection([
        ('Nasal', 'Nasal'),
        ('Oral', 'Oral'),
        ('Trachestory', 'Trachestory'),
    ], readonly=True, states=start)
    suction_yes_frequency = fields.Integer(readonly=True, states=start)

    nebulization_yes_no = fields.Selection(yes_no, readonly=True, states=start)
    nebulization_yes_frequency = fields.Integer(readonly=True, states=start)
    nebulization_yes_medication = fields.Many2one('oeh.medical.medicines', string='Medicines', readonly=True,
                                                  states=start)
    respiratory_remarks = fields.Text(readonly=True, states=start)

    # Neuralogical

    neuralogical_show = fields.Boolean()
    neuralogical_left_eye = fields.Selection(number_neuralogical, readonly=True,
                                             states=start)
    neuralogical_right_eye = fields.Selection(number_neuralogical, readonly=True,
                                              states=start)
    neuralogical_pupil_reaction = fields.Selection([
        ('Equal round, reactive', 'Equal round, reactive'),
        ('Equal round, none reactive', 'Equal round, none reactive'),
        ('Miosis', 'Miosis'),
        ('Mydriasis', 'Mydriasis'),
        ('Sluggish', 'Sluggish'),
        ('Brisk', 'Brisk'),
        ('Elliptical', 'Elliptical'),
        ('Anisocoria', 'Anisocoria'),
    ], default='Equal round, reactive', readonly=True, states=start)
    neuralogical_old = fields.Selection([
        ('Greater Than 5 years Old', 'Greater Than 5 years Old'),
        ('2 to 5 Years Old', '2 to 5 Years Old'),
        ('Less than 2 Years Old', 'Less than 2 Years Old'),
    ], readonly=True, states=start)
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
    ], readonly=True, states=start)
    neuralogical_greater_than_5_years_facial = fields.Selection([
        ('Symmetric', 'Symmetric'),
        ('Unequal facial movement', 'Unequal facial movement'),
        ('Drooping left side of face', 'Drooping left side of face'),
        ('Drooping left side of mouth', 'Drooping left side of mouth'),
        ('Drooping right side of face', 'Drooping right side of face'),
        ('Drooping right side of mouth', 'Drooping right side of mouth'),
    ], readonly=True, states=start)
    neuralogical_greater_than_5_years_glascow = fields.Float(compute=_compute_greater_5_old)
    neuralogical_greater_than_5_years_eye = fields.Selection(eye_momement, readonly=True,
                                                             states=start)
    neuralogical_greater_than_5_years_motor = fields.Selection(motor_response, readonly=True,
                                                               states=start)
    neuralogical_greater_than_5_years_verbal = fields.Selection([
        ('Orient', 'Orient'),
        ('Confused', 'Confused'),
        ('Inappropriate', 'Inappropriate'),
        ('Incompratensive', 'Incompratensive'),
        ('No verable response', 'No verable response'),
    ], readonly=True, states=start)
    neuralogical_2_to_5_level = fields.Selection(level_consciousness, readonly=True,
                                                 states=start)
    neuralogical_2_to_5_glascow = fields.Float(compute=_compute_2_5_old)
    neuralogical_2_to_5_eye = fields.Selection(eye_momement, readonly=True, states=start)
    neuralogical_2_to_5_motor = fields.Selection(motor_response, readonly=True, states=start)
    neuralogical_2_to_5_verbal = fields.Selection([
        ('Appropriate Words', 'Appropriate Words'),
        ('Inappropriate Word', 'Inappropriate Word'),
        ('Cries/Screams', 'Cries/Screams'),
        ('Grunts', 'Grunts'),
        ('No response', 'No response'),
    ], readonly=True, states=start)
    neuralogical_less_than_2_level = fields.Selection(level_consciousness, readonly=True,
                                                      states=start)
    neuralogical_less_than_2_glascow = fields.Float(compute=_compute_less_2)
    neuralogical_less_than_2_eye = fields.Selection(eye_momement, readonly=True,
                                                    states=start)
    neuralogical_less_than_2_motor = fields.Selection([
        ('Spontaneous movements', 'Spontaneous movements'),
        ('Localizes pain', 'Localizes pain'),
        ('Flexion withdrawal', 'Flexion withdrawal'),
        ('Abnormal flexion', 'Abnormal flexion'),
        ('Abnormal extension', 'Abnormal extension'),
        ('No response', 'No response'),
    ], readonly=True, states=start)
    neuralogical_less_than_2_verbal = fields.Selection([
        ('Coos and smiles appropriate', 'Coos and smiles appropriate'),
        ('Cries', 'Cries'),
        ('Inappropriate crying/screaming', 'Inappropriate crying/screaming'),
        ('Grunts', 'Grunts'),
        ('No response', 'No response'),
    ], readonly=True, states=start)
    neuralogical_remarks = fields.Text(readonly=True, states=start)
    # Gastrointestinal
    gastrointestinal_show = fields.Boolean()
    gastrointestinal_bowel_sound = fields.Selection([
        ('Active', 'Active'),
        ('Absent', 'Absent'),
        ('Hypoactive', 'Hypoactive'),
        ('Hyperactive', 'Hyperactive'),
    ], default='Active', readonly=True, states=start)
    gastrointestinal_abdomen_lax = fields.Boolean(default=True, readonly=True, states=start)
    gastrointestinal_abdomen_soft = fields.Boolean(readonly=True, states=start)
    gastrointestinal_abdomen_firm = fields.Boolean(readonly=True, states=start)
    gastrointestinal_abdomen_distended = fields.Boolean(readonly=True, states=start)
    gastrointestinal_abdomen_tender = fields.Boolean(readonly=True, states=start)
    gastrointestinal_stool_color = fields.Selection([
        ('Brown', 'Brown'),
        ('Yellow', 'Yellow'),
        ('Black', 'Black'),
        ('Bright Red', 'Bright Red'),
        ('Dark Red', 'Dark Red'),
        ('Clay', 'Clay'),
    ], default='Brown', readonly=True, states=start)
    gastrointestinal_stool_loose = fields.Boolean(default=True, readonly=True, states=start)
    gastrointestinal_stool_hard = fields.Boolean(readonly=True, states=start)
    gastrointestinal_stool_mucoid = fields.Boolean(readonly=True, states=start)
    gastrointestinal_stool_soft = fields.Boolean(readonly=True, states=start)
    gastrointestinal_stool_tarry = fields.Boolean(readonly=True, states=start)
    gastrointestinal_stool_formed = fields.Boolean(readonly=True, states=start)
    gastrointestinal_stool_semi_formed = fields.Boolean(readonly=True, states=start)
    gastrointestinal_stool_bloody = fields.Boolean(readonly=True, states=start)
    gastrointestinal_stoma_none = fields.Boolean(default=True, readonly=True, states=start)
    gastrointestinal_stoma_colostory = fields.Boolean(readonly=True, states=start)
    gastrointestinal_stoma_ileostomy = fields.Boolean(readonly=True, states=start)
    gastrointestinal_stoma_peg = fields.Boolean(readonly=True, states=start)
    gastrointestinal_stoma_pej = fields.Boolean(readonly=True, states=start)
    gastrointestinal_stoma_urostomy = fields.Boolean(readonly=True, states=start)
    gastrointestinal_problem_none = fields.Boolean(default=True, readonly=True, states=start)
    gastrointestinal_problem_nausea = fields.Boolean(readonly=True, states=start)
    gastrointestinal_problem_vomiting = fields.Boolean(readonly=True, states=start)
    gastrointestinal_problem_colic = fields.Boolean(readonly=True, states=start)
    gastrointestinal_problem_diarrhea = fields.Boolean(readonly=True, states=start)
    gastrointestinal_problem_constipation = fields.Boolean(readonly=True, states=start)
    gastrointestinal_problem_dysphagia = fields.Boolean(readonly=True, states=start)
    gastrointestinal_problem_hemorrhoids = fields.Boolean(readonly=True, states=start)
    gastrointestinal_problem_anal_fissure = fields.Boolean(readonly=True, states=start)
    gastrointestinal_problem_anal_fistula = fields.Boolean(readonly=True, states=start)
    gastrointestinal_problem_other = fields.Boolean(readonly=True, states=start)
    gastrointestinal_problem_other_text = fields.Text(readonly=True, states=start)
    gastrointestinal_bowel_movement_none = fields.Boolean(default=True, readonly=True,
                                                          states=start)
    gastrointestinal_bowel_movement_laxative = fields.Boolean(readonly=True, states=start)
    gastrointestinal_bowel_movement_enema = fields.Boolean(readonly=True, states=start)
    gastrointestinal_bowel_movement_stoma = fields.Boolean(readonly=True, states=start)
    gastrointestinal_bowel_movement_stool_softener = fields.Boolean(readonly=True,
                                                                    states=start)
    gastrointestinal_bowel_movement_suppository = fields.Boolean(readonly=True, states=start)
    gastrointestinal_bowel_movement_digital = fields.Boolean(readonly=True, states=start)
    gastrointestinal_bowel_movement_other = fields.Boolean(readonly=True, states=start)
    gastrointestinal_bowel_movement_other_text = fields.Text(readonly=True, states=start)
    gastrointestinal_enteral_device_none = fields.Boolean(default=True, readonly=True,
                                                          states=start)
    gastrointestinal_enteral_device_nasogastric_tube = fields.Boolean(readonly=True,
                                                                      states=start)
    gastrointestinal_enteral_device_orogastric_tube = fields.Boolean(readonly=True,
                                                                     states=start)
    gastrointestinal_enteral_device_gastro_jejunal = fields.Boolean(readonly=True,
                                                                    states=start)
    gastrointestinal_enteral_device_peg = fields.Boolean(readonly=True, states=start)
    gastrointestinal_enteral_device_pej = fields.Boolean(readonly=True, states=start)
    gastrointestinal_enteral_device_pd = fields.Boolean(readonly=True, states=start)
    gastrointestinal_enteral_device_other = fields.Boolean(readonly=True, states=start)
    gastrointestinal_enteral_device_other_text = fields.Text(readonly=True, states=start)
    gastrointestinal_remarks = fields.Text(readonly=True, states=start)

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
    ], default='Pale Yellow', readonly=True, states=start)
    genitourinary_urine_appearance = fields.Selection([
        ('Clear', 'Clear'),
        ('Cloudy', 'Cloudy'),
        ('With Sediment', 'With Sediment'),
    ], default='Clear', readonly=True, states=start)
    genitourinary_urine_amount = fields.Selection([
        ('Adequate', 'Adequate'),
        ('Scanty', 'Scanty'),
        ('Large', 'Large'),
    ], default='Adequate', readonly=True, states=start)
    genitourinary_urination_none = fields.Boolean(default=True, readonly=True, states=start)
    genitourinary_urination_dysuria = fields.Boolean(readonly=True, states=start)
    genitourinary_urination_frequency = fields.Boolean(readonly=True, states=start)
    genitourinary_urination_urgency = fields.Boolean(readonly=True, states=start)
    genitourinary_urination_hesitancy = fields.Boolean(readonly=True, states=start)
    genitourinary_urination_incontinence = fields.Boolean(readonly=True, states=start)
    genitourinary_urination_inability_to_void = fields.Boolean(readonly=True, states=start)
    genitourinary_urination_nocturia = fields.Boolean(readonly=True, states=start)
    genitourinary_urination_retention = fields.Boolean(readonly=True, states=start)
    genitourinary_urination_suprapubic_pain = fields.Boolean(readonly=True, states=start)
    genitourinary_urination_loin_pain = fields.Boolean(readonly=True, states=start)
    genitourinary_urination_colicky_pain = fields.Boolean(readonly=True, states=start)
    genitourinary_urination_difficult_control = fields.Boolean(readonly=True, states=start)
    genitourinary_urination_other = fields.Boolean(readonly=True, states=start)
    genitourinary_urination_other_text = fields.Text(readonly=True, states=start)
    genitourinary_urination_assistance = fields.Selection([
        ('None', 'None'),
        ('Indwelling Catheter', 'Indwelling Catheter'),
        ('Condom Catheter', 'Condom Catheter'),
        ('Intermittent bladder Wash', 'Intermittent bladder Wash'),
        ('Urostomy', 'Urostomy'),
        ('Suprapubic Catheter', 'Suprapubic Catheter'),
    ], default='None', readonly=True, states=start)
    genitourinary_remarks = fields.Text(readonly=True, states=start)
    # Integumentary
    integumentary_show = fields.Boolean()
    appearance_normal = fields.Boolean(string='Normal', default=True, readonly=True,
                                       states=start)
    appearance_dry = fields.Boolean(string='Dry', readonly=True, states=start)
    appearance_edema = fields.Boolean(string='Edema', readonly=True, states=start)
    appearance_flushed = fields.Boolean(string='Flushed', readonly=True, states=start)
    appearance_pale = fields.Boolean(string='clay', readonly=True, states=start)
    appearance_rash = fields.Boolean(string='Rash', readonly=True, states=start)
    appearance_jundiced = fields.Boolean(string='Jandiced', readonly=True, states=start)
    appearance_eczema = fields.Boolean(string='Eczema', readonly=True, states=start)
    appearance_hemayome = fields.Boolean(string='Hemayome', readonly=True, states=start)
    appearance_rusty = fields.Boolean(string='Rusty', readonly=True, states=start)
    appearance_cyanotic = fields.Boolean(string='Cyanotic', readonly=True, states=start)
    appearance_bruises = fields.Boolean(string='Bruises', readonly=True, states=start)
    appearance_abrasion = fields.Boolean(string='Abrasion', readonly=True, states=start)
    appearance_sores = fields.Boolean(string='Sores', readonly=True, states=start)
    integumentary_turgor = fields.Selection([
        ('Elastic', 'Elastic'),
        ('Normal for age', 'Normal for age'),
        ('Poor', 'Poor'),
    ], default='Elastic', readonly=True, states=start)
    integumentary_temperature = fields.Selection([
        ('Normal', 'Normal'),
        ('Cool', 'Cool'),
        ('Cold', 'Cold'),
        ('Warm', 'Warm'),
        ('Hot', 'Hot'),
    ], default='Normal', readonly=True, states=start)
    integumentary_remarks = fields.Text(readonly=True, states=start)

    # Infections
    infection_show = fields.Boolean()
    infection_nad = fields.Boolean(readonly=True, states=start)
    infection_content = fields.Char(readonly=True, states=start)

    # psychological
    psychological_show = fields.Boolean()
    psychological_nad = fields.Boolean(readonly=True, states=start)
    psychological_content = fields.Char(readonly=True, states=start)
    # reproductive
    reproductive_show = fields.Boolean()
    reproductive_nad = fields.Boolean(readonly=True, states=start)
    reproductive_content = fields.Char(readonly=True, states=start)
    # musculoskeletal
    musculoskeletal_show = fields.Boolean()
    musculoskeletal_left_upper_extremity = fields.Selection(musculoskeletal_extremity,
                                                            default='Active Against Gravity and Resistance',
                                                            readonly=True, states=start)
    musculoskeletal_right_upper_extremity = fields.Selection(musculoskeletal_extremity,
                                                             default='Active Against Gravity and Resistance',
                                                             readonly=True, states=start)
    musculoskeletal_left_lower_extremity = fields.Selection(musculoskeletal_extremity,
                                                            default='Active Against Gravity and Resistance',
                                                            readonly=True, states=start)
    musculoskeletal_right_lower_extremity = fields.Selection(musculoskeletal_extremity,
                                                             default='Active Against Gravity and Resistance',
                                                             readonly=True, states=start)
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
    ], default='Normal', readonly=True, states=start)
    musculoskeletal_remarks = fields.Text(readonly=True, states=start)

    # sensory
    sensory_show = fields.Boolean()
    sensory_nad = fields.Boolean(readonly=True, states=start)
    sensory_content = fields.Char(readonly=True, states=start)
    consent_show = fields.Boolean()
    consent_file1 = fields.Binary()
    consent_file2 = fields.Binary()
    active = fields.Boolean(default=True)

    def action_archive(self):
        for rec in self:
            if rec.state not in ['Discharged', 'Done']:
                raise UserError(_("You can archive only if it discharged assessments or done"))
        return super().action_archive()


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


class PhysicianAssessmentLabRequestTest(models.Model):
    _inherit = 'sm.shifa.lab.request.line'

    phy_ass = fields.Many2one("sm.shifa.physician.assessment", string='phy_ass')


class PhysicianAssessmentImagingRequestTest(models.Model):
    _inherit = 'sm.shifa.imaging.request.line'

    phy_ass = fields.Many2one("sm.shifa.physician.assessment", string='phy_ass')

class PhysicianAssessmentImagingRequest(models.Model):
    _inherit = 'sm.shifa.imaging.request'

    phy_ass = fields.Many2one("sm.shifa.physician.assessment", string='phy_ass')


class PhysicianAssessmentMedicalCareTab(models.Model):
    _inherit = 'sm.shifa.physician.assessment'
    start = {'Start': [('readonly', False)]}
    # medical care plan tab
    medical_care_plan = fields.Text(string='Medical Care Plan', readonly=True, states=start)
    program_chronic_anticoagulation = fields.Boolean(readonly=True, states=start)
    program_general_nursing_care = fields.Boolean(readonly=True, states=start)
    program_wound_care = fields.Boolean(readonly=True, states=start)
    program_palliative_care = fields.Boolean(readonly=True, states=start)
    program_acute_anticoagulation = fields.Boolean(readonly=True, states=start)
    program_home_infusion = fields.Boolean(readonly=True, states=start)
    program_other = fields.Boolean(readonly=True, states=start)
    program_other_text = fields.Text(readonly=True, states=start)
    services_provided_oxygen_dependent = fields.Boolean(readonly=True, states=start)
    services_provided_tracheostomy = fields.Boolean(readonly=True, states=start)
    services_provided_wound_care = fields.Boolean(readonly=True, states=start)
    services_provided_pain_management = fields.Boolean(readonly=True, states=start)
    services_provided_hydration_therapy = fields.Boolean(readonly=True, states=start)
    services_provided_o2_via_nasal_cannula = fields.Boolean(readonly=True, states=start)
    services_provided_hypodermoclysis = fields.Boolean(readonly=True, states=start)
    services_provided_tpn = fields.Boolean(readonly=True, states=start)
    services_provided_stoma_care = fields.Boolean(readonly=True, states=start)
    services_provided_peg_tube = fields.Boolean(readonly=True, states=start)
    services_provided_inr_monitoring = fields.Boolean(readonly=True, states=start)
    services_provided_prevention_pressure = fields.Boolean(readonly=True, states=start)
    services_provided_vac_therapy = fields.Boolean(readonly=True, states=start)
    services_provided_drain_tube = fields.Boolean(readonly=True, states=start)
    services_provided_medication_management = fields.Boolean(readonly=True, states=start)
    services_provided_warfarin_stabilization = fields.Boolean(readonly=True, states=start)
    services_provided_parenteral_antimicrobial = fields.Boolean(readonly=True, states=start)
    services_provided_indwelling_foley_catheter = fields.Boolean(readonly=True, states=start)
    services_provided_ngt = fields.Boolean(readonly=True, states=start)
    services_provided_other = fields.Boolean(readonly=True, states=start)
    services_provided_other_text = fields.Text(readonly=True, states=start)
    patient_condition = fields.Selection([
        ('Declined', 'Declined'),
        ('Unstable', 'Unstable'),
        ('Unchanged', 'Unchanged'),
        ('Improved', 'Improved'),
        ('Stable', 'Stable'),
    ], readonly=True, states=start)
    prognosis = fields.Selection([
        ('Poor', 'Poor'),
        ('Guarded', 'Guarded'),
        ('Fair', 'Fair'),
        ('Good', 'Good'),
        ('Excellent', 'Excellent'),
    ], readonly=True, states=start)
    potential_risk = fields.Text(readonly=True, states=start)
    admission_goal = fields.Text(readonly=True, states=start)
    final_plan = fields.Text(readonly=True, states=start)
    re_certification_equipment_show = fields.Boolean()
    services_provided_show = fields.Boolean()
    program_show = fields.Boolean()
    patient_condition_show = fields.Boolean()
    potential_risk_safety_measures_show = fields.Boolean()
    admission_goal_show = fields.Boolean()
    final_plan_show = fields.Boolean()
    re_certification_oxygen_cylinder = fields.Boolean(readonly=True, states=start)
    re_certification_oxygen_concentrator = fields.Boolean(readonly=True, states=start)
    re_certification_feeding_pump = fields.Boolean(readonly=True, states=start)
    re_certification_pulse_oximetry = fields.Boolean(readonly=True, states=start)
    re_certification_air_compressor = fields.Boolean(readonly=True, states=start)
    re_certification_ventilator = fields.Boolean(readonly=True, states=start)
    re_certification_suction_machine = fields.Boolean(readonly=True, states=start)
    re_certification_acti_VAC_machine = fields.Boolean(readonly=True, states=start)
    re_certification_vest = fields.Boolean(readonly=True, states=start)
    re_certification_nebulizer_machine = fields.Boolean(readonly=True, states=start)
    re_certification_electronic_bed = fields.Boolean(readonly=True, states=start)
    re_certification_wheel_chair = fields.Boolean(readonly=True, states=start)
    re_certification_infusion_pump = fields.Boolean(readonly=True, states=start)
    re_certification_hoyer_lift = fields.Boolean(readonly=True, states=start)
    re_certification_BIPAP_CPAP_AUTO_CPAP = fields.Boolean(readonly=True, states=start)
    v_frequency = [
        ('Daily', 'Daily'), ('Every Two Days', 'Every Two Days'),
        ('3X Weekly', '3X Weekly'), ('2X Weekly', '2X Weekly'),
        ('Weekly', 'Weekly'),
        ('Bimonthly', 'Bimonthly'), ('Monthly', 'Monthly'),
        ('Every 2 Months', 'Every 2 Months'),
        ('Every 3 Months', 'Every 3 Months'),
        ('Every 6 Months', 'Every 6 Months'),
        ('None', 'None'),
        ('As needed', 'As needed'),
    ]
    visit_frequency = fields.Selection(v_frequency, string="Visit Frequency", readonly=True, states=start)
    nurse_visit_frequency = fields.Selection(v_frequency, string="Visit Frequency", readonly=True, states=start)
    respiratory_visit_frequency = fields.Selection(v_frequency, string="Visit Frequency", readonly=True, states=start)
    physiotherapist_visit_frequency = fields.Selection(v_frequency, string="Visit Frequency", readonly=True,
                                                       states=start)
    occupational_visit_frequency = fields.Selection(v_frequency, string="Visit Frequency", readonly=True, states=start)
    social_visit_frequency = fields.Selection(v_frequency, string="Visit Frequency", readonly=True, states=start)
    nutritionist_visit_frequency = fields.Selection(v_frequency, string="Visit Frequency", readonly=True, states=start)
    p_frequency = [
        ('None', 'None'), ('As needed', 'As needed'),
        ('Daily', 'Daily'), ('Monthly', 'Monthly'),
        ('Weekly', 'Weekly'), ('Bimonthly', 'Bimonthly'), ]
    prn_frequency = fields.Selection(p_frequency, string="PRN Frequency", readonly=True, states=start)
    nurse_prn_frequency = fields.Selection(p_frequency, string="PRN Frequency", readonly=True, states=start)
    respiratory_prn_frequency = fields.Selection(p_frequency, string="PRN Frequency", readonly=True, states=start)
    physiotherapist_prn_frequency = fields.Selection(p_frequency, string="PRN Frequency", readonly=True, states=start)
    occupational_prn_frequency = fields.Selection(p_frequency, string="PRN Frequency", readonly=True, states=start)
    social_prn_frequency = fields.Selection(p_frequency, string="PRN Frequency", readonly=True, states=start)
    nutritionist_prn_frequency = fields.Selection(p_frequency, string="PRN Frequency", readonly=True, states=start)


class PhysicianAssessmentPhysicianDiagnosisTab(models.Model):
    _inherit = 'sm.shifa.physician.assessment'
    start = {'Start': [('readonly', False)]}
    # diagnosis tab
    provisional_diagnosis = fields.Many2one('oeh.medical.pathology', string='Disease', readonly=True,
                                            states=start)
    provisional_diagnosis_add_other = fields.Boolean(readonly=True, states=start)
    provisional_diagnosis_add = fields.Many2one('oeh.medical.pathology', string='Disease', readonly=True,
                                                states=start)
    provisional_diagnosis_add_other2 = fields.Boolean(readonly=True, states=start)
    provisional_diagnosis_add2 = fields.Many2one('oeh.medical.pathology', string='Disease', readonly=True,
                                                 states=start)
    provisional_diagnosis_add_other3 = fields.Boolean(readonly=True, states=start)
    provisional_diagnosis_add3 = fields.Many2one('oeh.medical.pathology', string='Disease', readonly=True,
                                                 states=start)

    provisional_diagnosis_add_other4 = fields.Boolean(readonly=True, states=start)
    provisional_diagnosis_add4 = fields.Many2one('oeh.medical.pathology', string='Disease', readonly=True,
                                                 states=start)
    provisional_diagnosis_add_other5 = fields.Boolean(readonly=True, states=start)
    provisional_diagnosis_add5 = fields.Many2one('oeh.medical.pathology', string='Disease', readonly=True,
                                                 states=start)
    provisional_diagnosis_add_other6 = fields.Boolean(readonly=True, states=start)
    provisional_diagnosis_add6 = fields.Many2one('oeh.medical.pathology', string='Disease', readonly=True,
                                                 states=start)
    provisional_diagnosis_add_other7 = fields.Boolean(readonly=True, states=start)
    provisional_diagnosis_add7 = fields.Many2one('oeh.medical.pathology', string='Disease', readonly=True,
                                                 states=start)
    provisional_diagnosis_add_other8 = fields.Boolean(readonly=True, states=start)
    provisional_diagnosis_add8 = fields.Many2one('oeh.medical.pathology', string='Disease', readonly=True,
                                                 states=start)
    provisional_diagnosis_add_other9 = fields.Boolean(readonly=True, states=start)
    provisional_diagnosis_add9 = fields.Many2one('oeh.medical.pathology', string='Disease', readonly=True,
                                                 states=start)

    differential_diagnosis = fields.Many2one('oeh.medical.pathology', string='Disease', readonly=True,
                                             states=start)

    differential_diagnosis_add = fields.Many2one('oeh.medical.pathology', string='Disease', readonly=True,
                                                 states=start)
    differential_diagnosis_add_other = fields.Boolean(readonly=True, states=start)


class PhysicianAssessmentHistoryTab(models.Model):
    _inherit = 'sm.shifa.physician.assessment'

    YES_NO = [
        ('yes', 'Yes'),
        ('no', 'No'),
    ]
    start = {'Start': [('readonly', False)]}
    complete = {
        'Draft': [('readonly', True)],
        'Admitted': [('readonly', True)],
        'Discharged': [('readonly', True)]
    }
    # History tab
    # History of present illness
    history_present_illness_show = fields.Boolean()
    history_present_illness = fields.Text(readonly=False, states=complete)
    # review systems details
    review_systems_show = fields.Boolean()
    constitutional = fields.Boolean(readonly=False, states=complete)
    constitutional_content = fields.Char(readonly=False, states=complete)
    head = fields.Boolean(readonly=False, states=complete)
    head_content = fields.Char(readonly=False, states=complete)
    cardiovascular = fields.Boolean(readonly=False, states=complete)
    cardiovascular_content = fields.Char(readonly=False, states=complete)
    pulmonary = fields.Boolean(readonly=False, states=complete)
    pulmonary_content = fields.Char(readonly=False, states=complete)
    gastroenterology = fields.Boolean(readonly=False, states=complete)
    gastroenterology_content = fields.Char(readonly=False, states=complete)
    genitourinary = fields.Boolean(readonly=False, states=complete)
    genitourinary_content = fields.Char(readonly=False, states=complete)
    dermatological = fields.Boolean(readonly=False, states=complete)
    dermatological_content = fields.Char(readonly=False, states=complete)
    musculoskeletal = fields.Boolean(readonly=False, states=complete)
    musculoskeletal_content = fields.Char(readonly=False, states=complete)
    neurological = fields.Boolean(readonly=False, states=complete)
    neurological_content = fields.Char(readonly=False, states=complete)
    psychiatric = fields.Boolean(readonly=False, states=complete)
    psychiatric_content = fields.Char(readonly=False, states=complete)
    endocrine = fields.Boolean(readonly=False, states=complete)
    endocrine_content = fields.Char(readonly=False, states=complete)
    hematology = fields.Boolean(readonly=False, states=complete)
    hematology_content = fields.Char(readonly=False, states=complete)

    # Past medical History
    past_medical_history_show = fields.Boolean()
    past_medical_history = fields.Many2one('oeh.medical.pathology', string='Disease', readonly=False,
                                           states=complete, related='patient.past_medical_history')
    past_medical_history_date = fields.Date(string='Date', readonly=False,
                                            states=complete, related='patient.past_medical_history_date')
    past_medical_history_1st_add = fields.Many2one('oeh.medical.pathology.category', string='Disease', readonly=False,
                                                   states=complete, related='patient.past_medical_history_1st_add')
    past_medical_history_1st_add_other = fields.Boolean(readonly=False, states=complete,
                                                        related='patient.past_medical_history_1st_add_other')
    past_medical_history_1st_add_date = fields.Date(string='Date', readonly=False,
                                                    states=complete,
                                                    related='patient.past_medical_history_1st_add_date')
    past_medical_history_2nd_add = fields.Many2one('oeh.medical.pathology.category', string='Disease', readonly=False,
                                                   states=complete, related='patient.past_medical_history_2nd_add')
    past_medical_history_2nd_add_date = fields.Date(string='Date', readonly=False,
                                                    states=complete,
                                                    related='patient.past_medical_history_2nd_add_date')
    past_medical_history_2nd_add_other = fields.Boolean(readonly=False, states=complete,
                                                        related='patient.past_medical_history_2nd_add_other')

    # Surgical History
    surgical_history_show = fields.Boolean()
    surgical_history_procedures = fields.Many2one('oeh.medical.procedure', string='Procedures', readonly=False,
                                                  states=complete,
                                                  related='patient.surgical_history_procedures')
    surgical_history_procedures_date = fields.Date(string='Date', readonly=False, states=complete,
                                                   related='patient.surgical_history_procedures_date')

    surgical_history_procedures_1st_add_other = fields.Boolean(readonly=False, states=complete,
                                                               related='patient.surgical_history_procedures_1st_add_other')
    surgical_history_procedures_1st_add = fields.Many2one('oeh.medical.procedure', string='Procedures', readonly=False,
                                                          states=complete,
                                                          related='patient.surgical_history_procedures_1st_add')
    surgical_history_procedures_1st_add_date = fields.Date(string='Date', readonly=False,
                                                           states=complete,
                                                           related='patient.surgical_history_procedures_1st_add_date')

    surgical_history_procedures_2nd_add_other = fields.Boolean(readonly=False, states=complete,
                                                               related='patient.surgical_history_procedures_2nd_add_other')
    surgical_history_procedures_2nd_add = fields.Many2one('oeh.medical.procedure', string='Procedures', readonly=False,
                                                          states=complete,
                                                          related='patient.surgical_history_procedures_2nd_add')
    surgical_history_procedures_2nd_add_date = fields.Date(string='Date', readonly=False, states=complete,
                                                           related='patient.surgical_history_procedures_2nd_add_date')
    # Family History
    family_history_show = fields.Boolean()
    family_history = fields.Text(readonly=False, states=complete, related='patient.family_history')
    services_provided_caregiver = fields.Boolean(readonly=True, states=start)
    services_provided_BP_monitoring = fields.Boolean(readonly=True, states=start)
    services_provided_blood_sugar_monitoring = fields.Boolean(readonly=True, states=start)
    services_provided_fall_risk_prevention = fields.Boolean(readonly=True, states=start)
    services_provided_BIPAP_CPAP_management = fields.Boolean(readonly=True, states=start)

    @api.onchange('drug_allergy', 'food_allergy', 'other_allergy')
    def get_selection(self):
        print(self.drug_allergy)
        if self.drug_allergy:
            self.has_drug_allergy = "yes"
        else:
            self.has_drug_allergy = "no"

        if self.food_allergy:
            self.has_food_allergy = "yes"
        else:
            self.has_food_allergy = "no"

        if self.other_allergy:
            self.has_other_allergy = "yes"
        else:
            self.has_other_allergy = "no"

    @api.onchange('has_drug_allergy', 'has_food_allergy', 'has_other_allergy')
    def get_boolean(self):
        if self.has_drug_allergy == "yes":
            self.drug_allergy = True
        else:
            self.drug_allergy = False

        if self.has_food_allergy == "yes":
            self.food_allergy = True
        else:
            self.food_allergy = False

        if self.has_other_allergy == "yes":
            self.other_allergy = True
        else:
            self.other_allergy = False

    # Allergies
    allergies_show = fields.Boolean()
    has_drug_allergy = fields.Selection(YES_NO, string='Drug Allergy', readonly=False,
                                        states=complete, related='patient.has_drug_allergy')
    drug_allergy = fields.Boolean(default=False, readonly=False, states=complete, related='patient.drug_allergy')
    drug_allergy_content = fields.Char(readonly=False, states=complete, related='patient.drug_allergy_content')

    has_food_allergy = fields.Selection(YES_NO, string='Food Allergy', readonly=False,
                                        states=complete, related='patient.has_food_allergy')
    food_allergy = fields.Boolean(default=False, readonly=False, states=complete, related='patient.food_allergy')
    food_allergy_content = fields.Char(readonly=False, states=complete, related='patient.food_allergy_content')

    has_other_allergy = fields.Selection(YES_NO, string='Other Allergy', readonly=False,
                                         states=complete, related='patient.has_other_allergy')
    other_allergy = fields.Boolean(default=False, readonly=False, states=complete, related='patient.other_allergy')
    other_allergy_content = fields.Char(readonly=False, states=complete, related='patient.other_allergy_content')

    # Personal Habits
    personal_habits_show = fields.Boolean()
    # Physical Exercise
    exercise = fields.Boolean(string='Exercise', readonly=False, states=complete, related='patient.exercise')
    exercise_minutes_day = fields.Integer(string='Minutes / day', help="How many minutes a day the patient exercises",
                                          readonly=False, states=complete, related='patient.exercise_minutes_day')
    # sleep
    sleep_hours = fields.Integer(string='Hours of Sleep', help="Average hours of sleep per day", readonly=False,
                                 states=complete, related='patient.sleep_hours')
    sleep_during_daytime = fields.Boolean(string='Sleeps at Daytime',
                                          help="Check if the patient sleep hours are during daylight rather than at night",
                                          readonly=False, states=complete, related='patient.sleep_during_daytime')
    # Smoking
    smoking = fields.Boolean(string='Smokes', readonly=False, states=complete, related='patient.smoking')
    smoking_number = fields.Integer(string='Cigarretes a Day', readonly=False,
                                    states=complete, related='patient.smoking_number')
    age_start_smoking = fields.Integer(string='Age Started to Smoke', readonly=False,
                                       states=complete, related='patient.age_start_smoking')

    ex_smoker = fields.Boolean(string='Ex-smoker', readonly=False, states=complete, related='patient.ex_smoker')
    age_start_ex_smoking = fields.Integer(string='Age Started to Smoke', readonly=False,
                                          states=complete, related='patient.age_start_ex_smoking')
    age_quit_smoking = fields.Integer(string='Age of Quitting', help="Age of quitting smoking", readonly=False,
                                      states=complete, related='patient.age_quit_smoking')
    second_hand_smoker = fields.Boolean(string='Passive Smoker', readonly=False, states=complete,
                                        related='patient.second_hand_smoker',
                                        help="Check it the patient is a passive / second-hand smoker")
    # drink
    alcohol = fields.Boolean(string='Drinks Alcohol', readonly=False, states=complete, related='patient.alcohol')
    age_start_drinking = fields.Integer(string='Age Started to Drink ', help="Date to start drinking", readonly=False,
                                        states=complete, related='patient.age_start_drinking')
    alcohol_beer_number = fields.Integer(string='Beer / day', readonly=False,
                                         states=complete, related='patient.alcohol_beer_number')
    alcohol_liquor_number = fields.Integer(string='Liquor / day', readonly=False,
                                           states=complete, related='patient.alcohol_liquor_number')
    ex_alcoholic = fields.Boolean(string='Ex Alcoholic', readonly=False, states=complete,
                                  related='patient.ex_alcoholic')
    alcohol_wine_number = fields.Integer(string='Wine / day', readonly=False,
                                         states=complete, related='patient.alcohol_wine_number')
    age_quit_drinking = fields.Integer(string='Age Quit Drinking ', help="Date to stop drinking", readonly=False,
                                       states=complete, related='patient.age_quit_drinking')

    # Vaccination
    vaccination_show = fields.Boolean()
    Vaccination = fields.Many2one('sm.shifa.generic.vaccines', string='Vaccine', readonly=False,
                                  states=complete, related='patient.Vaccination')
    vaccination_date = fields.Date(string='Date', readonly=False, states=complete, related='patient.vaccination_date')

    Vaccination_1st_add_other = fields.Boolean(readonly=False,
                                               states=complete, related='patient.Vaccination_1st_add_other')
    Vaccination_1st_add = fields.Many2one('sm.shifa.generic.vaccines', string='Procedures', readonly=False,
                                          states=complete, related='patient.Vaccination_1st_add')
    Vaccination_1st_add_date = fields.Date(string='Date', readonly=False,
                                           states=complete, related='patient.Vaccination_1st_add_date')

    Vaccination_2nd_add_other = fields.Boolean(readonly=False, states=complete,
                                               related='patient.Vaccination_2nd_add_other')
    Vaccination_2nd_add = fields.Many2one('sm.shifa.generic.vaccines', string='Procedures', readonly=False,
                                          states=complete, related='patient.Vaccination_2nd_add')
    Vaccination_2nd_add_date = fields.Date(string='Date', readonly=False, states=complete,
                                           related='patient.Vaccination_2nd_add_date')

    @api.onchange('cardiovascular', 'constitutional', 'head', 'pulmonary', 'genitourinary', 'gastroenterology',
                  'dermatological', 'musculoskeletal', 'neurological', 'psychiatric', 'endocrine', 'hematology')
    def _onchange_cardiovascular(self):
        if self.cardiovascular:
            self.cardiovascular_content = ''
        if self.constitutional:
            self.constitutional_content = ''
        if self.head:
            self.head_content = ''
        if self.pulmonary:
            self.pulmonary_content = ''
        if self.genitourinary:
            self.genitourinary_content = ''
        if self.gastroenterology:
            self.gastroenterology_content = ''
        if self.dermatological:
            self.dermatological_content = ''
        if self.musculoskeletal:
            self.musculoskeletal_content = ''
        if self.neurological:
            self.neurological_content = ''
        if self.psychiatric:
            self.psychiatric_content = ''
        if self.endocrine:
            self.endocrine_content = ''
        if self.hematology:
            self.hematology_content = ''
