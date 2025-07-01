from datetime import timedelta

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
from datetime import timedelta
from datetime import date


class Slider(models.Model):
    _name = "sm.slider"
    _description = "Sliders"

    name = fields.Char()
    active = fields.Boolean(default=True)
    attachment = fields.Binary('Attach')

