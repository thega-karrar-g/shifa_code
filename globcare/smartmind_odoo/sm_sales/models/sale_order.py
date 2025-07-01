from odoo import models, fields, api


class SmartMindSaleOrder(models.Model):
    _inherit = 'sale.order'

    patient_name = fields.Char(string='Patient Name')
    patient_id = fields.Char(string='Patient ID')
