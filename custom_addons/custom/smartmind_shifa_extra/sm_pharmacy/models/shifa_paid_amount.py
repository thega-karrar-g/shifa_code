from odoo import models, fields, api


class PaidAmount(models.Model):
    _name = 'sm.shifa.paid.amount'
    _description = 'Paid Amount'

    amount = fields.Float(string='Amount')
    date = fields.Char(string='Date')
    reference = fields.Char(string='Reference')
    comment = fields.Char(string='Comment')


