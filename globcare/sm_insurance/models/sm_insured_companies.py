from datetime import timedelta, datetime
from odoo import api, fields, models, _


# insured Companies
class SMInsuredCompanies(models.Model):
    _name = 'sm.medical.insured.companies'
    _description = 'insured Companies'
    _rec_name = 'company_name'

    insured_Status = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('expired', 'Expired'),
    ]

    def _insurance_policies_count(self):
        oe_insu = self.env['sm.insurance.policy']
        for insured in self:
            domain = [('company_name_id', '=', insured.id)]
            insur_ids = oe_insu.search(domain)
            insur = oe_insu.browse(insur_ids)
            in_count = 0
            for bed in insur:
                in_count+=1
            insured.insured_count = in_count
        return True
    def _insurance_classes_count(self):
        oe_insu = self.env['sm.medical.insurance.classes']
        for classes in self:
            domain = [('insured_company_id', '=', classes.id)]
            class_ids = oe_insu.search(domain)
            insur = oe_insu.browse(class_ids)
            in_count = 0
            for bed in insur:
                in_count += 1
            classes.classes_count = in_count
        return True

    image_1920 = fields.Image("Image", max_width=1920, max_height=1920)
    image_1024 = fields.Image("Image 1024", related="image_1920", max_width=1024, max_height=1024, store=True)
    image_512 = fields.Image("Image 512", related="image_1920", max_width=512, max_height=512, store=True)
    image_256 = fields.Image("Image 256", related="image_1920", max_width=256, max_height=256, store=True)
    image_128 = fields.Image("Image 128", related="image_1920", max_width=128, max_height=128, store=True)

    name = fields.Char('Reference', index=True, copy=False)

    state = fields.Selection(insured_Status, string='Insurance Status', default=lambda *a: 'draft', readonly=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    company_name = fields.Char('Company Name', required=True)
    company_code = fields.Char('Company Code')
    street = fields.Char(string='Street')
    street2 = fields.Char(string='Street2')
    zip = fields.Char(string='Zip')
    city = fields.Char(string='City')
    country_id = fields.Many2one('res.country', 'Nationality (Country)')
    phone = fields.Char(string='Phone', readonly=False)
    email = fields.Char(string='Email', related=False, readonly=False)
    contact_person = fields.Char(string='Contact Person', related=False, readonly=False)
    insured_count = fields.Integer(compute=_insurance_policies_count)
    classes_count = fields.Integer(compute=_insurance_classes_count)



    def open_policies_view(self):
        # Method to open the prescription view for a specific patient.
        action = self.env['ir.actions.act_window']._for_xml_id(
            'sm_insurance.open_insurance_policies_action')
        action['domain'] = [('company_name_id', '=', self.id)]
        return action

    def open_classes_view(self):
        # Method to open the prescription view for a specific patient.
        action = self.env['ir.actions.act_window']._for_xml_id(
            'sm_insurance.open_insurance_classes_action')
        action['domain'] = [('insured_company_id', '=', self.id)]
        return action

    @api.model
    def create(self, vals):
        record = super(SMInsuredCompanies, self).create(vals)
        record['name'] = self.sudo().env.ref('sm_insurance.seq_sm_insured_companies').next_by_id()
        return record