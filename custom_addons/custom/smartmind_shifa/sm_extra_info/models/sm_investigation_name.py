from odoo import models, fields, api
import datetime


class ShifaInvestigationName(models.Model):
    _name = 'sm.shifa.investigation.name'
    _description = 'Investigation Name'

    name = fields.Char(string='Name')
    price = fields.Integer(string='Price')
    active = fields.Boolean(default=True)


