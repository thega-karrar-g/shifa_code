from odoo import http
from odoo.http import request
from odoo.addons.oehealth.oeh_rest_api.controllers.main import authenticate_token
from odoo.addons.oehealth.oeh_rest_api.common_methods import invalid_response, valid_response, upload_attached_file, convert_utc_to_local

from odoo.addons.oehealth.oeh_rest_api.common_methods import extract_arguments
import json

class SmartMindTestRESTAPIController(http.Controller):

    def __init__(self):
        self._model = 'ir.model'

    @authenticate_token
    @http.route(['/sehati/prescription/get-url/<patient_id>'], type='http', auth="none", methods=['GET'], csrf=False)
    def get_file_url(self, patient_id=None, **payload):
        model_name = 'oeh.medical.prescription'
        model = request.env[self._model].sudo().search([('model', '=', model_name)], limit=1)
        payload['fields'] = "['name', 'date', 'link', 'state']"

        # if not patient_id:
        #     return invalid_response('patient_id not found', 'patient_id not found in request ! ')
        if model:
            domain, fields, offset, limit, order = extract_arguments(
                payload)
            if patient_id:
                domain = [('patient.id', '=', patient_id)]

            data = request.env[model.model].sudo().search_read(
                domain=domain, fields=fields, offset=offset, limit=limit, order=order)

            data_to_push = []
            patient_id = False
            for x in data:
                for k, v in x.items():
                    if str(type(v)) in ("<class 'datetime.datetime'>", "<class 'datetime.date'>"):
                        date = convert_utc_to_local(v.strftime("%Y-%m-%d %H:%M:%S"))
                        x[k] = str(date)
                #     for k, v in x.items():
                #         if str(k) == "patient":
                #             if v and len(v) > 0:
                #                 patient_id = v[0]
                #                 x[k] = v[1]
                #             else:
                #                 x[k] = ""
                #
                #     x['patient_id'] = patient_id
                data_to_push.append(x)

            return valid_response(data_to_push)
        return invalid_response('invalid object model', 'The model %s is not available in the registry.' % model_name)

    @authenticate_token
    @http.route(['/sehati/report/get-url/<patient_id>'], type='http', auth="none", methods=['GET'], csrf=False)
    def get_report_file_url(self, patient_id=None, **payload):
        model_name = 'sm.medical.report'
        model = request.env[self._model].sudo().search([('model', '=', model_name)], limit=1)
        payload['fields'] = "['name', 'date', 'state']"
        if model:
            domain, fields, offset, limit, order = extract_arguments(
                payload)
            if patient_id:
                domain = [('patient.id', '=', patient_id)]

            data = request.env[model.model].sudo().search_read(
                domain=domain, fields=fields, offset=offset, limit=limit, order=order)

            data_to_push = []
            patient_id = False
            for x in data:
                for k, v in x.items():
                    if k == "id":
                        url_link = self.get_attachment_pdf(model_name, v, x['name'], x['date'])
                        if len(url_link) == 1:
                            data_to_push.append(url_link[0])
                        elif len(url_link) > 1:
                            for i in url_link:
                                data_to_push.append(i)
                        else:
                            pass
            return valid_response(data_to_push)
        return invalid_response('invalid object model', 'The model %s is not available in the registry.' % model_name)

    @authenticate_token
    @http.route(['/sehati/lab-request/get-url/<patient_id>'], type='http', auth="none", methods=['GET'], csrf=False)
    def get_lab_request_file_url(self, patient_id=None, **payload):
        model_name = 'sm.shifa.lab.request'
        model = request.env[self._model].sudo().search([('model', '=', model_name)], limit=1)
        payload['fields'] = "['name', 'admission_date', 'link', 'state']"
        if model:
            domain, fields, offset, limit, order = extract_arguments(
                payload)
            if patient_id:
                domain = [('patient.id', '=', patient_id), ('state', 'in', ['Done', 'Patient'])]
            data = request.env[model.model].sudo().search_read(
                domain=domain, fields=fields, offset=offset, limit=limit, order=order)
            data_to_push = []
            for x in data:
                x['state'] = x['state'].lower()
                if x['state'] == 'done':
                    for k, v in x.items():
                        if str(type(v)) in ("<class 'datetime.datetime'>", "<class 'datetime.date'>"):
                            date = convert_utc_to_local(v.strftime("%Y-%m-%d %H:%M:%S"))
                            x[k] = str(date)
                    x["date"] = x.pop("admission_date")
                    data_to_push.append(x)
            return valid_response(data_to_push)
        return invalid_response('invalid object model', 'The model %s is not available in the registry.' % model_name)

    @http.route(['/sehati/image-request/get-url/<patient_id>'], type='http', auth="none", methods=['GET'], csrf=False)
    def get_image_request_file_url(self, patient_id=None, **payload):
        model_name = 'sm.shifa.imaging.request'
        model = request.env[self._model].sudo().search([('model', '=', model_name)], limit=1)
        payload['fields'] = "['name', 'admission_date', 'link', 'state']"
        if model:
            domain, fields, offset, limit, order = extract_arguments(
                payload)
            if patient_id:
                domain = [('patient.id', '=', patient_id), ('state', 'in', ['Done', 'Patient'])]
            data = request.env[model.model].sudo().search_read(
                domain=domain, fields=fields, offset=offset, limit=limit, order=order)

            data_to_push = []
            for x in data:
                x['state'] = x['state'].lower()
                if x['state'] == 'done':
                    for k, v in x.items():
                        if str(type(v)) in ("<class 'datetime.datetime'>", "<class 'datetime.date'>"):
                            date_utc = str(v).split('.')[0]
                            date_local = convert_utc_to_local(date_utc)
                            x[k] = date_local
                    x["date"] = x.pop("admission_date")
                    data_to_push.append(x)
            return valid_response(data_to_push)
        return invalid_response('invalid object model', 'The model %s is not available in the registry.' % model_name)

    @http.route(['/sehati/image-tests/get-url/<patient_id>'], type='http', auth="none", methods=['GET'], csrf=False)
    def get_image_tests_file_url(self, patient_id=None, **payload):
        model_name = 'oeh.medical.imaging'
        model = request.env[self._model].sudo().search([('model', '=', model_name)], limit=1)
        payload['fields'] = "['name', 'date_analysis', 'state']"
        if model:
            domain, fields, offset, limit, order = extract_arguments(
                payload)
            if patient_id:
                domain = [('patient.id', '=', patient_id), ('state', '=', 'Done')]
            data = request.env[model.model].sudo().search_read(
                domain=domain, fields=fields, offset=offset, limit=limit, order=order)
            data_to_push = []
            patient_id = False
            for x in data:
                for k, v in x.items():
                    if k == "id":
                        url_link = self.get_attachment_pdf(model_name, v, x['name'], x['date_analysis'])
                        if len(url_link) == 1:
                            data_to_push.append(url_link[0])
                        elif len(url_link) > 1:
                            for i in url_link:
                                data_to_push.append(i)
                        else:
                            pass
            return valid_response(data_to_push)
        return invalid_response('invalid object model', 'The model %s is not available in the registry.' % model_name)

    @authenticate_token
    @http.route(['/sehati/image-test-request/get-url/<patient_id>'], type='http', auth="none", methods=['GET'], csrf=False)
    def get_image_test_request_file_url(self, patient_id=None, **payload):
        imagetest_model_name = 'oeh.medical.imaging'
        imagerequest_model_name = 'sm.shifa.imaging.request'
        
        data_to_push = {
            'test': [],
            'request': []
        }

        # Process Image Tests
        imagetest_model = request.env[self._model].sudo().search([('model', '=', imagetest_model_name)], limit=1)
        if imagetest_model:
            payload['fields'] = "['name', 'date_analysis', 'state']"
            domain, fields, offset, limit, order = extract_arguments(payload)
            if patient_id:
                domain = [('patient.id', '=', patient_id), ('state', '=', 'Done')]
            imagetest_data = request.env[imagetest_model.model].sudo().search_read(
                domain=domain, fields=fields, offset=offset, limit=limit, order=order)
            for record in imagetest_data:
                url_links = self.get_attachment_pdf(imagetest_model_name, record['id'], record['name'], record['date_analysis'])
                for url in url_links:
                    data_to_push['test'].append(url)

        # Process Image Requests
        imagerequest_model = request.env[self._model].sudo().search([('model', '=', imagerequest_model_name)], limit=1)
        if imagerequest_model:
            payload['fields'] = "['name', 'admission_date', 'link', 'state']"
            domain, fields, offset, limit, order = extract_arguments(payload)
            if patient_id:
                domain = [('patient.id', '=', patient_id), ('state', 'in', ['Done', 'Patient'])]
            imagerequest_data = request.env[imagerequest_model.model].sudo().search_read(
                domain=domain, fields=fields, offset=offset, limit=limit, order=order)
            for record in imagerequest_data:
                record['state'] = record['state'].lower()
                if record['state'] == 'done':
                    for key, value in record.items():
                        if str(type(value)) in ("<class 'datetime.datetime'>", "<class 'datetime.date'>"):
                            record[key] = str(convert_utc_to_local(value.strftime("%Y-%m-%d %H:%M:%S")))
                    record["date"] = record.pop("admission_date")
                    data_to_push['request'].append(record)

        # Return Combined Response
        return valid_response(data_to_push)


    @http.route(['/sehati/lab-tests/get-url/<patient_id>'], type='http', auth="none", methods=['GET'], csrf=False)
    def get_lab_tests_file_url(self, patient_id=None, **payload):
        model_name = 'oeh.medical.lab.test'
        model = request.env[self._model].sudo().search([('model', '=', model_name)], limit=1)
        payload['fields'] = "['id', 'name', 'date_analysis', 'state']"
        if model:
            domain, fields, offset, limit, order = extract_arguments(payload)
            if patient_id:
                domain = [('patient.id', '=', patient_id), ('state', '=', 'Done')]
            data = request.env[model.model].sudo().search_read(
                domain=domain, fields=fields, offset=offset, limit=limit, order=order)
            data_to_push = []
            patient_id = False
            for x in data:
                for k, v in x.items():
                    if k == "id":
                        url_link = self.get_attachment_pdf(model_name, v, x['name'], x['date_analysis'])
                        if len(url_link) == 1:
                            data_to_push.append(url_link[0])
                        elif len(url_link) > 1:
                            for i in url_link:
                                data_to_push.append(i)
                        else:
                            pass
            return valid_response(data_to_push)
        return invalid_response('invalid object model', 'The model %s is not available in the registry.' % model_name)

    @authenticate_token
    @http.route(['/sehati/lab-test-request/get-url/<patient_id>'], type='http', auth="none", methods=['GET'], csrf=False)
    def get_lab_test_request_file_url(self, patient_id=None, **payload):
        labtest_model_name = 'oeh.medical.lab.test'
        labrequest_model_name = 'sm.shifa.lab.request'
        
        data_to_push = {
            'test': [],
            'request': []
        }

        # Process Lab Tests
        labtest_model = request.env[self._model].sudo().search([('model', '=', labtest_model_name)], limit=1)
        if labtest_model:
            payload['fields'] = "['id', 'name', 'date_analysis', 'state']"
            domain, fields, offset, limit, order = extract_arguments(payload)
            if patient_id:
                domain = [('patient.id', '=', patient_id), ('state', '=', 'Done')]
            labtest_data = request.env[labtest_model.model].sudo().search_read(
                domain=domain, fields=fields, offset=offset, limit=limit, order=order)
            for record in labtest_data:
                url_links = self.get_attachment_pdf(labtest_model_name, record['id'], record['name'], record['date_analysis'])
                for url in url_links:
                    data_to_push['test'].append(url)

        # Process Lab Requests
        labrequest_model = request.env[self._model].sudo().search([('model', '=', labrequest_model_name)], limit=1)
        if labrequest_model:
            payload['fields'] = "['name', 'admission_date', 'link', 'state']"
            domain, fields, offset, limit, order = extract_arguments(payload)
            if patient_id:
                domain = [('patient.id', '=', patient_id), ('state', 'in', ['Done', 'Patient'])]
            labrequest_data = request.env[labrequest_model.model].sudo().search_read(
                domain=domain, fields=fields, offset=offset, limit=limit, order=order)
            for record in labrequest_data:
                record['state'] = record['state'].lower()
                if record['state'] == 'done':
                    for key, value in record.items():
                        if str(type(value)) in ("<class 'datetime.datetime'>", "<class 'datetime.date'>"):
                            record[key] = str(convert_utc_to_local(value.strftime("%Y-%m-%d %H:%M:%S")))
                    record["date"] = record.pop("admission_date")
                    data_to_push['request'].append(record)

        # Return Combined Response
        return valid_response(data_to_push)


    def get_attachment_pdf(self, mo_name, id, name, date, **payload):
        url_date = convert_utc_to_local(date.strftime("%Y-%m-%d %H:%M:%S"))
        model_name = 'ir.attachment'
        model = request.env[self._model].sudo().search([('model', '=', model_name)], limit=1)
        payload['fields'] = "['name', 'access_token', 'res_id']"
        if model:
            domain, fields, offset, limit, order = extract_arguments(payload)
            domain = [('res_model', '=', mo_name), ('res_id', '=', id)]
            data = request.env[model.model].sudo().search_read(
                domain=domain, fields=fields, offset=offset, limit=limit, order=order)
        config_obj = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        attachment_url = config_obj + "/web/attachments/token/"
        for x in data:
            for k, v in x.items():
                if k == 'access_token':
                    x['access_token'] = attachment_url + v
                if k == 'name':
                    if name != v[:4]:
                        x[k] = name + "_" + v
                    else:
                        x[k] = v
            x["link"] = x.pop("access_token")
            x['date'] = url_date
            x["id"] = x.pop("res_id")
        return data
    
    @authenticate_token
    @http.route(['/sehati/sliders'], type='http', auth='none', methods=['GET'], csrf=False)
    def get_sliders(self, **kwargs):
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        sliders = request.env['sm.slider'].sudo().search([])
        result = []

        for slider in sliders:
            # Construct the link to the attachment field
            attachment_url = f"{base_url}/web/content/sm.slider/{slider.id}/attachment"
            result.append({
                'id': slider.id,
                'name': slider.name,
                'image_url': attachment_url
            })

        # Return the response with 'success' and 'data' keys as in the image
        response_data = {
            'success': 1,
            'data': result
        }

        return request.make_response(
            json.dumps(response_data),
            headers=[('Content-Type', 'application/json')]
        )
