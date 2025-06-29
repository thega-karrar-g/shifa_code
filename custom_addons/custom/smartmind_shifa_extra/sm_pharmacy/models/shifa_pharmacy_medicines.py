from odoo import models, fields, api, SUPERUSER_ID, tools, _


class PharmacyMedicines(models.Model):
    _name = 'sm.shifa.pharmacy.medicines'
    _description = 'Pharmacy Medicines'
    _rec_name = "pharmacy_medicines"

    pharmacy_medicines = fields.Text(string='Pharmacy Medicine', required=True)
    generic_medicine = fields.Text(string='Generic Medicine', required=True)
    code = fields.Text(string='Code', required=True)
    type = fields.Selection([('brand', 'Brand'), ('generic', 'Generic')], string='Type')
    active = fields.Boolean(default=True)
