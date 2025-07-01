from odoo import models, fields, api
import datetime
from odoo.exceptions import ValidationError
from datetime import date
from psycopg2._psycopg import List


class ContinenceCare(models.Model):
    _name = 'sm.shifa.continence.care'
    _description = 'Continence Care'
    _rec_name = 'continence_care_code'

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

    def _get_continence(self):
        """Return default continence value"""
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

    continence_care_code = fields.Char('Reference', index=True, copy=False)
    patient = fields.Many2one('oeh.medical.patient', string='Patient', help="Patient Name", required=True,
                              readonly=False, states={'Draft': [('readonly', False)]})
    hhc_appointment = fields.Many2one('sm.shifa.hhc.appointment', string='HHC-Appointment',
                                      readonly=False, states={'Draft': [('readonly', False)]})
    doctor = fields.Many2one('oeh.medical.physician', string='Nurse', help="Current primary care / family doctor",
                             readonly=False, states={'Draft': [('readonly', False)]},
                             domain=[('role_type', '=', ['HHCN', 'HN']), ('active', '=', True)], required=True, default=_get_continence)
    state = fields.Selection(ADMISSION_STATES, string='State', default=lambda *a: 'Draft', readonly=False)
    # dob = fields.Date(string='Date of Birth', related='patient.dob')
    marital_status = fields.Selection(string='Marital Status', related='patient.marital_status')
    sex = fields.Selection(string='Sex', related='patient.sex')
    blood_type = fields.Selection(string='Blood Type', related='patient.blood_type')
    rh = fields.Selection(string='Rh', related='patient.rh')
    weight = fields.Float(string='Weight', related='patient.weight')
    age = fields.Char(string='Age', related='patient.age')
    admission_date = fields.Datetime(string='Admission Date')
    discharge_date = fields.Datetime(string='Discharge Date')

    clinical_pathway_show = fields.Boolean()
    clinical_pathway = fields.Selection([
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
    # at_room_air = fields.Boolean(string="at room air", readonly=False, states={'Start': [('readonly', False)]})
    # with_oxygen_support = fields.Boolean(string="with oxygen Support", readonly=False,
    #                                      states={'Start': [('readonly', False)]})
    char_other_oxygen = fields.Float(readonly=False, states={'Start': [('readonly', False)]})

    type_continence_show = fields.Boolean()
    bladder = fields.Boolean(readonly=False, states={'Start': [('readonly', False)]})
    bowel = fields.Boolean(readonly=False, states={'Start': [('readonly', False)]})

    type_devices_used_show = fields.Boolean()
    indwelling_foley = fields.Boolean(readonly=False, states={'Start': [('readonly', False)]})
    suprapubic_catheter = fields.Boolean(readonly=False, states={'Start': [('readonly', False)]})
    urosheath_condom = fields.Boolean(readonly=False, states={'Start': [('readonly', False)]})
    diaper = fields.Boolean(readonly=False, states={'Start': [('readonly', False)]})

    con_potential_actual_risk_show = fields.Boolean()
    impaired_skin_integrity_related_bowel_or_bladder = fields.Selection(yes_no_na, readonly=False,
                                                                        states={'Start': [('readonly', False)]})
    complications_related_indwelling_urinary_catheter = fields.Selection(yes_no_na, readonly=False,
                                                                         states={'Start': [('readonly', False)]})

    con_measurable_goals_show = fields.Boolean()
    will_remain_clean_dry_free_from_urinary_or_faecal = fields.Selection(yes_no_na, readonly=False,
                                                                         states={'Start': [('readonly', False)]})
    will_remain_free_signs_and_symptoms_of_complications = fields.Selection(yes_no_na, readonly=False,
                                                                            states={'Start': [('readonly', False)]})

    patient_assessment_show = fields.Boolean()
    color_urine = fields.Selection([
        ('Amber', 'Amber'),
        ('Light Yellow', 'Light Yellow'),
        ('Dark Yellow', 'Dark Yellow'),
        ('Cloudy', 'Cloudy'),
        ('Light Hematuria', 'Light Hematuria'),
        ('Gross Hematuria', 'Gross Hematuria'),
    ], readonly=False, states={'Start': [('readonly', False)]})
    consistency = fields.Selection([
        ('Clear', 'Clear'),
        ('With Blood Streak', 'With Blood Streak'),
        ('With Blood Clots', 'With Blood Clots'),
        ('With Sediments', 'With Sediments'),
    ], readonly=False, states={'Start': [('readonly', False)]})
    amount_ml = fields.Float(readonly=False, states={'Start': [('readonly', False)]})
    presence_urinary_frequency = fields.Selection(yes_no_na, readonly=False, states={'Start': [('readonly', False)]})
    diaper_changed = fields.Selection([
        ('2-3 times per day', '2-3 times per day'),
        ('3 times per day', '3 times per day'),
        ('3-4 times per day', '3-4 times per day'),
        ('4 times per day', '4 times per day'),
        ('4-5 times per day', '4-5 times per day'),
        ('NA', 'NA'),
    ], readonly=False, states={'Start': [('readonly', False)]})
    presence_burning = fields.Selection(yes_no_na, readonly=False, states={'Start': [('readonly', False)]})
    presence_foul_smelling = fields.Selection(yes_no_na, readonly=False, states={'Start': [('readonly', False)]})
    presence_altered_mental = fields.Selection(yes_no_na, readonly=False, states={'Start': [('readonly', False)]})
    catheter_still_required = fields.Selection(yes_no_na, readonly=False, states={'Start': [('readonly', False)]})

    urinaty_catheter_bag_show = fields.Boolean()
    secured_appropriately = fields.Selection(yes_no_na, readonly=False, states={'Start': [('readonly', False)]})
    bag_off_floor = fields.Selection(yes_no_na, readonly=False, states={'Start': [('readonly', False)]})
    bag_below_level = fields.Selection(yes_no_na, readonly=False, states={'Start': [('readonly', False)]})
    tubing_not_taut = fields.Selection(yes_no_na, readonly=False, states={'Start': [('readonly', False)]})

    catheter_change_show = fields.Boolean()
    catheter_change_done = fields.Selection(yes_no_na, readonly=False, states={'Start': [('readonly', False)]})
    type_of_catheter = fields.Selection([
        ('Silicone', 'Silicone'),
        ('Rubber/Latex', 'Rubber/Latex'),
        ('Condom', 'Condom'),
        ('Urosheath', 'Urosheath'),
        ('Suprapubic', 'Suprapubic'),
        ('Nephrostomy', 'Nephrostomy'),
    ], readonly=False, states={'Start': [('readonly', False)]})
    size_of_catheter = fields.Text(readonly=False, states={'Start': [('readonly', False)]})
    catheter_change_due_on = fields.Text(readonly=False, states={'Start': [('readonly', False)]})

    bowel_assessment_show = fields.Boolean()
    bowels_opened = fields.Selection([
        ('2 times daily', '2 times daily'),
        ('more than 5 times daily', 'more than 5 times daily'),
        ('more than 10 times daily', 'more than 10 times daily'),
        ('every 2 days', 'every 2 days'),
        ('every other day', 'every other day'),
        ('once a week', 'once a week'),
        ('Bowel not opened', 'Bowel not opened'),
    ], readonly=False, states={'Start': [('readonly', False)]})
    color_of_stool = fields.Selection([
        ('Brown', 'Brown'),
        ('Black', 'Black'),
        ('Reddish Brown', 'Reddish Brown'),
        ('Yellow', 'Yellow'),
        ('Green', 'Green'),
        ('Red', 'Red'),
    ], readonly=False, states={'Start': [('readonly', False)]})
    consistency_of_stool = fields.Selection([
        ('Hard', 'Hard'),
        ('Soft', 'Soft'),
        ('Loose', 'Loose'),
        ('Watery', 'Watery'),
        ('Mucoid', 'Mucoid'),
        ('NA', 'NA'),
    ], readonly=False, states={'Start': [('readonly', False)]})
    perineal_area = fields.Selection([
        ('Dry and intact', 'Dry and intact'),
        ('Excoriation', 'Excoriation'),
        ('Redness', 'Redness'),
        ('Blisters', 'Blisters'),
        ('NA', 'NA'),
    ], readonly=False, states={'Start': [('readonly', False)]})

    caregiver_assessment_show = fields.Boolean()
    maintain_patient_hygiene = fields.Selection([
        ('Well', 'Well'),
        ('Very Well', 'Very Well'),
        ('Yes', 'Yes'),
        ('No', 'No'),
        ('NA', 'NA'),
        ('Fair', 'Fair'),
        ('Poor', 'Poor'),
    ], readonly=False, states={'Start': [('readonly', False)]})
    use_incontinence_products = fields.Selection([
        ('Competent', 'Competent'),
        ('Yes', 'Yes'),
        ('No', 'No'),
        ('NA', 'NA'),
    ], readonly=False, states={'Start': [('readonly', False)]})
    keep_patient_odourless = fields.Selection(yes_no_na, readonly=False, states={'Start': [('readonly', False)]})
    ability_cope_care = fields.Selection(yes_no_na, readonly=False, states={'Start': [('readonly', False)]})

    patient_caregiver_education_show = fields.Boolean()
    patient_caregiver_should = fields.Selection(yes_no_na, readonly=False, states={'Start': [('readonly', False)]})
    maintain_fluids_high_fibre = fields.Selection(yes_no_na, readonly=False, states={'Start': [('readonly', False)]})
    drinking_least_litres_fluid = fields.Selection(yes_no_na, readonly=False, states={'Start': [('readonly', False)]})
    do_not_kink_clamp = fields.Selection(yes_no_na, readonly=False, states={'Start': [('readonly', False)]})
    always_attach_catheter = fields.Selection(yes_no_na, readonly=False, states={'Start': [('readonly', False)]})
    keep_closed_system_drainage = fields.Selection(yes_no_na, readonly=False, states={'Start': [('readonly', False)]})
    carers_should_wash_their = fields.Selection(yes_no_na, readonly=False, states={'Start': [('readonly', False)]})
    remarks_show = fields.Boolean()
    remarks = fields.Text(readonly=False, states={'Start': [('readonly', False)]})

    continence_follow_up_id = fields.One2many('sm.shifa.continence.care.follow.up', 'continence_care_id',
                                              string='continence follow up')
    referral_id = fields.One2many('sm.shifa.referral', 'continence_care_ref_id', string='continence referral')
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
        vals['continence_care_code'] = self.env['ir.sequence'].next_by_code('continence.care')
        return super(ContinenceCare, self).create(vals)


class ShifaReferralInherit(models.Model):
    _inherit = 'sm.shifa.referral'

    continence_care_ref_id = fields.Many2one('sm.shifa.continence.care', string='continence care', ondelete='cascade')
