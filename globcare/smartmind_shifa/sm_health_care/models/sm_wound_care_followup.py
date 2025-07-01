from odoo import models, fields, api
import datetime
from odoo.exceptions import ValidationError


class WoundCareFollowUp(models.Model):
    _name = 'sm.shifa.wound.care.followup'
    _description = 'Wound Care Follow Up'
    _rec_name = 'wound_care_follow_up_code'
    STATES = [
        ('Draft', 'Draft'),
        ('Start', 'Start'),
        ('Done', 'Done'),
    ]

    @api.onchange('hhc_appointment')
    def _onchange_hhc_appointment(self):
        if self.hhc_appointment:
            self.patient = self.hhc_appointment.patient

    def _get_nurse(self):
        """Return default stoma value"""
        therapist_obj = self.env['oeh.medical.physician']
        domain = [('oeh_user_id', '=', self.env.uid)]
        user_ids = therapist_obj.search(domain, limit=1)
        if user_ids:
            return user_ids.id or False
        else:
            return False

    def set_to_start(self):
        admission_date = False
        for ina in self:
            if ina.admission_date:
                admission_date = ina.admission_date
            else:
                admission_date = datetime.datetime.now()
        return self.write({'state': 'Start', 'admission_date': admission_date})

        #     admitted date method

    def set_to_admitted(self):
        discharged_date = False
        for ina in self:
            if ina.discharge_date:
                discharged_date = ina.discharge_date
            else:
                discharged_date = datetime.datetime.now()
        return self.write({'state': 'Done', 'discharge_date': discharged_date})

    @api.onchange('hhc_appointment')
    def _onchange_sc_st(self):
        if self.hhc_appointment:
            self.patient = self.hhc_appointment.patient

    wound_care_follow_up_code = fields.Char('Reference', index=True, copy=False)
    state = fields.Selection(STATES, string='State', default=lambda *a: 'Draft', readonly=True)
    patient = fields.Many2one('oeh.medical.patient', string='Patient', help="Patient Name", required=True,
                              readonly=False, states={'Draft': [('readonly', False)]})
    hhc_appointment = fields.Many2one('sm.shifa.hhc.appointment', string='HHC-Appointment',
                                      readonly=False, states={'Draft': [('readonly', False)]})
    wound_care_ref = fields.Many2one('sm.shifa.wound.assessment', required=True, string='WA#',
                                     domain="[('patient', '=', patient), ('state', 'in', ('Admitted', 'Start'))]",
                                     readonly=False, states={'Draft': [('readonly', False)]})
    nurse_name = fields.Many2one('oeh.medical.physician', string='Nurse', readonly=False, required=True,
                                 states={'Draft': [('readonly', False)]}, domain=[('role_type', '=', ['HHCN', 'HN']), ('active', '=', True)],
                                 default=_get_nurse)
    admission_date = fields.Datetime(string='Start Date')
    discharge_date = fields.Datetime(string='Completed Date')
    # patient info
    dob = fields.Date(string='Date of Birth', related='patient.dob', readonly='1')
    marital_status = fields.Selection(string='Marital Status', related='patient.marital_status', readonly='1')
    sex = fields.Selection(string='Sex', related='patient.sex')
    blood_type = fields.Selection(string='Blood Type', related='patient.blood_type', readonly='1')
    rh = fields.Selection(string='Rh', related='patient.rh', readonly='1')

    # observation Tab
    conscious_state_show = fields.Boolean()
    conscious_state = fields.Selection([
        ('Alert', 'Alert'),
        ('Response to Voice', 'Response to Voice'),
        ('Response to pain', 'Response to pain'),
        ('Unresponsive', 'Unresponsive'),
    ], readonly=False, states={'Start': [('readonly', False)]})
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
    o2_sat = fields.Float(readonly=False, states={'Start': [('readonly', False)]})

    the_following_early_show = fields.Boolean()
    deterioration = fields.Boolean(readonly=False, states={'Start': [('readonly', False)]})
    systolic = fields.Boolean(readonly=False, states={'Start': [('readonly', False)]})
    heart_rate = fields.Boolean(readonly=False, states={'Start': [('readonly', False)]})
    respiratory_rate = fields.Boolean(readonly=False, states={'Start': [('readonly', False)]})
    difficulty_breathing = fields.Boolean(readonly=False, states={'Start': [('readonly', False)]})
    multiple_convulsion = fields.Boolean(readonly=False, states={'Start': [('readonly', False)]})
    chest_pain = fields.Boolean(readonly=False, states={'Start': [('readonly', False)]})
    progress_noted_show = fields.Boolean()
    care_rendered_show = fields.Boolean()
    progress_noted = fields.Text(readonly=False, states={'Start': [('readonly', False)]})
    care_rendered = fields.Text(readonly=False, states={'Start': [('readonly', False)]})
    # link wound care to follow up
    wound_care_id = fields.Many2one('sm.shifa.wound.assessment', string='Wound Care', ondelete='cascade')
    notification_id = fields.One2many('sm.physician.notification', 'wound_care_id',
                                      string='Wound Notification')
    consent_show = fields.Boolean()
    consent_file1 = fields.Binary()
    consent_file2 = fields.Binary()

    # self.env.cr.execute(
    #     "SELECT id FROM sm_shifa_wound_assessment where  patient=%s",
    #     (self.patient.id))
    # wa = self.env.cr.fetchall()
    # print(wa)
    # self.wound_care_ref = wa
    # if len(wa) == 0:
    #     self.wound_care_ref = ''
    #     print(len(wa))
    # else:
    # print(len(wa))
    # for i in wa:
    #     if self.patient:
    #         self.wound_care_ref = i[0]
    #         print(i[0])

    @api.model
    def create(self, vals):
        vals['wound_care_follow_up_code'] = self.env['ir.sequence'].next_by_code('sm.shifa.wound.care.followup')
        return super(WoundCareFollowUp, self).create(vals)


class ShifaNotificationInherit(models.Model):
    _inherit = 'sm.physician.notification'

    wound_care_id = fields.Many2one('sm.shifa.wound.care.followup', string='wound care follow up',
                                    ondelete='cascade')
