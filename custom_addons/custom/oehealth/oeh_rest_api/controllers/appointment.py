from odoo import http, _
from odoo.http import request
from datetime import datetime, timedelta
import base64

from odoo.addons.oehealth.oeh_rest_api.common_methods import invalid_response, valid_response, extract_arguments, \
    get_file_name, upload_attached_file, convert_utc_to_local
from odoo.addons.oehealth.oeh_rest_api.controllers.main import authenticate_token
from odoo.addons.oehealth.oeh_rest_api.shared_methods import SmartMindSharedMethods


class SmartMindAppointmentRESTAPIController(http.Controller, SmartMindSharedMethods):
    def __init__(self):
        self._model = 'ir.model'

    @authenticate_token
    @http.route(['/sehati/appointment/create'], type='http', auth="none", methods=['POST'],
                csrf=False)
    def create_appointment(self, **post):
        date_format = "%Y-%m-%d"  # %H:%M:%S
        model_name = 'oeh.medical.appointment'
        model = request.env[self._model].sudo().search([('model', '=', model_name)], limit=1)

        patient_id = post.get('patient_id')
        doctor_id = post.get('doctor_id')
        app_version = post.get('app_version')
        appointment_date = post.get('appointment_date')
        branch = post.get('branch')
        if not branch:
            branch = ''
        if not patient_id:
            return invalid_response('patient_id not found', 'Patient ID not found in request!')
        if not doctor_id:
            return invalid_response('doctor_id not found', 'Doctor ID not found in request!')
        if not app_version:
            return invalid_response('app_version not found',
                                    'Please update to the latest version of this app to complete this service, thank you.')
        if not appointment_date:
            return invalid_response('appointment_date not found', 'Appointment date not found in request!')

        if model:
            try:
                values = {}
                values['name'] = request.env.ref('oehealth.seq_oeh_medical_appointment').next_by_id()
                appointment_time_str = post.get('appointment_time')
                appointment_time = self.convert_timeslot_to_time(appointment_time_str)
                patient = False
                count_patient = request.env['oeh.medical.patient'].sudo().search_count(
                    [('id', '=', int(patient_id))])
                if count_patient > 0:
                    patient = request.env['oeh.medical.patient'].sudo().browse(int(patient_id))
                    values['patient'] = patient.id
                else:
                    return invalid_response('invalid patient_id', 'Invalid Patient ID ! ')

                doctor = False
                count_doctor = request.env['oeh.medical.physician'].sudo().search_count([('id', '=', int(doctor_id))])
                if count_doctor > 0:
                    doctor = request.env['oeh.medical.physician'].sudo().browse(int(doctor_id))
                    values['doctor'] = doctor.id
                    values['total_service_price'] = doctor.tele_price
                else:
                    return invalid_response('invalid doctor_id', 'Invalid Doctor ID ! ')

                appointment_date_only = datetime.strptime(appointment_date, date_format)
                appointment_date = self.get_appointment_date_time(appointment_date_only, appointment_time)
                appointment_end = self.get_appointment_end(appointment_date_only, doctor_id, appointment_date)

                values['timeslot'] = self.get_timeslot_id(doctor_id, appointment_date, appointment_time_str)
                # get files name
                file1 = get_file_name(post.get('attached_file'), 'attached_file')
                file2 = get_file_name(post.get('attached_file_2'), 'attached_file_2')
                filename = "{0}, {1}".format(file1, file2)
                # filename = "{0}, {1}, {2}".format(file1, file2, file3)
                # upload files from request
                values['attached_file'] = upload_attached_file(post.get('attached_file'), 'attached_file')
                values['attached_file_2'] = upload_attached_file(post.get('attached_file_2'), 'attached_file_2')
                values['patient_comment'] = post.get('patient_comment')
                payment_type = post.get('payment_type')
                values['payment_made_through'] = 'mobile'
                values['branch'] = branch
                values['state'] = 'Scheduled'
                if 'patient_status' in post and post.get('patient_status') in ['Ambulatory', 'Outpatient',
                                                                               'Inpatient']:
                    values['patient_status'] = post.get('patient_status')

                if 'urgency_level' in post and post.get('urgency_level') in ['Normal', 'Urgent',
                                                                             'Medical Emergency']:
                    values['urgency_level'] = post.get('urgency_level')

                # ----------------------------------------------------------------------------------------------
                values['appointment_date_only'] = appointment_date_only
                values['appointment_time'] = appointment_time
                values['appointment_date'] = appointment_date
                values['appointment_end'] = appointment_end
                # ----------------------------------------------------------------------------------------------
                jitsi_link = False
                if payment_type == 'pay':
                    values['payment_type'] = 'Payment Process'
                else:
                    values['payment_type'] = 'Insurance'

                appointment = request.env[model_name].sudo().create(values)
                appointment_id = appointment.id

                if payment_type == 'pay':  # VI: It must be here after creation appointment not before it.
                    jitsi_link = self._create_jitsi_meeting(appointment_id)

                data = {
                    'id': appointment_id,
                    'payment_type': payment_type,
                    'upload file name': filename,
                    'jitsi  meeting link': jitsi_link,
                    'message': 'Appointment created successfully!',
                    'appointment_date': str(appointment_date),
                    'appointment_time': str(appointment_time),
                    'appointment_end': str(appointment_end),
                }
                self._add_service_request(
                    patient_id, False, appointment_date, appointment.name,
                    post.get('location'),
                    post.get('attached_file'),
                    post.get('attached_file_2'),
                    post.get('attached_file_3')
                )
                return valid_response(data)

            except Exception as e:
                #print(e)
                return invalid_response('failed to add appointment', str(e))
        return invalid_response('invalid object model', 'The model %s is not available in the registry.' % model_name)

    @authenticate_token
    @http.route(['/sehati/appointment/create-hvd'], type='http', auth="none", methods=['POST'],
                csrf=False)
    def create_hvd_appointment(self, **post):
        date_format = "%Y-%m-%d"  # %H:%M:%S
        model_name = 'sm.shifa.hvd.appointment'
        model = request.env[self._model].sudo().search([('model', '=', model_name)], limit=1)

        patient_id = post.get('patient_id')
        doctor_id = post.get('doctor_id')
        app_version = post.get('app_version')
        appointment_date = post.get('appointment_date')
        appointment_time_str = post.get('appointment_time')
        branch = post.get('branch')
        if not branch:
            branch = ''
        if not patient_id:
            return invalid_response('patient_id not found', 'Patient ID not found in request!')
        if not doctor_id:
            return invalid_response('doctor_id not found', 'Doctor ID not found in request!')
        if not app_version:
            return invalid_response('app_version not found',
                                    'Please update to the latest version of this app to complete this service, thank you.')
        if not appointment_date:
            return invalid_response('appointment_date not found', 'Appointment date not found in request!')
        if not appointment_time_str:
            return invalid_response('appointment_time_str not found', 'Appointment time not found in request!')

        if model:
            try:
                values = {}
                values['name'] = request.env.ref('smartmind_shifa.sequence_hvd_appointment').next_by_id()
                appointment_time = self.convert_timeslot_to_time(appointment_time_str)

                patient = False
                count_patient = request.env['oeh.medical.patient'].sudo().search_count(
                    [('id', '=', int(patient_id))])
                if count_patient > 0:
                    patient = request.env['oeh.medical.patient'].sudo().browse(int(patient_id))
                    values['patient'] = patient.id
                else:
                    return invalid_response('invalid patient_id', 'Invalid Patient ID ! ')

                doctor = False
                count_doctor = request.env['oeh.medical.physician'].sudo().search_count([('id', '=', int(doctor_id))])
                if count_doctor > 0:
                    doctor = request.env['oeh.medical.physician'].sudo().browse(int(doctor_id))
                    values['doctor'] = doctor.id
                    values['total_service_price'] = doctor.hv_price
                else:
                    return invalid_response('invalid doctor_id', 'Invalid Doctor ID ! ')

                appointment_date_only = datetime.strptime(appointment_date, date_format)
                appointment_date = self.get_appointment_date_time(appointment_date_only, appointment_time)
                appointment_end = self.get_appointment_end(appointment_date_only, doctor_id, appointment_date)

                file1 = get_file_name(post.get('attached_file'), 'attached_file')
                file2 = get_file_name(post.get('attached_file_2'), 'attached_file_2')
                filename = "{0}, {1}".format(file1, file2)
                # upload files from request
                values['attached_file'] = upload_attached_file(post.get('attached_file'), 'attached_file')
                values['attached_file_2'] = upload_attached_file(post.get('attached_file_2'),
                                                                 'attached_file_2')
                values['patient_comment'] = post.get('patient_comment')
                payment_type = post.get('payment_type')
                values['state'] = 'Scheduled'
                values['location'] = post.get('location')
                values['payment_made_through'] = 'mobile'
                if 'patient_status' in post and post.get('patient_status') in ['Ambulatory', 'Outpatient',
                                                                               'Inpatient']:
                    values['patient_status'] = post.get('patient_status')

                if 'urgency_level' in post and post.get('urgency_level') in ['Normal', 'Urgent',
                                                                             'Medical Emergency']:
                    values['urgency_level'] = post.get('urgency_level')

                values['timeslot'] = self.get_timeslot_id(doctor_id, appointment_date, appointment_time_str)
                values['appointment_time'] = appointment_time
                values['appointment_date_only'] = appointment_date_only
                values['appointment_date'] = appointment_date
                values['appointment_end'] = appointment_end
                values['branch'] = branch
                # ----------------------------------------------------------------------------------------------
                if payment_type == 'pay':
                    values['payment_type'] = 'Payment Process'
                else:
                    values['payment_type'] = 'Insurance'

                appointment = request.env[model_name].sudo().create(values)
                appointment_id = appointment.id

                data = {
                    'id': appointment_id,
                    'upload file name': filename,
                    'appointment_date': str(appointment_date),
                    'appointment_time': str(appointment_time),
                    'appointment_end': str(appointment_end),
                    'message': 'Appointment created successfully!',
                }
                self._add_service_request(
                    patient_id, False, appointment_date, appointment.name,
                    post.get('location'),
                    post.get('attached_file'),
                    post.get('attached_file_2'),
                    post.get('attached_file_3')
                )
                return valid_response(data)

            except Exception as e:
                return invalid_response('failed to add appointment', str(e))
        return invalid_response('invalid object model', 'The model %s is not available in the registry.' % model_name)

    @authenticate_token
    @http.route(['/sehati/appointment/check-discount'], type='http', auth="none", methods=['POST'], csrf=False)
    def check_discount(self, **post):
        model_name = 'sm.shifa.discounts'
        model = request.env[self._model].sudo().search([('model', '=', model_name)], limit=1)
        code = post.get('code')
        type = post.get('type')
        try:
            if not code:
                return invalid_response('code not found', 'code is not found in request ! ')
            if not type:
                return invalid_response('type not found', 'type not found in request ! ')
            if model:
                if type == 'hhc':
                    value = True
                elif type == 'hvd':
                    value = True
                elif type == 'physiotherapy':
                    value = True
                elif type == 'tele':
                    value = True
                elif type == 'sleep':
                    value = True
                elif type == 'caregiver':
                    value = True
                else:
                    return invalid_response('type is not valid', 'type is invalid ')
                discount = request.env[model_name].sudo().search([('customer_code', '=', code), (type, '=', value)])
                if discount:
                    if discount.state == 'Active':
                        data = {
                            'id': discount.id,
                            'message': "Validation Code",
                            'percent': discount.fixed_type
                        }
                        return valid_response(data)

                    if discount.state == 'Expired':
                        invalid_response("The Code is Expired", "The Code is Expired")
                    if discount.state == 'Draft':
                        invalid_response("The Code is Not Valid", "The Code is Not Valid")
                else:
                    invalid_response("The Code is Not Valid", "The Code is Not Valid")

        except Exception as e:
            #print(e)
            return invalid_response('failed to send contact us', e)
        return invalid_response('invalid object model', 'The model %s is not available in the registry.' % model_name)

    @authenticate_token
    @http.route(['/sehati/appointment/create-hhc'], type='http', auth="none", methods=['POST'], csrf=False)
    def create_hhc_appointment(self, **post):
        model_name = 'sm.shifa.hhc.appointment'
        model = request.env[self._model].sudo().search([('model', '=', model_name)], limit=1)
        appointment_id = False
        invoice_id = False
        filename = False
        patient_id = post.get('patient_id')
        service_id = post.get('service_id')
        appointment_date = post.get('appointment_date')
        period = post.get('period')
        apt_type = post.get('type')
        service_2_id = post.get('service_2_id')
        service_3_id = post.get('service_3_id')
        discount_id = post.get('discount_id')
        branch = post.get('branch')
        if not branch:
            branch = ''
        if not discount_id:
            discount_id = False
        if not patient_id:
            return invalid_response('patient_id not found', 'Patient ID not found in request ! ')
        if not service_id:
            return invalid_response('service_id not found', 'Service ID not found in request ! ')
        if not appointment_date:
            return invalid_response('appointment_date not found', 'Appointment date not found in request ! ')
        if not period:
            return invalid_response('period not found', 'Period not found in request ! ')
        if not apt_type:
            return invalid_response('type not found', 'Type not found in request ! ')
        if not 'app_version' in post:
            return invalid_response('app_version not found',
                                    'Please update to the latest version of this app to complete this service, thank you.')

        if model:
            try:
                values = {}
                sequence = request.env.ref('smartmind_shifa.sequence_hhc_appointment').next_by_id()
                values['name'] = sequence
                patient = False
                patient_model = 'oeh.medical.patient'
                count_patient = request.env[patient_model].sudo().search_count(
                    [('id', '=', int(patient_id))])
                if count_patient > 0:
                    patient = request.env[patient_model].sudo().browse(int(patient_id))
                    values['patient'] = patient.id
                else:
                    return invalid_response('invalid patient_id', 'Invalid Patient ID ! ')

                count_service = self._is_service_found(service_id)
                if count_service:
                    service = request.env['sm.shifa.service'].sudo().browse(int(service_id))
                    values['service'] = service.id
                    values['service_price'] = service.list_price
                else:
                    return invalid_response('invalid service_id', 'Invalid Service ID ! ')

                if service_2_id:
                    count_service_2 = self._is_service_found(service_2_id)
                    if count_service_2:
                        service = request.env['sm.shifa.service'].sudo().browse(int(service_2_id))
                        values['service_2'] = service.id
                        values['service_2_price'] = service.list_price
                    else:
                        return invalid_response('invalid service_id', 'Invalid Service 2 ID ! ')

                if service_3_id:
                    count_service_3 = self._is_service_found(service_3_id)
                    if count_service_3:
                        service = request.env['sm.shifa.service'].sudo().browse(int(service_3_id))
                        values['service_3'] = service.id
                        values['service_3_price'] = service.list_price
                    else:
                        return invalid_response('invalid service_id', 'Invalid Service 3 ID ! ')

                instance = request.env['sm.shifa.instant.consultancy.charge'].search([('code', '=', 'HVF')], limit=1)
                # values['home_visit_fee'] = instance.charge
                # get available services for current period in this date
                team = request.env['sm.shifa.team.period'].sudo().search(
                    [('date', '=', appointment_date), ('period', '=', period), ('type', '=', apt_type)], limit=1)

                if team:
                    if team.available > 0:
                        # get files name
                        file1 = self._get_file_name(post.get('attached_file'), 'attached_file')
                        file2 = self._get_file_name(post.get('attached_file_2'), 'attached_file_2')
                        # file3 = self._get_file_name(post.get('attached_file_3'), 'attached_file_3')
                        filename = "{0}, {1}".format(file1, file2)
                        # upload files from request
                        values['attached_file'] = self._upload_attached_file(post.get('attached_file'), 'attached_file')
                        values['attached_file_2'] = self._upload_attached_file(post.get('attached_file_2'),
                                                                               'attached_file_2')
                        home_obj = request.env['sm.shifa.miscellaneous.charge.service'].sudo().search(
                            [('code', '=', 'HHC-HVF')], limit=1)
                        values['miscellaneous_price'] = home_obj.list_price
                        values['patient_comment'] = post.get('patient_comment')
                        values['period'] = period
                        values['type'] = apt_type
                        payment_type = post.get('payment_type')
                        values['payment_type'] = payment_type
                        values['location'] = post.get('location')
                        values['appointment_date_only'] = appointment_date
                        values['state'] = 'scheduled'
                        values['service_type_choice'] = 'main'
                        values['payment_made_through'] = 'mobile'
                        values['available_appointment'] = team.available
                        values['branch'] = branch
                        values['discount_name'] = int(discount_id)
                        if payment_type == 'pay':
                            values['payment_type'] = 'Payment Process'
                        else:
                            values['payment_type'] = 'Insurance'

                        appointment = request.env[model_name].sudo().create(values)
                        appointment_id = appointment.id
                        data = {
                            'id': appointment_id,
                            'upload file name': filename,
                            'message': 'Appointment created successfully!'
                        }
                        self._add_service_request(
                            patient_id, service_id, appointment_date, appointment.name,
                            post.get('location'),
                            post.get('attached_file'),
                            post.get('attached_file_2'),
                            post.get('attached_file_3')
                        )
                        return valid_response(data)
                    else:
                        return invalid_response('booking full',
                                                '%s period is full or not determined yet, please book appointment in another period.' % period)
                else:
                    return invalid_response('no period',
                                            'No period is determined for selected date, please try another date!')

            except Exception as e:
                return invalid_response('failed to add appointment', str(e))
        return invalid_response('invalid object model', 'The model %s is not available in the registry.' % model_name)

    @authenticate_token
    @http.route(['/sehati/appointment/create-physiotherapy'], type='http', auth="none", methods=['POST'], csrf=False)
    def create_physiotherapy_appointment(self, **post):
        date_format = "%Y-%m-%d"
        model_name = 'sm.shifa.physiotherapy.appointment'
        model = request.env[self._model].sudo().search([('model', '=', model_name)], limit=1)
        appointment_id = False
        invoice_id = False
        filename = False
        patient_id = post.get('patient_id')
        service_id = post.get('service_id')
        appointment_date = post.get('appointment_date')
        period = post.get('period')
        gender = post.get('gender')
        discount_id = post.get('discount_id')
        branch = post.get('branch')
        if not branch:
            branch = ''
        if not discount_id:
            discount_id = False

        if not patient_id:
            return invalid_response('patient_id not found', 'Patient ID not found in request ! ')
        if not service_id:
            return invalid_response('service_id not found', 'Service ID not found in request ! ')
        if not appointment_date:
            return invalid_response('appointment_date not found', 'Appointment date not found in request ! ')
        if not period:
            return invalid_response('period not found', 'Period not found in request ! ')
        if not gender:
            return invalid_response('gender not found', 'Gender not found in request ! ')
        if not 'app_version' in post:
            return invalid_response('app_version not found',
                                    'Please update to the latest version of this app to complete this service, thank you.')

        if model:
            try:
                values = {}
                values['name'] = request.env.ref('smartmind_shifa.sequence_hhc_physiotherapy').next_by_id()
                appointment_date = datetime.strptime(appointment_date, date_format)
                patient = False
                patient_model = 'oeh.medical.patient'
                count_patient = request.env[patient_model].sudo().search_count(
                    [('id', '=', int(patient_id))])
                if count_patient > 0:
                    patient = request.env[patient_model].sudo().browse(int(patient_id))
                    values['patient'] = patient.id
                else:
                    return invalid_response('invalid patient_id', 'Invalid Patient ID !')

                service = False
                count_service = request.env['sm.shifa.service'].sudo().search_count([('id', '=', int(service_id))])
                if count_service > 0:
                    service = request.env['sm.shifa.service'].sudo().browse(int(service_id))
                    values['service'] = service.id
                    values['service_price'] = service.list_price
                else:
                    return invalid_response('invalid doctor_id', 'Invalid Service ID ! ')

                instance = request.env['sm.shifa.instant.consultancy.charge'].search([('code', '=', 'HVF')], limit=1)
                # values['home_visit_fee'] = instance.charge
                appointment_date = post.get('appointment_date')
                # get total of service for current period in this date
                team = request.env['sm.shifa.team.period.physiotherapy'].sudo().search(
                    [('date', '=', appointment_date), ('period', '=', period), ('gender', '=', gender)], limit=1)
                if team:
                    if team.available > 0:
                        # get files name
                        file1 = self._get_file_name(post.get('attached_file'), 'attached_file')
                        file2 = self._get_file_name(post.get('attached_file_2'), 'attached_file_2')
                        # file3 = self._get_file_name(post.get('attached_file_3'), 'attached_file_3')
                        filename = "{0}, {1}".format(file1, file2)
                        # upload files from request
                        values['attached_file'] = self._upload_attached_file(post.get('attached_file'), 'attached_file')
                        values['attached_file_2'] = self._upload_attached_file(post.get('attached_file_2'),
                                                                                'attached_file_2')
                        values['patient_comment'] = post.get('patient_comment')
                        values['period'] = period
                        payment_type = post.get('payment_type')
                        values['payment_type'] = payment_type
                        values['location'] = post.get('location')
                        values['appointment_date_only'] = appointment_date
                        values['gender'] = gender
                        values['state'] = 'scheduled'
                        values['service_type_choice'] = 'main'
                        values['payment_made_through'] = 'mobile'
                        values['available_appointment'] = team.available
                        values['discount_name'] = int(discount_id)
                        values['branch'] = branch
                        # values['timeslot'] = self.get_timeslot_id(doctor_id, appointment_date, appointment_time_str)
                        # values['appointment_time'] = appointment_time
                        # values['appointment_date'] = appointment_date
                        # values['appointment_end'] = appointment_end
                        home_obj = request.env['sm.shifa.miscellaneous.charge.service'].sudo().search(
                            [('code', '=', 'PHY-HVF')], limit=1)
                        values['miscellaneous_price'] = home_obj.list_price
                        if payment_type == 'pay':
                            values['payment_type'] = 'Payment Process'
                        else:
                            values['payment_type'] = 'Insurance'

                        appointment = request.env[model_name].sudo().create(values)
                        appointment_id = appointment.id
                        data = {
                            'id': appointment_id,
                            'upload file name': filename,
                            'appointment_date': str(appointment_date),
                            # 'appointment_time': str(appointment_time),
                            # 'appointment_end': str(appointment_end),
                            'message': 'Appointment created successfully!'
                        }
                        self._add_service_request(
                            patient_id, service_id, appointment_date, appointment.name,
                            post.get('location'),
                            post.get('attached_file'),
                            post.get('attached_file_2'),
                            post.get('attached_file_3')
                        )
                        return valid_response(data)
                    else:
                        return invalid_response('booking full',
                                                '%s period is full or not determined yet, please book appointment in another period.' % period)
                else:
                    return invalid_response('no period',
                                            'No period is determined for selected date, please try another date!')

            except Exception as e:
                print(e)
                return invalid_response('failed to add appointment', str(e))
        return invalid_response('invalid object model', 'The model %s is not available in the registry.' % model_name)

    @authenticate_token
    @http.route(['/sehati/appointment/create-pcr'], type='http', auth="none", methods=['POST'], csrf=False)
    def create_pcr_appointment(self, **post):
        model_name = 'sm.shifa.pcr.appointment'
        model = request.env[self._model].sudo().search([('model', '=', model_name)], limit=1)
        appointment_id = False
        invoice_id = False
        filename = False
        patient_id = post.get('patient_id')
        service_id = post.get('service_id')
        appointment_date = post.get('appointment_date')
        hour = post.get('hour')
        patient_followers = post.get('patient_followers')
        app_version = post.get('app_version')

        if not patient_id:
            return invalid_response('patient_id not found', 'Patient ID not found in request ! ')
        if not service_id:
            return invalid_response('service_id not found', 'Service ID not found in request ! ')
        if not appointment_date:
            return invalid_response('appointment_date not found', 'Appointment date not found in request ! ')
        if not hour:
            return invalid_response('hour not found', 'Hour not found in request ! ')
        if not patient_followers:
            return invalid_response('patient_followers not found', 'Patient followers not found in request ! ')
        if not app_version:
            return invalid_response('app_version not found',
                                    'Please update to the latest version of this app to complete this service, thank you.')

        if model:
            try:
                values = {}
                patient_id = post.get('patient_id')
                service_id = post.get('service_id')
                hour = post.get('hour')
                patient = False
                patient_model = 'oeh.medical.patient'
                count_patient = request.env[patient_model].sudo().search_count(
                    [('id', '=', int(patient_id))])
                if count_patient > 0:
                    patient = request.env[patient_model].sudo().browse(int(patient_id))
                    values['patient'] = patient.id
                else:
                    return invalid_response('invalid patient_id', 'Invalid Patient ID ! ')

                # check if service found in db or throw error not found
                service = False
                count_service = request.env['sm.shifa.service'].sudo().search_count([('id', '=', int(service_id))])
                if count_service > 0:
                    service = request.env['sm.shifa.service'].sudo().browse(int(service_id))
                    values['service'] = service.id
                else:
                    return invalid_response('invalid doctor_id', 'Invalid Service ID ! ')

                instance = request.env['sm.shifa.instant.consultancy.charge'].search([('code', '=', 'HVF')], limit=1)
                values['home_visit_fee'] = instance.charge
                appointment_date = post.get('appointment_date')
                # get available services for current period in this date
                team = request.env['sm.shifa.team.period.pcr'].sudo().search(
                    [('date', '=', appointment_date), ('hour', '=', hour)], limit=1)
                # print(team)
                if team:
                    if team.available > 0:
                        # get files name
                        file1 = self._get_file_name(post.get('attached_file'), 'attached_file')
                        file2 = self._get_file_name(post.get('attached_file_2'), 'attached_file_2')
                        # file3 = self._get_file_name(post.get('attached_file_3'), 'attached_file_3')
                        filename = "{0}, {1}".format(file1, file2)
                        # upload files from request
                        values['attached_file'] = self._upload_attached_file(post.get('attached_file'), 'attached_file')
                        values['attached_file_2'] = self._upload_attached_file(post.get('attached_file_2'),
                                                                               'attached_file_2')
                        # values['attached_file_3'] = self._upload_attached_file(post.get('attached_file_3'), 'attached_file_3')
                        values['patient_comment'] = post.get('patient_comment')
                        values['appointment_time'] = float(hour)
                        payment_type = post.get('payment_type')
                        values['payment_type'] = payment_type
                        values['location'] = post.get('location')
                        values['appointment_date_only'] = appointment_date
                        values['payment_made_through'] = 'mobile'
                        values['state'] = 'scheduled'
                        if payment_type == 'pay':
                            values['payment_type'] = 'Payment Process'
                        else:
                            values['payment_type'] = 'Insurance'

                        values['patient_followers'] = post.get('patient_followers')
                        appointment = request.env[model_name].sudo().create(values)
                        appointment_id = appointment.id
                        data = {
                            'id': appointment_id,
                            'upload file name': filename,
                            # 'created invoice id': invoice_id,
                            'message': 'Appointment created successfully!'
                        }
                        self._add_service_request(
                            patient_id, service_id, appointment_date, appointment.name,
                            post.get('location'),
                            post.get('attached_file'),
                            post.get('attached_file_2'),
                            post.get('attached_file_3')
                        )
                        return valid_response(data)
                    else:
                        return invalid_response('booking full',
                                                '[%s] hour is full or not determined yet, please book appointment in another hour.' % hour)
                else:
                    return invalid_response('no hour',
                                            'No hour is determined for selected date, please try another date!')

            except Exception as e:
                #print(e)
                return invalid_response('failed to add appointment', str(e))
        return invalid_response('invalid object model', 'The model %s is not available in the registry.' % model_name)

    @authenticate_token
    @http.route(['/sehati/create-caregiver'], type='http', auth="none", methods=['POST'], csrf=False)
    def create_caregiver(self, **post):
        model_name = 'sm.shifa.hhc.appointment'
        model = request.env[self._model].sudo().search([('model', '=', model_name)], limit=1)
        if model:
            try:
                if not 'patient_id' in post:
                    return invalid_response('patient_id not found', 'Patient ID not found in request ! ')
                if not 'service_id' in post:
                    return invalid_response('service_id not found', 'Service ID not found in request ! ')
                if not 'period' in post:
                    return invalid_response('period not found', 'Period not found in request ! ')

                values = {}
                patient_id = post.get('patient_id')
                service_id = post.get('service_id')
                period = post.get('period')

                patient = False
                patient_model = 'oeh.medical.patient'
                count_patient = request.env[patient_model].sudo().search_count(
                    [('id', '=', int(patient_id))])
                if count_patient > 0:
                    patient = request.env[patient_model].sudo().browse(int(patient_id))
                    values['patient'] = patient.id
                else:
                    return invalid_response('invalid patient_id', 'Invalid Patient ID ! ')

                count_service = self._is_service_found(service_id)
                if count_service > 0:
                    values['service'] = service_id
                else:
                    return invalid_response('invalid service_id', 'Invalid Service ID ! ')

                # get files name
                file1 = self._get_file_name(post.get('attached_file'), 'attached_file')
                file2 = self._get_file_name(post.get('attached_file_2'), 'attached_file_2')
                file3 = self._get_file_name(post.get('attached_file_3'), 'attached_file_3')
                filename = "{0}, {1}, {2}".format(file1, file2, file3)
                # upload files from request
                values['attached_file'] = self._upload_attached_file(post.get('attached_file'), 'attached_file')
                values['attached_file_2'] = self._upload_attached_file(post.get('attached_file_2'),
                                                                       'attached_file_2')
                values['attached_file_3'] = self._upload_attached_file(post.get('attached_file_3'),
                                                                       'attached_file_3')
                today = datetime.now()
                today_date = today.strftime('%Y-%m-%d')
                values['appointment_date_only'] = today_date

                values['period'] = period
                values['type'] = 'N'
                # payment_type = post.get('payment_type')
                # values['payment_type'] = payment_type
                values['location'] = post.get('location')
                values['state'] = 'scheduled'

                appointment = request.env[model_name].sudo().create(values)
                appointment_id = appointment.id
                data = {
                    'id': appointment_id,
                    'upload file name': filename,
                    'message': 'Appointment created successfully!'
                }
                return valid_response(data)

            except Exception as e:
                return invalid_response('failed to add appointment', str(e))

    @authenticate_token
    @http.route(['/sehati/appointment/request-cancellation-appointment'], type='http', auth="none", methods=['POST'],
                csrf=False)
    def request_cancellation_confirmed_appointment(self, **post):
        model_name = 'sm.shifa.cancellation.refund'

        if not 'patient_id' in post:
            return invalid_response('patient_id not found', 'patient id not found in request ! ')

        if not 'appointment_id' in post:
            return invalid_response('appointment_id not found', 'appointment id not found in request ! ')

        if not 'type' in post:
            return invalid_response('type not found', 'type not found in request ! ')

        try:
            patient_id = post.get('patient_id')
            appointment_id = post.get('appointment_id')
            apt_type = post.get('type')
            reason = post.get('reason')

            appointment_model_name = False
            appointment_field_name = False
            count_apt_patient = False
            domain_state = False
            if apt_type == 'tele':
                appointment_field_name = 'appointment'
                appointment_model_name = 'oeh.medical.appointment'
                domain_state = [('state', 'in', ['scheduled', 'confirmed'])]
            elif apt_type == 'hvd':
                appointment_field_name = 'hvd_appointment'
                appointment_model_name = 'sm.shifa.hvd.appointment'
                domain_state = [('state', 'in', ['Scheduled', 'Confirmed'])]
            elif apt_type == 'hhc':
                appointment_field_name = 'hhc_appointment'
                appointment_model_name = 'sm.shifa.hhc.appointment'
                domain_state = [
                    ('state', 'in', ['scheduled', 'head_doctor', 'head_nurse', 'operation_manager', 'team'])]
            elif apt_type == 'phy':
                appointment_field_name = 'phy_appointment'
                appointment_model_name = 'sm.shifa.physiotherapy.appointment'
                domain_state = [
                    ('state', 'in', ['scheduled', 'head_doctor', 'head_nurse', 'operation_manager', 'team'])]
            elif apt_type == 'pcr':
                appointment_field_name = 'pcr_appointment'
                appointment_model_name = 'sm.shifa.pcr.appointment'
                domain_state = [('state', 'in', ['scheduled', 'operation_manager', 'team'])]

            domain = [('id', '=', int(appointment_id)), ('patient.id', '=', int(patient_id))]
            count_apt_patient = request.env[appointment_model_name].sudo().search_count(domain)
            if count_apt_patient > 0:
                can_cancel_count = request.env[appointment_model_name].sudo().search_count(domain_state)
                if can_cancel_count:
                    appointment_obj = request.env[appointment_model_name].sudo().browse(int(appointment_id))
                    appointment_obj.write({
                        'state': 'requestCancellation',
                        'cancellation_requested': True,
                    })
                    # make if cond.
                    refund_obj = request.env[model_name].sudo().search([(appointment_field_name, '=', int(appointment_id)), ('patient.id', '=', int(patient_id))], limit = 1)
                    # if flag = true show msg with flag val
                    if refund_obj.cancellation_requested:
                        data = {
                            'id': refund_obj.id,
                            'cancellation_requested': refund_obj.cancellation_requested,
                            'message': "You've already requested to cancel this appointment.",
                        }
                    else:
                        model = request.env[model_name].sudo().create({
                            'patient': patient_id,
                            appointment_field_name: appointment_id,
                            'state': 'received',
                            'type': appointment_field_name,
                            'reason': reason,
                            'cancellation_requested': True,
                        })
                        data = {
                            'id': model.id,
                            'appointment status': 'requestCancellation',
                            'cancellation_requested': model.cancellation_requested,
                            'message': 'Your appointment has been set to be requested cancellation.',
                        }
                    return valid_response(data)
                else:
                    return invalid_response('not_allowed',
                                            'Sorry! you cannot cancel this appointment, its in progress or in start state')
            else:
                return invalid_response('invalid data',
                                        'Sorry! either this appointment id is not belong to this patient id or there is no appointment for this patient id')
        except Exception as e:
            return invalid_response('error', e)

    @authenticate_token
    @http.route(['/sehati/get-appointment/<user_type>/<user_id>'], type='http', auth="none", methods=['GET'],
                csrf=False)
    def get_appointment(self, user_type=None, user_id=None, **payload):
        """This method will allow list all the appointments for given user id and type

        Args:
            token: must contain in headers to validate the call
            <user_type> must contain user's type [1: Patient, 2: Physician]
            <user_id> Logged in User ID
        Returns:
            - Data dictionary containing list of appointments for given in user type and id.
            - Returns if failed error message in the body in json format
        """
        if not user_type:
            return invalid_response('user_type not found', 'User type not found in request ! ')

        if not user_id:
            return invalid_response('user_id not found', 'User ID not found in request ! ')

        model_name = 'oeh.medical.appointment'
        model = request.env[self._model].sudo().search([('model', '=', model_name)], limit=1)
        payload[
            'fields'] = "['id', 'name', 'patient', 'doctor', 'appointment_date', 'appointment_time', 'urgency_level', 'jitsi_link', 'comments', 'patient_status', 'state',  'cancellation_requested', 'deduction_amount']"

        if user_type == '1':
            payload['domain'] = "[('patient', '=', " + str(user_id) + ")]"
        elif user_type == '2':
            payload['domain'] = "[('doctor', '=', " + str(user_id) + ")]"

        payload['order'] = 'appointment_date desc'

        if model:
            domain, fields, offset, limit, order = extract_arguments(
                payload)
            data = request.env[model.model].sudo().search_read(
                domain=domain, fields=fields, offset=offset, limit=limit, order=order)

            data_to_push = []
            for x in data:
                for k, v in x.items():
                    if str(type(v)) in ("<class 'datetime.datetime'>", "<class 'datetime.date'>"):
                        date = convert_utc_to_local(v.strftime("%Y-%m-%d %H:%M:%S"))
                        x[k] = str(date)
                    if str(k) == "comments":
                        if v and len(v) > 0:
                            x[k] = v[1]
                        else:
                            x[k] = ""
                    if str(k) == "patient":
                        if v and len(v) > 0:
                            x[k] = v[1]
                        else:
                            x[k] = ""
                    if str(k) == "doctor":
                        if v and len(v) > 0:
                            x[k] = v[1]
                        else:
                            x[k] = ""
                data_to_push.append(x)

            return valid_response(data_to_push)
        return invalid_response('invalid object model', 'The model %s is not available in the registry.' % model_name)

    @authenticate_token
    @http.route(['/sehati/get-hvd-appointment/<user_type>/<user_id>'], type='http', auth="none", methods=['GET'],
                csrf=False)
    def get_hvd_appointment(self, user_type=None, user_id=None, **payload):
        """This method will allow list all the appointments for given user id and type

        Args:
            token: must contain in headers to validate the call
            <user_type> must contain user's type [1: Patient, 2: Physician]
            <user_id> Logged in User ID
        Returns:
            - Data dictionary containing list of appointments for given in user type and id.
            - Returns if failed error message in the body in json format
        """
        if not user_type:
            return invalid_response('user_type not found', 'User type not found in request ! ')

        if not user_id:
            return invalid_response('user_id not found', 'User ID not found in request ! ')

        model_name = 'sm.shifa.hvd.appointment'
        model = request.env[self._model].sudo().search([('model', '=', model_name)], limit=1)
        payload[
            'fields'] = "['id', 'name', 'patient', 'doctor', 'appointment_date', 'appointment_time', 'urgency_level', 'comments', 'patient_status', 'state',  'cancellation_requested','deduction_amount']"

        if user_type == '1':
            payload['domain'] = "[('patient', '=', " + str(user_id) + ")]"
        elif user_type == '2':
            payload['domain'] = "[('doctor', '=', " + str(user_id) + ")]"

        payload['order'] = 'appointment_date desc'

        if model:
            domain, fields, offset, limit, order = extract_arguments(
                payload)
            data = request.env[model.model].sudo().search_read(
                domain=domain, fields=fields, offset=offset, limit=limit, order=order)

            data_to_push = []
            for x in data:
                for k, v in x.items():
                    if str(type(v)) in ("<class 'datetime.datetime'>", "<class 'datetime.date'>"):
                        date = convert_utc_to_local(v.strftime("%Y-%m-%d %H:%M:%S"))
                        x[k] = str(date)
                    if str(k) == "comments":
                        if v and len(v) > 0:
                            x[k] = v[1]
                        else:
                            x[k] = ""
                    if str(k) == "patient":
                        if v and len(v) > 0:
                            x[k] = v[1]
                        else:
                            x[k] = ""
                    if str(k) == "doctor":
                        if v and len(v) > 0:
                            x[k] = v[1]
                        else:
                            x[k] = ""
                data_to_push.append(x)

            return valid_response(data_to_push)
        return invalid_response('invalid object model', 'The model %s is not available in the registry.' % model_name)

    @authenticate_token
    @http.route(['/sehati/get-hhc-appointment/<user_type>/<user_id>'], type='http', auth="none", methods=['GET'],
                csrf=False)
    def get_hhc_appointment(self, user_type=None, user_id=None, **payload):
        """This method will allow list all the appointments for given user id and type

        Args:
            token: must contain in headers to validate the call
            <user_type> must contain user's type [1: Patient, 2: Physician]
            <user_id> Logged in User ID
        Returns:
            - Data dictionary containing list of appointments for given in user type and id.
            - Returns if failed error message in the body in json format
        """
        if not user_type:
            return invalid_response('user_type not found', 'User type not found in request ! ')

        if not user_id:
            return invalid_response('user_id not found', 'User ID not found in request ! ')

        model_name = 'sm.shifa.hhc.appointment'
        model = request.env[self._model].sudo().search([('model', '=', model_name)], limit=1)
        payload[
            'fields'] = "['id', 'name', 'patient', 'doctor', 'appointment_date', 'appointment_time', 'service', 'service_2', 'service_3', 'type', 'comments', 'period', 'payment_type', 'payment_reference', 'treatment_comment', 'state',  'cancellation_requested', 'deduction_amount']"

        if user_type == '1':
            payload['domain'] = "[('patient', '=', " + str(user_id) + ")]"
        elif user_type == '2':
            payload['domain'] = "[('doctor', '=', " + str(user_id) + ")]"

        payload['order'] = 'appointment_date desc'

        if model:
            domain, fields, offset, limit, order = extract_arguments(
                payload)
            data = request.env[model.model].sudo().search_read(
                domain=domain, fields=fields, offset=offset, limit=limit, order=order)

            data_to_push = []
            for x in data:
                for k, v in x.items():
                    if str(type(v)) in ("<class 'datetime.datetime'>", "<class 'datetime.date'>"):
                        date = v.strftime("%Y-%m-%d")  # %H:%M:%S
                        x[k] = str(date)
                    if str(k) == "comments":
                        if v and len(v) > 0:
                            x[k] = v[1]
                        else:
                            x[k] = ""
                    if str(k) == "patient":
                        if v and len(v) > 0:
                            x[k] = v[1]
                        else:
                            x[k] = ""
                    if str(k) == "doctor":
                        if v and len(v) > 0:
                            x[k] = v[1]
                        else:
                            x[k] = ""

                data_to_push.append(x)

            return valid_response(data_to_push)
        return invalid_response('invalid object model', 'The model %s is not available in the registry.' % model_name)

    @authenticate_token
    @http.route(['/sehati/get-pcr-appointment/<user_type>/<user_id>'], type='http', auth="none", methods=['GET'],
                csrf=False)
    def get_pcr_appointment(self, user_type=None, user_id=None, **payload):
        if not user_type:
            return invalid_response('user_type not found', 'User type not found in request ! ')

        if not user_id:
            return invalid_response('user_id not found', 'User ID not found in request ! ')

        model_name = 'sm.shifa.pcr.appointment'
        model = request.env[self._model].sudo().search([('model', '=', model_name)], limit=1)
        payload[
            'fields'] = "['id', 'name', 'patient', 'head_doctor', 'appointment_date', 'appointment_time', 'service', 'comments', 'payment_type', 'payment_reference', 'treatment_comment', 'state']"

        if user_type == '1':
            payload['domain'] = "[('patient', '=', " + str(user_id) + ")]"
        elif user_type == '2':
            payload['domain'] = "[('head_doctor', '=', " + str(user_id) + ")]"

        payload['order'] = 'appointment_date desc'

        if model:
            domain, fields, offset, limit, order = extract_arguments(
                payload)
            data = request.env[model.model].sudo().search_read(
                domain=domain, fields=fields, offset=offset, limit=limit, order=order)

            data_to_push = []
            for x in data:
                for k, v in x.items():
                    if str(type(v)) in ("<class 'datetime.datetime'>", "<class 'datetime.date'>"):
                        date = v.strftime("%Y-%m-%d")  # %H:%M:%S
                        x[k] = str(date)
                    if str(k) == "comments":
                        if v and len(v) > 0:
                            x[k] = v[1]
                        else:
                            x[k] = ""
                    if str(k) == "patient":
                        if v and len(v) > 0:
                            x[k] = v[1]
                        else:
                            x[k] = ""
                    if str(k) == "doctor":
                        if v and len(v) > 0:
                            x[k] = v[1]
                        else:
                            x[k] = ""
                data_to_push.append(x)

            return valid_response(data_to_push)
        return invalid_response('invalid object model', 'The model %s is not available in the registry.' % model_name)

    @authenticate_token
    @http.route(['/sehati/get-physiotherapy-appointment/<user_type>/<user_id>'], type='http', auth="none",
                methods=['GET'],
                csrf=False)
    def get_physiotherapy_appointment(self, user_type=None, user_id=None, **payload):
        if not user_type:
            return invalid_response('user_type not found', 'User type not found in request ! ')

        if not user_id:
            return invalid_response('user_id not found', 'User ID not found in request ! ')

        model_name = 'sm.shifa.physiotherapy.appointment'
        model = request.env[self._model].sudo().search([('model', '=', model_name)], limit=1)
        payload[
            'fields'] = "['id', 'name', 'gender', 'patient', 'appointment_date', 'appointment_time', 'service', 'comments', 'period', 'payment_type', 'payment_reference', 'state',  'cancellation_requested','deduction_amount']"

        if user_type == '1':
            payload['domain'] = "[('patient', '=', " + str(user_id) + ")]"
        elif user_type == '2':
            payload['domain'] = "[('doctor', '=', " + str(user_id) + ")]"

        payload['order'] = 'appointment_date desc'

        if model:
            domain, fields, offset, limit, order = extract_arguments(
                payload)
            data = request.env[model.model].sudo().search_read(
                domain=domain, fields=fields, offset=offset, limit=limit, order=order)

            data_to_push = []
            for x in data:
                for k, v in x.items():
                    if str(type(v)) in ("<class 'datetime.datetime'>", "<class 'datetime.date'>"):
                        date = v.strftime("%Y-%m-%d")  # %H:%M:%S
                        x[k] = str(date)
                    if str(k) == "comments":
                        if v and len(v) > 0:
                            x[k] = v[1]
                        else:
                            x[k] = ""
                    if str(k) == "patient":
                        if v and len(v) > 0:
                            x[k] = v[1]
                        else:
                            x[k] = ""
                    if str(k) == "doctor":
                        if v and len(v) > 0:
                            x[k] = v[1]
                        else:
                            x[k] = ""
                data_to_push.append(x)

            return valid_response(data_to_push)
        return invalid_response('invalid object model', 'The model %s is not available in the registry.' % model_name)

    @authenticate_token
    @http.route(['/sehati/appointment/count-all/<patient_id>'], type='http', auth="none", methods=['GET'], csrf=False)
    def get_appointment_count_all(self, patient_id=None):

        if not patient_id:
            return invalid_response('patient_id not found', 'Patient id not found in request ! ')

        tele_appointment = request.env['oeh.medical.appointment'].sudo().search_count(
            [('patient.id', '=', int(patient_id))])
        hvd_appointment = request.env['sm.shifa.hvd.appointment'].sudo().search_count(
            [('patient.id', '=', int(patient_id))])
        hhc_appointment = request.env['sm.shifa.hhc.appointment'].sudo().search_count(
            [('patient.id', '=', int(patient_id))])
        phys_appointment = request.env['sm.shifa.physiotherapy.appointment'].sudo().search_count(
            [('patient.id', '=', int(patient_id))])
        pcr_appointment = request.env['sm.shifa.pcr.appointment'].sudo().search_count(
            [('patient.id', '=', int(patient_id))])

        data = {
            'tele_appointment': tele_appointment,
            'hvd_appointment': hvd_appointment,
            'hhc_appointment': hhc_appointment,
            'phys_appointment': phys_appointment,
            'pcr_appointment': pcr_appointment,
        }
        return valid_response(data)

    @authenticate_token
    @http.route(['/sehati/appointment/get-home-visit-fee'], type='http', auth="none", methods=['GET'], csrf=False)
    def get_home_visit_fee(self):
        instant = request.env['sm.shifa.instant.consultancy.charge'].sudo().search([('code', '=', 'HHC-HVF')], limit=1)
        instant2 = request.env['sm.shifa.instant.consultancy.charge'].sudo().search([('code', '=', 'PHY-HVF')], limit=1)
        instant3 = request.env['sm.shifa.instant.consultancy.charge'].sudo().search([('code', '=', 'CTF')], limit=1)

        try:
            if instant:
                data = {
                    'home_visit_fee': str(instant.charge),
                    'home_visit_fee_phy': str(instant2.charge),
                    'home_visit_fee_caregiver': str(instant3.charge),
                }
                return valid_response(data)
            else:
                return invalid_response('No data to show')

        except Exception as e:
            #print(e)
            return invalid_response('error', e)
        return invalid_response('invalid object model', 'The model %s is not available in the registry.' % model_name)

    @authenticate_token
    @http.route(['/sehati/appointment/set-payment-status'], type='http', auth="none", methods=['POST'], csrf=False)
    def set_payment_status(self, **post):
        appointment_type = post.get('appointment_type')
        appointment_id = post.get('appointment_id')
        payment_reference = post.get('payment_reference')
        deduction_amount = post.get('consultancy_price')
        payment_method_name = post.get('payment_method_name')
        if not payment_method_name:
            payment_method_name = " "
        if not appointment_type:
            return invalid_response('appointment_type not found')
        if not appointment_id:
            return invalid_response('appointment_id not found')
        if not payment_reference:
            return invalid_response('payment_reference not found')
        if not deduction_amount:
            return invalid_response('deduction_amount_not_found')

        appointment_type = post.get('appointment_type')
        appointment_id = post.get('appointment_id')
        payment_reference = post.get('payment_reference')

        try:
            model_name = False
            state_val = False
            if appointment_type == 'hhc':  # HHC Appointment tele, hvd
                model_name = 'sm.shifa.hhc.appointment'
                state_val = 'head_doctor'
                if int(payment_reference) < 0:
                    state_val = 'canceled'
            elif appointment_type == 'phy':  # PHY Appointment
                model_name = 'sm.shifa.physiotherapy.appointment'
                state_val = 'head_physiotherapist'
                if int(payment_reference) < 0:
                    state_val = 'canceled'
            elif appointment_type == 'pcr':  # PCR Appointment
                model_name = 'sm.shifa.pcr.appointment'
                state_val = 'operation_manager'
                if int(payment_reference) < 0:
                    state_val = 'canceled'
            elif appointment_type == 'tele':  # PCR Appointment
                model_name = 'oeh.medical.appointment'
                state_val = 'Confirmed'
                if int(payment_reference) < 0:
                    state_val = 'canceled'
            elif appointment_type == 'hvd':  # HVD Appointment
                model_name = 'sm.shifa.hvd.appointment'
                state_val = 'Confirmed'
                if int(payment_reference) < 0:
                    state_val = 'canceled'
            elif appointment_type == 'sleep':  # Sleep Medicine Request
                model_name = 'sm.sleep.medicine.request'
                state_val = 'paid'
                if int(payment_reference) < 0:
                    state_val = 'cancel'
            elif appointment_type == 'caregiver':  # Caregiver Contracts
                model_name = 'sm.caregiver.contracts'
                state_val = 'paid'
                if int(payment_reference) < 0:
                    state_val = 'cancel'

            ref = int(payment_reference)
            appointment_obj = request.env[model_name]
            
            count = appointment_obj.sudo().search_count([('id', '=', int(appointment_id))])
            if count > 0:
                patient_id = False
                details = False
                apt_date = False
                if ref > 0:
                    if appointment_type == 'hhc' or appointment_type == 'phy' or appointment_type == 'pcr':                        
                        appointment = appointment_obj.sudo().search([('id', '=', int(appointment_id))], limit=1)
                        patient_id = appointment.patient.id
                        apt_date = appointment.appointment_date_only
                        details = appointment.name
                        rp_id = self.create_requested_payment(appointment_type, patient_id, datetime.now().date(), deduction_amount,
                                                              payment_reference, payment_method_name,
                                                              details)
                        #rp_id = appointment.pay_req_id.id
                        appointment.with_user(2).write({
                            'state': state_val,
                            'payment_reference': payment_reference,
                            'payment_method_name': payment_method_name,
                            'pay_req_id': rp_id,
                            'payment_type': 'Paid',
                            'deduction_amount': deduction_amount,
                        })
                        self.update_requested_payment(rp_id, appointment_type, appointment_id, apt_date)
                        # appointment.sudo().create_invoice()
                    elif appointment_type == 'tele' or appointment_type == 'hvd':
                        appointment = appointment_obj.sudo().search([('id', '=', int(appointment_id))], limit=1)
                        patient_id = appointment.patient.id
                        apt_date = appointment.appointment_date_only
                        details = appointment.name
                        rp_id = self.create_requested_payment(appointment_type, patient_id, datetime.now().date(), deduction_amount,
                                                              payment_reference, payment_method_name,
                                                              details)

                        appointment.with_user(2).write({
                            'state': state_val,
                            'payment_reference': payment_reference,
                            'payment_method_name': payment_method_name,
                            'pay_req_id': rp_id,
                            'payment_type': 'Paid',
                            'deduction_amount': deduction_amount,
                        })

                        self.update_requested_payment(rp_id, appointment_type, appointment_id, apt_date)
                    elif appointment_type == 'sleep' or appointment_type == 'caregiver':
                        appointment = appointment_obj.sudo().search([('id', '=', int(appointment_id))], limit=1)
                        patient_id = appointment.patient_id.id
                        apt_date = appointment.date
                        details = appointment.name
                        rp_id = self.create_requested_payment(appointment_type, patient_id, datetime.now().date(), deduction_amount,
                                                              payment_reference, payment_method_name,
                                                              details)


                        appointment.with_user(2).write({
                            'state': state_val,
                            'payment_reference': payment_reference,
                            'payment_method_name': payment_method_name,
                            'request_payment_id': rp_id,
                            'deduction_amount': deduction_amount,
                        })

                        self.update_requested_payment(rp_id, appointment_type, appointment_id, apt_date)

                    data = {
                        'id': appointment_id,
                        # 'rp_id': rp_id,
                        'patient_id': patient_id,
                        'payment reference': payment_reference,
                        'payment deduction amount': deduction_amount,
                        'message': 'Payment has been set successfully!'
                    }
                    return valid_response(data)
                else:
                    # remove appointment
                    appointment = appointment_obj.sudo().search([('id', '=', int(appointment_id))], limit=1)
                    appointment.with_user(2).unlink()
                    data = {
                        'id': appointment_id,
                        'payment reference': payment_reference,
                        'message': 'Payment failed, Appointment has been deleted successfully!'
                    }
                    return valid_response(data)
            else:
                return invalid_response('appointment not found')

        except Exception as e:
            #print(e)
            return invalid_response(e)

    @authenticate_token
    @http.route(['/sehati/service-request/create-caregiver'], type='http', auth="none", methods=['POST'], csrf=False)
    def set_caregiver_service_request(self, **post):
        model_name = 'sm.shifa.service.request'

        if not 'patient' in post:
            return invalid_response('patient not found', 'patient not found in request ! ')
        if not 'service_id' in post:
            return invalid_response('service_id not found', 'service_id not found in request ! ')
        if not 'ksa_nationality' in post:
            return invalid_response('ksa_nationality not found', 'ksa nationality not found in request ! ')
        if not 'location' in post:
            return invalid_response('location not found', 'location not found in request ! ')

        try:
            values = {}
            values['name'] = request.env.ref('smartmind_shifa.sequence_service_request').next_by_id()
            patient_id = post.get('patient')
            service_id = post.get('service_id')
            caregiver_nationality = post.get('caregiver_nationality')
            if not caregiver_nationality:
                caregiver_nationality = False
            patient_model = 'oeh.medical.patient'
            count_patient = request.env[patient_model].sudo().search_count(
                [('id', '=', int(patient_id))])
            if count_patient > 0:
                patient = request.env[patient_model].sudo().browse(int(patient_id))
                values['patient'] = patient.id
            else:
                return invalid_response('invalid patient_id', 'Invalid Patient ID ! ')

            count_service = request.env['sm.shifa.service'].sudo().search_count([('id', '=', int(service_id))])
            if count_service > 0:
                service = request.env['sm.shifa.service'].sudo().browse(int(service_id))
                values['service'] = service.id
            else:
                return invalid_response('invalid doctor_id', 'Invalid Service ID ! ')

            values['location'] = post.get('location')
            values['mobile'] = post.get('mobile')
            is_ksa_nationality = bool(post.get('ksa_nationality'))
            if is_ksa_nationality:
                values['ksa_nationality'] = 'yes'
            else:
                values['ksa_nationality'] = 'no'

            file1 = self._get_file_name(post.get('attached_file'), 'attached_file')
            file2 = self._get_file_name(post.get('attached_file_2'), 'attached_file_2')
            file3 = self._get_file_name(post.get('attached_file_3'), 'attached_file_3')
            filename = "{0}, {1}, {2}".format(file1, file2, file3)
            # upload files from request
            values['attached_file'] = self._upload_attached_file(post.get('attached_file'), 'attached_file')
            values['attached_file_2'] = self._upload_attached_file(post.get('attached_file_2'),
                                                                   'attached_file_2')
            values['attached_file_3'] = self._upload_attached_file(post.get('attached_file_3'),
                                                                   'attached_file_3')
            values['caregiver_nationality'] = caregiver_nationality

            serv_req = request.env[model_name].sudo().create(values)

            data = {
                'id': serv_req.id,
                'upload file name': filename,
                'message': 'Your caregiver service has been saved successfully!'
            }
            return valid_response(data)

        except Exception as e:
            #print(e)
            return invalid_response('failed to send contact us', e)

        return invalid_response('invalid object model', 'The model %s is not available in the registry.' % model_name)

    @authenticate_token
    @http.route(['/sehati/service-request/create-sleep-medicine'], type='http', auth="none", methods=['POST'],
                csrf=False)
    def set_sleep_medicine_service_request(self, **post):
        model_name = 'sm.shifa.service.request'

        if not 'patient' in post:
            return invalid_response('patient_id not found', 'patient_id not found in request ! ')
        if not 'service_id' in post:
            return invalid_response('service_id not found', 'service_id not found in request ! ')
        if not 'ksa_nationality' in post:
            return invalid_response('ksa_nationality not found', 'ksa nationality not found in request ! ')
        if not 'location' in post:
            return invalid_response('location not found', 'location not found in request ! ')

        try:
            values = {}
            # Main information
            patient_id = post.get('patient')
            patient_model = 'oeh.medical.patient'
            count_patient = request.env[patient_model].sudo().search_count(
                [('id', '=', int(patient_id))])
            if count_patient > 0:
                patient = request.env[patient_model].sudo().browse(int(patient_id))
                values['patient'] = patient.id
            else:
                return invalid_response('invalid patient_id', 'Invalid Patient ID ! ')

            service_id = post.get('service_id')
            count_service = request.env['sm.shifa.service'].sudo().search_count([('id', '=', int(service_id))])
            if count_service > 0:
                service = request.env['sm.shifa.service'].sudo().browse(int(service_id))
                values['service'] = service.id
            else:
                return invalid_response('invalid doctor_id', 'Invalid Service ID ! ')

            values['location'] = post.get('location')
            values['mobile'] = post.get('mobile')
            is_ksa_nationality = bool(post.get('ksa_nationality'))
            if is_ksa_nationality:
                values['ksa_nationality'] = 'yes'
            else:
                values['ksa_nationality'] = 'no'

            file1 = self._get_file_name(post.get('attached_file'), 'attached_file')
            file2 = self._get_file_name(post.get('attached_file_2'), 'attached_file_2')
            file3 = self._get_file_name(post.get('attached_file_3'), 'attached_file_3')
            filename = "{0}, {1}, {2}".format(file1, file2, file3)
            # upload files from request
            values['attached_file'] = self._upload_attached_file(post.get('attached_file'), 'attached_file')
            values['attached_file_2'] = self._upload_attached_file(post.get('attached_file_2'),
                                                                   'attached_file_2')
            values['attached_file_3'] = self._upload_attached_file(post.get('attached_file_3'),
                                                                   'attached_file_3')

            # save questionnaire to database
            # values['neck_circ'] = post.get('neck_circ')
            values['weight'] = post.get('weight')
            values['height'] = post.get('height')

            values['snore'] = post.get('question1')
            values['wakeup_feeling_hasnt_sleep'] = post.get('question2')
            values['stop_breathing_night'] = post.get('question3')
            values['gasp_air_choke'] = post.get('question4')
            values['is_male'] = post.get('question5')
            values['age_50_older'] = post.get('question6')
            values['name'] = request.env.ref('sm_caregiver.sequence_sleep_medicine_request').next_by_id()

            values['comment'] = post.get('comment')
            serv_req = request.env[model_name].sudo().create(values)

            data = {
                # 'id': serv_req.id,
                'upload file name': filename,
                'message': 'Your sleep medicine service has been saved successfully!'
            }
            return valid_response(data)

        except Exception as e:
            #print('Exception')
            #print(e)
            return invalid_response('error', e)

        return invalid_response('invalid object model', 'The model %s is not available in the registry.' % model_name)

    @authenticate_token
    @http.route(['/sehati/service-request/payment-checker'], type='http', auth="none", methods=['POST'],
                csrf=False)
    def set_payment_request_checker(self, **post):
        model_name = 'sm.shifa.requested.payments'

        if not 'payment_id' in post:
            return invalid_response('payment_id not found', 'payment request id not found in request ! ')
        if not 'payment_reference' in post:
            return invalid_response('payment_reference not found', 'payment reference not found in request ! ')
        # this condition because of  app version in apps store
        if not 'deduction_amount' in post:
            deduction_amount = 0.0
        else:
            deduction_amount = post.get('deduction_amount')
            
            # return invalid_response('payment_reference not found', 'payment deduction amount not found in request ! ')

        payment_id = post.get('payment_id')
        payment_reference = post.get('payment_reference')
        payment_method_name = post.get('payment_method_name')
        if not payment_method_name:
            payment_method_name = " "
        try:
            count_payment = request.env[model_name].sudo().search_count([('id', '=', int(payment_id))])
            message = False
            if count_payment > 0:
                payment_reference = post.get('payment_reference')
                if payment_reference != '':
                    action = self._update_payment_reference(payment_id, 'Paid', payment_reference,
                                                            float(deduction_amount), payment_method_name)
                    if action:
                        message = 'Requested Payments has changed to Paid state successfully'
                    else:
                        return invalid_response('payment_reference not valid', 'payment reference is invalid ')
                else:
                    action = self._update_payment_reference(payment_id, 'Reject', payment_reference,
                                                            float(deduction_amount), payment_method_name)
                    if action:
                        message = 'Requested Payments has changed to Reject state successfully'
            else:
                return invalid_response('payment_id not valid', 'payment id is invalid ')
            data = {
                'message': message
            }
            return valid_response(data)

        except Exception as e:
            #print(e)
            return invalid_response('failed to send contact us', e)

        return invalid_response('invalid object model', 'The model %s is not available in the registry.' % model_name)

    @authenticate_token
    @http.route(['/sehati/appointment/get-discounts'], type='http', auth="none", methods=['GET'],
                csrf=False)
    def get_appointments_discount(self, **payload):
        model_name = 'sm.shifa.discounts'
        model = request.env[self._model].sudo().search([('model', '=', model_name)], limit=1)
        payload[
            'fields'] = "['id', 'name', 'start_date', 'exp_date', 'state', 'discounts_type', 'fixed_type', 'apply_to', 'hhc', 'tele', 'pcr', 'hvd', 'physiotherapy', 'customer_code']"

        if model:
            domain, fields, offset, limit, order = extract_arguments(
                payload)
            data = request.env[model.model].sudo().search_read(
                domain=domain, fields=fields, offset=offset, limit=limit, order=order)

            return valid_response(data)
        return invalid_response('invalid object model',
                                'The model %s is not available in the registry.' % model_name)

    # Other Methods
    def _is_service_found(self, service_id):
        count_service = request.env['sm.shifa.service'].sudo().search_count([('id', '=', int(service_id))])
        if count_service > 0:
            return True
        else:
            return False

    def _get_file_name(self, file, file_name):
        if file:
            files = request.httprequest.files.getlist(file_name)
            for ufile in files:
                return ufile.filename

    def _upload_attached_file(self, file, file_name):
        if file:
            files = request.httprequest.files.getlist(file_name)
            for ufile in files:
                try:
                    file_data = base64.encodestring(ufile.read())
                    file_data_to_send = file_data.decode('utf-8')
                    return file_data_to_send
                except Exception as e:
                    return invalid_response('failed to upload file', e)

    def _add_service_request(self, patient_id, service, date, appointment_name, location, file_1, file_2, file_3):
        vals = {}
        vals['patient'] = patient_id
        vals['service'] = service
        vals['date'] = date
        vals['location'] = location
        vals['appointment'] = appointment_name
        vals['attached_file'] = self._upload_attached_file(file_1, 'attached_file')
        vals['attached_file_2'] = self._upload_attached_file(file_2, 'attached_file_2')
        vals['attached_file_3'] = self._upload_attached_file(file_3, 'attached_file_3')

        request.env['sm.shifa.service.request'].sudo().create(vals)

    def _update_payment_reference(self, payment_id, state, payment_reference, deduction_amount, payment_method_name):
        model = request.env['sm.shifa.requested.payments'].sudo().browse(int(payment_id))
        if model:
            model.sudo().write({
                'state': state,
                'payment_reference': payment_reference,
                'deduction_amount': deduction_amount,
                'payment_method_name': payment_method_name,
                'payment_method': 'mobile',
            })
            if state == 'Paid':
                model.sudo().create_account_payment()
                model.sudo().notification()
            return True
        else:
            return False

    def create_requested_payment(self, apt_type, patient_id, date, payment_amount, ref, payment_method_name, details):
        # Mapping from input apt_type to PAY_TYPE
        apt_type_mapping = {
            'hhc': 'hhc_appointment',
            'phy': 'phy_appointment',
            'pcr': 'pcr_appointment',
            'tele': 'tele_appointment',
            'hvd': 'hvd_appointment',
            'sleep': 'sleep_medicine_request',
            'caregiver': 'caregiver',
        }

        # Get the corresponding rp_type from the mapping
        rp_type = apt_type_mapping.get(apt_type)

        if not rp_type:
            raise http.HttpError(
                description=f"Invalid apt_type provided: {apt_type}",
                code=400  # Bad Request
            )

        model_name = 'sm.shifa.requested.payments'

        rp = request.env[model_name].sudo().create({
            'name': request.env.ref('smartmind_shifa_extra.sequence_requested_payment').next_by_id(),
            'patient': int(patient_id),
            'type': rp_type,
            'date': date,
            'payment_amount': payment_amount,
            'deduction_amount': payment_amount,
            'payment_reference': ref,
            'details': details,
            'payment_method_name': payment_method_name,
            'payment_method': 'mobile',
            'state': 'Done',
        })

        rp.sudo().create_account_payment()
        return rp.id
    # def create_requested_payment(self, apt_type, patient_id, date, payment_amount, ref, payment_method_name, details):
    #     model_name = 'sm.shifa.requested.payments'
    #
    #     rp = request.env[model_name].sudo().create({
    #         'patient': int(patient_id),
    #         'date': date,
    #         'payment_amount': payment_amount,
    #         'deduction_amount': payment_amount,
    #         'payment_reference': ref,
    #         'details': details,
    #         'payment_method_name': payment_method_name,
    #         'payment_method': 'mobile',
    #         'state': 'Done',
    #     })
    #     rp.sudo().create_account_payment()
    #     return rp.id

    def update_requested_payment(self, rq_id, apt_type, apt_id, apt_date):
        model_name = 'sm.shifa.requested.payments'
        requested_payment = request.env[model_name].sudo().search([('id', '=', int(rq_id))], limit=1)
        vals = {}
        if apt_type == 'hhc':
            vals = {'hhc_appointment': apt_id, 'date_hhc_appointment': apt_date}
        elif apt_type == 'phy':
            vals = {'phy_appointment': apt_id, 'date_phy_appointment': apt_date}
        elif apt_type == 'pcr':
            vals = {'pcr_appointment': apt_id, 'date_pcr_appointment': apt_date}
        elif apt_type == 'tele':
            vals = {'appointment': apt_id, 'date_appointment': apt_date}
        elif apt_type == 'hvd':
            vals = {'hvd_appointment': apt_id, 'date_hvd_appointment': apt_date}
        elif apt_type == 'sleep':
            vals = {'sleep_medicine_request': apt_id, 'date_sleep_medicine_request': apt_date}
        elif apt_type == 'caregiver':
            vals = {'caregiver_contract_id': apt_id, 'date_caregiver_contract': apt_date}

        requested_payment.write(vals)

    def convert_timeslot_to_time(self, time_str):
        hm = time_str.split(':')
        sch_time = int(hm[0]) + int(hm[1]) / 60
        return sch_time

    def get_timeslot_id(self, doctor_id, date, time_str):
        timeslot = request.env['sm.shifa.physician.schedule.timeslot'].search(
            [('physician_id', '=', doctor_id), ('date', '=', date), ('available_time', '=', time_str)], limit=1)
        if timeslot:
            return timeslot.id

    def get_appointment_date_time(self, date, apt_time):
        dt_format = '%Y-%m-%d %H:%M:%S'
        return datetime.strptime(date.strftime(dt_format), dt_format) + timedelta(hours=apt_time - 3)

    def get_appointment_end(self, date, doctor_id, apt_date_time):
        sch_model = 'sm.shifa.physician.schedule'
        domain = [('doctor.id', '=', int(doctor_id))]
        count = request.env[sch_model].search_count(domain)
        if count > 0:
            schedule = request.env[sch_model].search(domain, limit=1)
            sch_line = request.env['sm.shifa.physician.schedule.line'].search(
                [('schedule_id', '=', schedule.id), ('date', '=', date)], limit=1)
            end_date = datetime.strptime(apt_date_time.strftime("%Y-%m-%d %H:%M:%S"),
                                         "%Y-%m-%d %H:%M:%S") + timedelta(hours=sch_line.duration)
            return end_date
        else:
            end_date = datetime.strptime(apt_date_time.strftime("%Y-%m-%d %H:%M:%S"),
                                         "%Y-%m-%d %H:%M:%S") + timedelta(hours=30)
            return end_date
