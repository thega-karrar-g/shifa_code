
from odoo import api, fields, models, tools


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    active = fields.Boolean(default=True)
