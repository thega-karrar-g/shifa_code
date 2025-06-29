from odoo import models, fields, api
import datetime
from odoo.exceptions import ValidationError
from datetime import date
from psycopg2._psycopg import List


class PalliativeCare(models.Model):
    _name = 'sm.shifa.palliative.care'
    _description = 'Palliative Care'
    _rec_name = 'palliative_care_code'

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
    yes_no = [
        ('Yes', 'Yes'),
        ('No', 'No'),
    ]

    def _get_palliative(self):
        """Return default palliative value"""
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

    palliative_care_code = fields.Char('Reference', index=True, copy=False)
    patient = fields.Many2one('oeh.medical.patient', string='Patient', help="Patient Name", required=True,
                              readonly=True, states={'Draft': [('readonly', False)]})
    hhc_appointment = fields.Many2one('sm.shifa.hhc.appointment', string='HHC-Appointment',
                                      readonly=True, states={'Draft': [('readonly', False)]})
    doctor = fields.Many2one('oeh.medical.physician', string='Nurse', help="Current primary care / family doctor",
                             readonly=True, states={'Draft': [('readonly', False)]},
                             domain=[('role_type', '=', ['HHCN', 'HN']), ('active', '=', True)], required=True, default=_get_palliative)
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

    palliative_care_type_show = fields.Boolean()
    pain_management = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    symptom_management = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    subcutaneous_infusion = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    palliative_other = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    palliative_other_text = fields.Text(readonly=True, states={'Start': [('readonly', False)]})
    # conscious_state = fields.Selection([
    #         ('Alert', 'Alert'),
    #         ('Response to Voice', 'Response to Voice'),
    #         ('Response to pain', 'Response to pain'),
    #         ('Unresponsive', 'Unresponsive'),
    # ], readonly=True, states={'Start': [('readonly', False)]})
    #
    # pain_present_show = fields.Boolean()
    # pain_score = fields.Selection([
    #     ('0', '0'),
    #     ('1', '1'),
    #     ('2', '2'),
    #     ('3', '3'),
    #     ('4', '4'),
    #     ('5', '5'),
    #     ('6', '6'),
    #     ('7', '7'),
    #     ('8', '8'),
    #     ('9', '9'),
    #     ('10', '10'),
    # ], readonly=True, states={'Start': [('readonly', False)]})
    # scale_used = fields.Selection([
    #     ('Numerical', 'Numerical'),
    #     ('Faces', 'Faces'),
    #     ('FLACC', 'FLACC'),
    #     ('ABBEY', 'ABBEY'),
    # ], readonly=True, states={'Start': [('readonly', False)]})
    #
    # functional_activity_show = fields.Boolean()
    # functional_activity = fields.Selection([
    #     ('No Limitation', 'No Limitation'),
    #     ('Mild Limitation', 'Mild Limitation'),
    #     ('Severe Limitation', 'Severe Limitation'),
    # ], readonly=True, states={'Start': [('readonly', False)]})
    #
    # vital_signs_show = fields.Boolean()
    # systolic_bp = fields.Integer(readonly=True, states={'Start': [('readonly', False)]})
    # hr_min = fields.Integer(readonly=True, states={'Start': [('readonly', False)]})
    # diastolic_br = fields.Integer(readonly=True, states={'Start': [('readonly', False)]})
    # rr_min = fields.Integer(readonly=True, states={'Start': [('readonly', False)]})
    # temperature_c = fields.Float(readonly=True, states={'Start': [('readonly', False)]})
    # o2_sat = fields.Float(readonly=True, states={'Start': [('readonly', False)]})

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

    patient_assessment_show = fields.Boolean()
    presence_of_pain = fields.Selection(yes_no, readonly=True, states={'Start': [('readonly', False)]})
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

    caregiver_assessment_show = fields.Boolean()
    management_of_patient_pain = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    management_of_patient_nutrition = fields.Selection(yes_no_na, readonly=True,
                                                       states={'Start': [('readonly', False)]})
    coping_psychologically = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    coping_with_patient_care = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})

    patient_caregiver_education_show = fields.Boolean()
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
    remarks_show = fields.Boolean()
    remarks = fields.Text(readonly=True, states={'Start': [('readonly', False)]})

    palliative_follow_up_id = fields.One2many('sm.shifa.palliative.care.follow.up', 'palliative_care_id',
                                              string='palliative follow up')
    referral_id = fields.One2many('sm.shifa.referral', 'palliative_care_ref_id',
                                  string='palliative referral')
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
        vals['palliative_care_code'] = self.env['ir.sequence'].next_by_code('palliative.care')
        return super(PalliativeCare, self).create(vals)


class ShifaReferralInherit(models.Model):
    _inherit = 'sm.shifa.referral'

    palliative_care_ref_id = fields.Many2one('sm.shifa.palliative.care',
                                             string='palliative care', ondelete='cascade')
