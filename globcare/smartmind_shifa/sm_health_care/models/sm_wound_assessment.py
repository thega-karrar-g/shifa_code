from odoo import models, fields, api
import datetime
from odoo.exceptions import ValidationError


class ShifaWoundAssessment(models.Model):
    _name = 'sm.shifa.wound.assessment'
    _description = "Wound Assessment for Patient"
    _rec_name = "wound_assessment_code"

    STATES = [
        ('Draft', 'Draft'),
        ('Start', 'Start'),
        ('Admitted', 'Admitted'),
        ('Discharged', 'Discharged'),
    ]

    def _get_nurse(self):
        """Return default stoma value"""
        therapist_obj = self.env['oeh.medical.physician']
        domain = [('oeh_user_id', '=', self.env.uid)]
        user_ids = therapist_obj.search(domain, limit=1)
        if user_ids:
            return user_ids.id or False
        else:
            return False

        #     draft method

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

    state = fields.Selection(STATES, string='State', default=lambda *a: 'Draft', readonly=True)
    patient = fields.Many2one('oeh.medical.patient', string='Patient', required=True, store=True, readonly=False,
                              states={'Draft': [('readonly', False)]})
    nurse_name = fields.Many2one('oeh.medical.physician', string='Nurse Name', default=_get_nurse, required=True,
                                 store=True, domain=[('role_type', '=', 'HHCN'),('active', '=', True)], readonly=False,
                                 states={'Draft': [('readonly', False)]})
    register_walk_in = fields.Many2one('sm.shifa.hhc.appointment', string='HHC Appointment')
    hhc_appointment = fields.Many2one('sm.shifa.hhc.appointment', string='HHC-Appointment', readonly=False,
                                      states={'Draft': [('readonly', False)]})
    wound_assessment_code = fields.Char('Reference', index=True, copy=False)
    # add new fields
    admission_date = fields.Datetime(string='Admission date')
    discharge_date = fields.Datetime(string='Discharge date')
    dob = fields.Date(string='Date of Birth', related='patient.dob')
    marital_status = fields.Selection(string='Marital Status', related='patient.marital_status')
    sex = fields.Selection(string='Sex', related='patient.sex')
    blood_type = fields.Selection(string='Blood Type', related='patient.blood_type')
    rh = fields.Selection(string='Rh', related='patient.rh')
    # Clinical Pathway tab
    conscious_state_show = fields.Boolean()
    conscious_state = fields.Selection([
        ('Alert', 'Alert'),
        ('Response to Voice', 'Response to Voice'),
        ('Response to pain', 'Response to pain'),
        ('Unresponsive', 'Unresponsive'),
    ], readonly=False, states={'Start': [('readonly', False)]})
    # pain present
    pain_present_show = fields.Boolean()
    pain_score = fields.Selection([
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
    # functional activity
    functional_activity_show = fields.Boolean()
    functional_activity = fields.Selection([
        ('No Limitation', 'No Limitation'),
        ('Mild Limitation', 'Mild Limitation'),
        ('Severe Limitation', 'Severe Limitation'),
    ], readonly=False, states={'Start': [('readonly', False)]})
    # vital signs
    vital_signs_show = fields.Boolean()
    systolic_bp = fields.Integer(readonly=False, states={'Start': [('readonly', False)]})
    hr_min = fields.Integer(readonly=False, states={'Start': [('readonly', False)]})
    diastolic_br = fields.Integer(readonly=False, states={'Start': [('readonly', False)]})
    rr_min = fields.Integer(readonly=False, states={'Start': [('readonly', False)]})
    temperature_c = fields.Float(readonly=False, states={'Start': [('readonly', False)]})
    o2_sat = fields.Float(readonly=False, states={'Start': [('readonly', False)]})
    # wound history
    wound_history_show = fields.Boolean()
    wound_history = fields.Text(string='Wound History', readonly=False, states={'Start': [('readonly', False)]})
    # Type of Wound fields
    type_wound_show = fields.Boolean()
    surgical = fields.Boolean(string='Surgical', readonly=False, states={'Start': [('readonly', False)]})
    pressure_ulcer = fields.Boolean(string='Pressure Ulcer', readonly=False, states={'Start': [('readonly', False)]})
    diabetic = fields.Boolean(string='Diabetic', readonly=False, states={'Start': [('readonly', False)]})
    other_types = fields.Boolean(string='Other', readonly=False, states={'Start': [('readonly', False)]})
    other_types_content = fields.Char(readonly=False, states={'Start': [('readonly', False)]})

    # Factors Influencing Wound Healing
    factors_influencing_show = fields.Boolean()
    diabetes = fields.Boolean(string='Diabetes', readonly=False, states={'Start': [('readonly', False)]})
    immobility = fields.Boolean(string='Immobility', readonly=False, states={'Start': [('readonly', False)]})
    tissue_perfusion = fields.Boolean(string='Tissue perfusion', readonly=False, states={'Start': [('readonly', False)]})
    infection = fields.Boolean(string='Infection', readonly=False, states={'Start': [('readonly', False)]})

    incontinence = fields.Boolean(string='Incontinence', readonly=False, states={'Start': [('readonly', False)]})
    malnutrition = fields.Boolean(string='Malnutrition', readonly=False, states={'Start': [('readonly', False)]})
    immnuno_compromised = fields.Boolean(string='Immnuno compromised', readonly=False,
                                         states={'Start': [('readonly', False)]})
    blood_related = fields.Boolean(string='Blood related', readonly=False, states={'Start': [('readonly', False)]})
    blood_related_content = fields.Char(readonly=False, states={'Start': [('readonly', False)]})
    other_factors = fields.Boolean(string='Other', readonly=False, states={'Start': [('readonly', False)]})
    other_factors_content = fields.Char(readonly=False, states={'Start': [('readonly', False)]})

    # Potential Risk
    potential_risk_show = fields.Boolean()
    infection_potential = fields.Boolean(string='Infection', readonly=False, states={'Start': [('readonly', False)]})
    Poor_healing = fields.Boolean(string='Poor healing', readonly=False, states={'Start': [('readonly', False)]})
    other_potential = fields.Boolean(string='Other', readonly=False, states={'Start': [('readonly', False)]})
    other_potential_content = fields.Char(readonly=False, states={'Start': [('readonly', False)]})

    # Measurable Goals
    measurable_goals_show = fields.Boolean()
    free_signs_infection = fields.Boolean(string='Free from signs of infection', readonly=False,
                                          states={'Start': [('readonly', False)]})
    increase_area_granulating_tissue = fields.Boolean(string='Increase in area granulating tissue', readonly=False,
                                                      states={'Start': [('readonly', False)]})
    free_skin_excoriation = fields.Boolean(string='Free from skin excoriation', readonly=False,
                                           states={'Start': [('readonly', False)]})
    free_necrosis = fields.Boolean(string='Free from necrosis', readonly=False, states={'Start': [('readonly', False)]})
    # Annotation image
    annotation_image_show = fields.Boolean()
    annotation_image = fields.Binary(readonly=False, states={'Start': [('readonly', False)]})
    # wound assessment and dressing plan
    wound_assessment_show = fields.Boolean()
    add_new_wound_assessment = fields.Boolean()
    wound_add = fields.One2many('sm.shifa.wound.assessment.values', 'wound_number_id', string='Wound Assessment',
                                states={'Admitted': [('readonly', False)]})
    wound_new_add = fields.One2many('sm.shifa.wound.assessment.values', 'wound_number_id', string='Wound Assessment',
                                    states={'Admitted': [('readonly', False)]})

    add_new_wound_assessment_date = fields.Date(string='Date', readonly=False,
                                                states={'Admitted': [('readonly', False)]})
    add_other_wound_assessment = fields.Boolean()
    add_other_wound_assessment_date = fields.Date(string='Date', readonly=False,
                                                  states={'Admitted': [('readonly', False)]})
    wound_ids = fields.One2many('sm.shifa.wound.assessment.values', 'wound_number_id', string='Wound Assessment',
                                states={'Start': [('readonly', False)]})
    referral_id = fields.One2many('sm.shifa.referral', 'wound_care_id', string='wound referral')
    wound_follow_up_id = fields.One2many('sm.shifa.wound.care.followup', 'wound_care_ref',
                                         string='Wound Care Follow up')
    consent_show = fields.Boolean()
    consent_file1 = fields.Binary()
    consent_file2 = fields.Binary()

    @api.model
    def create(self, vals):
        vals['wound_assessment_code'] = self.env['ir.sequence'].next_by_code('sm.shifa.wound.assessment')
        return super(ShifaWoundAssessment, self).create(vals)

    @api.onchange('hhc_appointment')
    def _onchange_hhc_appointment(self):
        if self.hhc_appointment:
            self.patient = self.hhc_appointment.patient

    @api.onchange('systolic_bp', 'hr_min', 'diastolic_br', 'rr_min', 'temperature_c', 'o2_sat')
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
        if self.o2_sat > 100:
            raise ValidationError("invalid O2 Sat(%)")


# Inheriting register for walkins module to add "Wound Assessment" screen reference
class ShifaWoundAssessmentForRegisterForWalkin(models.Model):
    _inherit = 'sm.shifa.hhc.appointment'

    wound_ids = fields.One2many('sm.shifa.wound.assessment', 'register_walk_in', string='Wound Assessment')

# It cases problems
# class ShifaWoundReferralInherit(models.Model):
#     _inherit = 'sm.shifa.referral'
#
#     wound_care_id = fields.Many2one('sm.shifa.wound.assessment', string='wound care', ondelete='cascade')
