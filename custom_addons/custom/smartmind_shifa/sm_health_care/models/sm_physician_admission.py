import datetime
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ShifaPhysicianAdmission(models.Model):
    _name = 'sm.shifa.physician.admission'
    _description = 'Physician Admission'
    _rec_name = 'name'

    ADMISSION_STATES = [
        ('Draft', 'Draft'),
        ('Start', 'Start'),
        ('Admitted', 'Admitted'),
        ('Discharged', 'Discharged'),
    ]

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

    def _get_physician(self):
        """Return default physician value"""
        therapist_obj = self.env['oeh.medical.physician']
        domain = [('oeh_user_id', '=', self.env.uid)]
        user_ids = therapist_obj.search(domain, limit=1)
        if user_ids:
            return user_ids.id or False
        else:
            return False

    state = fields.Selection(ADMISSION_STATES, string='State', default=lambda *a: 'Draft', readonly=True)
    name = fields.Char('PhyAd #', index=True, copy=False)
    # patient details
    patient = fields.Many2one('oeh.medical.patient', string='Patient', help="Patient Name", required=True,
                              readonly=False, states={'Discharged': [('readonly', True)]})
    dob = fields.Date(string='Date of Birth', related='patient.dob')
    marital_status = fields.Selection(string='Marital Status', related='patient.marital_status')
    sex = fields.Selection(string='Sex', related='patient.sex')
    blood_type = fields.Selection(string='Blood Type', related='patient.blood_type')
    rh = fields.Selection(string='Rh', related='patient.rh')
    ssn = fields.Char(size=256, string='National ID', related='patient.ssn')
    phone = fields.Char(string='Mobile', related='patient.mobile')

    service = fields.Many2one('sm.shifa.service', string='Service Name',
                              required=True,
                              domain=[('service_type', 'in', ['SM', 'MH', 'GCP', 'Car', 'HVD'])],
                              readonly=False, states={'Discharged': [('readonly', True)]})
    service_type = fields.Selection(string='Service type', related='service.service_type', readonly=False, store=False)
    # appointment register link
    hhc_appointment = fields.Many2one('sm.shifa.hhc.appointment', string='HHC-Appointment',
                                      domain=[('service_type', 'in',
                                               ['SM', 'MH', 'GCP', 'Car'])],
                                      readonly=False, states={'Discharged': [('readonly', True)]})
    service_name = fields.Char(string='Service Name', related='service.abbreviation', readonly=False, store=False)
    doctor = fields.Many2one('oeh.medical.physician', string='Doctor', help="Current primary care / family doctor",
                             domain=[('role_type', 'in', ['HD', 'HHCD', 'HVD']), ('active', '=', True)],
                             readonly=False, states={'Discharged': [('readonly', True)]}, required=True,
                             default=_get_physician)
    admission_date = fields.Datetime(string='Admission Date')
    discharge_date = fields.Datetime(string='Discharge Date')

    chief_complaint = fields.Char(string='Chief Complaint', readonly=False, states={'Discharged': [('readonly', True)]})
    # relate prescription to physician
    prescription_ids = fields.One2many('oeh.medical.prescription', 'physician_admission')
    # relate prescription to investigation
    investigation_ids = fields.One2many('sm.shifa.investigation', 'physician_admission', string='Investigation')
    labtest_line = fields.One2many('sm.shifa.lab.request', 'physician_admission', string='Lab Request')
    image_test_ids = fields.One2many('sm.shifa.imaging.request', 'physician_admission')

    followup_ids = fields.One2many('sm.physician.admission.followup', 'physician_admission', string='Follow Up')
    referral_ids = fields.One2many('sm.shifa.referral', 'physician_admission')

    vital_signs_show = fields.Boolean()
    temperature = fields.Float(string="Temperature (c)", readonly=False, states={'Discharged': [('readonly', True)]})
    systolic = fields.Integer(string="Systolic BP(mmHg)", readonly=False, states={'Discharged': [('readonly', True)]})
    respiratory_rate = fields.Integer(string="RR (/min)", readonly=False, states={'Discharged': [('readonly', True)]})
    # osat = fields.Float(string="O2 Sat(%)", readonly=False, states={'Discharged': [('readonly', True)]})
    at_room_air = fields.Boolean(string="at room air", readonly=False, states={'Discharged': [('readonly', True)]})
    with_oxygen_support = fields.Boolean(string="with oxygen Support", readonly=False, states={'Discharged': [('readonly', True)]})
    char_other_oxygen = fields.Char(readonly=False, states={'Discharged': [('readonly', True)]})
    diastolic = fields.Integer(string="Diastolic BR(mmHg)", readonly=False, states={'Discharged': [('readonly', True)]})
    bpm = fields.Integer(string="HR (/min)", readonly=False, states={'Discharged': [('readonly', True)]})

    pain_present_show = fields.Boolean()
    # metabolic
    metabolic_show = fields.Boolean()
    weight = fields.Float(string='Weight (kg)', readonly=False, states={'Discharged': [('readonly', True)]})
    waist_circ = fields.Float(string='Waist Circumference (cm)', readonly=False, states={'Discharged': [('readonly', True)]})
    bmi = fields.Float(compute=_compute_bmi, string='Body Mass Index (BMI)', store=True)
    height = fields.Float(string='Height (cm)', readonly=False, states={'Discharged': [('readonly', True)]})
    head_circumference = fields.Float(string='Head Circumference(cm)', help="Head circumference", readonly=False, states={'Discharged': [('readonly', False)]})

    lab_request_test_line = fields.One2many('sm.shifa.lab.request.line', 'phy_adm', string='Lab Request',
                                   readonly=False, states={'Discharged': [('readonly', True)]})
    image_request_test_ids = fields.One2many('sm.shifa.imaging.request.line', 'phy_adm', string='Image Request',
                                   readonly=False, states={'Discharged': [('readonly', True)]})

    # connect the patient details with appointment
    @api.onchange('hhc_appointment')
    def _onchange_hhc_appointment(self):
        if self.hhc_appointment:
            self.patient = self.hhc_appointment.patient
            self.service = self.hhc_appointment.service

    # sequence number method
    @api.model
    def create(self, vals):
        vals['physician_admission_code'] = self.env['ir.sequence'].next_by_code('sm.shifa.physician.admission')
        return super(ShifaPhysicianAdmission, self).create(vals)

    #     draft method
    def set_to_start(self):
        return self.write({'state': 'Start'})

    #     admitted date method
    def set_to_admitted(self):
        for rec in self:
            if not rec.pres_phy_line:
                pass
            else:
                rec.env['oeh.medical.prescription'].create({
                    'patient': rec.patient.id,
                    'doctor': rec.doctor.id,
                    'phy_admission': rec.id,
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
                    'prescription_line': rec.pres_phy_line,
                })
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

    #     download prescription pdf
    def download_pdf(self):
        for rec in self:
            if not rec.pres_phy_line:
                raise ValidationError(_("No Prescription to print"))
            else:
                therapist_obj = self.env['oeh.medical.prescription']
                domain = [('phy_admission', '=', self.id)]
                pres_id = therapist_obj.search(domain)
                return self.env.ref('smartmind_shifa.sm_shifa_report_patient_prescriptions').report_action(pres_id)

    # send prescription via Email
    def action_send_email(self):
        for rec in self:
            if not rec.pres_phy_line:
                raise ValidationError(_("No Prescription to send"))
            else:
                therapist_obj = self.env['oeh.medical.prescription']
                domain = [('phy_admission', '=', rec.id)]
                pres_id = therapist_obj.search(domain, limit=1)
                pres_id.ensure_one()
                ir_model_data = pres_id.env['ir.model.data']
                try:
                    template_id = \
                        ir_model_data.get_object_reference('smartmind_shifa', 'patient_prescription_email_template')[1]
                except ValueError:
                    template_id = False
                try:
                    compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
                except ValueError:
                    compose_form_id = False
                ctx = {
                    'default_model': 'oeh.medical.prescription',
                    'default_res_id': pres_id.ids[0],
                    'default_use_template': bool(template_id),
                    'default_template_id': template_id,
                    'default_composition_mode': 'comment',
                }
                return {
                    'name': _('Compose Email'),
                    'type': 'ir.actions.act_window',
                    'view_mode': 'form',
                    'res_model': 'mail.compose.message',
                    'views': [(compose_form_id, 'form')],
                    'view_id': compose_form_id,
                    'target': 'new',
                    'context': ctx,
                }

    #  send prescription link via SMS
    def action_send_sms(self):
        for rec in self:
            if not rec.pres_phy_line:
                raise ValidationError(_("No Prescription to send"))
            else:
                therapist_obj = self.env['oeh.medical.prescription']
                domain = [('phy_admission', '=', rec.id)]
                pres_id = therapist_obj.search(domain, limit=1)
                my_model = pres_id._name
                # print(my_model)
                if pres_id.patient.mobile:
                    msg = "You can download Your prescription from: %s." % (pres_id.link)
                    # print(">>>>>>>>>>>>", msg)
                    pres_id.send_sms(self.patient.mobile, msg, my_model, pres_id.id)

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('sm.shifa.physician.admission') or _('New')
        return super(ShifaPhysicianAdmission, self).create(vals)

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

    # constrains on Respiratory
    @api.onchange('nebulization_yes_frequency', 'suction_yes_frequency')
    def _check_respiratory_frequency(self):
        if self.nebulization_yes_frequency > 100:
            raise ValidationError("invalid Nebulization frequency value")
        if self.suction_yes_frequency > 100:
            raise ValidationError("invalid Suction frequency value")

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
        # if self.osat > 100:
        #     raise ValidationError("invalid Oxygen Saturation value")


class ShifaPhysicianMedicalCareTab(models.Model):
    _inherit = 'sm.shifa.physician.admission'
    # medical care plan tab
    medical_care_plan = fields.Text(string='Medical Care Plan', readonly=False, states={'Discharged': [('readonly', True)]})
    program_chronic_anticoagulation = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    program_general_nursing_care = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    program_wound_care = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    program_palliative_care = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    program_acute_anticoagulation = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    program_home_infusion = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    program_other = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    program_other_text = fields.Text(readonly=False, states={'Discharged': [('readonly', True)]})
    services_provided_oxygen_dependent = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    services_provided_tracheostomy = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    services_provided_wound_care = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    services_provided_pain_management = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    services_provided_hydration_therapy = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    services_provided_o2_via_nasal_cannula = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    services_provided_hypodermoclysis = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    services_provided_tpn = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    services_provided_stoma_care = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    services_provided_peg_tube = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    services_provided_inr_monitoring = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    services_provided_prevention_pressure = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    services_provided_vac_therapy = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    services_provided_drain_tube = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    services_provided_medication_management = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    services_provided_warfarin_stabilization = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    services_provided_parenteral_antimicrobial = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    services_provided_indwelling_foley_catheter = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    services_provided_ngt = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    services_provided_other = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    services_provided_other_text = fields.Text(readonly=False, states={'Discharged': [('readonly', True)]})
    patient_condition = fields.Selection([
        ('Declined', 'Declined'),
        ('Unstable', 'Unstable'),
        ('Unchanged', 'Unchanged'),
        ('Improved', 'Improved'),
        ('Stable', 'Stable'),
    ], readonly=False, states={'Discharged': [('readonly', True)]})
    prognosis = fields.Selection([
        ('Poor', 'Poor'),
        ('Guarded', 'Guarded'),
        ('Fair', 'Fair'),
        ('Good', 'Good'),
        ('Excellent', 'Excellent'),
    ], readonly=False, states={'Discharged': [('readonly', True)]})
    potential_risk = fields.Text(readonly=False, states={'Discharged': [('readonly', True)]})
    admission_goal = fields.Text(readonly=False, states={'Discharged': [('readonly', True)]})
    final_plan = fields.Text(readonly=False, states={'Discharged': [('readonly', True)]})
    re_certification_equipment_show = fields.Boolean()
    services_provided_show = fields.Boolean()
    program_show = fields.Boolean()
    patient_condition_show = fields.Boolean()
    potential_risk_safety_measures_show = fields.Boolean()
    admission_goal_show = fields.Boolean()
    final_plan_show = fields.Boolean()
    re_certification_oxygen_cylinder = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    re_certification_oxygen_concentrator = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    re_certification_feeding_pump = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    re_certification_pulse_oximetry = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    re_certification_air_compressor = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    re_certification_ventilator = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    re_certification_suction_machine = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    re_certification_acti_VAC_machine = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    re_certification_vest = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    re_certification_nebulizer_machine = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    re_certification_electronic_bed = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    re_certification_wheel_chair = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    re_certification_infusion_pump = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    re_certification_hoyer_lift = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    re_certification_BIPAP_CPAP_AUTO_CPAP = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    v_frequency = [
        ('Daily', 'Daily'),('Every Two Days', 'Every Two Days'),
        ('3X Weekly', '3X Weekly'),('2X Weekly', '2X Weekly'),
        ('Bimonthly', 'Bimonthly'),('Monthly', 'Monthly'),
        ('Every 2 Months', 'Every 2 Months'),
        ('Every 3 Months', 'Every 3 Months'),
        ('Every 6 Months', 'Every 6 Months'),
        ('None', 'None'),
        ('As needed', 'As needed'),
    ]
    visit_frequency = fields.Selection(v_frequency, string="Visit Frequency")
    p_frequency = [
        ('None', 'None'), ('As needed', 'As needed'),
        ('Daily', 'Daily'), ('Monthly', 'Monthly'),
        ('Weekly', 'Weekly'), ('Bimonthly', 'Bimonthly'),]
    prn_frequency = fields.Selection(p_frequency, string="PRN Frequency")



class ShifaPhysicianDiagnosisTab(models.Model):
    _inherit = 'sm.shifa.physician.admission'

    # diagnosis tab
    provisional_diagnosis = fields.Many2one('oeh.medical.pathology', string='Disease', readonly=False, states={'Discharged': [('readonly', True)]})
    provisional_diagnosis_add_other = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    provisional_diagnosis_add = fields.Many2one('oeh.medical.pathology', string='Disease', readonly=False, states={'Discharged': [('readonly', True)]})
    provisional_diagnosis_add_other2 = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    provisional_diagnosis_add2 = fields.Many2one('oeh.medical.pathology', string='Disease', readonly=False, states={'Discharged': [('readonly', True)]})
    provisional_diagnosis_add_other3 = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    provisional_diagnosis_add3 = fields.Many2one('oeh.medical.pathology', string='Disease', readonly=False, states={'Discharged': [('readonly', True)]})

    provisional_diagnosis_add_other4 = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    provisional_diagnosis_add4 = fields.Many2one('oeh.medical.pathology', string='Disease', readonly=False, states={'Discharged': [('readonly', True)]})
    provisional_diagnosis_add_other5 = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    provisional_diagnosis_add5 = fields.Many2one('oeh.medical.pathology', string='Disease', readonly=False, states={'Discharged': [('readonly', True)]})
    provisional_diagnosis_add_other6 = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    provisional_diagnosis_add6 = fields.Many2one('oeh.medical.pathology', string='Disease', readonly=False, states={'Discharged': [('readonly', True)]})
    provisional_diagnosis_add_other7 = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    provisional_diagnosis_add7 = fields.Many2one('oeh.medical.pathology', string='Disease', readonly=False, states={'Discharged': [('readonly', True)]})
    provisional_diagnosis_add_other8 = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    provisional_diagnosis_add8 = fields.Many2one('oeh.medical.pathology', string='Disease', readonly=False, states={'Discharged': [('readonly', True)]})
    provisional_diagnosis_add_other9 = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    provisional_diagnosis_add9 = fields.Many2one('oeh.medical.pathology', string='Disease', readonly=False, states={'Discharged': [('readonly', True)]})

    differential_diagnosis = fields.Many2one('oeh.medical.pathology', string='Disease', readonly=False, states={'Discharged': [('readonly', True)]})

    differential_diagnosis_add = fields.Many2one('oeh.medical.pathology', string='Disease', readonly=False, states={'Discharged': [('readonly', True)]})
    differential_diagnosis_add_other = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})


class ShifaPhysicianHistoryTab(models.Model):
    _inherit = 'sm.shifa.physician.admission'

    YES_NO = [
        ('yes', 'Yes'),
        ('no', 'No'),
    ]
    # History tab
    # History of present illness
    history_present_illness_show = fields.Boolean()
    history_present_illness = fields.Text(readonly=False, states={'Discharged': [('readonly', True)]})
    # review systems details
    review_systems_show = fields.Boolean()
    constitutional = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    constitutional_content = fields.Char(readonly=False, states={'Discharged': [('readonly', True)]})
    head = fields.Boolean(readonly=False, states={'Draft': [('readonly', True)], 'Admitted': [('readonly', True)],
                                                  'Discharged': [('readonly', True)]})
    head_content = fields.Char(readonly=False, states={'Discharged': [('readonly', True)]})
    cardiovascular = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    cardiovascular_content = fields.Char(readonly=False, states={'Discharged': [('readonly', True)]})
    pulmonary = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    pulmonary_content = fields.Char(readonly=False, states={'Discharged': [('readonly', True)]})
    gastroenterology = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    gastroenterology_content = fields.Char(readonly=False, states={'Discharged': [('readonly', True)]})
    genitourinary = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    genitourinary_content = fields.Char(readonly=False, states={'Discharged': [('readonly', True)]})
    dermatological = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    dermatological_content = fields.Char(readonly=False, states={'Discharged': [('readonly', True)]})
    musculoskeletal = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    musculoskeletal_content = fields.Char(readonly=False, states={'Discharged': [('readonly', True)]})
    neurological = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    neurological_content = fields.Char(readonly=False, states={'Discharged': [('readonly', True)]})
    psychiatric = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    psychiatric_content = fields.Char(readonly=False, states={'Discharged': [('readonly', True)]})
    endocrine = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    endocrine_content = fields.Char(readonly=False, states={'Discharged': [('readonly', True)]})
    hematology = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    hematology_content = fields.Char(readonly=False, states={'Discharged': [('readonly', True)]})

    # Past medical History
    past_medical_history_show = fields.Boolean()
    past_medical_history = fields.Many2one('oeh.medical.pathology', string='Disease', readonly=False, states={'Discharged': [('readonly', True)]},
                                           related='patient.past_medical_history')
    past_medical_history_date = fields.Date(string='Date', readonly=False, states={'Discharged': [('readonly', True)]},
                                            related='patient.past_medical_history_date')
    past_medical_history_1st_add = fields.Many2one('oeh.medical.pathology.category', string='Disease',readonly=False, states={'Discharged': [('readonly', True)]},
                                                   related='patient.past_medical_history_1st_add')
    past_medical_history_1st_add_other = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]},
                                                        related='patient.past_medical_history_1st_add_other')
    past_medical_history_1st_add_date = fields.Date(string='Date', readonly=False, states={'Discharged': [('readonly', True)]},
                                                    related='patient.past_medical_history_1st_add_date')
    past_medical_history_2nd_add = fields.Many2one('oeh.medical.pathology.category', string='Disease', readonly=False, states={'Discharged': [('readonly', True)]},
                                                   related='patient.past_medical_history_2nd_add')
    past_medical_history_2nd_add_date = fields.Date(string='Date', readonly=False, states={'Discharged': [('readonly', True)]},
                                                    related='patient.past_medical_history_2nd_add_date')
    past_medical_history_2nd_add_other = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]},
                                                        related='patient.past_medical_history_2nd_add_other')

    # Surgical History
    surgical_history_show = fields.Boolean()
    surgical_history_procedures = fields.Many2one('oeh.medical.procedure', string='Procedures', readonly=False, states={'Discharged': [('readonly', True)]},
                                                  related='patient.surgical_history_procedures')
    surgical_history_procedures_date = fields.Date(string='Date', readonly=False, states={'Discharged': [('readonly', True)]},
                                                   related='patient.surgical_history_procedures_date')

    surgical_history_procedures_1st_add_other = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]},
                                                               related='patient.surgical_history_procedures_1st_add_other')
    surgical_history_procedures_1st_add = fields.Many2one('oeh.medical.procedure', string='Procedures', readonly=False, states={'Discharged': [('readonly', True)]},
                                                          related='patient.surgical_history_procedures_1st_add')
    surgical_history_procedures_1st_add_date = fields.Date(string='Date', readonly=False, states={'Discharged': [('readonly', True)]},
                                                           related='patient.surgical_history_procedures_1st_add_date')

    surgical_history_procedures_2nd_add_other = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]},
                                                               related='patient.surgical_history_procedures_2nd_add_other')
    surgical_history_procedures_2nd_add = fields.Many2one('oeh.medical.procedure', string='Procedures', readonly=False, states={'Discharged': [('readonly', True)]},
                                                          related='patient.surgical_history_procedures_2nd_add')
    surgical_history_procedures_2nd_add_date = fields.Date(string='Date', readonly=False, states={'Discharged': [('readonly', True)]},
                                                           related='patient.surgical_history_procedures_2nd_add_date')
    # Family History
    family_history_show = fields.Boolean()
    family_history = fields.Text(readonly=False, states={'Discharged': [('readonly', True)]}, related='patient.family_history')
    services_provided_caregiver = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    services_provided_BP_monitoring = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    services_provided_blood_sugar_monitoring = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    services_provided_fall_risk_prevention = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    services_provided_BIPAP_CPAP_management = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})


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
    has_drug_allergy = fields.Selection(YES_NO, string='Drug Allergy', readonly=False, states={'Discharged': [('readonly', True)]},
                                        related='patient.has_drug_allergy'
                                        )
    drug_allergy = fields.Boolean(default=False, readonly=False, states={'Discharged': [('readonly', True)]},
                                  related='patient.drug_allergy')
    drug_allergy_content = fields.Char(readonly=False, states={'Discharged': [('readonly', True)]},
                                       related='patient.drug_allergy_content')

    has_food_allergy = fields.Selection(YES_NO, string='Food Allergy', readonly=False, states={'Discharged': [('readonly', True)]},
                                        related='patient.has_food_allergy')
    food_allergy = fields.Boolean(default=False, readonly=False, states={'Discharged': [('readonly', True)]},
                                  related='patient.food_allergy')
    food_allergy_content = fields.Char(readonly=False, states={'Discharged': [('readonly', True)]},
                                       related='patient.food_allergy_content')

    has_other_allergy = fields.Selection(YES_NO, string='Other Allergy', readonly=False, states={'Discharged': [('readonly', True)]},
                                         related='patient.has_other_allergy')
    other_allergy = fields.Boolean(default=False, readonly=False, states={'Discharged': [('readonly', True)]},
                                   related='patient.other_allergy')
    other_allergy_content = fields.Char(readonly=False, states={'Discharged': [('readonly', True)]},
                                        related='patient.other_allergy_content')

    # Personal Habits
    personal_habits_show = fields.Boolean()
    # Physical Exercise
    exercise = fields.Boolean(string='Exercise', readonly=False, states={'Discharged': [('readonly', True)]}, related='patient.exercise')
    exercise_minutes_day = fields.Integer(string='Minutes / day', help="How many minutes a day the patient exercises",
                                          readonly=False, states={'Discharged': [('readonly', True)]},
                                          related='patient.exercise_minutes_day')
    # sleep
    sleep_hours = fields.Integer(string='Hours of Sleep', help="Average hours of sleep per day", readonly=False, states={'Discharged': [('readonly', True)]}, related='patient.sleep_hours')
    sleep_during_daytime = fields.Boolean(string='Sleeps at Daytime',
                                          help="Check if the patient sleep hours are during daylight rather than at night",
                                          readonly=False, states={'Discharged': [('readonly', True)]},
                                          related='patient.sleep_during_daytime')
    # Smoking
    smoking = fields.Boolean(string='Smokes', readonly=False, states={'Discharged': [('readonly', True)]}, related='patient.smoking')
    smoking_number = fields.Integer(string='Cigarretes a Day', readonly=False, states={'Discharged': [('readonly', True)]}, related='patient.smoking_number')
    age_start_smoking = fields.Integer(string='Age Started to Smoke', readonly=False, states={'Discharged': [('readonly', True)]}, related='patient.age_start_smoking')

    ex_smoker = fields.Boolean(string='Ex-smoker', readonly=False, states={'Discharged': [('readonly', True)]}, related='patient.ex_smoker')
    age_start_ex_smoking = fields.Integer(string='Age Started to Smoke', readonly=False, states={'Discharged': [('readonly', True)]},
                                          related='patient.age_start_ex_smoking')
    age_quit_smoking = fields.Integer(string='Age of Quitting', help="Age of quitting smoking", readonly=False, states={'Discharged': [('readonly', True)]}, related='patient.age_quit_smoking')
    second_hand_smoker = fields.Boolean(string='Passive Smoker',
                                        help="Check it the patient is a passive / second-hand smoker", readonly=False, states={'Discharged': [('readonly', True)]},
                                        related='patient.second_hand_smoker')
    # drink
    alcohol = fields.Boolean(string='Drinks Alcohol', readonly=False, states={'Discharged': [('readonly', True)]}, related='patient.alcohol')
    age_start_drinking = fields.Integer(string='Age Started to Drink ', help="Date to start drinking", readonly=False, states={'Discharged': [('readonly', True)]},
                                        related='patient.age_start_drinking')

    alcohol_beer_number = fields.Integer(string='Beer / day', readonly=False, states={'Discharged': [('readonly', True)]},
                                         related='patient.alcohol_beer_number')
    alcohol_liquor_number = fields.Integer(string='Liquor / day', readonly=False, states={'Discharged': [('readonly', True)]},
                                           related='patient.alcohol_liquor_number')
    ex_alcoholic = fields.Boolean(string='Ex Alcoholic', readonly=False, states={'Discharged': [('readonly', True)]}, related='patient.ex_alcoholic')
    alcohol_wine_number = fields.Integer(string='Wine / day', readonly=False, states={'Discharged': [('readonly', True)]},
                                         related='patient.alcohol_wine_number')
    age_quit_drinking = fields.Integer(string='Age Quit Drinking ', help="Date to stop drinking", readonly=False, states={'Discharged': [('readonly', True)]}, related='patient.age_quit_drinking')

    # Vaccination
    vaccination_show = fields.Boolean()
    Vaccination = fields.Many2one('sm.shifa.generic.vaccines', string='Vaccine', readonly=False, states={'Discharged': [('readonly', True)]}, related='patient.Vaccination')
    vaccination_date = fields.Date(string='Date', readonly=False, states={'Discharged': [('readonly', True)]}, related='patient.vaccination_date')

    Vaccination_1st_add_other = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]},
                                               related='patient.Vaccination_1st_add_other')
    Vaccination_1st_add = fields.Many2one('sm.shifa.generic.vaccines', string='Procedures', readonly=False, states={'Discharged': [('readonly', True)]},
                                          related='patient.Vaccination_1st_add')
    Vaccination_1st_add_date = fields.Date(string='Date', readonly=False, states={'Discharged': [('readonly', True)]},
                                           related='patient.Vaccination_1st_add_date')

    Vaccination_2nd_add_other = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]},
                                               related='patient.Vaccination_2nd_add_other')
    Vaccination_2nd_add = fields.Many2one('sm.shifa.generic.vaccines', string='Procedures', readonly=False, states={'Discharged': [('readonly', True)]},
                                          related='patient.Vaccination_2nd_add')
    Vaccination_2nd_add_date = fields.Date(string='Date', readonly=False, states={'Discharged': [('readonly', True)]},
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


class ShifaPrescriptionInherit(models.Model):
    _inherit = 'oeh.medical.prescription'

    physician_admission = fields.Many2one('sm.shifa.physician.admission', string='physician',
                                          ondelete='cascade')


class ShifaFollowupInherit(models.Model):
    _inherit = 'sm.physician.admission.followup'

    physician_admission = fields.Many2one('sm.shifa.physician.admission', string='physician',
                                          ondelete='cascade')


class ShifaLabTestInherit(models.Model):
    _inherit = 'sm.shifa.lab.request'

    physician_admission = fields.Many2one('sm.shifa.physician.admission', string='physician',
                                          ondelete='cascade')


class ShifaImageTestInherit(models.Model):
    _inherit = 'sm.shifa.imaging.request'

    physician_admission = fields.Many2one('sm.shifa.physician.admission', string='physician',
                                          ondelete='cascade')


class ShifaReferralInherit(models.Model):
    _inherit = 'sm.shifa.referral'

    physician_admission = fields.Many2one('sm.shifa.physician.admission', string='physician',
                                          ondelete='cascade')


class ShifaInvestigationInherit(models.Model):
    _inherit = 'sm.shifa.investigation'

    physician_admission = fields.Many2one('sm.shifa.physician.admission', string='physician', ondelete='cascade')


class ShifaPhysicianAdmissionInvestigation(models.Model):
    _inherit = 'sm.shifa.physician.admission'

    investigation_ids = fields.One2many('sm.shifa.investigation', 'physician_Admission', string='Physician Admission')


class ShifaImagingTestForPhysicianAdmission(models.Model):
    _inherit = 'oeh.medical.imaging'

    physician_Admission = fields.Many2one('sm.shifa.physician.admission', string='Physician Admission')


class ShifaLabTestForPhysicianAdmission(models.Model):
    _inherit = 'oeh.medical.lab.test'

    physician_Admission = fields.Many2one('sm.shifa.physician.admission', string='Physician Admission')


class ShifaEvaluationForPhysicianAdmission(models.Model):
    _inherit = 'oeh.medical.evaluation'

    physician_Admission = fields.Many2one('sm.shifa.physician.admission', string='Physician Admission')


class ShifaPhysicianAdmissionExamination(models.Model):
    _inherit = 'sm.shifa.physician.admission'

    home_rounding_ids = fields.One2many('sm.shifa.home.rounding', 'admission_id', string='Home Rounding')

    # , readonly = True,
    # states = {'Hospitalized': [('readonly', False)],
    #           'On Ventilation': [('readonly', False)],
    #           'Ventilation Removed': [('readonly', False)]}

    # Glucose
    glycemia = fields.Float(string="Glycemia")
    hba1c = fields.Float(string="Glycated Hemoglobin")

    # Nutrition
    malnutrition = fields.Boolean(string="Malnutrition")
    dehydration = fields.Boolean(string="Dehydration")

    head_neck = fields.Boolean()
    head_neck_content = fields.Char()

    cardiovascular = fields.Boolean()
    cardiovascular_content = fields.Char()

    chest = fields.Boolean()
    chest_content = fields.Char()

    abdomen = fields.Boolean()
    abdomen_content = fields.Char()

    musculo = fields.Boolean()
    musculo_content = fields.Char()

    cns = fields.Boolean()
    cns_content = fields.Char()

    psychiatric = fields.Boolean()
    psychiatric_content = fields.Char()

    rectal = fields.Boolean()
    rectal_content = fields.Char()

    skin = fields.Boolean()
    skin_content = fields.Char()

    urine_test = fields.Boolean()
    urine_test_content = fields.Char()

    develop = fields.Boolean()
    develop_content = fields.Char()

    # Photo Images
    image1 = fields.Binary(string="Image 1")
    image2 = fields.Binary(string="Image 2")


class ShifaPrescribedMedicineForPhysicianAdmission(models.Model):
    _inherit = 'oeh.medical.inpatient.prescribed.medicine'

    physician_Admission = fields.Many2one('sm.shifa.physician.admission', string='Physician Admission', index=True)


class ShifaConsumedMedicineForPhysicianAdmission(models.Model):
    _inherit = 'oeh.medical.inpatient.consumed.medicine'

    physician_Admission = fields.Many2one('sm.shifa.physician.admission', string='Physician Admission', index=True)


class ShifaPhysicianExaminationTab(models.Model):
    _inherit = 'sm.shifa.physician.admission'
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

    # Examination tab
    # Pain Assessment
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
    ], readonly=False, states={'Discharged': [('readonly', True)]})
    admission_scale_used = fields.Selection([
        ('Numerical', 'Numerical'),
        ('Faces', 'Faces'),
        ('FLACC', 'FLACC'),
        ('ABBEY', 'ABBEY'),
    ], readonly=False, states={'Discharged': [('readonly', True)]})
    location_head = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    location_face = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    location_limbs = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    location_chest = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    location_abdomen = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    location_back = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    location_of_pain = fields.Text(readonly=False, states={'Discharged': [('readonly', True)]})

    Characteristics_dull = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    Characteristics_sharp = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    Characteristics_burning = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    Characteristics_throbbing = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    Characteristics_other = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    Characteristics_patient_own_words = fields.Text(readonly=False, states={'Discharged': [('readonly', True)]})

    onset_time_sudden = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    onset_time_gradual = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    onset_time_constant = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    onset_time_intermittent = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    onset_time_other = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    onset_time_fdv = fields.Text(readonly=False, states={'Discharged': [('readonly', True)]})

    provoking_factors_food = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    provoking_factors_rest = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    provoking_factors_movement = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    provoking_factors_palpation = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    provoking_factors_other = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    provoking_factors_patient_words = fields.Text(readonly=False, states={'Discharged': [('readonly', True)]})

    relieving_factors_rest = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    relieving_factors_medication = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    relieving_factors_heat = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    relieving_factors_distraction = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    relieving_factors_other = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    relieving_factors_patient_words = fields.Text(readonly=False, states={'Discharged': [('readonly', True)]})

    expressing_pain_verbal = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    expressing_pain_facial = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    expressing_pain_body = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    expressing_pain_other = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    expressing_pain_when_pain = fields.Text(readonly=False, states={'Discharged': [('readonly', True)]})

    effect_of_pain_nausea = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    effect_of_pain_vomiting = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    effect_of_pain_appetite = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    effect_of_pain_activity = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    effect_of_pain_relationship = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    effect_of_pain_emotions = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    effect_of_pain_concentration = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    effect_of_pain_sleep = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    effect_of_pain_other = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    effect_of_pain_other_text = fields.Text(readonly=False, states={'Discharged': [('readonly', True)]})

    pain_management_advice_analgesia = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    pain_management_change_of = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    pain_management_refer_physician = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    pain_management_refer_physician_home = fields.Boolean(string="Home Care", readonly=False,
                                                          states={'Start': [('readonly', False)]})
    pain_management_refer_physician_palliative = fields.Boolean(string="palliative", readonly=False, states={'Discharged': [('readonly', True)]})
    pain_management_refer_physician_primary = fields.Boolean(string="primary", readonly=False, states={'Discharged': [('readonly', True)]})
    pain_management_refer_hospital = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    pain_management_other = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    pain_management_other_text = fields.Text(readonly=False, states={'Discharged': [('readonly', True)]})
    pain_management_comment = fields.Text(readonly=False, states={'Discharged': [('readonly', True)]})

    # General Condition
    general_condition_show = fields.Boolean()
    general_condition = fields.Text(string='General Condition', readonly=False, states={'Discharged': [('readonly', True)]})

    # EENT
    EENT_show = fields.Boolean()
    eent_eye = fields.Boolean(default=True, readonly=False, states={'Discharged': [('readonly', True)]})
    eent_eye_condition = fields.Char(readonly=False, states={'Discharged': [('readonly', True)]})
    eent_eye_vision = fields.Char(readonly=False, states={'Discharged': [('readonly', True)]})
    eent_ear = fields.Boolean(default=True, readonly=False, states={'Discharged': [('readonly', True)]})
    eent_ear_content = fields.Char(readonly=False, states={'Discharged': [('readonly', True)]})
    eent_nose = fields.Boolean(default=True, readonly=False, states={'Discharged': [('readonly', True)]})
    eent_nose_content = fields.Char(readonly=False, states={'Discharged': [('readonly', True)]})
    eent_throut = fields.Boolean(default=True, readonly=False, states={'Discharged': [('readonly', True)]})
    eent_throut_content = fields.Char(readonly=False, states={'Discharged': [('readonly', True)]})
    eent_neck = fields.Boolean(default=True, readonly=False, states={'Discharged': [('readonly', True)]})
    eent_neck_content = fields.Char(readonly=False, states={'Discharged': [('readonly', True)]})
    eent_remarks = fields.Text(readonly=False, states={'Discharged': [('readonly', True)]})

    # csv
    csv_show = fields.Boolean()
    cvs_h_sound_1_2 = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    cvs_h_sound_3 = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    cvs_h_sound_4 = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    cvs_h_sound_click = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    cvs_h_sound_murmurs = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    cvs_h_sound_other = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    cvs_h_sound_other_text = fields.Char(readonly=False, states={'Discharged': [('readonly', True)]})

    cvs_rhythm = fields.Selection([
        ('Regular', 'Regular'),
        ('Irregular', 'Irregular'),
        ('Regular Irregular', 'Regular Irregular'),
        ('Irregular Irregular', 'Irregular Irregular'),
    ], default='Regular', readonly=False, states={'Discharged': [('readonly', True)]})
    cvs_peripherial_pulse = fields.Selection([
        ('Normal Palpable', 'Normal Palpable'),
        ('Absent Without Pulse', 'Absent Without Pulse'),
        ('Diminished', 'Diminished'),
        ('Bounding', 'Bounding'),
        ('Full and brisk', 'Full and brisk'),
    ], default='Normal Palpable', readonly=False, states={'Discharged': [('readonly', True)]})

    cvs_edema_yes_no = fields.Selection(yes_no, readonly=False, states={'Discharged': [('readonly', True)]})
    cvs_edema_yes_type = fields.Selection([
        ('Pitting', 'Pitting'),
        ('Non-Pitting', 'Non-Pitting'),
    ], readonly=False, states={'Discharged': [('readonly', True)]})
    cvs_edema_yes_location = fields.Text(readonly=False, states={'Discharged': [('readonly', True)]})
    cvs_edema_yes_grade = fields.Selection([
        ('I- 2mm Depth', 'I- 2mm Depth'),
        ('II- 4mm Depth', 'II- 4mm Depth'),
        ('III- 6mm Depth', 'III- 6mm Depth'),
        ('IV- 8mm Depth', 'IV- 8mm Depth'),
    ], readonly=False, states={'Discharged': [('readonly', True)]})
    cvs_edema_yes_capillary = fields.Selection([
        ('Less than', 'Less than'),
        ('2-3', '2-3'),
        ('3-4', '3-4'),
        ('4-5', '4-5'),
        ('More than 5', 'More than 5'),
    ], readonly=False, states={'Discharged': [('readonly', True)]})

    cvs_parenteral_devices_yes_no = fields.Selection(yes_no, readonly=False, states={'Discharged': [('readonly', True)]})
    cvs_parenteral_devices_yes_sel = fields.Selection([
        ('Central Line', 'Central Line'),
        ('TPN', 'TPN'),
        ('IV Therapy', 'IV Therapy'),
        ('PICC Line', 'PICC Line'),
        ('Other', 'Other'),
    ], readonly=False, states={'Discharged': [('readonly', True)]})
    cvs_remarks = fields.Text(readonly=False, states={'Discharged': [('readonly', True)]})
    # Respiratory
    respiratory_show = fields.Boolean()
    lung_sounds_clear = fields.Boolean(default=True, readonly=False, states={'Discharged': [('readonly', True)]})
    lung_sounds_diminished = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    lung_sounds_absent = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    lung_sounds_fine_crackles = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    lung_sounds_rhonchi = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    lung_sounds_stridor = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    lung_sounds_wheeze = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    lung_sounds_coarse_crackles = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})

    Location_bilateral = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    Location_left_lower = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    Location_left_middle = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    Location_left_upper = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    Location_lower = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    Location_upper = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    Location_right_lower = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    Location_right_middle = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    Location_right_upper = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})

    type_regular = fields.Boolean(default=True, readonly=False, states={'Discharged': [('readonly', True)]})
    type_irregular = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    type_rapid = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    type_dyspnea = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    type_apnea = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    type_tachypnea = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    type_orthopnea = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    type_accessory_muscles = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    type_snoring_mechanical = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    Cough_yes_no = fields.Selection(yes_no, readonly=False, states={'Discharged': [('readonly', True)]})
    cough_yes_type = fields.Selection([
        ('Productive', 'Productive'),
        ('none-productive', 'none-productive'),
        ('Spontaneous', 'Spontaneous'),
    ], readonly=False, states={'Discharged': [('readonly', True)]})
    cough_yes_frequency = fields.Selection([
        ('Spontaneous', 'Spontaneous'),
        ('Occassional', 'Occassional'),
        ('Persistent', 'Persistent'),
    ], readonly=False, states={'Discharged': [('readonly', True)]})
    cough_yes_amount = fields.Selection([
        ('Scanty', 'Scanty'),
        ('Moderate', 'Moderate'),
        ('Large', 'Large'),
    ], readonly=False, states={'Discharged': [('readonly', True)]})
    cough_yes_characteristic = fields.Selection([
        ('Clear', 'Clear'),
        ('Yellow', 'Yellow'),
        ('Mucoid', 'Mucoid'),
        ('Mucopurulent', 'Mucopurulent'),
        ('Purulent', 'Purulent'),
        ('Pink Frothy', 'Pink Frothy'),
        ('Blood streaked', 'Blood streaked'),
        ('Bloody', 'Bloody'),
    ], readonly=False, states={'Discharged': [('readonly', True)]})

    respiratory_support_yes_no = fields.Selection(yes_no, readonly=False, states={'Discharged': [('readonly', True)]})
    respiratory_support_yes_oxygen = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    respiratory_support_yes_oxygen_text = fields.Text(readonly=False, states={'Discharged': [('readonly', True)]})
    respiratory_support_yes_trachestory = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    respiratory_support_yes_trachestory_text = fields.Text(readonly=False, states={'Discharged': [('readonly', True)]})
    respiratory_support_yes_ventilator = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    respiratory_support_yes_ventilator_text = fields.Text(readonly=False, states={'Discharged': [('readonly', True)]})

    suction_yes_no = fields.Selection(yes_no, readonly=False, states={'Discharged': [('readonly', True)]})
    suction_yes_type = fields.Selection([
        ('Nasal', 'Nasal'),
        ('Oral', 'Oral'),
        ('Trachestory', 'Trachestory'),
    ], readonly=False, states={'Discharged': [('readonly', True)]})
    suction_yes_frequency = fields.Integer(readonly=False, states={'Discharged': [('readonly', True)]})

    nebulization_yes_no = fields.Selection(yes_no, readonly=False, states={'Discharged': [('readonly', True)]})
    nebulization_yes_frequency = fields.Integer(readonly=False, states={'Discharged': [('readonly', True)]})
    nebulization_yes_medication = fields.Many2one('oeh.medical.medicines', string='Medicines', readonly=False,
                                                  states={'Start': [('readonly', False)]})
    respiratory_remarks = fields.Text(readonly=False, states={'Discharged': [('readonly', True)]})

    # Neuralogical

    neuralogical_show = fields.Boolean()
    neuralogical_left_eye = fields.Selection(number_neuralogical, readonly=False, states={'Discharged': [('readonly', True)]})
    neuralogical_right_eye = fields.Selection(number_neuralogical, readonly=False, states={'Discharged': [('readonly', True)]})
    neuralogical_pupil_reaction = fields.Selection([
        ('Equal round, reactive', 'Equal round, reactive'),
        ('Equal round, none reactive', 'Equal round, none reactive'),
        ('Miosis', 'Miosis'),
        ('Mydriasis', 'Mydriasis'),
        ('Sluggish', 'Sluggish'),
        ('Brisk', 'Brisk'),
        ('Elliptical', 'Elliptical'),
        ('Anisocoria', 'Anisocoria'),
    ], default='Equal round, reactive', readonly=False, states={'Discharged': [('readonly', True)]})
    neuralogical_old = fields.Selection([
        ('Greater Than 5 years Old', 'Greater Than 5 years Old'),
        ('2 to 5 Years Old', '2 to 5 Years Old'),
        ('Less than 2 Years Old', 'Less than 2 Years Old'),
    ], readonly=False, states={'Discharged': [('readonly', True)]})
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
    ], readonly=False, states={'Discharged': [('readonly', True)]})
    neuralogical_greater_than_5_years_facial = fields.Selection([
        ('Symmetric', 'Symmetric'),
        ('Unequal facial movement', 'Unequal facial movement'),
        ('Drooping left side of face', 'Drooping left side of face'),
        ('Drooping left side of mouth', 'Drooping left side of mouth'),
        ('Drooping right side of face', 'Drooping right side of face'),
        ('Drooping right side of mouth', 'Drooping right side of mouth'),
    ], readonly=False, states={'Discharged': [('readonly', True)]})
    neuralogical_greater_than_5_years_glascow = fields.Float(compute=_compute_greater_5_old)
    neuralogical_greater_than_5_years_eye = fields.Selection(eye_momement, readonly=False, states={'Discharged': [('readonly', True)]})
    neuralogical_greater_than_5_years_motor = fields.Selection(motor_response, readonly=False, states={'Discharged': [('readonly', True)]})
    neuralogical_greater_than_5_years_verbal = fields.Selection([
        ('Orient', 'Orient'),
        ('Confused', 'Confused'),
        ('Inappropriate', 'Inappropriate'),
        ('Incompratensive', 'Incompratensive'),
        ('No verable response', 'No verable response'),
    ], readonly=False, states={'Discharged': [('readonly', True)]})
    neuralogical_2_to_5_level = fields.Selection(level_consciousness, readonly=False, states={'Discharged': [('readonly', True)]})
    neuralogical_2_to_5_glascow = fields.Float(compute=_compute_2_5_old)
    neuralogical_2_to_5_eye = fields.Selection(eye_momement, readonly=False, states={'Discharged': [('readonly', True)]})
    neuralogical_2_to_5_motor = fields.Selection(motor_response, readonly=False, states={'Discharged': [('readonly', True)]})
    neuralogical_2_to_5_verbal = fields.Selection([
        ('Appropriate Words', 'Appropriate Words'),
        ('Inappropriate Word', 'Inappropriate Word'),
        ('Cries/Screams', 'Cries/Screams'),
        ('Grunts', 'Grunts'),
        ('No response', 'No response'),
    ], readonly=False, states={'Discharged': [('readonly', True)]})
    neuralogical_less_than_2_level = fields.Selection(level_consciousness, readonly=False,
                                                      states={'Start': [('readonly', False)]})
    neuralogical_less_than_2_glascow = fields.Float(compute=_compute_less_2)
    neuralogical_less_than_2_eye = fields.Selection(eye_momement, readonly=False, states={'Discharged': [('readonly', True)]})
    neuralogical_less_than_2_motor = fields.Selection([
        ('Spontaneous movements', 'Spontaneous movements'),
        ('Localizes pain', 'Localizes pain'),
        ('Flexion withdrawal', 'Flexion withdrawal'),
        ('Abnormal flexion', 'Abnormal flexion'),
        ('Abnormal extension', 'Abnormal extension'),
        ('No response', 'No response'),
    ], readonly=False, states={'Discharged': [('readonly', True)]})
    neuralogical_less_than_2_verbal = fields.Selection([
        ('Coos and smiles appropriate', 'Coos and smiles appropriate'),
        ('Cries', 'Cries'),
        ('Inappropriate crying/screaming', 'Inappropriate crying/screaming'),
        ('Grunts', 'Grunts'),
        ('No response', 'No response'),
    ], readonly=False, states={'Discharged': [('readonly', True)]})
    neuralogical_remarks = fields.Text(readonly=False, states={'Discharged': [('readonly', True)]})
    # Gastrointestinal
    gastrointestinal_show = fields.Boolean()
    gastrointestinal_bowel_sound = fields.Selection([
        ('Active', 'Active'),
        ('Absent', 'Absent'),
        ('Hypoactive', 'Hypoactive'),
        ('Hyperactive', 'Hyperactive'),
    ], default='Active', readonly=False, states={'Discharged': [('readonly', True)]})
    gastrointestinal_abdomen_lax = fields.Boolean(default=True, readonly=False, states={'Discharged': [('readonly', True)]})
    gastrointestinal_abdomen_soft = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    gastrointestinal_abdomen_firm = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    gastrointestinal_abdomen_distended = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    gastrointestinal_abdomen_tender = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    gastrointestinal_stool_color = fields.Selection([
        ('Brown', 'Brown'),
        ('Yellow', 'Yellow'),
        ('Black', 'Black'),
        ('Bright Red', 'Bright Red'),
        ('Dark Red', 'Dark Red'),
        ('Clay', 'Clay'),
    ], default='Brown', readonly=False, states={'Discharged': [('readonly', True)]})
    gastrointestinal_stool_loose = fields.Boolean(default=True, readonly=False, states={'Discharged': [('readonly', True)]})
    gastrointestinal_stool_hard = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    gastrointestinal_stool_mucoid = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    gastrointestinal_stool_soft = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    gastrointestinal_stool_tarry = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    gastrointestinal_stool_formed = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    gastrointestinal_stool_semi_formed = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    gastrointestinal_stool_bloody = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    gastrointestinal_stoma_none = fields.Boolean(default=True, readonly=False, states={'Discharged': [('readonly', True)]})
    gastrointestinal_stoma_colostory = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    gastrointestinal_stoma_ileostomy = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    gastrointestinal_stoma_peg = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    gastrointestinal_stoma_pej = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    gastrointestinal_stoma_urostomy = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    gastrointestinal_problem_none = fields.Boolean(default=True, readonly=False, states={'Discharged': [('readonly', True)]})
    gastrointestinal_problem_nausea = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    gastrointestinal_problem_vomiting = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    gastrointestinal_problem_colic = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    gastrointestinal_problem_diarrhea = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    gastrointestinal_problem_constipation = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    gastrointestinal_problem_dysphagia = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    gastrointestinal_problem_hemorrhoids = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    gastrointestinal_problem_anal_fissure = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    gastrointestinal_problem_anal_fistula = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    gastrointestinal_problem_other = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    gastrointestinal_problem_other_text = fields.Text(readonly=False, states={'Discharged': [('readonly', True)]})
    gastrointestinal_bowel_movement_none = fields.Boolean(default=True, readonly=False, states={'Discharged': [('readonly', True)]})
    gastrointestinal_bowel_movement_laxative = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    gastrointestinal_bowel_movement_enema = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    gastrointestinal_bowel_movement_stoma = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    gastrointestinal_bowel_movement_stool_softener = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    gastrointestinal_bowel_movement_suppository = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    gastrointestinal_bowel_movement_digital = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    gastrointestinal_bowel_movement_other = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    gastrointestinal_bowel_movement_other_text = fields.Text(readonly=False, states={'Discharged': [('readonly', True)]})
    gastrointestinal_enteral_device_none = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    gastrointestinal_enteral_device_nasogastric_tube = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    gastrointestinal_enteral_device_orogastric_tube = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    gastrointestinal_enteral_device_gastro_jejunal = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    gastrointestinal_enteral_device_peg = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    gastrointestinal_enteral_device_pej = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    gastrointestinal_enteral_device_pd = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    gastrointestinal_enteral_device_other = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    gastrointestinal_enteral_device_other_text = fields.Text(readonly=False, states={'Discharged': [('readonly', True)]})
    gastrointestinal_remarks = fields.Text(readonly=False, states={'Discharged': [('readonly', True)]})

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
    ], default='Pale Yellow', readonly=False, states={'Discharged': [('readonly', True)]})
    genitourinary_urine_appearance = fields.Selection([
        ('Clear', 'Clear'),
        ('Cloudy', 'Cloudy'),
        ('With Sediment', 'With Sediment'),
    ], default='Clear', readonly=False, states={'Discharged': [('readonly', True)]})
    genitourinary_urine_amount = fields.Selection([
        ('Adequate', 'Adequate'),
        ('Scanty', 'Scanty'),
        ('Large', 'Large'),
    ], default='Adequate', readonly=False, states={'Discharged': [('readonly', True)]})
    genitourinary_urination_none = fields.Boolean(default=True, readonly=False, states={'Discharged': [('readonly', True)]})
    genitourinary_urination_dysuria = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    genitourinary_urination_frequency = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    genitourinary_urination_urgency = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    genitourinary_urination_hesitancy = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    genitourinary_urination_incontinence = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    genitourinary_urination_inability_to_void = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    genitourinary_urination_nocturia = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    genitourinary_urination_retention = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    genitourinary_urination_suprapubic_pain = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    genitourinary_urination_loin_pain = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    genitourinary_urination_colicky_pain = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    genitourinary_urination_difficult_control = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    genitourinary_urination_other = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    genitourinary_urination_other_text = fields.Text(readonly=False, states={'Discharged': [('readonly', True)]})
    genitourinary_urination_assistance = fields.Selection([
        ('None', 'None'),
        ('Indwelling Catheter', 'Indwelling Catheter'),
        ('Condom Catheter', 'Condom Catheter'),
        ('Intermittent bladder Wash', 'Intermittent bladder Wash'),
        ('Urostomy', 'Urostomy'),
        ('Suprapubic Catheter', 'Suprapubic Catheter'),
    ], default='None', readonly=False, states={'Discharged': [('readonly', True)]})
    genitourinary_remarks = fields.Text(readonly=False, states={'Discharged': [('readonly', True)]})
    # Integumentary
    integumentary_show = fields.Boolean()
    appearance_normal = fields.Boolean(string='Normal', default=True, readonly=False, states={'Discharged': [('readonly', True)]})
    appearance_dry = fields.Boolean(string='Dry', readonly=False, states={'Discharged': [('readonly', True)]})
    appearance_edema = fields.Boolean(string='Edema', readonly=False, states={'Discharged': [('readonly', True)]})
    appearance_flushed = fields.Boolean(string='Flushed', readonly=False, states={'Discharged': [('readonly', True)]})
    appearance_pale = fields.Boolean(string='clay', readonly=False, states={'Discharged': [('readonly', True)]})
    appearance_rash = fields.Boolean(string='Rash', readonly=False, states={'Discharged': [('readonly', True)]})
    appearance_jundiced = fields.Boolean(string='Jandiced', readonly=False, states={'Discharged': [('readonly', True)]})
    appearance_eczema = fields.Boolean(string='Eczema', readonly=False, states={'Discharged': [('readonly', True)]})
    appearance_hemayome = fields.Boolean(string='Hemayome', readonly=False, states={'Discharged': [('readonly', True)]})
    appearance_rusty = fields.Boolean(string='Rusty', readonly=False, states={'Discharged': [('readonly', True)]})
    appearance_cyanotic = fields.Boolean(string='Cyanotic', readonly=False, states={'Discharged': [('readonly', True)]})
    appearance_bruises = fields.Boolean(string='Bruises', readonly=False, states={'Discharged': [('readonly', True)]})
    appearance_abrasion = fields.Boolean(string='Abrasion', readonly=False, states={'Discharged': [('readonly', True)]})
    appearance_sores = fields.Boolean(string='Sores', readonly=False, states={'Discharged': [('readonly', True)]})
    integumentary_turgor = fields.Selection([
        ('Elastic', 'Elastic'),
        ('Normal for age', 'Normal for age'),
        ('Poor', 'Poor'),
    ], default='Elastic', readonly=False, states={'Discharged': [('readonly', True)]})
    integumentary_temperature = fields.Selection([
        ('Normal', 'Normal'),
        ('Cool', 'Cool'),
        ('Cold', 'Cold'),
        ('Warm', 'Warm'),
        ('Hot', 'Hot'),
    ], default='Normal', readonly=False, states={'Discharged': [('readonly', True)]})
    integumentary_remarks = fields.Text(readonly=False, states={'Discharged': [('readonly', True)]})

    # Infections
    infection_show = fields.Boolean()
    infection_nad = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    infection_content = fields.Char(readonly=False, states={'Discharged': [('readonly', True)]})

    # psychological
    psychological_show = fields.Boolean()
    psychological_nad = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    psychological_content = fields.Char(readonly=False, states={'Discharged': [('readonly', True)]})
    # reproductive
    reproductive_show = fields.Boolean()
    reproductive_nad = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    reproductive_content = fields.Char(readonly=False, states={'Discharged': [('readonly', True)]})
    # musculoskeletal
    musculoskeletal_show = fields.Boolean()
    musculoskeletal_left_upper_extremity = fields.Selection(musculoskeletal_extremity,
                                                            default='Active Against Gravity and Resistance',
                                                            readonly=False, states={'Discharged': [('readonly', True)]})
    musculoskeletal_right_upper_extremity = fields.Selection(musculoskeletal_extremity,
                                                             default='Active Against Gravity and Resistance',
                                                             readonly=False, states={'Discharged': [('readonly', True)]})
    musculoskeletal_left_lower_extremity = fields.Selection(musculoskeletal_extremity,
                                                            default='Active Against Gravity and Resistance',
                                                            readonly=False, states={'Discharged': [('readonly', True)]})
    musculoskeletal_right_lower_extremity = fields.Selection(musculoskeletal_extremity,
                                                             default='Active Against Gravity and Resistance',
                                                             readonly=False, states={'Discharged': [('readonly', True)]})
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
    ], default='Normal', readonly=False, states={'Discharged': [('readonly', True)]})
    musculoskeletal_remarks = fields.Text(readonly=False, states={'Discharged': [('readonly', True)]})

    # sensory
    sensory_show = fields.Boolean()
    sensory_nad = fields.Boolean(readonly=False, states={'Discharged': [('readonly', True)]})
    sensory_content = fields.Char(readonly=False, states={'Discharged': [('readonly', True)]})
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


class ShifaLabRequestTestPhyAdm(models.Model):
    _inherit = 'sm.shifa.lab.request.line'

    phy_adm = fields.Many2one("sm.shifa.physician.admission", string='phy_adm')


class ShifaImagingRequestTestPhyAdm(models.Model):
    _inherit = 'sm.shifa.imaging.request.line'

    phy_adm = fields.Many2one("sm.shifa.physician.admission", string='phy_adm')
