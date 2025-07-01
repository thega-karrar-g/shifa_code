from datetime import datetime, timedelta
import hashlib
import os
from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError

class Patient(models.Model):
    _inherit = 'oeh.medical.patient'
    
    def action_archive(self):
        user = self.env['res.users'].sudo().search([('partner_id','=',self.partner_id.id)]).action_archive()
        self.partner_id.action_archive()
        return super(Patient, self).action_archive()

class ResUsers(models.Model):
    _inherit = 'res.users'
    
    def action_archive(self):
        self.env['sm.api.access.token'].sudo().search([
            ('user_id','=',self.id)
        ]).unlink()
        return super(ResUsers, self).action_archive()


class SmAPIAccessToken(models.Model):
    _name = 'sm.api.access.token'
    _description = 'Store all access tokens of users'

    user_id = fields.Many2one('res.users', string='User', required=True, copy=False)
    token = fields.Char('Access Token', required=True, copy=False)
    token_expiry_date = fields.Datetime('Token Expiry Date', copy=False)
    scope = fields.Char("Scope")

    def find_or_create_token(self, user_id=None, create=False):
        model_name = 'sm.api.access.token'
        if not user_id:
            user_id = self.env.user.id

        access_token = self.env[model_name].sudo().search([('user_id', '=', user_id)], order="id DESC", limit=1)
        if access_token:
            access_token = access_token[0]
            if access_token.has_expired():
                access_token = None
        if not access_token and create:
            expiry_date = datetime.now() + timedelta(days=1)
            vals = {
                "user_id": user_id,
                "token": self.generate_random_token(),
                "token_expiry_date": expiry_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                "scope": "userinfo",
            }
            access_token = self.env[model_name].sudo().create(vals)
            if not access_token:
                return None
        return access_token.token

    def has_expired(self):
        self.ensure_one()
        return datetime.now() > fields.Datetime.from_string(self.token_expiry_date)

    def generate_random_token(self, length=40):
        rbytes = os.urandom(length)
        return '{}'.format(str(hashlib.sha1(rbytes).hexdigest()))
