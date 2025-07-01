from odoo import api, fields, models
from odoo.exceptions import UserError


class Employee(models.Model):
    _inherit = 'hr.employee'
    create_from_staff = fields.Boolean( string='Create from Staff',readonly=True)

class MedicalStaff(models.Model):
    _inherit = "oeh.medical.physician"
    _description = "inherit from smart_mind/sm_general/shifa_physician "

    active_contract_count = fields.Integer(string="Active Contracts",compute="_compute_active_contracts")

    active = fields.Boolean('AActive',copy=False,default=True)                   
    @api.model
    def create(self,vals):
        
        res = super(MedicalStaff,self).create(vals)
        for rec in res :
            rec.employee_id.write({'active':False,'create_from_staff':True})
            # rec.employee_id.unlink()
        return res

    def _compute_active_contracts(self):
        for rec in self:
            rec.active_contract_count = len(self.env['sm.caregiver.contracts'].search([('caregiver', '=', rec.id),('state','=','active'),('active','=',True)]))

    def action_view_active_contracts(self):
        # Replace with your actual logic
        return {
            'type': 'ir.actions.act_window',
            'name': 'Active Contracts',
            'res_model': 'sm.caregiver.contracts',
            'view_mode': 'tree,form',
            'domain': [('caregiver', '=', self.id),('state','=','active')],
            # 'context': dict(self.env.context),
        }
    ###################################################################################################################
    cancel_canceled_count = fields.Integer(string="Canceled Contracts",compute="_compute_canceled_contracts")

    def _compute_canceled_contracts(self):
        for rec in self:
            rec.cancel_canceled_count = len(self.env['sm.caregiver.contracts'].search([('caregiver', '=', rec.id),('state','=','cancel')]))

    def action_view_canceled_contracts(self):
        # Your logic here
        return {
            'type': 'ir.actions.act_window',
            'name': 'Canceled Contracts',
            'res_model': 'sm.caregiver.contracts',
            'view_mode': 'tree,form',
            'domain': [('caregiver', '=', self.id),('state', '=', 'cancel')],
            'context': {},
        }

    ###################################################################################################################
    terminated_contract_count = fields.Integer(string="Terminated Contracts",compute="_compute_terminated_contracts")

    def _compute_terminated_contracts(self):
        for rec in self:
            rec.terminated_contract_count = len(self.env['sm.caregiver.contracts'].search([('caregiver', '=', rec.id),('state','=','terminated')]))

    def action_view_terminated_contracts(self):
        # Replace with your actual logic
        return {
            'type': 'ir.actions.act_window',
            'name': 'Terminated Contracts',
            'res_model': 'sm.caregiver.contracts',
            'view_mode': 'tree,form',
            'domain': [('caregiver', '=', self.id),('state','=','terminated')],
            # 'context': dict(self.env.context),
        }

    ##################################################################################################################

    completed_contract_count = fields.Integer(string="Completed Contracts",compute="_compute_completed_contracts")

    def _compute_completed_contracts(self):
        for rec in self:
            rec.completed_contract_count = len(self.env['sm.caregiver.contracts'].search([('caregiver', '=', rec.id),('state','=','completed')]))

    def action_view_completed_contracts(self):
        # Replace with your actual logic
        return {
            'type': 'ir.actions.act_window',
            'name': 'Completed Contracts',
            'res_model': 'sm.caregiver.contracts',
            'view_mode': 'tree,form',
            'domain': [('caregiver', '=', self.id),('state','=','completed')],
            # 'context': dict(self.env.context),
        }

    canceled_contract_count = fields.Integer(string="Canceled Contracts", compute="_compute_canceled_contract_count")

    # def _compute_canceled_contract_count(self):
    #     for rec in self:
    #         # Dummy example, replace with actual logic
    #         rec.canceled_contract_count = len(self.env['sm.caregiver.contracts'].search([('caregiver', '=', rec.id),('state','=','canceled')]))

    # def action_view_renewal_contracts(self):
    #     # Replace with your actual logic
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': 'Renewal Contracts',
    #         'res_model': 'your.model.name',
    #         'view_mode': 'tree,form',
    #         'domain': [('physician_id', '=', self.id)],
    #         'context': dict(self.env.context),
    #     }
    renewal_contract_count = fields.Integer(string="Renewal Contract Count", compute="_compute_renewal_contract_count")

    def _compute_renewal_contract_count(self):
        for rec in self:
            rec.renewal_contract_count = self.env['your.model'].search_count([('physician_id', '=', rec.id)])

     # add for caregiver file
    nationality = fields.Selection([
        ('Philipino', 'Philipino'),
        ('Indonesian', 'Indonesian'),
        ('African', 'African'),
    ], string="Nationality", readonly=True,
    states={'draft': [('readonly', False)], 'active': [('readonly', False)]})

    skills = fields.Selection([
        ('Children', 'children'),
        ('Autism', 'autism'),
        ('Elderly', 'elderly'),
    ], string="Skills", readonly=True,
    states={'draft': [('readonly', False)], 'active': [('readonly', False)]})

    # company = fields.Selection([
    #     ('shifa', 'Shifa'),
    #     ('maharah', 'Maharah'),
    #     ('joan', 'Joan'),
    # ], string="company", readonly=True,
    # states={'draft': [('readonly', False)], 'active': [('readonly', False)]})

    company = fields.Selection([
        ('shifa', 'Shifa'),
        ('maharah', 'Maharah'),
        ('joan', 'Joan'),
    ], string="Company", states={'draft': [('readonly', False)], 'active': [('readonly', False)]})
    
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ], required=True, default='male',tracking=True)

    # caregiver = fields.Many2one('res.partner', string="Caregiver")

    arrival_date =fields.Date(string="Arrival Date")

    language_ids = fields.Many2many('res.lang', string="Languages Spoken")
    
    

   