from odoo import models, fields, api
import datetime
from odoo.exceptions import ValidationError


class PostnatalCare(models.Model):
    _name = 'sm.shifa.postnatal.care'
    _description = 'Postnatal Care'
    _rec_name = 'postnatal_care_code'

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

    def _get_postnatal(self):
        """Return default postnatal value"""
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

    postnatal_care_code = fields.Char('Reference', index=True, copy=False)
    patient = fields.Many2one('oeh.medical.patient', string='Patient', help="Patient Name", required=True,
                              readonly=True, states={'Draft': [('readonly', False)]})
    hhc_appointment = fields.Many2one('sm.shifa.hhc.appointment', string='HHC-Appointment',
                                      readonly=True, states={'Draft': [('readonly', False)]})
    doctor = fields.Many2one('oeh.medical.physician', string='Nurse', help="Current primary care / family doctor",
                             readonly=True, states={'Draft': [('readonly', False)]},
                             domain=[('role_type', '=', ['HHCN', 'HN']), ('active', '=', True)], required=True, default=_get_postnatal)
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

    patient_assessment_show = fields.Boolean()
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
    bladder = fields.Selection([
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

    nutrition_show = fields.Boolean()
    maintain_oral_intake = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    specific_dietary_needs = fields.Selection([
        ('Diabetic', 'Diabetic'),
        ('low salt', 'low salt'),
        ('law fat', 'law fat'),
        ('high fiber', 'high fiber'),
        ('low salt, low fat', 'low salt, low fat'),
        ('Regular diet', 'Regular diet'),
    ], readonly=True, states={'Start': [('readonly', False)]})

    medication_show = fields.Boolean()
    oral_medication_discussed = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    patient_caregiver_able = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    medication_review_done = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    next_review_due = fields.Text(readonly=True, states={'Start': [('readonly', False)]})

    patient_caregiver_education_show = fields.Boolean()
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
    remarks_show = fields.Boolean()
    remarks = fields.Text(readonly=True, states={'Start': [('readonly', False)]})

    postnatal_follow_up_id = fields.One2many('sm.shifa.postnatal.care.follow.up', 'postnatal_care_id',
                                             string='postnatal follow up')
    referral_id = fields.One2many('sm.shifa.referral', 'postnatal_care_ref_id',
                                  string='postnatal referral')
    consent_show = fields.Boolean()
    consent_file1 = fields.Binary()
    consent_file2 = fields.Binary()

    @api.model
    def create(self, vals):
        vals['postnatal_care_code'] = self.env['ir.sequence'].next_by_code('postnatal.care')
        return super(PostnatalCare, self).create(vals)

    @api.onchange('systolic_bp', 'hr_min', 'diastolic_br', 'rr_min', 'temperature_c', 'postnatal_day',
                  'char_other_oxygen')
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
        if self.postnatal_day > 1000:
            raise ValidationError("invalid Postnatal Day")
        if self.char_other_oxygen > 1000:
            raise ValidationError("invalid O2 Sat(%)")


class ShifaReferralInherit(models.Model):
    _inherit = 'sm.shifa.referral'

    postnatal_care_ref_id = fields.Many2one('sm.shifa.postnatal.care',
                                            string='postnatal care', ondelete='cascade')
