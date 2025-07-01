from odoo import http, _
from odoo.http import request
from datetime import datetime, timedelta
import base64

from odoo.addons.oehealth.oeh_rest_api.common_methods import invalid_response, valid_response, extract_arguments, \
    get_file_name, upload_attached_file, convert_utc_to_local
from odoo.addons.oehealth.oeh_rest_api.controllers.main import authenticate_token_portal, authenticate_token
from odoo.addons.oehealth.oeh_rest_api.shared_methods import SmartMindSharedMethods


class PortalPaymentRESTAPIController(http.Controller, SmartMindSharedMethods):
    def __init__(self):
        self._model = 'ir.model'

    @authenticate_token_portal
    @http.route(['/sehati/payment/get-send-requests'], type='http', auth="none", methods=['Get'], csrf=False)
    def payment_get_send_requests(self, **payload):
        model_name = 'sm.shifa.requested.payments'
        model = request.env[self._model].sudo().search([('model', '=', model_name)], limit=1)
        payload[
            'fields'] = "['id', 'name', 'patient', 'payment_amount', 'state', 'date']"

        payload['domain'] = "[('state', '=', 'Send')]"
        payload['order'] = 'id desc'
        if model:
            domain, fields, offset, limit, order = extract_arguments(
                payload)
            data = request.env[model.model].sudo().search_read(
                domain=domain, fields=fields, offset=offset, limit=limit, order=order)
            data_to_push = []
            mobile = ""
            for x in data:
                for k, v in x.items():
                    if str(type(v)) in ("<class 'datetime.datetime'>", "<class 'datetime.date'>"):
                        date = v.strftime("%Y-%m-%d")
                        x[k] = str(date)
                    if str(k) == "patient":
                        if v and len(v) > 0:
                            patient_obj = request.env['oeh.medical.patient'].sudo().search([('id', '=', v[0])])
                            mobile = patient_obj.mobile

                x['mobile'] = mobile

                data_to_push.append(x)
            return valid_response(data_to_push)
        return invalid_response('invalid object model', 'The model %s is not available in the registry.' % model_name)

    @authenticate_token_portal
    @http.route(['/sehati/payment/get-send-requests/<request_id>'], type='http', auth="none", methods=['Get'], csrf=False)
    def payment_get_request(self, request_id=None, **payload):
        model_name = 'sm.shifa.requested.payments'
        model = request.env[self._model].sudo().search([('model', '=', model_name)], limit=1)
        payload['fields'] = "['id', 'name', 'patient', 'payment_amount', 'state', 'date']"
        if model:
            domain, fields, offset, limit, order = extract_arguments(
                payload)
            if request_id:
                domain = [('id', '=', int(request_id)), ('state', '=', 'Send')]
            data = request.env[model.model].sudo().search_read(
                domain=domain, fields=fields, offset=offset, limit=limit, order=order)
            data_to_push = []
            mobile = ""
            if data:
                for x in data:
                    for k, v in x.items():
                        if str(type(v)) in ("<class 'datetime.datetime'>", "<class 'datetime.date'>"):
                            date = v.strftime("%Y-%m-%d")
                            x[k] = str(date)
                        if str(k) == "patient":
                            if v and len(v) > 0:
                                patient_obj = request.env['oeh.medical.patient'].sudo().search([('id', '=', v[0])])
                                mobile = patient_obj.mobile

                    x['mobile'] = mobile
                    data_to_push.append(x)
                return valid_response(data_to_push)
            else:
                return invalid_response('request record is not in send state or not found', 'request record is not in send state or not found!')
        return invalid_response('invalid object model', 'The model %s is not available in the registry.' % model_name)

# check state of payment request record
    @authenticate_token_portal
    @http.route(['/sehati/payment/check-state-request/<request_id>'], type='http', auth="none", methods=['Get'], csrf=False)
    def payment_check_state_request(self, request_id=None, **payload):
        model_name = 'sm.shifa.requested.payments'
        model = request.env[self._model].sudo().search([('model', '=', model_name)], limit=1)
        payload['fields'] = "['id', 'state']"
        if model:
            domain, fields, offset, limit, order = extract_arguments(
                payload)
            if request_id:
                domain = [('id', '=', int(request_id))]
                data = request.env[model.model].sudo().search_read(
                    domain=domain, fields=fields, offset=offset, limit=limit, order=order)
                if data:
                    return valid_response(data)
                else:
                    return invalid_response('request record is not found', 'request record is not found!')
        return invalid_response('invalid object model', 'The model %s is not available in the registry.' % model_name)

# pay method from portal
    @authenticate_token_portal
    @http.route(['/sehati/payment/pay-request'], type='http', auth="none", methods=['POST'], csrf=False)
    def payment_pay_request(self, **post):
        model_name = 'sm.shifa.requested.payments'
        model = request.env[self._model].sudo().search([('model', '=', model_name)], limit=1)
        amount = post.get('amount')
        payment_id = post.get('payment_id')
        request_id = post.get('request')
        payment_method = post.get('payment_method')
        if model:
            if request_id:
                request_obj = request.env['sm.shifa.requested.payments'].sudo().browse(int(request_id))
                request_obj.sudo().write({
                    'state': 'Paid',
                    'payment_reference': payment_id,
                    'deduction_amount': amount,
                    'payment_method_name': payment_method,
                    'payment_method': "portal",
                    'payment_note': "Paid from Web Portal Link",
                })
                request_obj.sudo().create_account_payment()
                request_obj.sudo().notification()
                data = {
                    'id': request_id,
                    'message': 'Your Request is Paid Successfully!'
                }
                return valid_response(data)
            else:
                return invalid_response('request record not found', 'request record not found!')
        return invalid_response('invalid object model', 'The model %s is not available in the registry.' % model_name)


# Cancel the request
    @authenticate_token_portal
    @http.route(['/sehati/payment/reject-request'], type='http', auth="none", methods=['POST'], csrf=False)
    def payment_reject_request(self, **post):
        model_name = 'sm.shifa.requested.payments'
        model = request.env[self._model].sudo().search([('model', '=', model_name)], limit=1)
        request_id = post.get('request')
        if model:
            if request_id:
                request_obj = request.env['sm.shifa.requested.payments'].sudo().browse(int(request_id))
                request_obj.sudo().write({
                    'state': 'Reject',
                    'payment_method': "portal",
                    'payment_note': "Rejected from Web Portal",
                })
                data = {
                    'id': request_id,
                    'message': 'Your Request is Reject Successfully!'
                }
                return valid_response(data)
            else:
                return invalid_response('request record not found', 'request record not found!')
        return invalid_response('invalid object model', 'The model %s is not available in the registry.' % model_name)


    @authenticate_token
    @http.route(['/sehati/get-notifications/<patient_id>'], type='http', auth="none", methods=['GET'],
                csrf=False)
    def get_notifications(self, patient_id=None):
        # notifications list
        notifications_row = request.env['sm.app.notification'].sudo().search([('send_type', '=', 'public'), ('state', '=', 'send')])
        notifications_list = []
        for i in notifications_row:
                notifications = {
                    'id': int(i.id),
                    'name_en': i.name_en or "",
                    'name_ar': i.name_ar or "",
                    'date': convert_utc_to_local(i.date.strftime("%Y-%m-%d %H:%M:%S")),
                    'content_en': i.content_en or "",
                    'content_ar': i.content_ar or "",
                    'type': i.send_type or "",
                    'image_url': self.get_image_url('image',
                                                    'sm.app.notification',
                                                    str(i.id))
                }
                notifications_list.append(notifications)
        # notifications list for specific patient
        p_notifications_row = request.env['sm.app.notification'].sudo().search(
            [('patient_id.id', '=', int(patient_id)), ('state', '=', 'send')])
        for i in p_notifications_row:
            p_notifications = {
                'id': int(i.id),
                'name_en': i.name_en or "",
                'name_ar': i.name_ar or "",
                'date': convert_utc_to_local(i.date.strftime("%Y-%m-%d %H:%M:%S")),
                'content_en': i.content_en or "",
                'content_ar': i.content_ar or "",
                'patient_id': i.patient_id.name or "",
                'read': i.x_read,
                'type': i.send_type or "",
                'image_url': self.get_image_url('image',
                                                    'sm.app.notification',
                                                    str(i.id))
            }
            notifications_list.append(p_notifications)

        return valid_response(notifications_list)
    

    @authenticate_token
    @http.route(['/sehati/update-notification'], type='http', auth="none", methods=['POST'],
                csrf=False)
    def update_notification(self, **post):
        notification_id = post.get('notification_id')
        patient_id = post.get('patient_id')
        notification = request.env['sm.app.notification'].sudo().search(
            [('id', '=', int(notification_id)),('patient_id','=',int(patient_id))])
        if notification:
            notification.sudo().write({"x_read": True})
            data = {
                'id': notification_id,
                'message': 'Your notification is updated Successfully!'
            }

            return valid_response(data)

        return invalid_response('request record not found')
    

