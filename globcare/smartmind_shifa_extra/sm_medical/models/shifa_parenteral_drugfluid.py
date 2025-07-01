from odoo import models, fields, api
import datetime
from odoo.exceptions import ValidationError
from datetime import date
from psycopg2._psycopg import List


class ParenteralDrugfluid(models.Model):
    _name = 'sm.shifa.parenteral.drugfluid'
    _description = 'Parenteral Drugfluid'
    _rec_name = 'parenteral_drugfluid_code'

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

    def _get_parenteral(self):
        """Return default parenteral value"""
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

    parenteral_drugfluid_code = fields.Char('Reference', index=True, copy=False)
    patient = fields.Many2one('oeh.medical.patient', string='Patient', help="Patient Name", required=True,
                              readonly=False, states={'Draft': [('readonly', False)]})
    hhc_appointment = fields.Many2one('sm.shifa.hhc.appointment', string='HHC-Appointment',
                                      readonly=False, states={'Draft': [('readonly', False)]})
    doctor = fields.Many2one('oeh.medical.physician', string='Nurse', help="Current primary care / family doctor",
                             readonly=False, states={'Draft': [('readonly', False)]},
                             domain=[('role_type', '=', ['HHCN', 'HN'])], required=True, default=_get_parenteral)
    phy_adm = fields.Many2one('sm.shifa.physician.admission', string='Phy_Adm', readonly=False,
                              states={'Discharged': [('readonly', True)]},
                              domain="[('patient', '=', patient), ('state', 'in', ('Admitted', 'Start','Draft'))]")
    state = fields.Selection(ADMISSION_STATES, string='State', default=lambda *a: 'Draft', readonly=False)
    weight = fields.Float(string='Weight', related='patient.weight')
    age = fields.Char(string='Age', related='patient.age')
    marital_status = fields.Selection(string='Marital Status', related='patient.marital_status')
    sex = fields.Selection(string='Sex', related='patient.sex')
    blood_type = fields.Selection(string='Blood Type', related='patient.blood_type')
    rh = fields.Selection(string='Rh', related='patient.rh')
    admission_date = fields.Datetime(string='Admission Date')
    discharge_date = fields.Datetime(string='Discharge Date')

    conscious_state_show = fields.Boolean()
    conscious_state = fields.Selection([
        ('Alert', 'Alert'),
        ('Response to Voice', 'Response to Voice'),
        ('Response to pain', 'Response to pain'),
        ('Unresponsive', 'Unresponsive'),
    ], readonly=False, states={'Start': [('readonly', False)]})
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
    ], readonly=False, states={'Start': [('readonly', False)]})
    scale_used = fields.Selection([
        ('Numerical', 'Numerical'),
        ('Faces', 'Faces'),
        ('FLACC', 'FLACC'),
        ('ABBEY', 'ABBEY'),
    ], readonly=False, states={'Start': [('readonly', False)]})
    functional_activity_show = fields.Boolean()
    functional_activity = fields.Selection([
        ('No Limitation', 'No Limitation'),
        ('Mild Limitation', 'Mild Limitation'),
        ('Severe Limitation', 'Severe Limitation'),
    ], readonly=False, states={'Start': [('readonly', False)]})

    vital_signs_show = fields.Boolean()
    systolic_bp = fields.Integer(readonly=False, states={'Start': [('readonly', False)]})
    hr_min = fields.Integer(readonly=False, states={'Start': [('readonly', False)]})
    diastolic_br = fields.Integer(readonly=False, states={'Start': [('readonly', False)]})
    rr_min = fields.Integer(readonly=False, states={'Start': [('readonly', False)]})
    temperature_c = fields.Float(readonly=False, states={'Start': [('readonly', False)]})
    # o2_sat = fields.Float(readonly=False, states={'Start': [('readonly', False)]})
    o2_sat = fields.Selection([
        ('at room air', 'at room air'),
        ('with oxygen Support', 'with oxygen Support')
    ], readonly=False, states={'Start': [('readonly', False)]})
    char_other_oxygen = fields.Float(readonly=False, states={'Start': [('readonly', False)]})

    parenteral_route_show = fields.Boolean()
    peripheral_intravenous_cannula = fields.Boolean(readonly=False, states={'Start': [('readonly', False)]})
    p_i_c_c_line = fields.Boolean(readonly=False, states={'Start': [('readonly', False)]})
    central_catheter = fields.Boolean(readonly=False, states={'Start': [('readonly', False)]})
    subcutaneous = fields.Boolean(readonly=False, states={'Start': [('readonly', False)]})
    intramuscular = fields.Boolean(readonly=False, states={'Start': [('readonly', False)]})
    portacath = fields.Boolean(readonly=False, states={'Start': [('readonly', False)]})
    parenteral_other = fields.Boolean(readonly=False, states={'Start': [('readonly', False)]})
    parenteral_other_text = fields.Text(readonly=False, states={'Start': [('readonly', False)]})

    par_potential_actual_risk_show = fields.Boolean()
    complications_related_to_parenteral_therapy = fields.Selection(yes_no_na, readonly=False,
                                                                   states={'Start': [('readonly', False)]})
    complications_related_to_parenteral_medications = fields.Selection(yes_no_na, readonly=False,
                                                                       states={'Start': [('readonly', False)]})
    local_irritation_inflammation_or_infection_related = fields.Selection(yes_no_na, readonly=False,
                                                                          states={'Start': [('readonly', False)]})
    no_complication_of_pulmonary_micro_embolism = fields.Selection(yes_no_na, readonly=False,
                                                                   states={'Start': [('readonly', False)]})
    apply_warm_compress_to_injection_site = fields.Selection(yes_no_na, readonly=False,
                                                             states={'Start': [('readonly', False)]})
    blood_test_done = fields.Selection(yes_no_na, readonly=False, states={'Start': [('readonly', False)]})

    par_measurable_goals_show = fields.Boolean()
    parenteral_device_remains_functional_as_evidence_by = fields.Selection(yes_no_na, readonly=False,
                                                                           states={'Start': [('readonly', False)]})
    no_parenteral_site_infection_as_evidence_by_site_free = fields.Selection(yes_no_na, readonly=False,
                                                                             states={'Start': [('readonly', False)]})
    no_systemic_infection_related_to_parenteral_site = fields.Selection(yes_no_na, readonly=False,
                                                                        states={'Start': [('readonly', False)]})
    local_irritation_inflammation_or_infection_related = fields.Selection(yes_no_na, readonly=False,
                                                                          states={'Start': [('readonly', False)]})

    patient_assessment_show = fields.Boolean()
    vital_signs_within_normal = fields.Selection(yes_no_na, readonly=False, states={'Start': [('readonly', False)]})
    general_condition_improved = fields.Selection(yes_no_na, readonly=False, states={'Start': [('readonly', False)]})
    presence_of_pain = fields.Selection(yes_no_na, readonly=False, states={'Start': [('readonly', False)]})
    signs_of_phlebitis = fields.Selection(yes_no_na, readonly=False, states={'Start': [('readonly', False)]})

    catheter_site_assessment_show = fields.Boolean()
    leakage_from_site = fields.Selection(yes_no_na, readonly=False, states={'Start': [('readonly', False)]})
    site_dressing_attended = fields.Selection(yes_no_na, readonly=False, states={'Start': [('readonly', False)]})
    device_resited = fields.Selection(yes_no_na, readonly=False, states={'Start': [('readonly', False)]})
    p_i_line_exposed_tube_daily = fields.Float(readonly=False, states={'Start': [('readonly', False)]})

    infusion_device_show = fields.Boolean()
    correct_infusion_administered = fields.Selection(yes_no_na, readonly=False, states={'Start': [('readonly', False)]})
    parameters_updated = fields.Selection(yes_no_na, readonly=False, states={'Start': [('readonly', False)]})
    infusion_therapy_started = fields.Selection(yes_no_na, readonly=False, states={'Start': [('readonly', False)]})
    batteries_changed_checked = fields.Selection(yes_no_na, readonly=False, states={'Start': [('readonly', False)]})

    caregiver_assessment_show = fields.Boolean()
    coping_with_patient_care = fields.Selection(yes_no_na, readonly=False, states={'Start': [('readonly', False)]})
    able_to_troubleshoot_device = fields.Selection(yes_no_na, readonly=False, states={'Start': [('readonly', False)]})
    care_of_parenteral_site = fields.Selection(yes_no_na, readonly=False, states={'Start': [('readonly', False)]})
    compliant_to_education = fields.Selection(yes_no_na, readonly=False, states={'Start': [('readonly', False)]})

    patient_caregiver_education_show = fields.Boolean()
    aware_of_action_and_side_effects = fields.Selection(yes_no_na, readonly=False,
                                                        states={'Start': [('readonly', False)]})
    care_iv_access_at_home_during = fields.Selection(yes_no_na, readonly=False, states={'Start': [('readonly', False)]})
    pain_management = fields.Selection(yes_no_na, readonly=False, states={'Start': [('readonly', False)]})
    advice_on_activity_tolerated = fields.Selection(yes_no_na, readonly=False, states={'Start': [('readonly', False)]})
    trouble_shoot_infusion_device = fields.Selection(yes_no_na, readonly=False, states={'Start': [('readonly', False)]})
    to_inform_home_care_when_parenteral_site = fields.Selection(yes_no_na, readonly=False,
                                                                states={'Start': [('readonly', False)]})
    remarks_show = fields.Boolean()
    remarks = fields.Text(readonly=False, states={'Start': [('readonly', False)]})

    parenteral_follow_up_id = fields.One2many('sm.shifa.parenteral.drugfluid.follow.up', 'parenteral_drugfluid_id',
                                              string='parenteral follow up')
    referral_id = fields.One2many('sm.shifa.referral', 'parenteral_drugfluid_ref_id',
                                  string='parenteral referral')
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
        vals['parenteral_drugfluid_code'] = self.env['ir.sequence'].next_by_code('parenteral.drugfluid')
        return super(ParenteralDrugfluid, self).create(vals)


class ShifaReferralInherit(models.Model):
    _inherit = 'sm.shifa.referral'

    parenteral_drugfluid_ref_id = fields.Many2one('sm.shifa.parenteral.drugfluid',
                                                  string='parenteral drugfluid', ondelete='cascade')
