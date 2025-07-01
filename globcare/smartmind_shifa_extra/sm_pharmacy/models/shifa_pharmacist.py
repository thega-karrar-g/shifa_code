from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools.translate import _
import logging
import string
import random

_logger = logging.getLogger(__name__)


class Pharmacist(models.Model):
    _name = 'sm.shifa.pharmacist'
    _description = 'Pharmacist'

    name = fields.Char(string="Pharmacist")
    pharmacy = fields.Many2one('sm.shifa.pharmacies', string="Pharmacy")
    institution = fields.Many2one('sm.shifa.pharmacy.chain', string="Pharmacy Chain")
    username = fields.Char('Username')
    password = fields.Char(string='Password', default=lambda *a: ''.join(random.choices(string.digits, k=6)))
    mobile = fields.Char(string='Mobile', required=True)
    is_admin = fields.Boolean(string='Is admin')

    @api.onchange('institution')
    def onchange_pharmacy_chain_id(self):
        for rec in self:
            return {'domain': {'pharmacy': [('institution', '=', rec.institution.id)]}}

    _sql_constraints = [
        ('full_name_uniq', 'unique (institution,name)', 'The pharmacist name must be unique !'),
        ('user_name_uniq',
         'unique(username)',
         "The user name must be unique")]

    @api.onchange('mobile')
    def mobile_check(self):
        if self.mobile:
            if self.mobile[0:4] == '9665':
                if str(len(self.mobile)) == '12':
                    self.username = self.mobile
                else:
                    lenth = len(self.mobile)
                    raise ValidationError("mobile number is {} digits should be 12 digits".format(lenth))
            else:
                raise ValidationError(_("Invalid mobile number, should be start with '9665' "))

    def action_send_sms(self):
        my_model = self._name
        if self.mobile:
            msg = "اسم المسخدم :%s   " \
                  "كلمة السر :%s   " % (
                      self.username, str(self.password))
            self.send_sms(self.mobile, msg, my_model, self.id)
        # else:
        #     raise ValidationError(_("Sorry! you did not enter a mobile number in mobile e"))

    def send_sms(self, mobile, msg, model, rec_id):
        gatewayurl_id = self.env['gateway_setup'].search([], limit=1)
        if gatewayurl_id and gatewayurl_id.gateway_url:
            try:
                self.env['gateway_setup'].sudo().send_sms_link(msg, mobile, rec_id, model, gatewayurl_id)
            except Exception as e:
                _logger.error(e)
        else:
            raise ValidationError(_("The SMS Gateway is not configured"))

    # def create(self, vals):
    #     return super(Pharmacist, self).create(vals)
