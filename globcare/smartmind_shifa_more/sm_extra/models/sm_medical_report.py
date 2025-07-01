import base64
from odoo import api, fields, models, _
import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError


class SMReoprt(models.Model):
    _name = 'sm.medical.report'
    _description = "Report"
    _inherit = ['mail.thread']

    STATES = [
        ('Draft', 'Draft'),
        ('upload_result', 'Upload Result'),
        ('start_record', 'Start Record'),
        ('Completed', 'Completed'),
    ]

    Languages = [
        ('Arabic', 'Arabic'),
        ('English', 'English'),
    ]
    Report = [
        ('treatment_plan', 'Treatment Plan (Physiotherapy)'),
        ('Physiotherapy_medical', 'Physiotherapy Medical Services'),
        ('Physician_home_visit', 'Physician Home Visit'),
    ]
    state = fields.Selection(STATES, string='State', default=lambda *a: 'Draft', readonly=True)
    name = fields.Char('Reference', index=True, copy=False, default=lambda *a: '/')
    patient = fields.Many2one('oeh.medical.patient', string='Patient', required=True, readonly=True,
                              states={'Draft': [('readonly', False)], 'start_record': [('readonly', False)]})
    dob = fields.Date(string='Date of Birth', related='patient.dob', readonly=False,
                      states={'Completed': [('readonly', True)]})
    marital_status = fields.Selection(string='Marital Status', related='patient.marital_status', readonly=False,
                                      states={'Completed': [('readonly', True)]})
    sex = fields.Selection(string='Sex', related='patient.sex', readonly=False,
                           states={'Completed': [('readonly', True)]})
    blood_type = fields.Selection(string='Blood Type', related='patient.blood_type', readonly=False,
                                  states={'Completed': [('readonly', True)]})
    rh = fields.Selection(string='Rh', related='patient.rh', readonly=False, states={'Completed': [('readonly', True)]})
    ssn = fields.Char(size=256, related='patient.ssn', readonly=False, states={'Completed': [('readonly', True)]})
    mobile = fields.Char(string='Mobile', related='patient.mobile', readonly=False,
                         states={'Completed': [('readonly', True)]})
    patient_weight = fields.Float(string='Weight(kg)', related='patient.weight', readonly=False,
                                  states={'Completed': [('readonly', True)]})
    age = fields.Char(string='Age', related='patient.age', readonly=False, states={'Completed': [('readonly', True)]})

    # this is old version of nationality patient
    # nationality = fields.Char(string='Nationality', related='patient.nationality', readonly=False, states={'Completed': [('readonly', True)]}
    nationality = fields.Selection(string='Nationality', related='patient.ksa_nationality', readonly=False,
                                   states={'Completed': [('readonly', True)]})
    date = fields.Datetime(string="Date", required=True, readonly=True, states={'Draft': [('readonly', False)], 'start_record': [('readonly', False)]})
    doctor = fields.Many2one('oeh.medical.physician', string='Doctor', help="Current primary care / family doctor",
                             domain=[('role_type', 'in', ['HD', 'HHCD', 'HVD']), ('active', '=', True)],
                             readonly=True, states={'Draft': [('readonly', False)], 'start_record': [('readonly', False)]})
    nurse = fields.Many2one('oeh.medical.physician', string='Nurse', help="Current primary care / family doctor",
                            domain=[('role_type', 'in', ['HN', 'HHCN']), ('active', '=', True)],
                            readonly=True, states={'Draft': [('readonly', False)], 'start_record': [('readonly', False)]})
    physiotherapist = fields.Many2one('oeh.medical.physician', string='Physiotherapist',
                                      help="Current primary care / family doctor",
                                      domain=[('role_type', '=', ['HP', 'HHCP']), ('active', '=', True)],
                                      readonly=True, states={'Draft': [('readonly', False)], 'start_record': [('readonly', False)]})
    respiratory_therapist = fields.Many2one('oeh.medical.physician', string='Respiratory Therapist',
                                            help="Current primary care / family doctor",
                                            domain=[('role_type', '=', 'RT'), ('active', '=', True)],
                                            readonly=True, states={'Draft': [('readonly', False)], 'start_record': [('readonly', False)]})
    diabetic_educator = fields.Many2one('oeh.medical.physician', string='Diabetic Educator',
                                        help="Current primary care / family doctor",
                                        domain=[('role_type', '=', 'DE'), ('active', '=', True)],
                                        readonly=True, states={'Draft': [('readonly', False)], 'start_record': [('readonly', False)]})
    clinical_dietitian = fields.Many2one('oeh.medical.physician', string='Clinical Dietitian',
                                         help="Current primary care / family doctor",
                                         domain=[('role_type', '=', 'CD'), ('active', '=', True)],
                                         readonly=True, states={'Draft': [('readonly', False)], 'start_record': [('readonly', False)]})
    social_worker = fields.Many2one('oeh.medical.physician', string='Social Worker',
                                    help="Current primary care / family doctor",
                                    domain=[('role_type', '=', ('SW'))],
                                    readonly=True, states={'Draft': [('readonly', False)], 'start_record': [('readonly', False)]})
    team_signatures_show = fields.Boolean()
    team_signatures_doctor = fields.Binary(string="Doctor", compute="_get_user_doctor_sig")
    team_signatures_nurse = fields.Binary(string="Nurse")
    team_signatures_physiotherapist = fields.Binary(string="Physiotherapist")
    team_signatures_respiratory_therapist = fields.Binary(string="Respiratory Therapist")
    team_signatures_diabetic_educator = fields.Binary(string="Diabetic Educator")
    team_signatures_clinical_dietitian = fields.Binary(string="Clinical Dietitian")
    team_signatures_social_worker = fields.Binary(string="Social Worker")
    language = fields.Selection(Languages, string="Language", defualt='Arabic')
    report = fields.Selection(Report, string="Type")
    patient_assessment = fields.Html()
    goals = fields.Html()
    diagnosis_comm = fields.Char()
    diagnosis_comm_2 = fields.Char()
    recommendation = fields.Char()
    # Treatment Plan field
    treatment_plan = fields.Html()
    health_after_treatment = fields.Html()
    number1 = fields.Char()
    number2 = fields.Char()
    number3 = fields.Char()
    number4 = fields.Char()
    chief_complaint = fields.Char(string='Chief Complaint', readonly=True, states={'Draft': [('readonly', False)], 'start_record': [('readonly', False)]})
    history_illness = fields.Char(string='History of present illness', readonly=True,
                                  states={'Draft': [('readonly', False)], 'start_record': [('readonly', False)]})
    plan_care = fields.Char(string='Plan of Care', readonly=True, states={'Draft': [('readonly', False)], 'start_record': [('readonly', False)]})

    vital_signs_show = fields.Boolean()
    systolic_bp = fields.Integer(readonly=True, states={'Draft': [('readonly', False)], 'start_record': [('readonly', False)]})
    hr_min = fields.Integer(readonly=True, states={'Draft': [('readonly', False)], 'start_record': [('readonly', False)]})
    diastolic_br = fields.Integer(readonly=True, states={'Draft': [('readonly', False)], 'start_record': [('readonly', False)]})
    rr_min = fields.Integer(readonly=True, states={'Draft': [('readonly', False)], 'start_record': [('readonly', False)]})
    temperature_c = fields.Float(readonly=True, states={'Draft': [('readonly', False)], 'start_record': [('readonly', False)]})
    o2_sat = fields.Selection([
        ('at room air', 'at room air'),
        ('with oxygen Support', 'with oxygen Support')
    ], readonly=True, states={'Draft': [('readonly', False)], 'start_record': [('readonly', False)]})
    char_other_oxygen = fields.Char(readonly=True, states={'Draft': [('readonly', False)], 'start_record': [('readonly', False)]})

    provisional_diagnosis = fields.Many2one('oeh.medical.pathology', string='Disease', readonly=True,
                                            states={'Draft': [('readonly', False)], 'start_record': [('readonly', False)]})
    provisional_diagnosis_add_other = fields.Boolean(readonly=True, states={'Draft': [('readonly', False)], 'start_record': [('readonly', False)]})
    provisional_diagnosis_add = fields.Many2one('oeh.medical.pathology', string='Disease', readonly=True,
                                                states={'Draft': [('readonly', False)], 'start_record': [('readonly', False)]})
    provisional_diagnosis_add_other2 = fields.Boolean(readonly=True, states={'Draft': [('readonly', False)], 'start_record': [('readonly', False)]})
    provisional_diagnosis_add2 = fields.Many2one('oeh.medical.pathology', string='Disease', readonly=True,
                                                 states={'Draft': [('readonly', False)], 'start_record': [('readonly', False)]})
    provisional_diagnosis_add_other3 = fields.Boolean(readonly=True, states={'Draft': [('readonly', False)], 'start_record': [('readonly', False)]})
    provisional_diagnosis_add3 = fields.Many2one('oeh.medical.pathology', string='Disease', readonly=True,
                                                 states={'Draft': [('readonly', False)], 'start_record': [('readonly', False)]})

    provisional_diagnosis_add_other4 = fields.Boolean(readonly=True, states={'Draft': [('readonly', False)], 'start_record': [('readonly', False)]})
    provisional_diagnosis_add4 = fields.Many2one('oeh.medical.pathology', string='Disease', readonly=True,
                                                 states={'Draft': [('readonly', False)], 'start_record': [('readonly', False)]})
    provisional_diagnosis_add_other5 = fields.Boolean(readonly=True, states={'Draft': [('readonly', False)], 'start_record': [('readonly', False)]})
    provisional_diagnosis_add5 = fields.Many2one('oeh.medical.pathology', string='Disease', readonly=True,
                                                 states={'Draft': [('readonly', False)], 'start_record': [('readonly', False)]})
    provisional_diagnosis_add_other6 = fields.Boolean(readonly=True, states={'Draft': [('readonly', False)], 'start_record': [('readonly', False)]})
    provisional_diagnosis_add6 = fields.Many2one('oeh.medical.pathology', string='Disease', readonly=True,
                                                 states={'Draft': [('readonly', False)], 'start_record': [('readonly', False)]})
    provisional_diagnosis_add_other7 = fields.Boolean(readonly=True, states={'Draft': [('readonly', False)], 'start_record': [('readonly', False)]})
    provisional_diagnosis_add7 = fields.Many2one('oeh.medical.pathology', string='Disease', readonly=True,
                                                 states={'Draft': [('readonly', False)], 'start_record': [('readonly', False)]})
    provisional_diagnosis_add_other8 = fields.Boolean(readonly=True, states={'Draft': [('readonly', False)], 'start_record': [('readonly', False)]})
    provisional_diagnosis_add8 = fields.Many2one('oeh.medical.pathology', string='Disease', readonly=True,
                                                 states={'Draft': [('readonly', False)], 'start_record': [('readonly', False)]})
    provisional_diagnosis_add_other9 = fields.Boolean(readonly=True, states={'Draft': [('readonly', False)], 'start_record': [('readonly', False)]})
    provisional_diagnosis_add9 = fields.Many2one('oeh.medical.pathology', string='Disease', readonly=True,
                                                 states={'Draft': [('readonly', False)], 'start_record': [('readonly', False)]})
    link = fields.Char(readonly=True)

    def _get_pdf_link(self):
        link = ""
        config_obj = self.env['ir.config_parameter'].get_param('web.base.url')
        attachment_url = config_obj + "/web/attachments/token/"
        # print("URL", str(attachment_url))
        attach_name = self.env['ir.attachment'].search(
            ['|', ('name', '=', str(self.name) + '.pdf'), ('res_model', '=', "sm.medical.report")])
        # print("attach name: ", str(attach_name))

        for att_obj in attach_name:
            if att_obj.name == str(self.name) + ".pdf":
                # print("access_token:", str(att_obj.access_token))
                # print("id:", str(att_obj.id))
                # print("name:", str(att_obj.name))
                link = attachment_url + str(att_obj.access_token)
        return link

    def control_generate_link(self):
        reports = self.search([
            ('state', '=', 'Completed'),
        ])
        if reports:
            for rep in reports:
                rep.link = rep._get_pdf_link()

    def set_to_done_upload(self):
        return self.write({'state': 'upload_result', 'date': datetime.datetime.now()})

    def set_to_done(self):
        return self.write({'state': 'Completed'})

    def set_to_start(self):
        return self.write({'state': 'start_record'})

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('sm.medical.report')
        return super(SMReoprt, self).create(vals)

    def mark_as_completed(self):
        report = self.env.ref('smartmind_shifa_more.sm_medical_report')._render_qweb_pdf(
            self.id)[0]
        report = base64.b64encode(report)
        return self.write({'state': 'Completed', 'date': datetime.datetime.now()})

    def download_report(self):
        return self.env.ref('smartmind_shifa_more.sm_medical_report').report_action(self)

    @api.depends('doctor')
    def _get_user_doctor_sig(self):
        for rec in self:
            if rec.doctor:
                rec.team_signatures_doctor = rec.doctor.oeh_user_id.user_signature
            else:
                rec.team_signatures_doctor = False

    @api.onchange('nurse')
    def _get_user_nurse_sig(self):
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
