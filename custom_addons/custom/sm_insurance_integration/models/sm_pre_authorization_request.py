from odoo import models, fields, api


class PreAuthorizationRequest(models.Model):
    _name = 'sm.pre.authorization.request'
    _description = 'Pre Authorization Request'

    name = fields.Char(string='Request Name')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('processed', 'Processed')
    ], string='Status', default='draft')

    patient_id = fields.Many2one('oeh.medical.patient', string='Patient', required=True)
    ssn = fields.Char(string='ID Number', related='patient_id.ssn')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    active = fields.Boolean('Active', default=True)


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

  # Authorization Details
    authorization_type = fields.Selection([
        ('institutional', 'Institutional'),
        ('dental', 'Dental'),
        ('pharmacy', 'Pharmacy'),
        ('professional', 'Professional'),
        ('optical', 'Optical')
    ], string='Authorization Type',required=True)
    sub_type = fields.Selection([
        ('inpatient', 'Inpatient'),
        ('outpatient', 'Outpatient')
    ], string='Sub Type',required=True)
    referral_type = fields.Selection([
        ('na', 'NA'),
        ('out', 'Out'),
        ('in', 'In')
    ], string='Referral Type')
    accident = fields.Boolean(string='Accident')

    # Appointment Details
    # department_id = fields.Many2one('sm.medical.staff.department', string='Department', required="True")
    # clinic_appointment_id = fields.Many2one('sm.clinic.appointment', string='Appointment Reference', required=True)
    # visit_date = fields.Date(string='Visit Date',related='clinic_appointment_id.date')
    # visit_time = fields.Float(string='Visit Time',related='clinic_appointment_id.appointment_time')
    # Care Team
    physician_id = fields.Many2one('oeh.medical.physician', string='Physician Name')
    license_id = fields.Char(string='License ID', related='physician_id.code')
    role_type = fields.Char(string='Role Type')
    # care_team_role = fields.Selection(string='Care Team Role', related='physician_id.care_team_role')
    qualification = fields.Many2one(string='Qualification (Speciality)',related='physician_id.speciality')

    # Case Description
    diagnoses_show = fields.Boolean()
    # diagnoses_ids = fields.One2many('sm.pre.authorization.diagnosis', 'authorization_request_id', string='Diagnoses')
    chief_complaint_show = fields.Boolean()
    chief_complaint = fields.Text(string='Chief Complaint and Main System')

    # Duration of Illness
    illness_duration = fields.Integer(string='Duration of Illness')
    illness_duration_unit = fields.Selection([
        ('days', 'Days'),
        ('months', 'Months'),
        ('years', 'Years')
    ], string='Unit')

    # Vital Signs
    temperature = fields.Float(string='Temperature (°C)')
    blood_pressure = fields.Char(string='Blood Pressure (BP)')
    pulse = fields.Integer(string='Pulse (bpm)')
    respiratory_rate = fields.Integer(string='Respiratory Rate (breaths/min)')
    weight = fields.Float(string='Weight (kg)')

    # Accident Information
    accident_type = fields.Selection([
        ('motor_vehicle', 'Motor Vehicle Accident'),
        ('school', 'School Accident'),
        ('sporting', 'Sporting Accident'),
        ('workplace', 'Workplace Accident')
    ], string='Accident Type')
    accident_country = fields.Many2one('res.country', string='Country')
    accident_city = fields.Char(string='City')
    accident_state = fields.Char(string='State/Province')
    accident_street = fields.Char(string='Street Name')
    accident_date = fields.Date(string='Date')

    # Attachment Information
    # attachment_ids = fields.One2many('sm.pre.authorization.attachment', 'authorization_request_id', string='Attachments')

    # Services
    # service_ids = fields.One2many('sm.physician.order.line', 'authorization_request_id',string='services')

    # Medications
    medication_ids = fields.Char('sm.shifa.medication.profile')
    # prescription_line_ids = fields.One2many('sm.shifa.prescription.line', 'authorization_request_id', string='Medications')

# Response Details (Visible in Processed State)
    approval_status = fields.Selection([
        ('pending', 'Pending - Under Processing'),
        ('approved', 'Approved/Granted'),
        ('disapproved', 'Disapproved/Rejected'),
        ('partial', 'Partial Approval'),
        ('further_details', 'Further Details Required'),
        ('conditional', 'Conditional Approval'),
        ('referral', 'Referral Approval')
    ], string='Approval Status', readonly=False)
    approval_reference = fields.Char(string='Approval Reference', readonly=False)
    approval_comment = fields.Text(string='Comment', readonly=False)

    @api.model
    def create(self, vals):
        vals['name'] = self.sudo().env.ref('sm_insurance_integration.seq_sm_pre_authorization_request').next_by_id()
        record = super(PreAuthorizationRequest, self).create(vals)
        return record


    def action_send(self):
        return self.write({'state': 'sent'})

    def action_process(self):
        return self.write({'state': 'processed'})

    # @api.onchange('authorization_type')
    # def _onchange_related_lines(self):
    #     # When the patient changes, automatically update the insurance_company_id
    #     for line in self.service_ids:
    #         line.insurance_company_id = self.insurance_company_id

    # def validate(self):
    #     # Get all the checked lines
    #     selected_lines = self.service_ids.filtered(lambda l: l.create_order)
    #     if not selected_lines:
    #         self.env.user.notify_warning(message="No lines selected!", title="Warning", sticky=False)
    #         return
    #
    #     # Create a service sale record for the selected lines
    #     service_sale = self.env['sm.service.sale'].sudo().create({
    #         'patient_id': self.patient_id.id,
    #         'physician_id': self.physician_id.id,
    #         'is_from_pre_auth': True,
    #         'payment_thru': 'insurance_pre_authorization',
    #         'pro_free_service': False,
    #         'state': 'invoiced',
    #         'name': self.env['ir.sequence'].next_by_code('sm_clinic_appointment.seq_sm_service_sale') or 'New',
    #         'service_order_ids': [(4, line.id) for line in selected_lines],  # Link the selected lines
    #     })
    #     service_sale.set_to_send()
    #     service_sale.set_to_invoiced()
    #     # Update the selected lines to indicate the order has been created
    #     selected_lines.sudo().update({
    #         'create_order': False,
    #     })
    #
    #     # Notify the user
    #     self.env.user.notify_success(message="Service Order created successfully!", title="Success", sticky=False)
    #
    #     # Redirect to the created service sale record
    #     form_view_id = self.env.ref('sm_clinic_appointment.sm_service_sale_form_view').id
    #     action = self.env["ir.actions.actions"]._for_xml_id("sm_clinic_appointment.sm_service_sale_action")
    #     action['views'] = [(form_view_id, 'form')]
    #     action['res_id'] = service_sale.id
    #     return action
