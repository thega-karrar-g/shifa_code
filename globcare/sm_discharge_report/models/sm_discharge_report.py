from odoo import api, fields, models, _
from datetime import date
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError


class SmDichargeReport(models.Model):
    _name = 'sm.discharge.report'
    _description = "Discharge Report"
    STATES = [
        ('draft', 'Draft'),
        ('completed', 'Completed'),
    ]
    yes_no = [
        ('yes', 'Yes'),
        ('no', 'No'),
    ]
    state = fields.Selection(STATES, string='State', default=lambda *a: 'draft', readonly=True)
    name = fields.Char('name', index=True, copy=False,  default=lambda *a: '/')
    patient_id = fields.Many2one('oeh.medical.patient', string='Patient', help="Patient Name", required=True,
                                 readonly=True, states={'draft': [('readonly', False)]})

    ssn = fields.Char(string='ID Number', readonly=False,
                      states={'completed': [('readonly', True)]},
                      related='patient_id.ssn')
    dob = fields.Date(string='Date of Birth', readonly=False,states={'completed': [('readonly', True)]},
                      related='patient_id.dob')
    mobile = fields.Char(string='Mobile', readonly=False, states={'completed': [('readonly', True)]},related='patient_id.mobile')
    sex = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female')], string='Gender', required=False, related='patient_id.sex', readonly=False,states={'completed': [('readonly', True)]})

    patient_weight = fields.Float(string='Weight(kg)', readonly=False,
                                  states={'Completed': [('readonly', True)]},
                                  related='patient_id.weight')
    age = fields.Char(string='Age', readonly=False,   states={'Completed': [('readonly', True)]}, related='patient_id.age')

    doctor_id = fields.Many2one('oeh.medical.physician', string='First Doctor',
                                domain=[('role_type', 'in', ['HHCD','HD'])],
                                required=True, readonly=False, states={'draft': [('readonly', False)]})

    doctor_id_2 = fields.Many2one('oeh.medical.physician', string='Second Doctor',
                                  domain=[('role_type', 'in', ['HHCD','HD'])],
                                  readonly=True, states={'draft': [('readonly', False)]})
    doctor_id_3 = fields.Many2one('oeh.medical.physician', string='Third Doctor', readonly=True,
                                  domain=[('role_type', 'in', ['HHCD','HD'])],
                                  states={'draft': [('readonly', False)]})
    nurse_id = fields.Many2one('oeh.medical.physician', string='First Nurse', help="Current primary care / family doctor",
                               domain=[('role_type', 'in', ['HN','HHCN'])],
                               readonly=True, states={'draft': [('readonly', False)]}, required=True)
    sec_nurse_id = fields.Many2one('oeh.medical.physician', string='Second Nurse',
                                help="Current primary care / family doctor",
                                domain=[('role_type',  'in', ['HN','HHCN'])],
                                readonly=True, states={'draft': [('readonly', False)]})

    physiotherapist_id = fields.Many2one('oeh.medical.physician', string='Physiotherapist',
                                      help="Current primary care / family doctor",
                                         domain=[('role_type',  'in', ['HP','HHCP'])],
                                         readonly=True, states={'draft': [('readonly', False)]})

    date_enrolled = fields.Datetime(string="Date Enrolled", required=True, readonly=True, states={'draft': [('readonly', False)]})
    transfer_date = fields.Datetime(string="Discharge / Transfer Date", required=True, readonly=True, states={'draft': [('readonly', False)]})
    physician_notified = fields.Selection(yes_no, string="Physician Notified", readonly=True, states={'draft': [('readonly', False)]})
    nursing_program = fields.Boolean(string='Nursing')
    respiratory_program = fields.Boolean(string='Respiratory')
    durable_medical_equipment_program = fields.Boolean(string='Durable Medical Equipment')
    other_program = fields.Boolean(string='Other')

    other_program_text = fields.Char( help="Specify other programs")

    nursing_2_program = fields.Boolean(string='Nursing')
    respiratory_2_program = fields.Boolean(string='Respiratory')
    durable_medical_2_equipment = fields.Boolean(string='Durable Medical Equipment')
    other_text = fields.Boolean(string='Other')

    program_text = fields.Char(help="Specify other programs")

    nursing = fields.Boolean(string='Nursing')
    respiratory = fields.Boolean(string='Respiratory')
    durable_medical_equipment = fields.Boolean(string='Durable Medical Equipment')
    other_text_transfer = fields.Boolean(string='Other')

    transfer_text = fields.Char(help="Specify other programs")
    open_text = fields.Text(string="Text")

    second_nursing = fields.Boolean(string='Nursing')
    second_respiratory = fields.Boolean(string='Respiratory')
    second_durable_equipment = fields.Boolean(string='Durable Medical Equipment')
    second_text = fields.Boolean(string='Other')

    second_transfer_text = fields.Char(help="Specify other programs")
    second_open_text = fields.Text(string="Text")
    condition = [
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
        ('varies', 'Varies'),
        ('other', 'Other'),
    ]
    patient_condition = fields.Selection(condition, readonly=True, states={'draft': [('readonly', False)]})
    other_condition = fields.Char(string="specify")
    conditions = [
        ('ambulates_independently', 'Ambulates independently'),
        ('ambulates_assistance', 'Ambulates with Assistance'),
        ('daily_activities', 'Independent with Daily Activities'),
        ('bedridden', 'Bedridden'),
        ('assistant_required', 'Assistant Required with Daily Activities'),
        ('other', 'Other'),
    ]
    patient_condition_transfer = fields.Selection(conditions,string="Patient Condition", readonly=True, states={'draft': [('readonly', False)]})
    other_condition_transfer = fields.Char(string="specify")
    home_care_service = fields.Boolean(string='No Further Home Care Service required')
    respiratory_home_care = fields.Boolean(string='No Further Respiratory Home Care Services Required')
    nursing_home_care = fields.Boolean(string='No Further Nursing Home Care Services Required')
    moved_out = fields.Boolean(string='Patient has moved out of Riyadh')
    physician_request_services = fields.Boolean(string='Patient, family, or physician request services terminated')
    home_care_criteria = fields.Boolean(string='Patient non-compliant to Home Care Criteria')
    refusing_treatment = fields.Boolean(string='Patient refusing treatment')
    patient_expired = fields.Boolean(string='Patient Expired')
    other_reason = fields.Boolean(string='Other')
    other_reason_text = fields.Char(string='Other')
    patient_equipments = fields.Selection([('yes','Yes'),('no','No'),('na','NA')],string="Patient require equipment(s) / consumables", readonly=True, states={'draft': [('readonly', False)]})
    caregiver_education = fields.Text(string='Patient/Family/Caregiver Health Education')
    discharge_note = fields.Text(string='DISCHARGE NOTES')
    team_signatures_show = fields.Boolean()
    signatures_doctor_1 = fields.Binary(string="First Doctor")
    signatures_doctor_2 = fields.Binary(string="Second Doctor")
    signatures_doctor_3 = fields.Binary(string="Third Doctor")
    signatures_nurse = fields.Binary(string="First Nurse")
    signatures_sec_nurse = fields.Binary(string="Second Nurse")
    sign_physiotherapist= fields.Binary(string="physiotherapist")






    @api.model
    def create(self, vals):
        record = super(SmDichargeReport, self).create(vals)
        record['name'] = self.env['ir.sequence'].next_by_code('sm.discharge.report')
        return record

    def mark_as_completed(self):
        self.write({'state': 'completed'})

    # download report at complete state
    def download_pdf(self):
        return self.env.ref('sm_discharge_report.sm_discharge_reports').report_action(self)

    @api.onchange('doctor_id')
    def _get_user_doctor_sig(self):
        for rec in self:
            rec.signatures_doctor_1 = rec.doctor_id.oeh_user_id.user_signature

    @api.onchange('doctor_id_2')
    def _get_user_sec_doctor_sig(self):
        for rec in self:
            rec.signatures_doctor_2 = rec.doctor_id_2.oeh_user_id.user_signature

    @api.onchange('doctor_id_3')
    def _get_user_thir_doctor_sig(self):
        for rec in self:
            rec.signatures_doctor_3 = rec.doctor_id_3.oeh_user_id.user_signature

    @api.onchange('nurse_id')
    def _get_user_nurse_sig(self):
        for rec in self:
            rec.signatures_nurse = rec.nurse_id.oeh_user_id.user_signature

    @api.onchange('sec_nurse_id')
    def _get_user_sec_nurse_sig(self):
        for rec in self:
            rec.signatures_sec_nurse = rec.sec_nurse_id.oeh_user_id.user_signature

    @api.onchange('physiotherapist_id')
    def _get_user_physiotherapist_sig(self):
        for rec in self:
            rec.sign_physiotherapist = rec.physiotherapist_id.oeh_user_id.user_signature