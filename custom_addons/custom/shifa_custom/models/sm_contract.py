from odoo import models, fields, api
from odoo.exceptions import ValidationError

class SmCaregiverContracts(models.Model):
    _inherit = "sm.caregiver.contracts"
    _description = 'Caregiver Contracts'


from odoo import api, fields, models, tools

class CaregiverContract(models.Model):
    _inherit = "sm.caregiver.contracts"
    _description = "inherit from smart_mind/sm_general/shifa_physician "


    caregiver = fields.Many2one('oeh.medical.physician', string='First Caregiver',required=True,
        states={'Draft': [('readonly', False)]})
                                # states={'Draft': [('readonly', False)]}, domain=[('role_type', '=', 'C'), ('active', '=', True)])
    caregiver_second = fields.Many2one('oeh.medical.physician', string='Second Caregiver',
                                       states={'Draft': [('readonly', False)]}, domain=[('role_type', '=', 'C'), ('active', '=', True)])
    caregiver_third = fields.Many2one('oeh.medical.physician', string='Third Caregiver',
                                      states={'Draft': [('readonly', False)]}, domain=[('role_type', '=', 'C'), ('active', '=', True)])

    allowed_caregivers_ids = fields.Many2many('oeh.medical.physician', string="Allowed Caregivers"
        ,compute="_compute_allowed_caregiver_ids")


    @api.depends('caregiver')
    def _compute_allowed_caregiver_ids(self):
        for rec in self:
            recs = self.env['sm.caregiver.contracts'].search([('state','=','active'),('active','=',True)])
            domain = [("id", "not in", recs.caregiver.ids),('role_type', '=', 'C'), ('active', '=', True)]
            rec.allowed_caregivers_ids = self.env['oeh.medical.physician'].search(domain)

    # @api.onchange('caregiver')
    # def onchange_caregiver(self):
    #     recs = self.env['sm.caregiver.contracts'].search([('state','=','active'),('active','=',True)])
    #     print('-------------------------------------------',recs.caregiver.ids)
    #     return {"domain": {"caregiver": [("id", "not in", recs.caregiver.ids),('role_type', '=', 'C'), ('active', '=', True)]}}