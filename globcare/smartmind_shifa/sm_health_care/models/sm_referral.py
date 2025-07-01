from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import ValidationError, UserError


class ShifaReferral(models.Model):
    _name = 'sm.shifa.referral'
    _description = 'Patient Referring Management'
    _rec_name = 'reference'

    STATE = [
        ('start', 'Start'),
        ('call_center', 'Call Center'),
        ('done', 'Done'),
        ('canceled', 'Canceled')
    ]

    URGENCY_LEVEL = [
        ('Normal', 'Normal'),
        ('Urgent', 'Urgent'),
        ('Medical Emergency', 'Medical Emergency'),
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

    reference = fields.Char(string='Reference', required=True, copy=False, readonly=True, index=True,
                            default=lambda self: _('New'))
    patient = fields.Many2one('oeh.medical.patient', string='Patient', required=True,  readonly=True, states={'start': [('readonly', False)]})
    dob = fields.Date(string='Date of Birth', related='patient.dob')
    marital_status = fields.Selection(string='Marital Status', related='patient.marital_status')
    sex = fields.Selection(string='Sex', related='patient.sex')
    blood_type = fields.Selection(string='Blood Type', related='patient.blood_type')
    rh = fields.Selection(string='Rh', related='patient.rh')
    phone = fields.Char(string='Phone', related='patient.phone')

    doctor = fields.Many2one('oeh.medical.physician', string='Requested by',  readonly=True, states={'start': [('readonly', False)]}, required=True, domain=[('active', '=', True)],
                             default=_get_nurse)
    #                              readonly=True, states={'start': [('readonly', False)]}
    date = fields.Datetime(string='Date & Time', required=True,
                           default=lambda *a: datetime.now())
    hhc_appointment = fields.Many2one('sm.shifa.hhc.appointment', string='HHC Appointment', readonly=True, states={'start': [('readonly', False)]})
    hvd_appointment = fields.Many2one('sm.shifa.hvd.appointment', string='HVD Appointment', readonly=True, states={'start': [('readonly', False)]})
    state = fields.Selection(STATE, default='start')

    referral_request_physiotherapy = fields.Boolean(string='Physiotherapy', readonly=True,
                                                    states={'start': [('readonly', False)]})
    referral_request_image_test = fields.Boolean(string='Image Test', readonly=True,
                                               states={'start': [('readonly', False)]})
    referral_request_lab_test = fields.Boolean(string='Lab Test', readonly=True,
                                               states={'start': [('readonly', False)]})

    urgency_level = fields.Selection(URGENCY_LEVEL, string='Urgency Level', default=lambda *a: 'Normal', readonly=True,
                                     states={'start': [('readonly', False)]})
    comment = fields.Text('Comment', readonly=True,
                          states={'start': [('readonly', False)]})
    call_center_comment = fields.Text('Call Center Comment', readonly=True,
                                      states={'call_center': [('readonly', False)]})
    # register_walk_in = fields.Many2one('sm.shifa.hhc.appointment', string='HHC Appointment')
    referral_lab_test = fields.Boolean(string='Lab Test', readonly=True, states={'start': [('readonly', False)]})
    referral_image_test = fields.Boolean(string='Image Test', readonly=True,
                                         states={'start': [('readonly', False)]})
    requested_date = fields.Datetime(string='Requested Date', readonly=True)
    processed_date = fields.Datetime(string='Processed Date', readonly=True)
    referral_respiratory_therapist = fields.Boolean(string='Respiratory Therapist', readonly=True,
                                                    states={'start': [('readonly', False)]})
    referral_clinical_dietitian = fields.Boolean(string='Clinical Dietitian', readonly=True,
                                                 states={'start': [('readonly', False)]})
    referral_physiotherapist = fields.Boolean(string='Physiotherapist', readonly=True,
                                              states={'start': [('readonly', False)]})
    referral_occupational = fields.Boolean(string='Occupational', readonly=True,
                                           states={'start': [('readonly', False)]})
    referral_therapist = fields.Boolean(string='Therapist', readonly=True,
                                        states={'start': [('readonly', False)]})
    referral_social_worker = fields.Boolean(string='Social Worker', readonly=True,
                                            states={'start': [('readonly', False)]})
    referral_physician = fields.Boolean(string='Physician', readonly=True,
                                        states={'start': [('readonly', False)]})
    # referral to wound care module
    wound_care_id = fields.Many2one('sm.shifa.wound.assessment', string='wound care', ondelete='cascade')
    home_questionnaire_ref_id = fields.Many2one('sm.shifa.safe.home.visit.screening', string='home questionnaire',
                                                ondelete='cascade')
    active = fields.Boolean(default=True)

    def action_archive(self):
        for rec in self:
            if rec.state not in ['done', 'canceled']:
                raise UserError(_("You can archive only if it done assessments"))
        return super().action_archive()

    @api.onchange('hhc_appointment')
    def _onchange_hhc_appointment(self):
        if self.hhc_appointment:
            self.patient = self.hhc_appointment.patient
            self.hvd_appointment = None

    @api.onchange('hvd_appointment')
    def _onchange_hvd_appointment(self):
        if self.hvd_appointment:
            self.patient = self.hvd_appointment.patient
            self.hhc_appointment = None

    @api.model
    def create(self, vals):
        if vals.get('reference', _('New')) == _('New'):
            vals['reference'] = self.env['ir.sequence'].next_by_code('sm.shifa.referral') or _(
                'New')
        result = super(ShifaReferral, self).create(vals)
        return result

    def set_to_call_center(self):
        requested_date = False
        for ina in self:
            if ina.requested_date:
                requested_date = ina.requested_date
            else:
                requested_date = datetime.now()
        return self.write({'state': 'call_center', 'requested_date': requested_date})

    def set_to_done(self):
        processed_date = False
        for ina in self:
            if ina.processed_date:
                processed_date = ina.processed_date
            else:
                processed_date = datetime.now()
        return self.write({'state': 'done', 'processed_date': processed_date})

    def set_to_cancel(self):
        return self.write({'state': 'canceled', 'processed_date': datetime.now()})
