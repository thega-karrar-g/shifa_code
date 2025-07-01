from datetime import datetime
from odoo import fields, models
from odoo.addons.smartmind_shifa_more.services.fcm_service import FCMService


class SmAppNotification(models.Model):
    _name = 'sm.app.notification'
    _description = "App notification"
    _rec_name = 'name_en'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('send', 'Send'),
    ], string='State', default=lambda *a: 'draft', readonly=True)
    name_ar = fields.Char(string='Title Arabic', readonly=True, states={'draft': [('readonly', False)]})
    name_en = fields.Char(string='Title English', readonly=True, states={'draft': [('readonly', False)]})
    content_en = fields.Text(string='Content English', readonly=True, states={'draft': [('readonly', False)]})
    content_ar = fields.Text(string='Content Arabic', readonly=True, states={'draft': [('readonly', False)]})
    date = fields.Date(string='Date', readonly=True, default=lambda *a: datetime.now())
    image = fields.Binary(string='Image', max_width=128, max_height=128, readonly=True,
                          states={'draft': [('readonly', False)]})
    send_type = fields.Selection([
        ('private', 'Private'),
        ('public', 'Public'),
    ], string='Type', readonly=True, states={'draft': [('readonly', False)]})
    patient_id = fields.Many2one('oeh.medical.patient', string='Patient', readonly=True,
                                 states={'draft': [('readonly', False)]})
    active = fields.Boolean(default=True)

    def set_send(self):
        for rec in self:
            fcm_service = FCMService()
            if rec.send_type == 'private':
                patient = self.env['oeh.medical.patient'].sudo().search([('id', '=', rec.patient_id.id)], limit=1)
                temp_token = 'dbJs9M5fRVWhgVkfQqQ0tt:APA91bE-x_QXO6Ju6nYldz2E6uIYCUwYAlX2fS48r9-UeiJKik69CACwW3KOFfEJB8k5QekonVFVaRLmL1onAbw_PLj_lFhwcHCr9Uq7dJ4MoAuoHygzRYqONu2PruGZCUh3oA4_8VnE'
                if patient:
                    if patient.device_type == 'android':
                        is_ios = False
                    else:
                        is_ios = True
                    # fcm_service.send_fcm_request('token', temp_token, is_ios, rec)
                    fcm_service.send_fcm_request('token', patient.patient_fcm_token, is_ios, rec)
            else:
                fcm_service.send_fcm_request('topic', 'globcare_news_android', False, rec)
                fcm_service.send_fcm_request('topic', 'globcare_news_ios', True, rec)

        return self.write({'state': 'send'})


    def get_image_url(self, image_type, model, model_id):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        image_url = base_url + '/web/image?' + 'model=' + model + '&id=' + str(model_id) + '&field=' + image_type
        return image_url

