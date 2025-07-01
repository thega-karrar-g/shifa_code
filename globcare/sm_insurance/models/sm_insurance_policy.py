from datetime import timedelta, datetime
from odoo import api, fields, models, _
from datetime import date
from odoo.exceptions import ValidationError


# insured Companies
class SMInsurancePolicy(models.Model):
    _name = 'sm.insurance.policy'
    _description = 'Insurance Policy'
    _rec_name = 'policy_number'


    POLICY_STATUS = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('expired', 'Expired'),
    ]

    image_1920 = fields.Image("Image", max_width=1920, max_height=1920)
    image_1024 = fields.Image("Image 1024", related="image_1920", max_width=1024, max_height=1024, store=True)
    image_512 = fields.Image("Image 512", related="image_1920", max_width=512, max_height=512, store=True)
    image_256 = fields.Image("Image 256", related="image_1920", max_width=256, max_height=256, store=True)
    image_128 = fields.Image("Image 128", related="image_1920", max_width=128, max_height=128, store=True)

    name = fields.Char('Reference', index=True, copy=False)

    state = fields.Selection(POLICY_STATUS, string='Insurance Status', default=lambda *a: 'draft', readonly=True)
    company_name_id = fields.Many2one('sm.medical.insured.companies',string='Insured company', required=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    company_code = fields.Char('Company Code', required=True,related='company_name_id.company_code')
    insurance_company_id = fields.Many2one('sm.insurance.companies', required=True)
    start_date = fields.Date('Start Date', required=True)
    expiration_date = fields.Date('Expiration Date', required=True)
    policy_number = fields.Char('Policy Number', required=True,unique=True)
    type = fields.Selection([
        ('home_visit', 'Home visit'),
        ('tele_consultation', 'Tele_Consultation'),
    ],string='Type')
    home_visit = fields.Boolean(string='home_visit')
    tele_consultation = fields.Boolean(string='Tele_Consultation')
    members_ids = fields.One2many('sm.medical.insured.companies.members', 'members_medical_id')
    def set_to_active(self):
        return self.write({'state': 'active'})

    @api.model
    def create(self, vals):
        record = super(SMInsurancePolicy, self).create(vals)
        record['name'] = self.sudo().env.ref('sm_insurance.seq_sm_insurance_policy').next_by_id()
        return record


    def write(self, vals):
        if 'start_date' in vals or 'expiration_date' in vals:
            self.make_active()
        return super(SMInsurancePolicy, self).write(vals)


    @api.constrains('start_date', 'expiration_date')
    def _check_dates(self):
        if self.filtered(lambda c: c.expiration_date and c.start_date > c.expiration_date):
            raise ValidationError(_('Contract start date must be earlier than contract end date.'))

    def make_active(self):
        """Sets the 'state' field of the current instance to 'active' if conditions are met, and updates 'expired' state."""
        draft_records = self.search(
            [('state', '=', 'draft'), ('start_date', '<=', fields.Date.to_string(date.today()))])
        if draft_records:
            for record in draft_records:
                record.write({'state': 'active'})

        active_records = self.search(
            [('state', '=', 'active'), ('expiration_date', '<=', fields.Date.to_string(date.today()))])
        if active_records:
            for record in active_records:
                record.write({'state': 'expired'})

    @api.constrains('policy_number')
    def _check_unique_policy_number(self):
        for record in self:
            if record.policy_number:
                existing_record = self.env['sm.insurance.policy'].search([('policy_number', '=', record.policy_number)])
                if len(existing_record) > 1:
                    raise ValidationError("Policy Number must be unique!")






class SMPatientMembers(models.Model):
    _name = 'sm.medical.insured.companies.members'
    _description = 'insured Companies Members'

    members_id = fields.Char(string='id')
    patient_id = fields.Many2one('oeh.medical.patient')
    member_card = fields.Char(string='Member Card')
    class_company_id = fields.Many2one('sm.medical.insurance.classes')
    sev_patient_deducted = fields.Integer(string='Sev. Patient Deducted', related='class_company_id.serv_patient_deduct')
    deduct_per_visit = fields.Integer(string='Pt. Deduct Per Visit', related='class_company_id.pt_deduct_visit')
    approval_limit = fields.Integer(string='Approval Limit', related='class_company_id.approval_limit')

    members_medical_id = fields.Many2one('sm.insurance.policy', string='Insured Companies',
                                              ondelete='cascade')



