from odoo import api, fields, models
from odoo.exceptions import UserError

class MedicalStaff(models.Model):
    _inherit = "sm.dashboard"
    _description = "inherit from smart_mind/custom_addons/custom/smartmind_dashboard "

    active_contract_count = fields.Integer(string="Active Contracts",compute="_compute_active_contracts")

    def _compute_active_contracts(self):
        for rec in self:
            rec.active_contract_count = len(self.env['sm.caregiver.contracts'].search([('caregiver', '=', rec.id),('state','=','active')]))


   