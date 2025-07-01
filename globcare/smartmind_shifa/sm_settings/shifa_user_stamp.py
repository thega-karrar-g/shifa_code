
from odoo import api, fields, models


class ResUserStamp(models.Model):
    _inherit = 'res.users'

    stamp = fields.Binary(string='Stamp')
    user_signature = fields.Binary(string='Signature')
    # totp_trusted_device_ids = fields.Char(string='Truest')



