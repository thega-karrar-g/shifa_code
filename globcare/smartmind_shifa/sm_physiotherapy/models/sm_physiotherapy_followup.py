from odoo import models, fields, api, _
import datetime
from odoo.exceptions import ValidationError, UserError


class ShifaPhysiotherapyFollowUp(models.Model):
    _name = "sm.shifa.physiotherapy.followup"
    _description = "Physiotherapy Follow Up"
    _rec_name = 'physiotherapy_assessment_follow_up_code'

    ADMISSION_STATES = [
        ('Draft', 'Draft'),
        ('Start', 'Start'),
        ('Done', 'Done'),
    ]

    @api.onchange('phys_appointment')
    def _onchange_phys_appointment(self):
        if self.phys_appointment:
            self.patient = self.phys_appointment.patient

    @api.onchange('phyio_as')
    def _onchange_join_phyio(self):
        if self.phyio_as:
            self.physiotherapy_assessment_id = self.phyio_as

    def _get_breast(self):
        """Return default breast value"""
        therapist_obj = self.env['oeh.medical.physician']
        domain = [('oeh_user_id', '=', self.env.uid)]
        user_ids = therapist_obj.search(domain, limit=1)
        if user_ids:
            return user_ids.id or False
        else:
            return False

    physiotherapy_assessment_follow_up_code = fields.Char('Reference', index=True,
                                                          copy=False)

    patient = fields.Many2one('oeh.medical.patient', string='Patient', help="Patient Name", required=True,
                              readonly=False, states={'Draft': [('readonly', False)]})
    phys_appointment = fields.Many2one('sm.shifa.physiotherapy.appointment', readonly=False,
                                       string='Physiotherapy appointment',
                                       states={'Draft': [('readonly', False)]})
    # hhc_appointment = fields.Many2one('sm.shifa.hhc.appointment', string='HHC-Appointment',
    #                                   readonly=False, states={'Draft': [('readonly', False)]} )
    phyio_as = fields.Many2one('sm.shifa.physiotherapy.assessment', string='Phyio-As#',
                               readonly=False, states={'Done': [('readonly', True)]},
                               domain="[('patient','=',patient), ('state', 'in', ('Admitted', 'Start'))]")
    nurse_name = fields.Many2one('oeh.medical.physician', string='Nurse', readonly=False,
                                 states={'Draft': [('readonly', False)]}, domain=[('role_type', '=', 'HHCN'), ('active', '=', True)],
                                 default=_get_breast)
    physiotherapist = fields.Many2one('oeh.medical.physician', string='Physiotherapist', readonly=False, required=True,
                                      states={'Draft': [('readonly', False)]},
                                      domain=[('role_type', 'in', ['HHCP', 'HP']), ('active', '=', True)],
                                      default=_get_breast)
    state = fields.Selection(ADMISSION_STATES, string='State', default=lambda *a: 'Draft', readonly=False)
    dob = fields.Date(string='Date of Birth', related='patient.dob')
    weight = fields.Float(string='Weight', related='patient.weight')
    age = fields.Char(string='Age', related='patient.age')
    marital_status = fields.Selection(string='Marital Status', related='patient.marital_status', readonly='1')
    sex = fields.Selection(string='Sex', related='patient.sex')
    blood_type = fields.Selection(string='Blood Type', related='patient.blood_type', readonly='1')
    rh = fields.Selection(string='Rh', related='patient.rh', readonly='1')
    start_date = fields.Datetime(string='Start Date', readonly=False, states={'Start': [('readonly', False)]})
    completed_date = fields.Datetime(string='Completed Date')

    vital_signs_show = fields.Boolean()
    systolic_bp = fields.Integer(readonly=False, states={'Start': [('readonly', False)]})
    hr_min = fields.Integer(readonly=False, states={'Start': [('readonly', False)]})
    diastolic_br = fields.Integer(readonly=False, states={'Start': [('readonly', False)]})
    rr_min = fields.Integer(readonly=False, states={'Start': [('readonly', False)]})
    temperature_c = fields.Float(readonly=False, states={'Start': [('readonly', False)]})
    o2_sat = fields.Selection([
        ('at room air', 'at room air'),
        ('with oxygen Support', 'with oxygen Support')
    ], readonly=False, states={'Start': [('readonly', False)]})
    char_other_oxygen = fields.Float(readonly=False, states={'Start': [('readonly', False)]})

    current_situation_show = fields.Boolean()
    current_situation = fields.Text(readonly=False, states={'Start': [('readonly', False)]})
    treatment_proposals_show = fields.Boolean()
    treatment_proposals = fields.Text(readonly=False, states={'Start': [('readonly', False)]})
    remarks_show = fields.Boolean()
    remarks = fields.Text(readonly=False, states={'Start': [('readonly', False)]})

    physiotherapy_assessment_id = fields.Many2one('sm.shifa.physiotherapy.assessment',
                                                  string='Physiotherapy Assessment', ondelete='cascade')
    notification_id = fields.One2many('sm.physician.notification', 'physiotherapy_assessment_not_id',
                                      string='physiotherapy notification')
    service = fields.Many2one('sm.shifa.service', string='Service Name',
                              required=True,
                              domain=[('name', 'in', ["Neuro Rehab Follow-up", "Geriatric Rehab Follow-up",
                                                      "Pediatric Rehab Follow-up",
                                                      "Ortho and Muscular Rehab Follow-up"])],
                              readonly=False, states={'Draft': [('readonly', False)]})
    consent_show = fields.Boolean()
    consent_file1 = fields.Binary()
    consent_file2 = fields.Binary()
    active = fields.Boolean(default=True)

    def action_archive(self):
        for rec in self:
            if rec.state != 'Done':
                raise UserError(_("You can archive only if it done assessments"))
        return super().action_archive()
    @api.onchange('physiotherapy_assessment_follow_up_code')
    def _onchange_join_physiotherapy_assessment_followup(self):
        if self.physiotherapy_assessment_follow_up_code:
            self.physiotherapy_assessment_id = self.physiotherapy_assessment_follow_up_code

    # @api.onchange('phyio_as')
    # def _onchange_phyio_as(self):
    #     if self.phyio_as:
    #         self.patient = self.phyio_as.patient
    # self.hhc_appointment = self.phyio_as.hhc_appointment

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
        vals['physiotherapy_assessment_follow_up_code'] = self.env['ir.sequence'].next_by_code(
            'sm.shifa.physiotherapy.followup')
        return super(ShifaPhysiotherapyFollowUp, self).create(vals)

    def set_to_done(self):
        return self.write({'state': 'Done', 'completed_date': datetime.datetime.now()})

    def set_to_start(self):
        return self.write({'state': 'Start', 'start_date': datetime.datetime.now()})


class ShifaNotificationInherit(models.Model):
    _inherit = 'sm.physician.notification'

    physiotherapy_assessment_not_id = fields.Many2one('sm.shifa.physiotherapy.followup',
                                                      string='physiotherapy assessment follow up', ondelete='cascade')
