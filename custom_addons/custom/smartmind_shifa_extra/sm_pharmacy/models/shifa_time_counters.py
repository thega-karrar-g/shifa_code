from odoo import models, fields, api
import datetime
from odoo.exceptions import ValidationError


class TimeCounters(models.Model):
    _name = 'sm.shifa.time.counters'
    _description = 'Time Counters'

    time_waiting = fields.Float(string='Waiting')
    time_approved = fields.Float(string='Approved')


