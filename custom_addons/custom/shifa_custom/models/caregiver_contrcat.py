from odoo import api, fields, models
from odoo.exceptions import UserError

class MedicalStaff(models.Model):
    _inherit = "sm.caregiver.contracts"
    _description = "inherit from smart_mind/model/sm.caregiver.contracts "

    caregiver = fields.Many2one('oeh.medical.physician', string='First Caregiver', readonly=False,
                                states={'terminated': [('readonly', True)], 'active': [('readonly', True)],
                                        'cancel': [('readonly', True)], 'hold': [('readonly', True)],
                                        'holdreq': [('readonly', True)]}, domain=[('role_type', '=', 'C')])
