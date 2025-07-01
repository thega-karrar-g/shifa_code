from odoo import api, fields, models, _
from datetime import date


class SMInsuranceCompanies(models.Model):
    _name = 'sm.service.price.list'
    _description = 'Price List'
    _rec_name = 'service_id'

    name = fields.Char(string='Reference #', size=64, default=lambda *a: '/')
    insurance_company_id = fields.Many2one('sm.insurance.companies',string='Insurance Company')
    service_id = fields.Many2one('sm.shifa.service',string='Service Name')
    public_price = fields.Float(related='service_id.list_price',string='Public Price',readonly=True)

    price = fields.Float(string='Price')
    discount = fields.Float(string='Discount(%)')
    code = fields.Char(string='Code')
    require_approval = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')],string="Require Approval")