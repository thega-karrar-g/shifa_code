from odoo import models, fields, api
import datetime


class ShifaMedicines(models.Model):
    _inherit = "oeh.medical.medicines"

    generic_name = fields.Many2one('sm.shifa.generic.medicines', string='Generic', help="Generic Medicine")
