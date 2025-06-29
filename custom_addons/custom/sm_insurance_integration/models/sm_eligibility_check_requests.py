from odoo import models, fields, api

class EligibilityCheckRequest(models.Model):
    _name = 'sm.eligibility.check.request'
    _description = 'Eligibility Check Request'

    # Fields
    name = fields.Char(string='Reference', readonly=True, default=lambda self: self._generate_reference())
    state = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('processed', 'Processed'),
    ], string='Status', default='draft', readonly=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)


    # Request Details
    patient_id = fields.Many2one('oeh.medical.patient', string='Patient', required=True)
    ssn = fields.Char(string='ID Number', related='patient_id.ssn')

    tele_appointment_id = fields.Many2one('oeh.medical.appointment', string='Tele-medicine Reference', required=True)
    physiotherapy_appointment_id = fields.Many2one('sm.shifa.physiotherapy.appointment', string='physiotherapy Reference', required=True)

    # department_id = fields.Many2one('sm.medical.staff.department', string='Department',required="True")
    # clinic_appointment_id = fields.Many2one('sm.clinic.appointment', string='Appointment Reference', required=True)
    # visit_date = fields.Date(string='Visit Date', related='clinic_appointment_id.date')
    # visit_time = fields.Float(string='Visit Time', related='clinic_appointment_id.appointment_time')

    # Insurance Details
    insured_company_id = fields.Many2one('sm.medical.insured.companies', string='Insured Company')
    insured_policy = fields.Many2one('sm.insurance.policy', string="Policy Number",
                                     domain="[('company_name_id', '=', insured_company_id), ('state', '=', 'active')]")
    insurance_company_id = fields.Many2one(related='insured_policy.insurance_company_id', string='Insurance Company')
    expiration_date = fields.Date(related='insured_policy.expiration_date')
    class_company_id = fields.Many2one('sm.medical.insurance.classes', string='Insurance Class',
                                       domain="[('insurance_policy_id', '=', insured_policy)]")
    serv_patient_deduct = fields.Integer(related='class_company_id.serv_patient_deduct', string='Patent Deduct(%)')
    pt_deduct_visit = fields.Integer(related='class_company_id.pt_deduct_visit', string='Deduct Per Visit')
    approval_limit = fields.Integer(related='class_company_id.approval_limit', string='Approval Limit')
    home_visit = fields.Boolean(related='insured_policy.home_visit')
    tele_consultation = fields.Boolean(related='insured_policy.tele_consultation')
    insurance_state = fields.Selection(related='insured_policy.state', string='state')
    active = fields.Boolean('Active', default=True)


    # Fields for Eligibility Response
    eligibility_response = fields.Selection([
        ('eligible', 'Eligible'),
        ('ineligible', 'Ineligible'),
    ], string='Eligibility Response')
    eligibility_reference = fields.Char(string='Eligibility Reference')
    comment = fields.Text(string='Comment')

    # Conditional Member Information (Appears only if 'eligibility_response' is 'eligible')
    member_name = fields.Char(string='Member Name')
    member_patient_id = fields.Char(string='Patient ID')
    sex = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
    ], string='Sex')
    date_of_birth = fields.Date(string='Date of Birth')
    marital_status = fields.Selection([
        ('single', 'Single'),
        ('married', 'Married'),
        ('widowed', 'Widowed'),
        ('divorced', 'Divorced'),
        ('separated', 'Separated'),
    ], string='Marital Status')
    member_id = fields.Char(string='Member ID')
    policy_number = fields.Char(string='Policy Number')
    insurance_class = fields.Char(string='Class')
    insured_company = fields.Char(string='Insured Company (Policy Holder)')
    start_date = fields.Date(string='Start Date')
    expired_date = fields.Date(string='Expired Date')

    # Treatment and Coverage Information (Conditional)
    max_consult_fee = fields.Float(string='Max. Consult Fee')
    approval_limit = fields.Float(string='Approval Limit')
    approval_threshold = fields.Float(string='Approval Threshold')
    deductible_percentage = fields.Float(string='Deductible (%)')
    deductible_description = fields.Text(string='Deductible Description')


    @api.model
    def create(self, vals):
        vals['name'] = self.sudo().env.ref('sm_insurance_integration.seq_sm_eligibility_check_request').next_by_id()
        record = super(EligibilityCheckRequest, self).create(vals)
        return record


    # Button Actions for Workflow
    def action_send(self):
        return self.write({'state': 'sent'})

    def action_process(self):
        return self.write({'state': 'processed'})

    def write(self, vals):
        result = super(EligibilityCheckRequest, self).write(vals)
        self._update_appointment_fields()
        return result

    def _update_appointment_fields(self):
        for record in self:
            if record.clinic_appointment_id:
                record.clinic_appointment_id.write({
                    'eligibility_response': record.eligibility_response,
                    'eligibility_reference': record.eligibility_reference,
                    'comment': record.comment,
                })
