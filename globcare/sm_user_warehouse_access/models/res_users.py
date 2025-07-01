from odoo import api, fields, models, _
import datetime


class Users(models.Model):
    _inherit = 'res.users'
    warehouse_ids = fields.Many2many('stock.warehouse',string='Allowed Warehouses')
