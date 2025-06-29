from odoo import models, fields, api
import datetime
from odoo.exceptions import ValidationError
from datetime import date
from psycopg2._psycopg import List


class AnticoagulationManagement(models.Model):
    _name = 'sm.shifa.anticoagulation.management'
    _description = 'Anticoagulation Management'
    _rec_name = 'anticoagulation_management_code'

    ADMISSION_STATES = [
        ('Draft', 'Draft'),
        ('Start', 'Start'),
        ('Admitted', 'Admitted'),
        ('Discharged', 'Discharged'),
    ]
    yes_no_na = [
        ('Yes', 'Yes'),
        ('No', 'No'),
        ('NA', 'NA'),
    ]

    def _get_anticoagulation(self):
        """Return default anticoagulation value"""
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

    anticoagulation_management_code = fields.Char('Reference', index=True, copy=False)
    patient = fields.Many2one('oeh.medical.patient', string='Patient', help="Patient Name", required=True,
                              readonly=True, states={'Draft': [('readonly', False)]})
    hhc_appointment = fields.Many2one('sm.shifa.hhc.appointment', string='HHC-Appointment',
                                      readonly=True, states={'Draft': [('readonly', False)]}, )
    doctor = fields.Many2one('oeh.medical.physician', string='Nurse', help="Current primary care / family doctor",
                             readonly=True, states={'Draft': [('readonly', False)]},
                             domain=[('role_type', '=', ['HHCN', 'HN'])], required=True, default=_get_anticoagulation)
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

    patient_assessment_show = fields.Boolean()
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

    caregiver_assessment_show = fields.Boolean()
    administer_correct_warfarin_dose_since = fields.Selection(yes_no_na, readonly=True,
                                                              states={'Start': [('readonly', False)]})
    understand_dosing_regime = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    medication_storage_appropriately = fields.Selection(yes_no_na, readonly=True,
                                                        states={'Start': [('readonly', False)]})
    one_reliable_family_member = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    caregiver_name_identified = fields.Text(readonly=True, states={'Start': [('readonly', False)]})

    patient_caregiver_education_show = fields.Boolean()
    warfarin_tablets_to_be_given = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    to_report_missed_dose = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    check_with_home_care_staff_before = fields.Selection(yes_no_na, readonly=True,
                                                         states={'Start': [('readonly', False)]})
    to_observe_for_any_bleeding = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    correct_technique_in_performing = fields.Selection(yes_no_na, readonly=True,
                                                       states={'Start': [('readonly', False)]})
    rotate_injection_sites = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    remarks_show = fields.Boolean()
    remarks = fields.Text(readonly=True, states={'Start': [('readonly', False)]})

    anticoagulation_follow_up_id = fields.One2many('sm.shifa.anticoagulation.management.follow.up',
                                                   'anticoagulation_management_id', string='anticoagulation follow up')
    referral_id = fields.One2many('sm.shifa.referral', 'anticoagulation_management_ref_id',
                                  string='anticoagulation referral')
    consent_show = fields.Boolean()
    consent_file1 = fields.Binary()
    consent_file2 = fields.Binary()

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
        vals['anticoagulation_management_code'] = self.env['ir.sequence'].next_by_code('anticoagulation.management')
        return super(AnticoagulationManagement, self).create(vals)


class ShifaReferralInherit(models.Model):
    _inherit = 'sm.shifa.referral'

    anticoagulation_management_ref_id = fields.Many2one('sm.shifa.anticoagulation.management',
                                                        string='anticoagulation management', ondelete='cascade')
