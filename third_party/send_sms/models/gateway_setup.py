# -*- coding: utf-8 -*-
from odoo import _, api, fields, models, tools
from odoo.exceptions import except_orm, UserError, Warning
# Ismail Modification Start......
import requests
from requests.structures import CaseInsensitiveDict
# Ismail Modification Stop....
import urllib
import re
import logging

_logger = logging.getLogger(__name__)


class GateWaysetup(models.Model):
    _name = "gateway_setup"
    _description = "GateWay Setup"

    name = fields.Char(required=True, string='Name')
    gateway_url = fields.Char(required=True, string='GateWay Url')
    message = fields.Text('to')
    mobile = fields.Char('text')

    # send_sms_link(message, mobile_no, self.id, active_model, self)
    def send_sms_link(self, sms_rendered_content, rendered_sms_to, record_id, model, gateway_url_id):
        # sms_rendered_content = sms_rendered_content.encode('UTF-8', 'ignore')
        # sms_rendered_content_msg = urllib.parse.quote_plus(sms_rendered_content)
        if rendered_sms_to:
            rendered_sms_to = re.sub(r' ', '', rendered_sms_to)
            if '+' in rendered_sms_to:
                rendered_sms_to = rendered_sms_to.replace('+', '')
            if '-' in rendered_sms_to:
                rendered_sms_to = rendered_sms_to.replace('-', '')

        if rendered_sms_to:
            send_url = gateway_url_id.gateway_url
            # Ismail Modification Start....
            # headers = CaseInsensitiveDict()
            # headers["Content-Type"] = 'application/json'
            # data = "to={to}&text={text}"
            # data = data.replace('{to}', rendered_sms_to).replace('{text}', sms_rendered_content_msg)
            # Ismail Modification Stop....
            # headers = {
            #     'Content-Type': 'application/json'
            # }
            #print(rendered_sms_to)
            #print(sms_rendered_content)
            # 7c3d4f38c80f792e558e81fa193e11f7
            values = '''{
                  "userName": "shifaa",
                  "numbers": "{0}",
                  "userSender": "GlobCare",
                  "apiKey": "CA62F3AF1694F585186542240D61213E",
                  "msg": "{1}"
                }'''
            # print(values)
            data = values.replace('{0}', rendered_sms_to).replace('{1}', sms_rendered_content)
            # send_link = send_url.replace('{to}',rendered_sms_to).replace('{text}',sms_rendered_content_msg)
            data = data.encode('utf-8')
            #print(data)
            try:
                # Ismail Modification Start.....

                response = requests.request("POST", url=send_url, headers={'Content-Type': 'application/json'}, data= data).text
                # print(response)
                # print(Warning(response))
                self.env['sms_track'].sms_track_create(record_id, sms_rendered_content, rendered_sms_to, response,
                                                       model,
                                                       gateway_url_id.id)
                # Ismail Modification Stop....
                _logger.error(data)
                _logger.error(response)
                return response
            except Exception as e:
                #print(">>>>>>>>>>>>", e)
                return e

    def sms_test_action(self):
        active_model = 'gateway_setup'
        message = self.env['send_sms'].render_template(self.message, active_model, self.id)
        mobile_no = self.env['send_sms'].render_template(self.mobile, active_model, self.id)
        response = self.send_sms_link(message, mobile_no, self.id, active_model, self)
        raise Warning(response)
