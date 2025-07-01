from odoo import models, fields, api
import datetime
from odoo.exceptions import ValidationError
from datetime import date


class NebulizationCare(models.Model):
    _name = 'sm.shifa.nebulization.care'
    _description = 'Nebulization Care'
    _rec_name = 'nebulization_care_code'

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

    def _get_nebulization(self):
        """Return default nebulization value"""
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

    nebulization_care_code = fields.Char('Reference', index=True, copy=False)
    patient = fields.Many2one('oeh.medical.patient', string='Patient', help="Patient Name", required=True,
                              readonly=True, states={'Draft': [('readonly', False)]})
    hhc_appointment = fields.Many2one('sm.shifa.hhc.appointment', string='HHC-Appointment',
                                      readonly=True, states={'Draft': [('readonly', False)]})
    doctor = fields.Many2one('oeh.medical.physician', string='Nurse', help="Current primary care / family doctor",
                             readonly=True, states={'Draft': [('readonly', False)]},
                             domain=[('role_type', '=', ['HHCN', 'HN']), ('active', '=', True)], required=True, default=_get_nebulization)
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

    potential_acual_risk_show = fields.Boolean()
    risk_for_faster_heartbeat = fields.Selection(yes_no, readonly=True, states={'Start': [('readonly', False)]})
    risk_for_slightly_shaking_muscles = fields.Selection(yes_no, readonly=True, states={'Start': [('readonly', False)]})

    measurable_goals_review_date_show = fields.Boolean()
    fast_relief_from_inflammation_and_allowing = fields.Selection(yes_no, readonly=True,
                                                                  states={'Start': [('readonly', False)]})

    patient_assessment_show = fields.Boolean()
    has_productive_cough = fields.Selection(yes_no, readonly=True,
                                            states={'Start': [('readonly', False)]})
    obvious_nasal_flaring_shortness_breath = fields.Selection(yes_no, readonly=True,
                                                              states={'Start': [('readonly', False)]})
    breathing_easier_after_nebulization = fields.Selection(yes_no, readonly=True,
                                                           states={'Start': [('readonly', False)]})

    patient_caregiver_education_show = fields.Boolean()
    lifestyle_changes_treat_shortness_breath = fields.Selection(yes_no, readonly=True,
                                                                states={'Start': [('readonly', False)]})
    educate_deep_breathing_exercises = fields.Selection(yes_no, readonly=True,
                                                        states={'Start': [('readonly', False)]})
    avoiding_exposure_pollutants_allergens = fields.Selection(yes_no, readonly=True,
                                                              states={'Start': [('readonly', False)]})
    comply_medication_prescribed = fields.Selection(yes_no, readonly=True,
                                                    states={'Start': [('readonly', False)]})

    remarks_show = fields.Boolean()
    remarks = fields.Text(states={'Start': [('readonly', False)]})

    nebulization_follow_up_id = fields.One2many('sm.shifa.nebulization.care.follow.up', 'nebulization_care_id',
                                                string='nebulization follow up')
    referral_id = fields.One2many('sm.shifa.referral', 'nebulization_care_ref_id', string='nebulization referral')
    consent_show = fields.Boolean()
    consent_file1 = fields.Binary()
    consent_file2 = fields.Binary()

    @api.model
    def create(self, vals):
        vals['nebulization_care_code'] = self.env['ir.sequence'].next_by_code('nebulization.care')
        return super(NebulizationCare, self).create(vals)

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


class ShifaReferralInherit(models.Model):
    _inherit = 'sm.shifa.referral'

    nebulization_care_ref_id = fields.Many2one('sm.shifa.nebulization.care', string='nebulization care',
                                               ondelete='cascade')
