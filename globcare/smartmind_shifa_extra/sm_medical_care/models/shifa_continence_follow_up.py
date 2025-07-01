from odoo import models, fields, api
import datetime
from odoo.exceptions import ValidationError


class ContinenceCareFollowUp(models.Model):
    _name = 'sm.shifa.continence.care.follow.up'
    _description = 'Continence Care Follow Up'
    _rec_name = 'continence_care_follow_up_code'

    ADMISSION_STATES = [
        ('Draft', 'Draft'),
        ('Start', 'Start'),
        ('Done', 'Done'),
    ]

    @api.onchange('cc_sf')
    def _onchange_join_cc(self):
        if self.cc_sf:
            self.continence_care_id = self.cc_sf

    @api.onchange('hhc_appointment')
    def _onchange_hhc_appointment(self):
        if self.hhc_appointment:
            self.patient = self.hhc_appointment.patient

    def _get_continence(self):
        """Return default continence value"""
        therapist_obj = self.env['oeh.medical.physician']
        domain = [('oeh_user_id', '=', self.env.uid)]
        user_ids = therapist_obj.search(domain, limit=1)
        if user_ids:
            return user_ids.id or False
        else:
            return False

    continence_care_follow_up_code = fields.Char('Reference', index=True, copy=False)

    patient = fields.Many2one('oeh.medical.patient', string='Patient', help="Patient Name", required=True,
                              readonly=True, states={'Draft': [('readonly', False)]})
    hhc_appointment = fields.Many2one('sm.shifa.hhc.appointment', string='HHC-Appointment',
                                      readonly=True, states={'Draft': [('readonly', False)]})
    cc_sf = fields.Many2one('sm.shifa.continence.care', string='CC#', required=True,
                            readonly=True, states={'Draft': [('readonly', False)]},
                            domain="[('patient','=',patient), ('state', 'in', ('Admitted', 'Start'))]")
    nurse_name = fields.Many2one('oeh.medical.physician', string='Nurse', readonly=True, required=True,
                                 states={'Draft': [('readonly', False)]}, domain=[('role_type', '=', ['HHCN', 'HN']), ('active', '=', True)],
                                 default=_get_continence)
    state = fields.Selection(ADMISSION_STATES, string='State', default=lambda *a: 'Draft', readonly=True)
    weight = fields.Float(string='Weight', related='patient.weight')
    age = fields.Char(string='Age', related='patient.age')
    marital_status = fields.Selection(string='Marital Status', related='patient.marital_status', readonly='1')
    sex = fields.Selection(string='Sex', related='patient.sex')
    blood_type = fields.Selection(string='Blood Type', related='patient.blood_type', readonly='1')
    rh = fields.Selection(string='Rh', related='patient.rh', readonly='1')
    start_date = fields.Datetime(string='Start Date', readonly='1')
    completed_date = fields.Datetime(string='Completed Date', readonly='1')

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

    the_following_early_show = fields.Boolean()
    deterioration = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    systolic = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    heart_rate = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    respiratory_rate = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    difficulty_breathing = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    multiple_convulsion = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    chest_pain = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    progress_noted_show = fields.Boolean()
    care_rendered_show = fields.Boolean()
    progress_noted = fields.Text(readonly=True, states={'Start': [('readonly', False)]})
    care_rendered = fields.Text(readonly=True, states={'Start': [('readonly', False)]})

    # link to stoma care
    continence_care_id = fields.Many2one('sm.shifa.continence.care', string='Continence Care', ondelete='cascade')
    notification_id = fields.One2many('sm.physician.notification', 'continence_care_not_id',
                                      string='pressure notification')
    consent_show = fields.Boolean()
    consent_file1 = fields.Binary()
    consent_file2 = fields.Binary()

    @api.model
    def create(self, vals):
        vals['continence_care_follow_up_code'] = self.env['ir.sequence'].next_by_code('continence.care.follow.up')
        return super(ContinenceCareFollowUp, self).create(vals)

    def set_to_done(self):
        return self.write({'state': 'Done', 'completed_date': datetime.datetime.now()})

    def set_to_start(self):
        return self.write({'state': 'Start', 'start_date': datetime.datetime.now()})

    # @api.onchange('cc_sf')
    # def _onchange_cc_sf(self):
    #     if self.cc_sf:
    #         self.patient = self.cc_sf.patient
    #         self.hhc_appointment = self.cc_sf.hhc_appointment

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


class ShifaNotificationInherit(models.Model):
    _inherit = 'sm.physician.notification'

    continence_care_not_id = fields.Many2one('sm.shifa.continence.care.follow.up', string='continence care follow up',
                                             ondelete='cascade')
