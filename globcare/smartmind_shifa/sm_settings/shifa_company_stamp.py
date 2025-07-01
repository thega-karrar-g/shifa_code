
from odoo import api, fields, models


class ResCompanyStamp(models.Model):
    _inherit = 'res.company'

    stamp = fields.Binary(string='Stamp')


