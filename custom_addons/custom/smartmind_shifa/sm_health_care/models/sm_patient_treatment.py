from datetime import datetime

from dateutil.relativedelta import relativedelta
from odoo import models, fields, api


class ShifaPatientTreatment(models.Model):
    _name = "sm.shifa.patient.treatment"
    _description = "Patient Treatment Plan and Progress Summary"
    home_care = [
        ('Visit Frequency', 'Visit Frequency'),
        ('PRN Frequency', 'PRN Frequency'),
    ]
    Yes_No = [
        ('Yes', 'Yes'),
        ('No', 'No'),
    ]
    visit = [
        ('Visited', 'Visited'),
        ('Not visited', 'Not visited'),
    ]
    visit_times = [
        ('Once', 'Once'),
        ('Twice', 'Twice'),
        ('Multiple', 'Multiple'),
    ]

    icu_admission_id = fields.Many2one('oeh.medical.icu.admission', string='Home Admission', index=True)
    patient_treatment_code = fields.Char('Patient Treatment Plan Reference', index=True, copy=False)
    patient = fields.Many2one('oeh.medical.patient', string='Patient', help="Patient Name", required=True)
    date_enrolled = fields.Date(string='Date Enrolled')
    date_60days = fields.Date()
    program = fields.Char(string='Program')
    # ========= Services Provided ========= #
    services_provided_wound_care = fields.Boolean()
    services_provided_stoma_care = fields.Boolean()
    services_provided_PEG_tube = fields.Boolean()
    services_provided_TPN = fields.Boolean()
    services_provided_NGT = fields.Boolean()
    services_provided_oxygen_dependent = fields.Boolean()
    services_provided_CPAP_dependent = fields.Boolean()
    services_provided_BiPAP_dependent = fields.Boolean()
    services_provided_hydration_therapy = fields.Boolean()
    services_provided_hypodermoclysis = fields.Boolean()
    services_VAC_therapy = fields.Boolean()
    services_provided_ventilator_dependent = fields.Boolean()
    services_provided_tracheostomy = fields.Boolean()
    services_provided_pain_management = fields.Boolean()
    services_provided_indwelling_foley_catheter = fields.Boolean()
    services_provided_parenteral_antimicrobial = fields.Boolean()
    services_provided_INR_monitoring = fields.Boolean()
    services_provided_prevention_pressure_ulcer = fields.Boolean()
    services_provided_O2_via_nasal_cannula = fields.Boolean()
    services_provided_symptom_management = fields.Boolean()
    services_provided_drain_tube_management = fields.Boolean()
    services_provided_medication_management = fields.Boolean()
    services_provided_warfarin_stabilization = fields.Boolean()

    # ============ mental_status ========#
    mental_status_oriented = fields.Boolean()
    mental_status_comatose = fields.Boolean()
    mental_status_forgetful = fields.Boolean()
    mental_status_depressed = fields.Boolean()
    mental_status_lethargic = fields.Boolean()
    mental_status_agitated = fields.Boolean()
    mental_status_disoriented = fields.Boolean()

    # ============ functional_limitation ========#
    functional_limitation_amputation = fields.Boolean()
    functional_limitation_contracture = fields.Boolean()
    functional_limitation_paralysis = fields.Boolean()
    functional_limitation_ambulation = fields.Boolean()
    functional_limitation_speech = fields.Boolean()
    functional_limitation_hearing = fields.Boolean()
    functional_limitation_endurance = fields.Boolean()
    functional_limitation_legally_blind = fields.Boolean()
    functional_limitation_bowel_bladder = fields.Boolean()
    functional_limitation_dyspnea_minimal_exertion = fields.Boolean()
    functional_limitation_other = fields.Boolean()
    functional_limitation_other_content = fields.Char()

    # ============= Activities Permitted =============== #
    activities_permitted_bed_rest = fields.Boolean()
    activities_permitted_exercises_prescribed = fields.Boolean()
    activities_permitted_transfer_bed_chair = fields.Boolean()
    activities_permitted_cane = fields.Boolean()
    activities_permitted_crutches = fields.Boolean()
    activities_permitted_up_tolerated = fields.Boolean()
    activities_permitted_complete_bed_rest = fields.Boolean()
    activities_permitted_partial_weight_bearing = fields.Boolean()
    activities_permitted_Walker = fields.Boolean()
    activities_permitted_wheelchair = fields.Boolean()
    activities_permitted_No_restrictions = fields.Boolean()
    activities_permitted_independent_home = fields.Boolean()

    patient_condition = fields.Selection([
        ('Declined', 'Declined'),
        ('Unstable', 'Unstable'),
        ('Stable', 'Stable'),
        ('Improved', 'Improved'),
        ('Unchanged', 'Unchanged'),
    ], string='Patient Condition')
    prognosis = fields.Selection([
        ('Poor', 'Poor'),
        ('Guarded', 'Guarded'),
        ('Fair', 'Fair'),
        ('Good', 'Good'),
        ('Excellent', 'Excellent'),
    ], string='Prognosis')

    potential_risks_safety_measures = fields.Text()
    admission_goal = fields.Text()

    # ============ Nursing Progress Summary ============== #
    nursing_visit = fields.Selection(visit, string='Visit')
    nursing_visit_times = fields.Selection(visit_times, string='How many times?')
    nursing_maintain_blood_pressure = fields.Selection(Yes_No)
    nursing_maintain_blood_pressure_ifNo = fields.Text()
    nursing_maintain_blood_glucose = fields.Selection(Yes_No)
    nursing_maintain_blood_glucose_ifNo = fields.Text()
    nursing_status_improved_homestay = fields.Selection(Yes_No)
    nursing_status_improved_homestay_ifNo = fields.Text()
    nursing_urinary_infection_indwelling = fields.Selection(Yes_No)
    nursing_urinary_infection_indwelling_ifYes = fields.Text()
    nursing_latest_wound_measurement = fields.Text()
    nursing_comments = fields.Text()

    # ============ Respiratory Therapist Progress Summary ============== #
    respiratory_visit = fields.Selection(visit, string='Visit')
    respiratory_visit_times = fields.Selection(visit_times, string='How many times?')
    respiratory_hospitalized_2months = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No'),
        ('Once', 'Once'),
        ('Twice', 'Twice'),
        ('Multiple', 'Multiple'),
        ('KFMC', 'KFMC'),
        ('Other', 'Other'),

    ])
    respiratory_hospitalized_2months_others = fields.Text()
    respiratory_trache_changed = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No'),
        ('NA', 'NA'),
        ('Other', 'Other'),
    ])
    respiratory_trache_changed_others = fields.Text()
    respiratory_ventilator_support = fields.Selection(Yes_No)
    respiratory_history_ventilator_malfunctioning = fields.Selection(Yes_No)
    respiratory_ventilator_current_setting = fields.Text()
    respiratory_comments = fields.Text()

    # ============ Occupational Therapist Progress Summary ============== #
    occupational_visit = fields.Selection(visit, string='Visit')
    occupational_visit_times = fields.Selection(visit_times, string='How many times?')
    occupational_comments = fields.Text()

    # ============ Physiotherapist Progress Summary ============== #
    physiotherapist_visit = fields.Selection(visit, string='Visit')
    physiotherapist_visit_times = fields.Selection(visit_times, string='How many times?')
    physiotherapist_comments = fields.Text()

    # ============ Social Worker Progress Summary ============== #
    social_worker_visit = fields.Selection(visit, string='Visit')
    social_worker_visit_times = fields.Selection(visit_times, string='How many times?')
    social_worker_comments = fields.Text()

    # ============ Nutritionist Progress Summary ============== #
    nutritionist_visit = fields.Selection(visit, string='Visit')
    nutritionist_visit_times = fields.Selection(visit_times, string='How many times?')
    nutritionist_comments = fields.Text()

    # ======= Goal and treatment plan ======== #
    new_goal = fields.Text()
    plan_care = fields.Text()

    following_protocol_wound_care = fields.Boolean()
    following_protocol_vac_therapy = fields.Boolean()
    following_protocol_home_tpn = fields.Boolean()
    following_protocol_home_infusion = fields.Boolean()
    following_protocol_home_antibiotics = fields.Boolean()
    following_protocol_enteral_feeding = fields.Boolean()
    following_protocol_advanced_airway = fields.Boolean()
    following_protocol_indwelling_urinary = fields.Boolean()
    following_protocol_prevention_pressure = fields.Boolean()
    following_protocol_drain_tube = fields.Boolean()
    following_protocol_anticoagulation = fields.Boolean()
    following_protocol_bipap_manag = fields.Boolean()
    following_protocol_cpap_manag = fields.Boolean()
    following_protocol_adult_oxygen = fields.Boolean()
    following_protocol_pediatric_oxygen = fields.Boolean()
    following_protocol_mechanical_ventilation = fields.Boolean()
    following_protocol_pediatric_tracheotomy = fields.Boolean()
    following_protocol_adult_tracheotomy = fields.Boolean()
    following_protocol_apnea_monitoring = fields.Boolean()

    re_certification_oxygen_cylinder = fields.Boolean()
    re_certification_oxygen_concentrator = fields.Boolean()
    re_certification_feeding_pump = fields.Boolean()
    re_certification_vest = fields.Boolean()
    re_certification_pulse_oximetry = fields.Boolean()
    re_certification_acti_vac_machine = fields.Boolean()
    re_certification_infusion_pump = fields.Boolean()
    re_certification_air_compressor = fields.Boolean()
    re_certification_ventilator = fields.Boolean()
    re_certification_suction_machine = fields.Boolean()
    re_certification_nebulizer_machine = fields.Boolean()
    re_certification_electronic_bed = fields.Boolean()
    re_certification_wheel_chair = fields.Boolean()
    re_certification_hoyer_lift = fields.Boolean()
    re_certification_bipap_cpap = fields.Boolean()

    following_services_physician = fields.Selection(home_care)
    following_services_nurse = fields.Selection(home_care)
    following_services_respiratory = fields.Selection(home_care)
    following_services_physiotherapist = fields.Selection(home_care)
    following_services_occupational = fields.Selection(home_care)
    following_services_social_worker = fields.Selection(home_care)
    following_services_nutritionist = fields.Selection(home_care)

    #  doctor name
    approved_by_doctor = fields.Many2one('oeh.medical.physician',domain=[('role_type', '=', 'HD'), ('active', '=', True)])
    consent_show = fields.Boolean()
    consent_file1 = fields.Binary()
    consent_file2 = fields.Binary()

    @api.model
    def create(self, vals):
        vals['patient_treatment_code'] = self.env['ir.sequence'].next_by_code('sm.shifa.patient.treatment')
        return super(ShifaPatientTreatment, self).create(vals)

    @api.onchange('date_enrolled')
    def _check_change_60days(self):
        if self.date_enrolled:
            date_1 = (datetime.strptime(str(self.date_enrolled), '%Y-%m-%d') + relativedelta(days=+ 60))
            self.date_60days = date_1
        else:
            self.date_60days = datetime.today()

    @api.onchange('nursing_visit', 'respiratory_visit', 'occupational_visit', 'physiotherapist_visit',
                  'social_worker_visit', 'nutritionist_visit')
    def _check_visit(self):
        if self.nursing_visit == 'Not visited':
            self.nursing_visit_times = ''
        if self.respiratory_visit == 'Not visited':
            self.respiratory_visit_times = ''
        if self.occupational_visit == 'Not visited':
            self.occupational_visit_times = ''
        if self.physiotherapist_visit == 'Not visited':
            self.physiotherapist_visit_times = ''
        if self.social_worker_visit == 'Not visited':
            self.social_worker_visit_times = ''
        if self.nutritionist_visit == 'Not visited':
            self.nutritionist_visit_times = ''

    @api.onchange('nursing_maintain_blood_pressure', 'nursing_maintain_blood_glucose',
                  'nursing_status_improved_homestay', 'nursing_urinary_infection_indwelling',
                  'respiratory_hospitalized_2months', 'functional_limitation_other', 'respiratory_trache_changed')
    def _check_yes(self):
        if not self.nursing_maintain_blood_pressure == 'No':
            self.nursing_maintain_blood_pressure_ifNo = ''
        if not self.nursing_maintain_blood_glucose == 'No':
            self.nursing_maintain_blood_glucose_ifNo = ''
        if not self.nursing_status_improved_homestay == 'No':
            self.nursing_status_improved_homestay_ifNo = ''
        if self.nursing_urinary_infection_indwelling == 'No':
            self.nursing_urinary_infection_indwelling_ifYes = ''
        if not self.respiratory_hospitalized_2months == 'Other':
            self.respiratory_hospitalized_2months_others = ''
        if not self.functional_limitation_other:
            self.functional_limitation_other_content = ''
        if not self.respiratory_trache_changed == 'Other':
            self.respiratory_trache_changed_others = ''
