from odoo import models, fields, api


class Penalties(models.Model):
    _name = 'sm.shifa.penalties'
    _description = 'Penalties'

    missed_conslt = fields.Char(string='Missed Conslt')
    amount = fields.Float(string='Amount')
    comment = fields.Char(string='Comment')


