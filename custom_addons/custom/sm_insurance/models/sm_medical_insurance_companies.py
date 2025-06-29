from odoo import api, fields, models, _
from datetime import date
from odoo.exceptions import ValidationError

# Insurance Companies
class SMInsuranceCompanies(models.Model):
    _name = 'sm.insurance.companies'
    _description = 'Insurance Companies'
    _rec_name = 'company_name'

    Insurance_Status = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('expired', 'Expired'),
    ]

    def _service_count(self):
        oe_class = self.env['sm.service.price.list']
        for classing in self:
            domain = [('insurance_company_id', '=', classing.id)]
            clas_ids = oe_class.search(domain)
            clas = oe_class.browse(clas_ids)
            cl_count = 0
            for bed in clas:
                cl_count+=1
            classing.price_list_count = cl_count
        return True

    def _insurance_policies_count(self):
        oe_insu = self.env['sm.insurance.policy']
        for insured in self:
            domain = [('insurance_company_id', '=', insured.id)]
            insur_ids = oe_insu.search(domain)
            insur = oe_insu.browse(insur_ids)
            in_count = 0
            for bed in insur:
                in_count+=1
            insured.insured_count = in_count
        return True

    image_1920 = fields.Image("Image", max_width=1920, max_height=1920)

    # resized fields stored (as attachment) for performance
    image_1024 = fields.Image("Image 1024", related="image_1920", max_width=1024, max_height=1024, store=True)
    image_512 = fields.Image("Image 512", related="image_1920", max_width=512, max_height=512, store=True)
    image_256 = fields.Image("Image 256", related="image_1920", max_width=256, max_height=256, store=True)
    image_128 = fields.Image("Image 128", related="image_1920", max_width=128, max_height=128, store=True)

    name = fields.Char(string='Reference #', size=64, default=lambda *a: '/')
    state = fields.Selection(Insurance_Status, string='Insurance Status', default=lambda *a: 'draft', readonly=True)
    company_name = fields.Char('Company Name', required=True)
    company_code = fields.Char('Company Code', required=True)
    start_date = fields.Date('Start Date', required=True)
    expiration_date = fields.Date('Expiration Date', required=True)
    parent_company_id = fields.Many2one('sm.insurance.companies',string='Parent Company')
    follow_up = fields.Integer(string='Follow_up(days)')
    street = fields.Char(string='Street')
    street2 = fields.Char(string='Street2')
    zip = fields.Char(string='Zip')
    city = fields.Char(string='City')
    country_id = fields.Many2one('res.country', 'Nationality (Country)')
    phone = fields.Char(string='Phone',readonly=False)
    email = fields.Char(string='Email', related=False, readonly=False)
    contact_person = fields.Char(string='Contact Person', related=False, readonly=False)

    contract_document = fields.Binary('Contract Document')
    price_list = fields.Binary('Price List')

    price_list_count = fields.Integer(compute=_service_count, string="Beds")
    insured_count = fields.Integer(compute=_insurance_policies_count, string="Clinics")
    partner_id = fields.Many2one('res.partner', string='Partner',ondelete='cascade')

    @api.model
    def create(self, vals):
        vals['name'] = self.sudo().env.ref('sm_insurance.seq_sm_insurance_companies').next_by_id()
        insurance_company = super(SMInsuranceCompanies, self).create(vals)
        partner_vals = {
            'name': insurance_company.company_name,
            'street': insurance_company.street,
            'street2': insurance_company.street2,
            'zip': insurance_company.zip,
            'city': insurance_company.city,
            'country_id': insurance_company.country_id.id,
            'phone': insurance_company.phone,
            'email': insurance_company.email,
            'is_company': True,
            'company_type': 'company',
        }
        partner = self.env['res.partner'].create(partner_vals)
        insurance_company.partner_id = partner.id

        return insurance_company

    def write(self, vals):
        if 'start_date' in vals or 'expiration_date' in vals:
            self.make_active()
        return super(SMInsuranceCompanies, self).write(vals)

    @api.constrains('start_date', 'expiration_date')
    def _check_dates(self):
        if self.filtered(lambda c: c.expiration_date and c.start_date > c.expiration_date):
            raise ValidationError(_('Contract start date must be earlier than contract end date.'))


    def open_policies_view(self):
        # Method to open the prescription view for a specific patient.
        action = self.env['ir.actions.act_window']._for_xml_id(
            'sm_insurance.open_insurance_policies_action')
        action['domain'] = [('insurance_company_id', '=', self.id)]
        return action

    def open_price_list_view(self):
        # Method to open the prescription view for a specific patient.
        action = self.env['ir.actions.act_window']._for_xml_id(
            'sm_insurance.open_price_list_action')
        action['domain'] = [('insurance_company_id', '=', self.id)]
        return action

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

    def unlink(self):
        model_name = 'res.partner'
        partner_obj = self.env[model_name].sudo().search([('id', '=', self.partner_id.id)], limit=1)
        partner_obj.unlink()
        return super(SMInsuranceCompanies, self).unlink()


