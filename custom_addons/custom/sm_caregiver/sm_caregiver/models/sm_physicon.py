from odoo import models, fields, api, _


class SmPhysician(models.Model):
    _inherit = "oeh.medical.physician"

    role_type = fields.Selection(selection_add=[
        ('caregiver_supervisor', 'Caregiver Supervisor'),
    ], string='Role Type')