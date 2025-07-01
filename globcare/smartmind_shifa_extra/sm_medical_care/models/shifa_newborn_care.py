from odoo import models, fields, api
import datetime
from odoo.exceptions import ValidationError
from datetime import date
from psycopg2._psycopg import List


class NewbornCare(models.Model):
    _name = 'sm.shifa.newborn.care'
    _description = 'Newborn Care'
    _rec_name = 'newborn_care_code'

    ADMISSION_STATES = [
        ('Draft', 'Draft'),
        ('Start', 'Start'),
        ('Admitted', 'Admitted'),
        ('Discharged', 'Discharged'),
    ]
    yes_no = [
        ('Yes', 'Yes'),
        ('No', 'No'),
    ]
    yes_no_na = [
        ('Yes', 'Yes'),
        ('No', 'No'),
        ('NA', 'NA'),
    ]

    def _get_newborn(self):
        """Return default newborn value"""
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

    newborn_care_code = fields.Char('Reference', index=True, copy=False)
    patient = fields.Many2one('oeh.medical.patient', string='Baby', help="Patient Name", required=True,
                              readonly=True, states={'Draft': [('readonly', False)]})
    hhc_appointment = fields.Many2one('sm.shifa.hhc.appointment', string='HHC-Appointment',
                                      readonly=True, states={'Draft': [('readonly', False)]})
    doctor = fields.Many2one('oeh.medical.physician', string='Nurse', help="Current primary care / family doctor",
                             readonly=True, states={'Draft': [('readonly', False)]},
                             domain=[('role_type', '=', ['HHCN', 'HN']), ('active', '=', True)], required=True, default=_get_newborn)
    state = fields.Selection(ADMISSION_STATES, string='State', default=lambda *a: 'Draft', readonly=True)
    weight = fields.Float(string='Weight', related='patient.weight')
    age = fields.Char(string='Age', related='patient.age')
    marital_status = fields.Selection(string='Marital Status', related='patient.marital_status')
    sex = fields.Selection(string='Sex', related='patient.sex')
    blood_type = fields.Selection(string='Blood Type', related='patient.blood_type')
    rh = fields.Selection(string='Rh', related='patient.rh')
    admission_date = fields.Datetime(string='Admission Date', readonly='1')
    discharge_date = fields.Datetime(string='Discharge Date', readonly='1')

    mother_name = fields.Many2one('oeh.medical.patient', domain=[('sex', '=', 'Female')],
                                  readonly=True, states={'Draft': [('readonly', False)]})
    gestational_age = fields.Text(readonly=True, states={'Draft': [('readonly', False)]})
    birth_weigth = fields.Float(readonly=True, states={'Draft': [('readonly', False)]})
    family_history_sudden = fields.Selection(yes_no, readonly=True, states={'Draft': [('readonly', False)]})

    vital_signs_show = fields.Boolean()
    hr_min = fields.Integer(readonly=True, states={'Start': [('readonly', False)]})
    temperature_c = fields.Float(readonly=True, states={'Start': [('readonly', False)]})
    rr_min = fields.Integer(readonly=True, states={'Start': [('readonly', False)]})
    # o2_sat = fields.Float(readonly=True, states={'Start': [('readonly', False)]})
    o2_sat = fields.Selection([
        ('at room air', 'at room air'),
        ('with oxygen Support', 'with oxygen Support')
    ], readonly=True, states={'Start': [('readonly', False)]})
    char_other_oxygen = fields.Float(readonly=True, states={'Start': [('readonly', False)]})
    weight_kg = fields.Float(readonly=True, states={'Start': [('readonly', False)]})
    length = fields.Float(readonly=True, states={'Start': [('readonly', False)]})
    head_circumference = fields.Float(readonly=True, states={'Start': [('readonly', False)]})

    clinical_assessments_show = fields.Boolean()
    head_normal = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    head_abnormal = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    head_abnormal_content = fields.Char(readonly=True, states={'Start': [('readonly', False)]})
    skin_normal = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    skin_abnormal = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    skin_abnormal_content = fields.Char(readonly=True, states={'Start': [('readonly', False)]})
    lunge_normal = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    lunge_abnormal = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    lunge_abnormal_content = fields.Char(readonly=True, states={'Start': [('readonly', False)]})
    chest_normal = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    chest_abnormal = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    chest_abnormal_content = fields.Char(readonly=True, states={'Start': [('readonly', False)]})
    abdomen_normal = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    abdomen_abnormal = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    abdomen_abnormal_content = fields.Char(readonly=True, states={'Start': [('readonly', False)]})
    elimination_normal = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    elimination_abnormal = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    elimination_abnormal_content = fields.Char(readonly=True, states={'Start': [('readonly', False)]})
    genitalia_normal = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    genitalia_abnormal = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    genitalia_abnormal_content = fields.Char(readonly=True, states={'Start': [('readonly', False)]})
    extremities_normal = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    extremities_abnormal = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    extremities_abnormal_content = fields.Char(readonly=True, states={'Start': [('readonly', False)]})
    number_of_diaper_per_day = fields.Integer(readonly=True, states={'Start': [('readonly', False)]})
    number_of_stools_per_day = fields.Integer(readonly=True, states={'Start': [('readonly', False)]})
    adequate_amount_diapers_home = fields.Selection(yes_no, readonly=True, states={'Start': [('readonly', False)]})
    adequate_amount_diapers_home_text = fields.Char(readonly=True, states={'Start': [('readonly', False)]})
    circumcised = fields.Selection(yes_no, readonly=True, states={'Start': [('readonly', False)]})

    mental_assessments_show = fields.Boolean()
    amount_crying_normal = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    amount_crying_abnormal = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    amount_crying_abnormal_content = fields.Char(readonly=True, states={'Start': [('readonly', False)]})
    makes_eye_contact_normal = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    makes_eye_contact_abnormal = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    makes_eye_contact_abnormal_content = fields.Char(readonly=True, states={'Start': [('readonly', False)]})
    quiet_when_pick_normal = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    quiet_when_pick_abnormal = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    quiet_when_pick_abnormal_content = fields.Char(readonly=True, states={'Start': [('readonly', False)]})

    nutrition_show = fields.Boolean()
    feeding_type = fields.Selection([
        ('Breast', 'Breast'),
        ('Bottle', 'Bottle'),
        ('Breast and Bottle', 'Breast and Bottle'),
    ], readonly=True, states={'Start': [('readonly', False)]})
    formula_feeding = fields.Text(readonly=True, states={'Start': [('readonly', False)]})
    amount_frequency = fields.Text(readonly=True, states={'Start': [('readonly', False)]})
    adequate_amount_of_formula = fields.Selection(yes_no, readonly=True, states={'Start': [('readonly', False)]})
    adequate_amount_of_formula_text = fields.Char(readonly=True, states={'Start': [('readonly', False)]})

    other_assessment_show = fields.Boolean()
    other_assessment_show_text = fields.Text(readonly=True, states={'Start': [('readonly', False)]})

    immunization_show = fields.Boolean()
    received_initial_hepatitis = fields.Selection(yes_no, readonly=True, states={'Start': [('readonly', False)]})
    where_and_when = fields.Text(readonly=True, states={'Start': [('readonly', False)]})
    has_an_appointment_been = fields.Selection(yes_no, readonly=True, states={'Start': [('readonly', False)]})
    has_an_appointment_been_date = fields.Date(readonly=True, states={'Start': [('readonly', False)]})
    has_an_appointment_been_where = fields.Char(readonly=True, states={'Start': [('readonly', False)]})
    has_an_appointment_been_no_text = fields.Text(readonly=True, states={'Start': [('readonly', False)]})

    safe_sleep_show = fields.Boolean()
    crib = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    bassinet = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    other = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    other_content = fields.Char(readonly=True, states={'Start': [('readonly', False)]})

    mother_caregiver_education_show = fields.Boolean()
    advise_to_refrain_putting_stuffed_animals = fields.Selection(yes_no_na, readonly=True,
                                                                 states={'Start': [('readonly', False)]})
    advise_that_sleep_environment_should = fields.Selection(yes_no_na, readonly=True,
                                                            states={'Start': [('readonly', False)]})
    advise_not_to_share_sleep = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    advise_on_proper_position = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    advise_to_refrain_from_smoking = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    advise_to_change_clothes_before_holding = fields.Selection(yes_no_na, readonly=True,
                                                               states={'Start': [('readonly', False)]})
    advise_that_supervision_needed_when = fields.Selection(yes_no_na, readonly=True,
                                                           states={'Start': [('readonly', False)]})
    remarks_show = fields.Boolean()
    remarks = fields.Text(readonly=True, states={'Start': [('readonly', False)]})

    newborn_follow_up_id = fields.One2many('sm.shifa.newborn.care.follow.up', 'newborn_care_id',
                                           string='newborn follow up')
    referral_id = fields.One2many('sm.shifa.referral', 'newborn_care_ref_id',
                                  string='newborn referral')
    consent_show = fields.Boolean()
    consent_file1 = fields.Binary()
    consent_file2 = fields.Binary()

    @api.onchange('hr_min', 'rr_min', 'temperature_c', 'weight_kg', 'length', 'head_circumference',
                  'number_of_diaper_per_day', 'number_of_stools_per_day', 'char_other_oxygen')
    def _check_vital_signs(self):
        if self.hr_min > 1000:
            raise ValidationError("invalid HR(/min)")
        if self.temperature_c > 100:
            raise ValidationError("invalid Temperature(C)")
        if self.rr_min > 100:
            raise ValidationError("invalid RR(/min)")
        # if self.o2_sat > 100:
        #     raise ValidationError("invalid O2 Sat(%)")
        if self.weight_kg > 100:
            raise ValidationError("invalid Weight (kg)")
        if self.length > 1000:
            raise ValidationError("invalid Length")
        if self.head_circumference > 1000:
            raise ValidationError("invalid Head Circumference")
        if self.number_of_diaper_per_day > 100:
            raise ValidationError("invalid Number of diaper per day")
        if self.number_of_stools_per_day > 100:
            raise ValidationError("invalid Number of Stools per day")
        if self.char_other_oxygen > 1000:
            raise ValidationError("invalid O2 Sat(%)")

    @api.model
    def create(self, vals):
        vals['newborn_care_code'] = self.env['ir.sequence'].next_by_code('newborn.care')
        return super(NewbornCare, self).create(vals)


class ShifaReferralInherit(models.Model):
    _inherit = 'sm.shifa.referral'

    newborn_care_ref_id = fields.Many2one('sm.shifa.newborn.care',
                                          string='newborn care', ondelete='cascade')
