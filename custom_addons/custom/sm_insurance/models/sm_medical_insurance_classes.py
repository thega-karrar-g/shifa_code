from datetime import timedelta, datetime
from odoo import api, fields, models, _


# Insurance Companies
class SMInsuranceClasses(models.Model):
    _name = 'sm.medical.insurance.classes'
    _description = 'Insurance Classes'
    _rec_name = 'class_name'

    name = fields.Char('Reference', index=True, copy=False)
    insured_company_id = fields.Many2one('sm.medical.insured.companies', string='Insured company', required=True)
    class_name = fields.Char('Class Name', required=True)
    code = fields.Char('Code', related='insured_company_id.company_code')
    insurance_policy_id = fields.Many2one('sm.insurance.policy', string='Insurance Policy',
                                          domain="[('company_name_id', '=', insured_company_id), ('state', '=', 'active')]")
    insurance_company_id = fields.Many2one(related='insurance_policy_id.insurance_company_id',store=True)
    approval_limit = fields.Integer('Approval Limit', required=True)
    pt_deduct_visit = fields.Integer('pt.Deduct per Visit', required=True)
    serv_patient_deduct = fields.Integer('Serv.Patient Deduct.%', required=True)

    @api.model
    def create(self, vals):
        record = super(SMInsuranceClasses, self).create(vals)
        record['name'] = self.sudo().env.ref('sm_insurance.seq_sm_insurance_classes').next_by_id()
        return record

    @api.onchange('insurance_company_id')
    def _get_insurance_company(self):
        for rec in self:
            rec.insurance_company_id = rec.insurance_company_id
