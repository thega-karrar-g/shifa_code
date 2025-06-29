from odoo import api, fields, models
from odoo.exceptions import UserError

class CustomDashboard(models.Model):
    _inherit = "sm.dashboard"
    _description = "inherit from smartmind_dashboard/sm_dashboard "

    ## counter new contract group by month - counter active caregiver with customer - counter stay-in caregiver -
    new_contract_count = 0
    active_caregiver = 0
    stay_in_caregiver = 0

    
    ###################################################################################################################
  
    

   