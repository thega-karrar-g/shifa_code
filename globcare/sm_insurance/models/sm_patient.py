from odoo import api, fields, models, _
import time
import datetime
from odoo.exceptions import UserError
import base64


class SMPatientInherit(models.Model):
    """ to add insurance details in patient model """
    _inherit = "oeh.medical.patient"

    has_insurance = fields.Boolean(string='Has Insurance', help="Mark if the patient has Insurance")
    insured_company_id = fields.Many2one('sm.medical.insured.companies',string='Insured Company')
    insured_policy = fields.Many2one('sm.insurance.policy',string="Policy Number",domain="[('company_name_id', '=', insured_company_id), ('state', '=', 'active')]")
    insurance_company_id = fields.Many2one(related='insured_policy.insurance_company_id',string='Insurance Company')
    expiration_date = fields.Date(related='insured_policy.expiration_date')
    class_company_id = fields.Many2one('sm.medical.insurance.classes',string='Insurance Class',domain="[('insurance_policy_id', '=', insured_policy)]")
    serv_patient_deduct = fields.Integer(related='class_company_id.serv_patient_deduct',string='Patent Deduct(%)')
    pt_deduct_visit = fields.Integer(related='class_company_id.pt_deduct_visit',string='Deduct Per Visit')
    approval_limit = fields.Integer(related='class_company_id.approval_limit',string='Approval Limit')
    home_visit = fields.Boolean(related='insured_policy.home_visit')
    tele_consultation = fields.Boolean(related='insured_policy.tele_consultation')
    insurance_state = fields.Selection(related='insured_policy.state',string='state')

    def write(self, values):
        res = super(SMPatientInherit, self).write(values)
        insured_policy = self.insured_policy.id
        if 'insured_policy' in values:
            insured_policy = values['insured_policy']
        if insured_policy:
            member = self.env['sm.medical.insured.companies.members'].sudo().search([
                ('members_medical_id', '=', insured_policy),
                ('patient_id', '=', self.id),
            ])

            if not member:
                self.env['sm.medical.insured.companies.members'].create({
                    'patient_id': self.id,
                    'members_medical_id': insured_policy,
                    'class_company_id': self.class_company_id.id,
                    'deduct_per_visit': self.pt_deduct_visit,
                    'approval_limit': self.approval_limit,
                    'sev_patient_deducted': self.serv_patient_deduct,
                })
        return res








