from odoo import http, _
from odoo.http import request

from odoo.addons.oehealth.oeh_rest_api.common_methods import invalid_response, valid_response, extract_arguments
from odoo.addons.oehealth.oeh_rest_api.controllers.main import authenticate_token, authenticate_token_portal


class SmartMindExtraInfoRESTAPIController(http.Controller):
    def __init__(self):
        self._model = 'ir.model'

    @authenticate_token_portal
    @http.route(['/sehati/web-request/create'], type='http', auth="none", methods=['POST'],
                csrf=False)
    def create_web_request(self, **post):
        model_name = 'sm.shifa.web.request'
        service_name = post.get('service_name')
        if not service_name:
            return invalid_response('service_name not found', 'Service name not found in request!')

        requested_by = post.get('requested_by')
        if not requested_by:
            return invalid_response('requested_by not found', 'Requested by not found in request!')

        domain = [('service_name', '=', service_name), ('requested_by', '=', requested_by)]
        count = request.env[model_name].sudo().search_count(domain)

        if count == 0:
            values = {}

            values['service_name'] = service_name
            values['requested_by'] = requested_by

            address = post.get('address')
            if address:
                values['address'] = address

            mobile = post.get('mobile')
            if mobile:
                values['mobile'] = mobile

            email = post.get('email')
            if email:
                values['email'] = email

            patient_comment = post.get('patient_comment')
            if patient_comment:
                values['patient_comment'] = patient_comment

            call_center_comment = post.get('call_center_comment')
            if call_center_comment:
                values['call_center_comment'] = call_center_comment

            values['state'] = 'Received'
            values['serial_no'] = self.generate_next_serial_no(model_name)

            web_request = request.env[model_name].sudo().create(values)
            data = {
                'id': web_request.id,
                'message': 'Your data has been added successfully',
            }
            return valid_response(data)
        else:
            return invalid_response('record_found',
                                    'The service {0} is  already requested by {1}'.format(service_name, requested_by))

    @authenticate_token
    @http.route(['/sehati/web-request-serial/generate'], type='http', auth="none", methods=['GET'],
                csrf=False)
    def generate_web_request_serials(self):
        model_name = 'sm.shifa.web.request'

        count = request.env[model_name].sudo().search_count([])
        if count > 0:
            web_request = request.env[model_name].sudo().search([])

            for rec in web_request:
                serial_no = f"WR-{rec.id:08}"
                rec.write({
                    'serial_no': serial_no,
                })

            data = {
                'message': 'Your serial numbers has been generated successfully',
            }
            return valid_response(data)
        else:
            return invalid_response('record_not_found',
                                    'There is no any record is found in web request')

    def generate_next_serial_no(self, model_name):
        count = request.env[model_name].sudo().search_count([])
        next_serial_no = f"WR-{count + 1:08}"
        return next_serial_no

    def generate_serial_no(self):
        model_name = 'sm.shifa.web.request'
        count = request.env[model_name].sudo().search_count([])
        print('count', str(count))
        s_no2 = f"WR-{count + 1:05}"
        print('next serial no', str(s_no2))
        for i in range(1, count + 1):
            s_no = f"WR-{i:05}"
            print('serial no: ', str(s_no))

    @authenticate_token
    @http.route(['/sehati/web-request-serial/generate'], type='http', auth="none", methods=['GET'],
                csrf=False)
    def test_api(self):
        db_name = self._get_db_name()

    def _get_db_name(self, cr, uid, vals, context=None):
        attach_pool = self.pool.get("ir.logging")
        test = attach_pool.search(cr, uid, [('dbname', '!=', ' ')])
        return cr.dbname

