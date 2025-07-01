from odoo import api, fields, tools, models, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    id_number = fields.Char('ID', related='patient.ssn')
    patient = fields.Many2one('oeh.medical.patient', string='Related Patient', help="Patient Name")
    vat = fields.Char(string='Tax ID', related='partner_id.vat')
    company_type = fields.Selection(string='Tax ID', related='partner_id.company_type')

