from odoo import models, fields, api, _

class PreAuthorizationDiagnosis(models.Model):
    _name = 'sm.pre.authorization.diagnosis'
    _description = 'Diagnosis'

    authorization_request_id = fields.Many2one('sm.pre.authorization.request', string='Authorization Request')
    diagnosis_code = fields.Many2one('oeh.medical.pathology',string='Diagnosis Code')
    description = fields.Text(string='Description')
    type = fields.Selection([
        ('principal', 'Principal Diagnosis'),
        ('secondary', 'Secondary Diagnosis'),
        ('admitting', 'Admitting Diagnosis'),
        ('discharge', 'Discharge Diagnosis'),
        ('differential', 'Differential Diagnosis')
    ], string='Type')
    on_admission = fields.Text(string='ON Admission')
