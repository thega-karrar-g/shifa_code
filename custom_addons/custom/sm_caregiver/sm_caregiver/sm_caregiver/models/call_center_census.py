from odoo import models, fields, api, _


class SmCaregiverInvoice(models.Model):
    _inherit = 'sm.shifa.call.center.census'

    book_cg_cont_app = fields.Boolean(string='Book a Caregiver Contract')
    cg_cont_id = fields.One2many('sm.caregiver.contracts', 'call_center_census_id')
