import base64
import unicodedata

from odoo import http, _
from odoo.exceptions import AccessDenied, AccessError, ValidationError
from odoo.http import request
from datetime import datetime
from odoo.addons.oehealth.oeh_rest_api.common_methods import invalid_response, valid_response, extract_arguments, \
    convert_date_to_utc, get_file_name, upload_attached_file, convert_utc_to_local
from odoo.addons.oehealth.oeh_rest_api.controllers.main import authenticate_token
from odoo.addons.oehealth.oeh_rest_api.shared_methods import SmartMindSharedMethods
import logging
import ast

_logger = logging.getLogger(__name__)


class SmartMindCaregiverRESTAPIController(http.Controller, SmartMindSharedMethods):
    def __init__(self):
        self._model = 'ir.model'

    @authenticate_token
    @http.route(['/sehati/caregiver/login'], type='http', auth="none", methods=['POST'],
                csrf=False)
    def caregiver_login(self, **post):
        # db name production serve
        db = 'Globcare'
        # db test server
        # db = 'Globcare15'
        # db = 'journal'
        username = post.get('username')
        password = post.get('password')

        if not username:
            # throw error message if username is not provided
            error_msg = 'username is missing'
            return invalid_response('missing error', error_msg)
        if not password:
            error_msg = 'password is missing'
            return invalid_response('missing error', error_msg)

        try:
            request.session.authenticate(db, username, password)
        except AccessError as ae:
            return invalid_response("Access error", "Error: %s" % ae.name)
        except AccessDenied as ad:
            return invalid_response("Access denied", "Username or password is invalid")
        except Exception as e:
            info = "The database name is not valid {}".format((e))
            error = "invalid_database"
            _logger.error(info)
            return invalid_response(error, info, 403)

        uid = request.session.uid
        if not uid:
            info = "authentication failed"
            error = "authentication failed"
            _logger.error(info)
            return invalid_response("wrong database name", error, 401)
        model_name = 'oeh.medical.physician'
        caregiver = request.env[model_name].sudo().search([('oeh_user_id', '=', uid), ('active', '=', True)], limit=1)
        if caregiver:
            post['fields'] = "['id', 'name', 'name_ar', 'mobile', 'phone', 'role_type', 'doctor_fcm_token']"
            domain, fields, offset, limit, order = extract_arguments(post)
            domain = [('id', '=', caregiver.id), ('role_type', '=', 'C')]
            data = request.env[model_name].sudo().search_read(
                domain=domain, fields=fields, offset=offset, limit=limit, order=order)

            if data:
                # get caregiver module id
                model_caregiver = 'sm.caregiver'
                caregiver_obj = request.env[self._model].sudo().search([('model', '=', model_caregiver)], limit=1)
                post['fields'] = "['id']"
                domain, fields, offset, limit, order = extract_arguments(post)
                domain = ['|', '|', ('caregiver', '=', caregiver.id),
                          ('caregiver_second', '=', caregiver.id),
                          ('caregiver_third', '=', caregiver.id),
                          ('state', '=', 'In Progress')]
                caregiver_data = request.env[caregiver_obj.model].sudo().search_read(
                    domain=domain, fields=fields, offset=offset, limit=limit, order=order)
                if caregiver_data:
                    data[0]['record_id'] = caregiver_data[len(caregiver_data)-1]['id']
                else:
                    data[0]['record_id'] = ""
                return valid_response(data)
            else:
                return invalid_response("no data", "No Data Check Role Type")
        else:
            return invalid_response("the user is not active", "Medical Staff User is inactive")

    #  state in progrese only
    @authenticate_token
    @http.route(['/sehati/caregiver/get-my-patient/<caregiver_id>'], type='http', auth="none", methods=['Get'],
                csrf=False)
    def caregiver_get_patient(self, caregiver_id=None, **payload):
        model_name = 'sm.caregiver'
        model = request.env[self._model].sudo().search([('model', '=', model_name)], limit=1)

        payload[
            'fields'] = "['id', 'patient','state', 'provisional_diagnosis', 'provisional_diagnosis_add', 'provisional_diagnosis_add2', 'provisional_diagnosis_add3', 'medical_care_plan', 'special_instructions']"

        if not caregiver_id:
            # throw error message if caregiver id is not provided
            error_msg = 'caregiver id is missing'
            return invalid_response('missing error', error_msg)
        if model:
            try:
                domain, fields, offset, limit, order = extract_arguments(payload)
                domain = ['|', '|', ('caregiver', '=', int(caregiver_id)),
                          ('caregiver_second', '=', int(caregiver_id)),
                          ('caregiver_third', '=', int(caregiver_id)),
                          ('state', '=', 'In Progress')]
                data = request.env[model.model].sudo().search_read(
                    domain=domain, fields=fields, offset=offset, limit=limit, order=order)
                data_to_push = []
                for x in data:
                    for k, v in x.items():
                        if str(k) == "patient":
                            if v and len(v) > 0:
                                x[k] = v[1]
                            else:
                                x[k] = ""
                        if str(k) == "provisional_diagnosis":
                            if v and len(v) > 0:
                                x[k] = v[1]
                            else:
                                x[k] = ""
                        if str(k) == "provisional_diagnosis_add":
                            if v and len(v) > 0:
                                x[k] = v[1]
                            else:
                                x[k] = ""
                        if str(k) == "provisional_diagnosis_add2":
                            if v and len(v) > 0:
                                x[k] = v[1]
                            else:
                                x[k] = ""
                        if str(k) == "provisional_diagnosis_add3":
                            if v and len(v) > 0:
                                x[k] = v[1]
                            else:
                                x[k] = ""
                        if str(k) == "medical_care_plan":
                            if v and len(v) > 0:
                                x[k] = v
                            else:
                                x[k] = ""
                        if str(k) == "special_instructions":
                            if v and len(v) > 0:
                                x[k] = v
                            else:
                                x[k] = ""
                    data_to_push.append(x)
                return valid_response(data_to_push[len(data_to_push)-1])

            except Exception as e:

                return invalid_response('failed to get patient', e)

        return invalid_response('invalid object model',
                                'The model %s is not available in the registry.' % model_name)

    @authenticate_token
    @http.route(['/sehati/caregiver/get-patient-medicine/<record_id>'], type='http', auth="none", methods=['Get'],
                csrf=False)
    def caregiver_get_patient_medicines(self, record_id=None, **payload):
        model_name = 'sm.caregiver'
        model = request.env[self._model].sudo().search([('model', '=', model_name)], limit=1)

        payload['fields'] = "['id', 'prescribed_medicine_main']"

        if not record_id:
            # throw error message if caregiver id is not provided
            error_msg = 'record id is missing'
            return invalid_response('missing error', error_msg)
        if model:
            try:
                domain, fields, offset, limit, order = extract_arguments(payload)
                domain = [('id', '=', int(record_id))]

                data = request.env[model.model].sudo().search_read(
                    domain=domain, fields=fields, offset=offset, limit=limit, order=order)
                data_to_push = []
                image_url = False
                prescribed_medicine_list = []
                for x in data:
                    for k, v in x.items():
                        if str(k) == "prescribed_medicine_main":

                            if v and len(v) > 0:
                                for medicine_id in v:

                                    prescriped_obj = request.env['sm.caregiver.main.patient.medicine'].search(
                                        [('id', '=', int(medicine_id)), ('state', '=', 'activate')]
                                    )
                                    if prescriped_obj:
                                        medicine_values = {
                                            'id': prescriped_obj.id,
                                            'medicine': prescriped_obj.medicine,
                                            'dose': prescriped_obj.prescribed_dose if prescriped_obj.prescribed_dose else "",
                                            'dose_unit': prescriped_obj.prescribed_dose_unit.name if prescriped_obj.prescribed_dose_unit.name else "",
                                            'dose_route': prescriped_obj.prescribed_dose_route.name if prescriped_obj.prescribed_dose_route.name else "",
                                            'frequency': prescriped_obj.medicine_frequency.name if prescriped_obj.medicine_frequency.name else "",
                                            'image_url': self.get_image_url('medicine_image',
                                                                            'sm.caregiver.main.patient.medicine',
                                                                            str(medicine_id)),

                                        }
                                        prescribed_medicine_list.append(medicine_values)
                            else:
                                prescribed_medicine_list = v
                            x[k] = prescribed_medicine_list
                    data_to_push.append(x)
                return valid_response(prescribed_medicine_list)
            except Exception as e:

                return invalid_response('failed to get patient medicines', e)


    @authenticate_token
    @http.route(['/sehati/caregiver/add-vital-signs'], type='http', auth="none", methods=['Post'],
                csrf=False)
    def caregiver_add_vital_signs(self, **post):
        model_name = 'sm.caregiver.vital.signs.lines'
        model = request.env[self._model].sudo().search([('model', '=', model_name)], limit=1)
        data = ast.literal_eval(post.get('data'))
        record_id = data.get('caregiver_vital_signs_id')
        caregiver_id = data.get('caregiver')
        if not record_id:
            # throw error message if record id is not provided
            error_msg = 'record id is missing'
            return invalid_response('missing error', error_msg)
        if not caregiver_id:
            # throw error message if caregiver id is not provided
            error_msg = 'caregiver id is missing'
            return invalid_response('missing error', error_msg)
        if model:
            try:
                vital_signs_obj = request.env[model_name].sudo().create(data)
                data = {
                    'id': vital_signs_obj.id,
                    'message': 'Vital Signs has been saved successfully!'
                }
                return valid_response(data)
            except Exception as e:

                return invalid_response('failed to add Vital Signs', e)

    # Get vital signs
    @authenticate_token
    @http.route(['/sehati/caregiver/get-vital-signs/<record_id>'], type='http', auth="none", methods=['Get'],
                csrf=False)
    def caregiver_get_vital_signs(self, record_id=None, **payload):
        model_name = 'sm.caregiver.vital.signs.lines'
        model = request.env[self._model].sudo().search([('model', '=', model_name)], limit=1)
        payload[
            'fields'] = "['id', 'caregiver_vital_signs_id', 'systolic', 'diastolic', 'blood_sugar', 'heart_rate', 'temperature', 'respiratory_rate', 'o2_sat', 'oxygen_saturation', 'date','day', 'caregiver']"
        if not record_id:
            # throw error message if caregiver id is not provided
            error_msg = 'record id is missing'
            return invalid_response('missing error', error_msg)
        if model:
            try:
                domain, fields, offset, limit, order = extract_arguments(payload)
                domain = [('caregiver_vital_signs_id', '=', int(record_id))]
                data = request.env[model.model].sudo().search_read(
                    domain=domain, fields=fields, offset=offset, limit=5, order='id desc')
                data_to_push = []
                for x in data:
                    for k, v in x.items():
                        if str(k) == "caregiver_vital_signs_id":
                            if v:
                                x[k] = v[0]
                            else:
                                x[k] = ""
                        if str(k) == "caregiver":
                            if v:
                                x[k] = v[1]
                            else:
                                x[k] = ""
                        if str(type(v)) in ("<class 'datetime.datetime'>", "<class 'datetime.date'>"):
                            date = convert_utc_to_local(v.strftime("%Y-%m-%d %H:%M:%S"))
                            x[k] = str(date)
                        if str(k) in ['systolic', 'diastolic', 'blood_sugar', 'heart_rate', 'temperature', 'respiratory_rate', 'oxygen_saturation']:
                            if v and v > 0:
                                x[k] = v
                            else:
                                x[k] = 0
                        if str(k) == 'o2_sat':
                            if v and len(v) > 0:
                                x[k] = v
                            else:
                                x[k] = ""
                    data_to_push.append(x)
                return valid_response(data_to_push)
            except Exception as e:

                return invalid_response('failed to get vital sign', e)

    @authenticate_token
    @http.route(['/sehati/caregiver/add-pain-present'], type='http', auth="none", methods=['Post'],
                csrf=False)
    def caregiver_add_pain_present(self, **post):
        model_name = 'sm.caregiver.pain.present.lines'
        model = request.env[self._model].sudo().search([('model', '=', model_name)], limit=1)
        data = ast.literal_eval(post.get('data'))
        record_id = data.get('caregiver_pain_present_id')
        caregiver_id = data.get('caregiver')
        if not record_id:
            # throw error message if record id is not provided
            error_msg = 'record id is missing'
            return invalid_response('missing error', error_msg)
        if not caregiver_id:
            # throw error message if caregiver id is not provided
            error_msg = 'caregiver id is missing'
            return invalid_response('missing error', error_msg)
        if model:
            try:
                pain_obj = request.env[model_name].sudo().create(data)
                data = {
                    'id': pain_obj.id,
                    'message': 'Pain Present has been saved successfully!'
                }
                return valid_response(data)
            except Exception as e:
                return invalid_response('failed to add Pain present', e)

    @authenticate_token
    @http.route(['/sehati/caregiver/get-pain-present/<record_id>'], type='http', auth="none", methods=['Get'],
                csrf=False)
    def caregiver_get_pain_present(self, record_id=None, **payload):
        model_name = 'sm.caregiver.pain.present.lines'
        model = request.env[self._model].sudo().search([('model', '=', model_name)], limit=1)
        payload[
            'fields'] = "['id', 'caregiver_pain_present_id', 'pain_area', 'pain_score', 'scale_used', 'comment', 'date', 'day', 'caregiver']"

        if not record_id:
            # throw error message if caregiver id is not provided
            error_msg = 'record id is missing'
            return invalid_response('missing error', error_msg)
        if model:
            try:
                domain, fields, offset, limit, order = extract_arguments(payload)
                domain = [('caregiver_pain_present_id', '=', int(record_id))]
                data = request.env[model.model].sudo().search_read(
                    domain=domain, fields=fields, offset=offset, limit=5, order='id desc')
                data_to_push = []
                for x in data:
                    for k, v in x.items():
                        if str(k) == "caregiver_pain_present_id":
                            if v:
                                x[k] = v[0]
                            else:
                                x[k] = ""
                        if str(k) == "caregiver":
                            if v:
                                x[k] = v[1]
                            else:
                                x[k] = ""
                        if str(type(v)) in ("<class 'datetime.datetime'>", "<class 'datetime.date'>"):
                            date = convert_utc_to_local(v.strftime("%Y-%m-%d %H:%M:%S"))
                            x[k] = str(date)
                        if str(k) in ['pain_score', 'scale_used', 'comment', 'pain_area']:
                            if v and len(v) > 0:
                                x[k] = v
                            else:
                                x[k] = ""
                    data_to_push.append(x)
                return valid_response(data_to_push)
            except Exception as e:

                return invalid_response('failed to get pain present records', e)

    @authenticate_token
    @http.route(['/sehati/caregiver/observation'], type='http', auth="none", methods=['Post'],
                csrf=False)
    def caregiver_observation(self, **post):
        model_name = 'sm.caregiver.observation.lines'
        model = request.env[self._model].sudo().search([('model', '=', model_name)], limit=1)
        data = ast.literal_eval(post.get('data'))
        record_id = data.get('caregiver_objective_id')
        caregiver_id = data.get('caregiver')
        if not record_id:
            return invalid_response('missing error', 'Record id is missing')
        if not caregiver_id:
            return invalid_response('missing error', 'Caregiver id is missing')

        if model:
            try:
                objective_obj = request.env[model_name].sudo().create(data)
                data = {
                    'id': objective_obj.id,
                    'message': 'Objective has been saved successfully!'
                }
                return valid_response(data)
            except Exception as e:

                return invalid_response('failed to add Given medicine', e)

    @authenticate_token
    @http.route(['/sehati/caregiver/get-observation/<record_id>'], type='http', auth="none", methods=['Get'],
                csrf=False)
    def caregiver_get_observation(self, record_id=None, **payload):
        model_name = 'sm.caregiver.observation.lines'
        model = request.env[self._model].sudo().search([('model', '=', model_name)], limit=1)
        payload[
            'fields'] = "['id', 'nutritional_status', 'feeding', 'sleeping_pattern', 'first_number_hours', 'first_from', 'second_to', 'progress_noted', 'caregiver_objective_id', 'caregiver', 'date']"

        if not record_id:
            # throw error message if caregiver id is not provided
            error_msg = 'record id is missing'
            return invalid_response('missing error', error_msg)
        if model:
            try:
                domain, fields, offset, limit, order = extract_arguments(payload)
                domain = [('caregiver_objective_id', '=', int(record_id))]
                data = request.env[model.model].sudo().search_read(
                    domain=domain, fields=fields, offset=offset, limit=5, order='id desc')
                data_to_push = []
                for x in data:
                    for k, v in x.items():
                        if str(k) == "caregiver_objective_id":
                            x[k] = v[0]
                        if str(type(v)) in ("<class 'datetime.datetime'>", "<class 'datetime.date'>"):
                            date = convert_utc_to_local(v.strftime("%Y-%m-%d %H:%M:%S"))
                            x[k] = str(date)
                        if str(k) in [ 'nutritional_status', 'feeding', 'sleeping_pattern', 'first_number_hours', 'first_from', 'second_to', 'progress_noted']:
                           if v and len(v) > 0:
                               x[k] = v
                           else:
                               x[k] = ""
                        if str(k) == "caregiver":
                            if v and len(v) > 0:
                                x[k] = v[1]
                            else:
                                x[k] = ""
                    data_to_push.append(x)
                return valid_response(data_to_push)
            except Exception as e:

                return invalid_response('failed to get pain present records', e)

    @authenticate_token
    @http.route(['/sehati/caregiver/get-medicine-times'], type='http', auth="none", methods=['POST'],
                csrf=False)
    def caregiver_get_medicine_times(self, **post):
        model_name = 'sm.caregiver.main.patient.medicine'
        model = request.env[self._model].sudo().search([('model', '=', model_name)], limit=1)
        post['fields'] = "['id', 'caregiver_id','schedule_lines']"
        record_id = post.get('record_id')
        medicine_id = post.get('medicine_id')
        if not record_id:
            # throw error message if caregiver id is not provided
            error_msg = 'record id is missing'
            return invalid_response('missing error', error_msg)
        if model:
            try:
                domain, fields, offset, limit, order = extract_arguments(post)
                domain = [('caregiver_id', '=', int(record_id)), ('id', '=', int(medicine_id))]
                data = request.env[model.model].sudo().search_read(
                    domain=domain, fields=fields, offset=offset)
                schedule = []
                for k, v in data[0].items():
                    if k == 'schedule_lines':
                        schedule = v
                        break
                post['fields'] = "['id', 'medicine','date','time','state', 'comment']"
                domain, fields, offset, limit, order = extract_arguments(post)
                domain = [('id', 'in', schedule)]
                model_name = 'sm.caregiver.medicine.schedule'
                model = request.env[self._model].sudo().search([('model', '=', model_name)], limit=1)
                data = request.env[model.model].sudo().search_read(
                    domain=domain, fields=fields, offset=offset)
                data_to_push = []
                for x in data:
                    for k, v in x.items():
                        if str(type(v)) in ("<class 'datetime.date'>"):
                            date = v.strftime("%Y-%m-%d")
                            x[k] = str(date)
                        if k == 'time':
                            x[k] = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(v) * 60, 60))
                        if k == 'state':
                            if v == False:
                                x[k] = ''
                        if k == 'comment':
                            if v == False:
                                x[k] = ''
                    data_to_push.append(x)
                return valid_response(data_to_push)

            except Exception as e:

                return invalid_response('failed to get pain present records', e)

    @authenticate_token
    @http.route(['/sehati/caregiver/update-medicine-state'], type='http', auth="none", methods=['POST'],
                csrf=False)
    def caregiver_update_medicine_state(self, **post):
        model_name = 'sm.caregiver.medicine.schedule'
        model = request.env[self._model].sudo().search([('model', '=', model_name)], limit=1)
        slot_id = post.get('slot_id')
        medicine_state = post.get('state')
        caregiver = post.get('caregiver')
        comment = post.get('comment')
        medicine_obj = request.env[model.model].sudo().browse(int(slot_id))
        values = {}
        if model:
            try:
                values['state'] = str(medicine_state)
                values['caregiver'] = int(caregiver)
                values['comment'] = comment
                medicine_obj.write(values)
                data = {
                    'id': slot_id,
                    'state': medicine_state,
                    'message': 'state updated successfully!'
                }
                return valid_response(data)
            except Exception as e:

                return invalid_response('failed to get pain present records', e)

    @authenticate_token
    @http.route(['/sehati/caregiver/get-medicine-slots/<record_id>'], type='http', auth="none", methods=['Get'],
                csrf=False)
    def caregiver_get_medicines_slots(self, record_id=None, **payload):
        model_name = 'sm.caregiver.main.patient.medicine'
        model = request.env[self._model].sudo().search([('model', '=', model_name)], limit=1)

        payload['fields'] = "['id', 'medicine', 'prescribed_dose', 'prescribed_dose_unit', 'prescribed_dose_route', 'medicine_frequency']"

        if not record_id:
            # throw error message if caregiver id is not provided
            error_msg = 'record id is missing'
            return invalid_response('missing error', error_msg)
        if model:
            try:
                domain, fields, offset, limit, order = extract_arguments(payload)
                domain = [('caregiver_id', '=', int(record_id)), ('state', '=', 'activate')]
                data = request.env[model.model].sudo().search_read(
                    domain=domain, fields=fields, offset=offset, limit=limit, order=order)
                image_url = False
                prescribed_medicine_list = []

                if data:
                    for x in data:
                        slots = self.get_slot(int(x['id']))
                        medicine_values = {
                                                    'id': x['id'],
                                                    'medicine': x['medicine'],
                                                    'dose': x['prescribed_dose'] if x['prescribed_dose'] else "",
                                                    'dose_unit': x['prescribed_dose_unit'][1] if x['prescribed_dose_unit'] else "",
                                                    'dose_route': x['prescribed_dose_route'][1] if x['prescribed_dose_route'] else "",
                                                    'frequency': x['medicine_frequency'][1] if x['medicine_frequency'] else "",
                                                    'image_url': self.get_image_url('medicine_image',
                                                                                    'sm.caregiver.main.patient.medicine',
                                                                                    str(x['id'])) or "",
                                                    'slots': slots
                                                }
                        prescribed_medicine_list.append(medicine_values)
                else:
                    invalid_response('missing error', 'There is no active medicines')
                return valid_response(prescribed_medicine_list)
            except Exception as e:
                return invalid_response('failed to get patient medicines', e)

    @authenticate_token
    @http.route(['/sehati/caregiver/get-patient-details/<patient_id>'], type='http', auth="none", methods=['Get'],
                csrf=False)
    def caregiver_patient_details(self, patient_id=None, **payload):
        model_name = 'sm.caregiver'
        payload[
            'fields'] = "['id', 'prescribed_medicine_main', 'provisional_diagnosis', 'provisional_diagnosis_add', 'provisional_diagnosis_add2', 'provisional_diagnosis_add3', 'medical_care_plan', 'special_instructions']"

        if not patient_id:
            # throw error message if caregiver id is not provided
            error_msg = 'patient id is missing'


            return invalid_response('missing error', error_msg)
        if model_name:
            try:
                domain, fields, offset, limit, order = extract_arguments(payload)
                domain = [('patient', '=', int(patient_id)),
                          ('state', '=', 'In Progress')]

                data = request.env[model_name].sudo().search_read(
                    domain=domain, fields=fields, offset=offset, limit=limit, order=order)
                
                if data:
                    data_to_push = []
                    prescribed_medicine_list = []
                    for x in data:
                        for k, v in x.items():
                            if str(k) == "provisional_diagnosis":
                                if v and len(v) > 0:
                                    x[k] = v[1]
                                else:
                                    x[k] = ""
                            if str(k) == "provisional_diagnosis_add":
                                if v and len(v) > 0:
                                    x[k] = v[1]
                                else:
                                    x[k] = ""
                            if str(k) == "provisional_diagnosis_add2":
                                if v and len(v) > 0:
                                    x[k] = v[1]
                                else:
                                    x[k] = ""
                            if str(k) == "provisional_diagnosis_add3":
                                if v and len(v) > 0:
                                    x[k] = v[1]
                                else:
                                    x[k] = ""
                            if str(k) == "medical_care_plan":
                                if v and len(v) > 0:
                                    x[k] = v
                                else:
                                    x[k] = ""
                            if str(k) == "special_instructions":
                                if v and len(v) > 0:
                                    x[k] = v
                                else:
                                    x[k] = ""

                            if str(k) == "prescribed_medicine_main":

                                if v and len(v) > 0:
                                    for medicine_id in v:
                                        prescriped_obj = request.env['sm.caregiver.main.patient.medicine'].search(
                                            [('id', '=', int(medicine_id)), ('state', '=', 'activate')]
                                        )
                                        if prescriped_obj:
                                            slots = self.get_slot(int(medicine_id))
                                            medicine_values = {
                                                'id': prescriped_obj.id,
                                                'medicine': prescriped_obj.medicine,
                                                'dose': prescriped_obj.prescribed_dose if prescriped_obj.prescribed_dose else "",
                                                'dose_unit': prescriped_obj.prescribed_dose_unit.name if prescriped_obj.prescribed_dose_unit.name else "",
                                                'dose_route': prescriped_obj.prescribed_dose_route.name if prescriped_obj.prescribed_dose_route.name else "",
                                                'frequency': prescriped_obj.medicine_frequency.name if prescriped_obj.medicine_frequency.name else "",
                                                'image_url': self.get_image_url('medicine_image',
                                                                                'sm.caregiver.main.patient.medicine',
                                                                                str(medicine_id)),
                                                'slots': slots
                                            }
                                            prescribed_medicine_list.append(medicine_values)
                                else:
                                    prescribed_medicine_list = v
                                x[k] = prescribed_medicine_list

                        x["medicines"] = x.pop("prescribed_medicine_main")
                        data_to_push.append(x)
                return valid_response(data_to_push[len(data_to_push)-1])

            except Exception as e:

                return invalid_response('failed to get patient')

        return invalid_response('invalid object model',
                                'The model %s is not available in the registry.' % model_name)

    def get_slot(self, medicine_id):
        slot_list = []
        model_name = 'sm.caregiver.main.patient.medicine'
        domain = [('id', '=', int(medicine_id))]
        medicine_obj = request.env[model_name].sudo().search(domain)
        for rec in medicine_obj.schedule_lines:
            slots = {
                'id': rec.id,
                'date': rec.date.strftime("%Y-%m-%d"),
                'time': '{0:02.0f}:{1:02.0f}'.format(*divmod(float(rec.time) * 60, 60)),
                'state': rec.state or '',
                'comment': rec.comment or '',
            }
            slot_list.append(slots)
        return slot_list
