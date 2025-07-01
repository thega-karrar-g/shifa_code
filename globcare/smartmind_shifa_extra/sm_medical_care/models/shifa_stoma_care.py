from _ast import Tuple

from odoo import models, fields, api
import datetime
from odoo.exceptions import ValidationError
from datetime import date
from psycopg2._psycopg import List


class StomaCare(models.Model):
    _name = 'sm.shifa.stoma.care'
    _description = 'Stoma Care'
    _rec_name = 'stoma_care_code'

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

    def _get_stoma(self):
        """Return default stoma value"""
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

    stoma_care_code = fields.Char('Reference', index=True, copy=False)
    patient = fields.Many2one('oeh.medical.patient', string='Patient', help="Patient Name", required=True,
                              readonly=True, states={'Draft': [('readonly', False)]})
    hhc_appointment = fields.Many2one('sm.shifa.hhc.appointment', string='HHC-Appointment',
                                      readonly=True, states={'Draft': [('readonly', False)]})
    doctor = fields.Many2one('oeh.medical.physician', string='Nurse', help="Current primary care / family doctor",
                             readonly=True, states={'Draft': [('readonly', False)]},
                             domain=[('role_type', '=', ['HHCN', 'HN']), ('active', '=', True)], required=True, default=_get_stoma)
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

    type_surgery_show = fields.Boolean()
    type_surgery = fields.Text(readonly=True, states={'Start': [('readonly', False)]})

    patient_assessment_show = fields.Boolean()
    vital_signs_remain = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    coping_with_changing = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    managing_skin = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})

    stoma_site_assessment_show = fields.Boolean()
    stoma_appliance_intact = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    presence_of_skin = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    nature_of_effluent = fields.Selection([
        ('Stool', 'Stool'),
        ('Urine', 'Urine'),
        ('Blood', 'Blood'),
        ('Bile', 'Bile'),
        ('Nil', 'Nil'),
    ], readonly=True, states={'Start': [('readonly', False)]})
    amount = fields.Integer(readonly=True, states={'Start': [('readonly', False)]})
    consistency = fields.Selection([
        ('Hard', 'Hard'),
        ('Soft', 'Soft'),
        ('Loose', 'Loose'),
    ], readonly=True, states={'Start': [('readonly', False)]})

    follow_up_care_show = fields.Boolean()
    stoma_care_clinic = fields.Text(readonly=True, states={'Start': [('readonly', False)]})
    review_dates = fields.Text(readonly=True, states={'Start': [('readonly', False)]})

    patient_caregiver_education_show = fields.Boolean()
    choose_outfit = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    eating_regular_ = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    drink_reqularly = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    observe_for_stomal = fields.Selection(yes_no_na, readonly=True, states={'Start': [('readonly', False)]})
    remarks_show = fields.Boolean()
    remarks = fields.Text(readonly=True, states={'Start': [('readonly', False)]})

    # notification
    stoma_follow_up_id = fields.One2many('sm.shifa.stoma.care.follow.up', 'stoma_care_id', string='stoma follow up')
    referral_id = fields.One2many('sm.shifa.referral', 'stoma_care_ref_id', string='stoma referral')
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
        vals['stoma_care_code'] = self.env['ir.sequence'].next_by_code('stoma.care')
        return super(StomaCare, self).create(vals)

    # def _labtest_count(self):
    #     oe_labs = self.env['sm.shifa.stoma.care.follow.up']
    #     for ls in self:
    #         domain = [('patient', '=', ls.id)]
    #         lab_ids = oe_labs.search(domain)
    #         labs = oe_labs.browse(lab_ids)
    #         labs_count = 0
    #         for lab in labs:
    #             labs_count+=1
    #         ls.labs_count = labs_count
    #     return True
    #
    # labs_count = fields.Integer(compute=_labtest_count, string="Lab Tests")


class ShifaReferralInherit(models.Model):
    _inherit = 'sm.shifa.referral'

    stoma_care_ref_id = fields.Many2one('sm.shifa.stoma.care', string='stoma care', ondelete='cascade')
