import datetime

from odoo import api, fields, models, _
from datetime import date
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError


class ShifaContactUs(models.Model):
    _name = 'sm.shifa.contactus'
    _description = "Contact Us"

    name = fields.Char(string='Person Name')
    email = fields.Char(string='Person Email', required=True)
    subject = fields.Char(string='Subject')
    mobile = fields.Char(string='Person Mobile', required=True)
    message = fields.Text(string='Message', required=True)

