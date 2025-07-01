from odoo import models, fields, api
import datetime
from odoo.exceptions import ValidationError
from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools.translate import _
import logging

_logger = logging.getLogger(__name__)


class Pharmacies(models.Model):
    _name = 'sm.shifa.pharmacies'
    _description = 'Pharmacies'
    _inherits = {
        'res.partner': 'partner_id',
    }

    def _pharmacist_count(self):
        pharmacist_obj = self.env['sm.shifa.pharmacist']
        for phist in self:
            domain = [('pharmacy', '=', phist.id)]
            pharmacist_ids = pharmacist_obj.search(domain)
            pharmacists = pharmacist_obj.browse(pharmacist_ids)
            pharmist_count = 0
            for ist_id in pharmacists:
                pharmist_count += 1
            phist.pharmacist_cuont = pharmist_count
        return True

    company_id = fields.Many2one(
        'res.company', store=True, default=lambda self: self.env.company
    )

    def open_pharmacist_view(self):
        action = self.env['ir.actions.act_window']._for_xml_id('smartmind_shifa_extra.sm_shifa_Pharmacist_action')
        action['domain'] = [('pharmacy', '=', self.id)]
        return action

    code = fields.Char('Reference', index=True, copy=False)
    partner_id = fields.Many2one('res.partner', string='Pharmacy Name', required=True, ondelete='cascade',
                                 help='Partner-related data of the hospitals')
    pharmacist = fields.Many2one('sm.shifa.pharmacist', string='Pharmacist Name', domain="[('pharmacy', '=', name)]")
    institution = fields.Many2one('sm.shifa.pharmacy.chain', required=True, string='Pharmacy Chain')
    username = fields.Char()
    password = fields.Char()
    mobile = fields.Char(string='Mobile')

    info = fields.Text(string='Extra Information')

    inst_pres_id = fields.One2many('sm.shifa.instant.prescriptions', 'pharmacy', string='Pharmacies Prescriptions')
    pharmacist_cuont = fields.Integer(compute=_pharmacist_count, string="Pharmacist")

    # _sql_constraints = [
    #     ('user_name_uniq',
    #      'unique(username)',
    #      "The user name must be unique")]


    @api.model
    def create(self, vals):
        vals['code'] = self.env['ir.sequence'].next_by_code('sm.shifa.pharmacies')
        # vals['name'] = self.pharmacy_name
        # print("name"+ str(self.name))
        # print("pharmacy_name"+ str(self.pharmacy_name))
        return super(Pharmacies, self).create(vals)


    @api.onchange('mobile')
    def mobile_check(self):
        if self.mobile:
            if self.mobile[0:4] == '9665':
                print(len(self.mobile))
                if str(len(self.mobile)) == '12':
                    pass
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


class ShifaInstantPrescriptionsInherit(models.Model):
    _inherit = 'sm.shifa.instant.prescriptions'

    pharmacies_ref_id = fields.Many2one('sm.shifa.pharmacies', string='Pharmacies', ondelete='cascade')
