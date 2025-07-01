from odoo import api, fields, models, _
from datetime import date
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, UserError


class ShifaMultidisciplinaryTeamMeeting(models.Model):
    _name = 'sm.shifa.multidisciplinary.team.meeting'
    _description = "Multidisciplinary Team Meeting"
    STATES = [
        ('Draft', 'Draft'),
        ('Completed', 'Completed'),
    ]
    state = fields.Selection(STATES, string='State', default=lambda *a: 'Draft', readonly=True)
    name = fields.Char('Reference', index=True, copy=False,  default=lambda *a: '/')
    patient = fields.Many2one('oeh.medical.patient', string='Patient', required=True, readonly=True, states={'Draft': [('readonly', False)]})
    dob = fields.Date(string='Date of Birth', related='patient.dob',  readonly=False, states={'Completed': [('readonly', True)]})
    marital_status = fields.Selection(string='Marital Status', related='patient.marital_status' ,  readonly=False, states={'Completed': [('readonly', True)]})
    sex = fields.Selection(string='Sex', related='patient.sex',  readonly=False, states={'Completed': [('readonly', True)]})
    blood_type = fields.Selection(string='Blood Type', related='patient.blood_type',  readonly=False, states={'Completed': [('readonly', True)]})
    rh = fields.Selection(string='Rh', related='patient.rh',  readonly=False, states={'Completed': [('readonly', True)]})
    ssn = fields.Char(size=256, related='patient.ssn',  readonly=False, states={'Completed': [('readonly', True)]})
    mobile = fields.Char(string='Mobile', related='patient.mobile',  readonly=False, states={'Completed': [('readonly', True)]})
    patient_weight = fields.Float(string='Weight(kg)', related='patient.weight',  readonly=False, states={'Completed': [('readonly', True)]})
    age = fields.Char(string='Age', related='patient.age',  readonly=False, states={'Completed': [('readonly', True)]})
    nationality = fields.Char(string='Nationality', related='patient.nationality', readonly=False, states={'Completed': [('readonly', True)]})
    date = fields.Datetime(string="Date" , required=True, readonly=True, states={'Draft': [('readonly', False)]})
    doctor = fields.Many2one('oeh.medical.physician', string='First Doctor', help="Current primary care / family doctor",
                             domain=[('role_type', 'in', ['HD', 'HHCD', 'HVD']), ('active', '=', True)],
                             readonly=True, states={'Draft': [('readonly', False)]})
    sec_doctor = fields.Many2one('oeh.medical.physician', string='Second Doctor', help="Current primary care / family doctor",
                             domain=[('role_type', 'in', ['HD', 'HHCD', 'HVD']), ('active', '=', True)],
                             readonly=True, states={'Draft': [('readonly', False)]})

    nurse = fields.Many2one('oeh.medical.physician', string='First Nurse', help="Current primary care / family doctor",
                             domain=[('role_type', 'in', ['HN', 'HHCN']), ('active', '=', True)],
                             readonly=True, states={'Draft': [('readonly', False)]}, required=True)
    sec_nurse = fields.Many2one('oeh.medical.physician', string='Second Nurse', help="Current primary care / family doctor",
                             domain=[('role_type', 'in', ['HN', 'HHCN']), ('active', '=', True)],
                             readonly=True, states={'Draft': [('readonly', False)]})

    physiotherapist = fields.Many2one('oeh.medical.physician', string='Physiotherapist', help="Current primary care / family doctor",
                             domain=[('role_type','in', ['HP', 'HHCP']), ('active', '=', True)],
                             readonly=True, states={'Draft': [('readonly', False)]})
    respiratory_therapist = fields.Many2one('oeh.medical.physician', string='Respiratory Therapist', help="Current primary care / family doctor",
                             domain=[('role_type', '=', 'RT'), ('active', '=', True)],
                             readonly=True, states={'Draft': [('readonly', False)]})
    diabetic_educator = fields.Many2one('oeh.medical.physician', string='Diabetic Educator', help="Current primary care / family doctor",
                             domain=[('role_type', '=', 'DE'), ('active', '=', True)],
                             readonly=True, states={'Draft': [('readonly', False)]})
    clinical_dietitian = fields.Many2one('oeh.medical.physician', string='Clinical Dietitian', help="Current primary care / family doctor",
                             domain=[('role_type','=', 'CD'), ('active', '=', True)],
                             readonly=True, states={'Draft': [('readonly', False)]})
    social_worker = fields.Many2one('oeh.medical.physician', string='Social Worker', help="Current primary care / family doctor",
                             domain=[('role_type', '=', 'SW'), ('active', '=', True)],
                             readonly=True, states={'Draft': [('readonly', False)]})

    diagnosis_show = fields.Boolean(default=True)
    provisional_diagnosis = fields.Many2one('oeh.medical.pathology', string='Disease', readonly=True, states={'Draft': [('readonly', False)]})
    provisional_diagnosis_add_other = fields.Boolean()
    provisional_diagnosis_add = fields.Many2one('oeh.medical.pathology', string='Disease', readonly=True, states={'Draft': [('readonly', False)]})
    provisional_diagnosis_add_other2 = fields.Boolean()
    provisional_diagnosis_add2 = fields.Many2one('oeh.medical.pathology', string='Disease', readonly=True, states={'Draft': [('readonly', False)]})
    provisional_diagnosis_add_other3 = fields.Boolean()
    provisional_diagnosis_add3 = fields.Many2one('oeh.medical.pathology', string='Disease', readonly=True, states={'Draft': [('readonly', False)]})
    provisional_diagnosis_add_other4 = fields.Boolean()
    provisional_diagnosis_add4 = fields.Many2one('oeh.medical.pathology', string='Disease', readonly=True, states={'Draft': [('readonly', False)]})
    provisional_diagnosis_add_other5 = fields.Boolean()
    provisional_diagnosis_add5 = fields.Many2one('oeh.medical.pathology', string='Disease',readonly=True, states={'Draft': [('readonly', False)]})
    provisional_diagnosis_add_other6 = fields.Boolean()
    provisional_diagnosis_add6 = fields.Many2one('oeh.medical.pathology', string='Disease',readonly=True, states={'Draft': [('readonly', False)]})
    provisional_diagnosis_add_other7 = fields.Boolean()
    provisional_diagnosis_add7 = fields.Many2one('oeh.medical.pathology', string='Disease', readonly=True, states={'Draft': [('readonly', False)]})
    provisional_diagnosis_add_other8 = fields.Boolean()
    provisional_diagnosis_add8 = fields.Many2one('oeh.medical.pathology', string='Disease', readonly=True, states={'Draft': [('readonly', False)]})
    provisional_diagnosis_add_other9 = fields.Boolean()
    provisional_diagnosis_add9 = fields.Many2one('oeh.medical.pathology', string='Disease', readonly=True, states={'Draft': [('readonly', False)]})

    issues_discussed_show = fields.Boolean()
    physician_notes_show = fields.Boolean()
    issues_discussed = fields.Text(readonly=True, states={'Draft': [('readonly', False)]})
    physician_notes = fields.Text(readonly=True, states={'Draft': [('readonly', False)]})
    actions_required_nurse = fields.Text(readonly=True, states={'Draft': [('readonly', False)]})
    actions_required_nurse_sec = fields.Text(readonly=True, states={'Draft': [('readonly', False)]})
    actions_required_physiotherapist = fields.Text(readonly=True, states={'Draft': [('readonly', False)]})
    actions_required_respiratory_therapist = fields.Text(readonly=True, states={'Draft': [('readonly', False)]})
    actions_required_diabetic_educator = fields.Text(readonly=True, states={'Draft': [('readonly', False)]})
    actions_required_clinical_dietitian = fields.Text(readonly=True, states={'Draft': [('readonly', False)]})
    actions_required_social_worker = fields.Text(readonly=True, states={'Draft': [('readonly', False)]})
    team_signatures_show = fields.Boolean()
    team_signatures_doctor = fields.Binary(string="First Doctor")
    team_signatures_sec_doctor = fields.Binary(string="Second Doctor")
    team_signatures_nurse = fields.Binary(string="First Nurse")
    team_signatures_sec_nurse = fields.Binary(string="Second Nurse")
    team_signatures_physiotherapist = fields.Binary(string="Physiotherapist")
    team_signatures_respiratory_therapist = fields.Binary(string="Respiratory Therapist")
    team_signatures_diabetic_educator = fields.Binary(string="Diabetic Educator")
    team_signatures_clinical_dietitian = fields.Binary(string="Clinical Dietitian")
    team_signatures_social_worker = fields.Binary(string="Social Worker")
    active = fields.Boolean(default=True)

    def action_archive(self):
        for rec in self:
            if rec.state != 'Completed':
                raise UserError(_("You can archive only if it completed record"))
        return super().action_archive()
    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('sm.shifa.multidisciplinary.team.meeting')
        return super(ShifaMultidisciplinaryTeamMeeting, self).create(vals)

    def mark_as_completed(self):
        self.state = 'Completed'

    @api.onchange('doctor')
    def _get_user_doctor_sig(self):
        for rec in self:
            rec.team_signatures_doctor = rec.doctor.oeh_user_id.user_signature

    @api.onchange('sec_doctor')
    def _get_user_sec_doctor_sig(self):
        for rec in self:
            rec.team_signatures_doctor = rec.doctor.oeh_user_id.user_signature

    @api.onchange('nurse')
    def _get_user_nurse_sig(self):
        for rec in self:
            rec.team_signatures_nurse = rec.nurse.oeh_user_id.user_signature

    @api.onchange('sec_nurse')
    def _get_user_sec_nurse_sig(self):
        for rec in self:
            rec.team_signatures_nurse = rec.nurse.oeh_user_id.user_signature

    @api.onchange('physiotherapist')
    def _get_user_physiotherapist_sig(self):
        for rec in self:
            rec.team_signatures_physiotherapist = rec.physiotherapist.oeh_user_id.user_signature

    @api.onchange('respiratory_therapist')
    def _get_user_respiratory_therapist_sig(self):
        for rec in self:
            rec.team_signatures_respiratory_therapist = rec.respiratory_therapist.oeh_user_id.user_signature

    @api.onchange('diabetic_educator')
    def _get_user_diabetic_educator_sig(self):
        for rec in self:
            rec.team_signatures_diabetic_educator = rec.diabetic_educator.oeh_user_id.user_signature

    @api.onchange('clinical_dietitian')
    def _get_user_clinical_dietitian_sig(self):
        for rec in self:
            rec.team_signatures_clinical_dietitian = rec.clinical_dietitian.oeh_user_id.user_signature

    @api.onchange('social_worker')
    def _get_user_social_worker_sig(self):
        for rec in self:
            rec.team_signatures_social_worker = rec.social_worker.oeh_user_id.user_signature

    # download report at complete state
    def download_pdf(self):
        return self.env.ref('smartmind_shifa_more.sm_shifa_multidisciplinary_team_meeting').report_action(self)

