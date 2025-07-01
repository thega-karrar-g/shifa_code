from datetime import timedelta, datetime
from odoo import models, fields, api


class SmAggregator(models.Model):
    _name = 'sm.aggregator'
    _description = 'Aggregator partener'
    _inherits = {
        'res.partner': 'partner_id',
    }

    partner_id = fields.Many2one('res.partner', string='Aggregator Partner', ondelete='cascade',
                                 help='Partner-related data of the patient')