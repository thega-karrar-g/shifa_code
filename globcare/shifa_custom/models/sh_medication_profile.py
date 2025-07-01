from odoo import api, fields, models
from odoo.exceptions import UserError


class MedicationProfile(models.Model):
    _inherit = "sm.shifa.medication.profile"
    _description = "inherit from smartmind_shifa/sm_general/model/shifa_medication_profile "

    p_generic_name = fields.Many2one('sm.shifa.generic.medicines')
    p_brand_medicine = fields.Many2one('sm.shifa.brand.medicines')



