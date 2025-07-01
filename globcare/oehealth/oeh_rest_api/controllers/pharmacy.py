import base64
import datetime
import json
import uuid

from odoo import http, _
from odoo.http import request

from odoo.addons.oehealth.oeh_rest_api.common_methods import invalid_response, valid_response, extract_arguments
from odoo.addons.oehealth.oeh_rest_api.controllers.main import authenticate_token, authenticate_token_portal
from odoo.addons.oehealth.oeh_rest_api.shared_methods import SmartMindSharedMethods
from odoo.addons.oehealth.oeh_rest_api.payment_methods import SmartMindPaymentMethods


class SmartMindPharmacyRESTAPIController(http.Controller, SmartMindSharedMethods, SmartMindPaymentMethods):

    def __init__(self):
        self._model = 'ir.model'

    @authenticate_token
    @http.route(['/sehati/pharmacy/get-price'], type='http', auth="none", methods=['GET'], csrf=False)
    def get_pharmacy_chain_price(self):
        instant = request.env['sm.shifa.instant.consultancy.charge'].sudo().search([('code', '=', 'ICP')], limit=1)

        try:
            if instant:
                data = {
                    'instant_consultation_pharmacy': str(instant.charge),
                }
                return valid_response(data)
            else:
                return invalid_response('No data to show')

        except Exception as e:
            print(e)
            return invalid_response('error', e)
        return invalid_response('invalid object model', 'The model %s is not available in the registry.' % model_name)

    @authenticate_token
    @http.route(['/sehati/pharmacy/patient/instant-consultation/create'], type='http', auth="none", methods=['POST'],
                csrf=False)
    def create_instant_consultation(self, **post):
        model_name = 'sm.shifa.instant.consultation'

        if not 'patient_id' in post:
            return invalid_response('patient_id not found', 'patient id not found in request ! ')

        # if not 'qr_code' in post:
        #     return invalid_response('qr_code not found', 'pharmacy qr code not found in request ! ')
        patient_id = post.get('patient_id')
        qr_code = post.get('qr_code')
        consultation_id = False
        try:
            instance = request.env['sm.shifa.instant.consultancy.charge'].search([('code', '=', 'ICP')], limit=1)
            discount = False
            if qr_code:
                pharmacy_model = 'sm.shifa.pharmacy.chain'
                pharmacy_chain_count = request.env[pharmacy_model].sudo().search_count([('qr_code', '=', qr_code)])
                if pharmacy_chain_count > 0:
                    pharmacy_chain = request.env[pharmacy_model].sudo().search([('qr_code', '=', qr_code)], limit=1)
                    model = request.env[model_name].sudo().create({
                        'patient': int(patient_id),
                        'price': instance.charge,
                        'pharmacy_chain': int(pharmacy_chain.id),
                        'discount': int(pharmacy_chain.discount),
                        'day': datetime.datetime.now().strftime("%A"),
                        'state': 'waiting',
                    })
                    model._set_pharmacy_chain_discount()
                    consultation_id = model.id
                else:
                    return invalid_response('invalid qr_code value',
                                            'The pharmacy with given qr code value not found, please check your inputs')
            else:
                model = request.env[model_name].sudo().create({
                    'patient': int(patient_id),
                    'price': instance.charge,
                    'state': 'waiting',
                })
                consultation_id = model.id

            instant_obj = request.env[model_name].sudo().browse(consultation_id)

            data = {
                'consultation_id': consultation_id,
                'price': str(instance.charge),
                'discount': str(instant_obj.discount),
                'vat': str(instant_obj.tax),
                'total price': str(instant_obj.amount_payable),
                'message': 'Your data has been created successfully',
            }
            return valid_response(data)

        except Exception as e:
            return invalid_response('error', e)
        return invalid_response('invalid object model', 'The model %s is not available in the registry.' % model_name)

    @authenticate_token
    @http.route(['/sehati/patient/get-instant-consultation/<patient_id>'], type='http', auth="none", methods=['GET'],
                csrf=False)
    def get_patient_instant_consultation(self, patient_id=None, user_id=None, **payload):
        model_name = 'sm.shifa.instant.consultation'
        model = request.env[self._model].sudo().search([('model', '=', model_name)], limit=1)
        payload[
            'fields'] = "['id', 'name', 'patient', 'patient_id', 'gender', 'doctor', 'date', 'age', 'price', 'discount', 'jitsi_link', 'state', 'link']"

        if model:
            domain, fields, offset, limit, order = extract_arguments(
                payload)
            # domain = [('patient.id', '=', int(patient_id)), ('state', 'not in', ['completed', 'dr_canceled', 'canceled'])]
            domain = [('patient.id', '=', int(patient_id)), ('state', 'not in', ['dr_canceled', 'canceled'])]
            data = request.env[model.model].sudo().search_read(
                domain=domain, fields=fields, offset=offset, limit=limit, order=order)

            data_to_push = []
            doctor_id = False
            for x in data:
                for k, v in x.items():
                    if str(type(v)) in ("<class 'datetime.datetime'>", "<class 'datetime.date'>"):
                        date = v.strftime("%Y-%m-%d")  # %H:%M:%S
                        x[k] = str(date)
                    if str(k) == "patient":
                        patient_list = []
                        if v and len(v) > 0:
                            patient = request.env['oeh.medical.patient'].browse(int(patient_id))
                            if patient:
                                patient_values = {
                                    'patient': patient.name,
                                    'patient_fcm_token': patient.patient_fcm_token,
                                    'device_type': patient.device_type,
                                }
                                patient_list.append(patient_values)
                        else:
                            patient_list = v
                        x[k] = patient_list
                    if str(k) == "doctor":
                        doctor_list = []
                        if v and len(v) > 0:
                            doctor_id = v[0]
                            doctor = request.env['oeh.medical.physician'].browse(int(doctor_id))
                            if doctor:
                                doctor_values = {
                                    'doctor': doctor.name,
                                    'doctor_fcm_token': doctor.doctor_fcm_token,
                                    'device_type': doctor.device_type,
                                }
                                doctor_list.append(doctor_values)
                        else:
                            doctor_list = v
                        x[k] = doctor_list
                x['doctor_image_url'] = self.get_image_url('image_512', 'oeh.medical.physician', doctor_id)
                x['patient_image_url'] = self.get_image_url('image_512', 'oeh.medical.patient', patient_id)
                data_to_push.append(x)
                # patient_obj
            return valid_response(data_to_push)
        return invalid_response('invalid object model', 'The model %s is not available in the registry.' % model_name)

    #@authenticate_token
    @http.route(['/sehati/doctor/get-instant-consultation/<doctor_id>'], type='http', auth="none", methods=['GET'],
                csrf=False)
    def get_doctor_instant_consultation(self, doctor_id=None, user_id=None, **payload):
        model_name = 'sm.shifa.instant.consultation'
        model = request.env[self._model].with_user(2).search([('model', '=', model_name)], limit=1)
        payload[
            'fields'] = "['id', 'name', 'patient', 'patient_id', 'gender', 'doctor', 'date','ssn','dob', 'age', 'price', 'discount', 'jitsi_link', 'state', 'link', 'pharmacy_chain', " \
                        "'chief_complaint', 'diagnosis', 'diagnosis_add2', 'diagnosis_add3', 'other_prescription_1', 'other_prescription_2', 'other_prescription_3']"
        # payload['domain'] = "[('id', '=', " + str(user_id) + ")]"

        if model:
            domain, fields, offset, limit, order = extract_arguments(
                payload)
            if doctor_id:
                domain = ['|',('doctor.id', '=', doctor_id),('state', 'not in', ['completed', 'dr_canceled', 'canceled'])]

            data = request.env[model.model].with_user(2).search_read(
                domain=domain, fields=fields, offset=offset, limit=limit, order=order)
            
            data_to_push = []
            # patient_id = False
            patient_id = discount = qr_code = ph_chain_name = False
            for x in data:
                for k, v in x.items():
                    if str(type(v)) in ("<class 'datetime.datetime'>", "<class 'datetime.date'>"):
                        date = v.strftime("%Y-%m-%d")  # %H:%M:%S
                        x[k] = str(date)
                    if str(k) == "patient":
                        patient_list = []
                        if v and len(v) > 0:
                            patient_id = v[0]
                            patient = request.env['oeh.medical.patient'].sudo().browse(int(patient_id))
                            if patient:
                                patient_values = {
                                    'patient': patient.name,
                                    'patient_fcm_token': patient.patient_fcm_token,
                                    'device_type': patient.device_type,
                                }
                                patient_list.append(patient_values)
                        else:
                            patient_list = v
                        x[k] = patient_list
                    if str(k) == "doctor":
                        doctor_list = []
                        if v and len(v) > 0:
                            doctor = request.env['oeh.medical.physician'].sudo().browse(int(doctor_id))
                            if doctor:
                                doctor_values = {
                                    'doctor': doctor.name,
                                    'doctor_fcm_token': doctor.doctor_fcm_token,
                                    'device_type': doctor.device_type,
                                }
                                doctor_list.append(doctor_values)
                        else:
                            doctor_list = v
                        x[k] = doctor_list
                    if str(k) == "pharmacy_chain":
                        if v and len(v) > 0:
                            ph_ch_id = v[0]
                            ph_chain_name = v[1]
                            x['pharmacy_chain'] = ph_chain_name
                            # x[k] = str(date)
                            if ph_ch_id:
                                pharmacy_chain = request.env['sm.shifa.pharmacy.chain'].sudo().search(
                                    [('id', '=', int(ph_ch_id))])
                                discount = pharmacy_chain.discount
                                qr_code = pharmacy_chain.qr_code
                    if str(k) == "chief_complaint":
                        if v and len(v) > 0:
                            x[k] = v[1]
                        else:
                            x[k] = ""
                    if str(k) == "diagnosis":
                        if v and len(v) > 0:
                            x[k] = v[1]
                        else:
                            x[k] = ""
                    if str(k) == "diagnosis_add2":
                        if v and len(v) > 0:
                            x[k] = v[1]
                        else:
                            x[k] = ""
                    if str(k) == "diagnosis_add3":
                        if v and len(v) > 0:
                            x[k] = v[1]
                        else:
                            x[k] = ""

                x['doctor_image_url'] = self.get_image_url('image_512', 'oeh.medical.physician', doctor_id)
                x['patient_image_url'] = self.get_image_url('image_512', 'oeh.medical.patient', patient_id)
                x['patient_id'] = patient_id
                x['discount'] = discount
                x['qr_code'] = qr_code
                # x['pharmacy_chain'] = ph_chain_name
                data_to_push.append(x)

            return valid_response(data_to_push)
        return invalid_response('invalid object model', 'The model %s is not available in the registry.' % model_name)

    @authenticate_token
    @http.route(['/sehati/doctor/get-list-instant-consultation/<doctor_id>'], type='http', auth="none", methods=['GET'],
                csrf=False)
    def get_doctor_list_instant_consultation(self, doctor_id=None, user_id=None, **payload):
        model_name = 'sm.shifa.instant.consultation'
        model = request.env[self._model].sudo().search([('model', '=', model_name)], limit=1)
        payload[
            'fields'] = "['id', 'name', 'patient', 'patient_id', 'gender', 'doctor', 'date', 'age', 'price', 'discount', 'pharmacy_chain', " \
                        "'chief_complaint', 'diagnosis', 'diagnosis_add2', 'diagnosis_add3', 'other_prescription_1', 'other_prescription_2', 'other_prescription_3', 'history', " \
                        "'weight', 'heart_rate', 'blood_pressure_s', 'blood_sugar', 'blood_pressure_s', 'blood_pressure_d', 'respiration', 'temperature', 'recommendations', 'prescription_line', 'dr_comment', 'state']"

        if model:
            domain, fields, offset, limit, order = extract_arguments(
                payload)
            if doctor_id:
                domain = ['|', ('doctor.id', '=', doctor_id), ('state', '=', 'waiting')]

            data = request.env[model.model].sudo().search_read(
                domain=domain, fields=fields, offset=offset, limit=limit, order=order)

            data_to_push = []
            # patient_id = False
            patient_id = discount = qr_code = ph_chain_name = False
            for x in data:
                for k, v in x.items():
                    if str(type(v)) in ("<class 'datetime.datetime'>", "<class 'datetime.date'>"):
                        date = v.strftime("%Y-%m-%d")  # %H:%M:%S
                        x[k] = str(date)
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
                    if str(k) == "pharmacy_chain":
                        if v and len(v) > 0:
                            ph_ch_id = v[0]
                            ph_chain_name = v[1]
                            x['pharmacy_chain'] = ph_chain_name
                            if ph_ch_id:
                                pharmacy_chain = request.env['sm.shifa.pharmacy.chain'].sudo().search(
                                    [('id', '=', int(ph_ch_id))])
                                discount = pharmacy_chain.discount
                                qr_code = pharmacy_chain.qr_code
                    if str(k) == "chief_complaint":
                        if v and len(v) > 0:
                            x[k] = v[1]
                        else:
                            x[k] = ""
                    if str(k) == "diagnosis":
                        if v and len(v) > 0:
                            x[k] = v[1]
                        else:
                            x[k] = ""
                    if str(k) == "diagnosis_add2":
                        if v and len(v) > 0:
                            x[k] = v[1]
                        else:
                            x[k] = ""
                    if str(k) == "diagnosis_add3":
                        if v and len(v) > 0:
                            x[k] = v[1]
                        else:
                            x[k] = ""
                    if str(k) == "prescription_line":
                        medicine_list = []
                        if v and len(v) > 0:
                            for pres_line_id in v:
                                pres_line = request.env['sm.shifa.prescription.line'].browse(int(pres_line_id))
                                if pres_line:
                                    pres_line_values = {
                                        'pharmacy_medicine': pres_line.pharmacy_medicines.pharmacy_medicines,
                                        'dose': pres_line.dose,
                                        'dose_form': pres_line.dose_form.name,
                                        'dose_route': pres_line.dose_route.name,
                                        'frequency': pres_line.common_dosage.name,
                                        'quantity': pres_line.qty,
                                        'duration': pres_line.duration,
                                        'unit': pres_line.frequency_unit,
                                    }
                                    medicine_list.append(pres_line_values)
                        else:
                            medicine_list = v
                        x[k] = medicine_list

                # x['pharmacy_chain'] = ph_chain_name
                data_to_push.append(x)

            return valid_response(data_to_push)
        return invalid_response('invalid object model', 'The model %s is not available in the registry.' % model_name)

    @authenticate_token
    @http.route(['/sehati/doctor/update-instant-consultation-state'], type='http', auth="none", methods=['POST'],
                csrf=False)
    def update_instant_consultation_sate(self, **post):
        model_name = 'sm.shifa.instant.consultation'

        if not 'consultation_id' in post:
            return invalid_response('consultation_id not found', 'consultation id not found in request ! ')
        if not 'doctor_id' in post:
            return invalid_response('doctor_id not found', 'Doctor id not found in request ! ')

        try:
            consultation_id = post.get('consultation_id')
            doctor_id = post.get('doctor_id')
            pharmacy_chain = request.env[model_name].sudo().search([('id', '=', int(consultation_id))], limit=1)
            if not pharmacy_chain.doctor.id:
                model = pharmacy_chain.sudo().write({
                    'doctor': int(doctor_id),
                    'state': 'approved',
                    'approved_date': datetime.datetime.now(),
                })
                data = {
                    'message': 'Your data has been updated successfully',
                }
                return valid_response(data)
            else:
                return invalid_response('This session has been accepted from other Doctor', 'This session has been accepted from other Doctor! ')

        except Exception as e:
            return invalid_response('error', e)
        return invalid_response('invalid object model', 'The model %s is not available in the registry.' % model_name)

    @authenticate_token
    @http.route(['/sehati/pharmacy/set-payment-status'], type='http', auth="none", methods=['POST'], csrf=False)
    def set_payment_status(self, **post):
        model_name = 'sm.shifa.instant.consultation'

        consultation_id = post.get('consultation_id')
        payment_reference = post.get('payment_reference')
        deduction_amount = post.get('consultancy_price')
        payment_method_name = post.get('payment_method_name')
        if not payment_method_name:
            payment_method_name = " "

        if not consultation_id:
            return invalid_response('consultation_id not found', 'Consultation ID not found in request ! ')
        if not payment_reference:
            return invalid_response('payment_reference not found', 'Payment reference not found in request ! ')
        if not deduction_amount:
            return invalid_response('deduction_amount_not_found', 'deduction_amount field is required!')

        try:
            consultation_id = post.get('consultation_id')
            payment_reference = post.get('payment_reference')
            invitation_text_jitsi = post.get('invitation_text_jitsi')
            consultation_obj = request.env[model_name]
            ref = str(payment_reference)

            if ref:
                consultation = consultation_obj.with_user(2).search([('id', '=', int(consultation_id))], limit=1)
                jitsi_link = self._create_jitsi_meeting(consultation.id)
                consultation.with_user(2).write({
                    'state': 'ready',
                    'ready_date': datetime.datetime.now(),
                    'payment_reference': payment_reference,
                    'payment_method_name': payment_method_name,
                    'payment_type': 'Paid',
                    'deduction_amount': deduction_amount
                })
                # create request send state
                requested_payment = consultation.with_user(2).create_requested_payment('Done', 'mobile')
                requested_payment.with_user(2).create_account_payment()
                # create Invoice
                consultation.with_user(2).create_invoice()

                data = {
                    'id': consultation_id,
                    'payment reference': payment_reference,
                    'jitsi  meeting link': jitsi_link,
                    'message': 'Payment has been set successfully!'
                }
                return valid_response(data)
            else:

                consultation = consultation_obj.with_user(2).search([('id', '=', int(consultation_id))], limit=1)
                consultation.with_user(2).write({
                    'state': 'canceled',
                })
                data = {
                    'id': consultation_id,
                    'message': 'Payment failed, Consultation has been deleted successfully!'
                }
                return valid_response(data)

        except Exception as e:
            return invalid_response('failed to set appointment payment', e)

    @authenticate_token
    @http.route(['/sehati/update-instant-consultation-state/evaluation'], type='http', auth="none", methods=['POST'],
                csrf=False)
    def update_instant_consultation_sate_evaluation(self, **post):
        model_name = 'sm.shifa.instant.consultation'

        if not 'consultation_id' in post:
            return invalid_response('consultation_id not found', 'consultation id not found in request ! ')

        try:
            consultation_id = post.get('consultation_id')
            consultation = request.env[model_name].sudo().search([('id', '=', int(consultation_id))], limit=1)
            if consultation:
                # save instant prescriptions
                """request.env['sm.shifa.instant.prescriptions'].create({
                    'name': consultation.name,
                    'patient': consultation.patient.id,
                    'doctor': consultation.doctor.id,
                    'inst_con': consultation.name,
                    'diagnosis': consultation.diagnosis.id,
                    'diagnosis_yes_no': consultation.diagnosis_yes_no,
                    'diagnosis_add2': consultation.diagnosis_add2.id,
                    'diagnosis_yes_no_2': consultation.diagnosis_yes_no_2,
                    'diagnosis_add3': consultation.diagnosis_add3.id,
                    'drug_allergy': consultation.drug_allergy,
                    'drug_allergy_text': consultation.drug_allergy_text,
                    'inst_prescription_line': consultation.prescription_line,
                    'other_prescription_1': consultation.other_prescription_1,
                    'other_prescription_2': consultation.other_prescription_2,
                    'other_prescription_3': consultation.other_prescription_3,
                    'recommendations': consultation.recommendations,
                    'pharmacy_chain': consultation.pharmacy_chain.id,
                })"""
                # create Bill for Doctor
                # consultation.sudo().create_bill()
                # update instant consultation state to complete
                consultation.sudo().write({
                    'state': 'evaluation',
                    'evaluation_date': datetime.datetime.now(),
                })
                # save report in attachment
                report = request.env.ref('smartmind_shifa_extra.sm_shifa_medical_pharmacy_report')._render_qweb_pdf(
                    consultation.id)[0]
                report = base64.b64encode(report)
                is_send_sms = consultation.sudo().set_to_evaluation()
                # is_send_sms = self.send_sms('sm.shifa.instant.prescriptions', consultation.name, consultation)
            else:
                return invalid_response('no_consultation_found', 'No Consultation found with given id')

            data = {
                'save_prescription': 'Your instant prescription has been created successfully',
                'sms_send': is_send_sms,
                'message': 'Your data has been updated successfully',
            }
            return valid_response(data)

        except Exception as e:
            return invalid_response('error', e)
        return invalid_response('invalid object model', 'The model %s is not available in the registry.' % model_name)

    # api for Canceled by DR state
    @authenticate_token
    @http.route(['/sehati/update-instant-consultation-state/dr_canceled'], type='http', auth="none", methods=['POST'],
                csrf=False)
    def update_instant_consultation_sate_canceled_via_doctor(self, **post):
        model_name = 'sm.shifa.instant.consultation'
        dr_comment = post.get('dr_comment')

        if not 'consultation_id' in post:
            return invalid_response('consultation_id not found', 'consultation id not found in request ! ')

        try:
            consultation_id = post.get('consultation_id')
            consultation = request.env[model_name].sudo().search([('id', '=', int(consultation_id))], limit=1)
            if consultation:
                # update instant consultation state to complete
                consultation.sudo().write({
                    'state': 'dr_canceled',
                    'dr_comment': dr_comment,
                })

            else:
                return invalid_response('no_consultation_found', 'No Consultation found with given id')

            data = {
                'message': 'Your data has been updated successfully',
            }
            return valid_response(data)

        except Exception as e:
            return invalid_response('error', e)
        return invalid_response('invalid object model', 'The model %s is not available in the registry.' % model_name)

    @authenticate_token
    @http.route(['/sehati/app/update-and-ios'], type='http', auth="none", methods=['GET'], csrf=False, cors="*")
    def get_app_update(self):
        android = request.env['sm.shifa.app.update'].sudo().search([('code', '=', 'and')], limit=1)
        ios = request.env['sm.shifa.app.update'].sudo().search([('code', '=', 'ios')], limit=1)
        try:
            if android:
                data = {
                    'Android': str(android.version),
                    'IOS': str(ios.version),
                }
                return valid_response(data)
            else:
                return invalid_response('No data to show')

        except Exception as e:
            print(e)
            return invalid_response('error', e)
        return invalid_response('invalid object model', 'The model %s is not available in the registry.' % model_name)

    @authenticate_token
    @http.route(['/sehati/update-instant-consultation-state/in-process'], type='http', auth="none", methods=['POST'],
                csrf=False)
    def update_instant_consultation_sate_process(self, **post):  # improved by Mukhtar MA on 06/03/2023.
        model_name = 'sm.shifa.instant.consultation'

        consultation_id = post.get('consultation_id')

        if not consultation_id:
            return invalid_response('consultation_id not found', 'consultation id is required! ')

        try:
            count_ins_cons = request.env[model_name].sudo().search_count([('id', '=', int(consultation_id))])
            if count_ins_cons > 0:
                ins_cons = request.env[model_name].sudo().search([('id', '=', int(consultation_id))], limit=1)
                # send sms for patient
                ins_cons.sudo().send_jitsi_sms()


                ins_cons.sudo().write({
                    'state': 'in_process',
                    'start_date': datetime.datetime.now(),
                })

                data = {
                    'action': 'Has been generated purchase order, payment request and sale order',
                    'message': 'Your data has been updated successfully',
                }
                return valid_response(data)
            else:
                return invalid_response('not_found', 'Sorry, the given consultation id is not found')

        except Exception as e:
            return invalid_response('error', e)
        return invalid_response('invalid object model', 'The model %s is not available in the registry.' % model_name)

    @authenticate_token
    @http.route(['/sehati/pharmacy-medicines'], type='http', auth="none", methods=['GET'], csrf=False)
    def get_pharmacy_medicines(self, **payload):

        model_name = 'sm.shifa.pharmacy.medicines'
        model = request.env[self._model].sudo().search([('model', '=', model_name)], limit=1)
        payload[
            'fields'] = "['id', 'pharmacy_medicines', 'code',]"

        if model:
            domain, fields, offset, limit, order = extract_arguments(
                payload)
            data = request.env[model.model].sudo().search_read(
                domain=domain, fields=fields, offset=offset, limit=limit, order=order)

            data_to_push = []
            for x in data:
                for k, v in x.items():
                    if str(k) == "pharmacy_medicines":
                        if v and len(v) > 0:
                            x[k] = v
                        else:
                            x[k] = ""
                    if str(k) == "code":
                        if v and len(v) > 0:
                            x[k] = v
                        else:
                            x[k] = ""

                data_to_push.append(x)
                # patient_obj
            return valid_response(data_to_push)
        return invalid_response('invalid object model', 'The model %s is not available in the registry.' % model_name)

    @authenticate_token
    @http.route(['/sehati/pharmacy-diagnosis'], type='http', auth="none", methods=['GET'], csrf=False)
    def get_pharmacy_diagnosis(self, **payload):

        model_name = 'oeh.medical.pathology'
        model = request.env[self._model].sudo().search([('model', '=', model_name)], limit=1)
        payload[
            'fields'] = "['id', 'name', 'code',]"

        if model:
            domain, fields, offset, limit, order = extract_arguments(
                payload)
            data = request.env[model.model].sudo().search_read(
                domain=domain, fields=fields, offset=offset, limit=limit, order=order)

            data_to_push = []
            for x in data:
                for k, v in x.items():
                    if str(k) == "name":
                        if v and len(v) > 0:
                            x[k] = v
                        else:
                            x[k] = ""
                    if str(k) == "code":
                        if v and len(v) > 0:
                            x[k] = v
                        else:
                            x[k] = ""

                data_to_push.append(x)
                # patient_obj
            return valid_response(data_to_push)
        return invalid_response('invalid object model', 'The model %s is not available in the registry.' % model_name)

    @authenticate_token
    @http.route(['/sehati/pharmacy-dose-unit'], type='http', auth="none", methods=['GET'], csrf=False)
    def get_pharmacy_dose_unit(self, **payload):

        model_name = 'oeh.medical.dose.unit'
        model = request.env[self._model].sudo().search([('model', '=', model_name)], limit=1)
        payload[
            'fields'] = "['id', 'name', 'desc',]"

        if model:
            domain, fields, offset, limit, order = extract_arguments(
                payload)
            data = request.env[model.model].sudo().search_read(
                domain=domain, fields=fields, offset=offset, limit=limit, order=order)

            data_to_push = []
            for x in data:
                for k, v in x.items():
                    if str(k) == "name":
                        if v and len(v) > 0:
                            x[k] = v
                        else:
                            x[k] = ""
                    if str(k) == "desc":
                        if v and len(v) > 0:
                            x[k] = v
                        else:
                            x[k] = ""

                data_to_push.append(x)
                # patient_obj
            return valid_response(data_to_push)
        return invalid_response('invalid object model', 'The model %s is not available in the registry.' % model_name)

    @authenticate_token
    @http.route(['/sehati/pharmacy-drug-form'], type='http', auth="none", methods=['GET'], csrf=False)
    def get_pharmacy_drug_form(self, **payload):

        model_name = 'oeh.medical.drug.form'
        model = request.env[self._model].sudo().search([('model', '=', model_name)], limit=1)
        payload[
            'fields'] = "['id', 'name', 'code',]"

        if model:
            domain, fields, offset, limit, order = extract_arguments(
                payload)
            data = request.env[model.model].sudo().search_read(
                domain=domain, fields=fields, offset=offset, limit=limit, order=order)

            data_to_push = []
            for x in data:
                for k, v in x.items():
                    if str(k) == "name":
                        if v and len(v) > 0:
                            x[k] = v
                        else:
                            x[k] = ""
                    if str(k) == "code":
                        if v and len(v) > 0:
                            x[k] = v
                        else:
                            x[k] = ""

                data_to_push.append(x)
                # patient_obj
            return valid_response(data_to_push)
        return invalid_response('invalid object model', 'The model %s is not available in the registry.' % model_name)

    @authenticate_token
    @http.route(['/sehati/pharmacy-drug-route'], type='http', auth="none", methods=['GET'], csrf=False)
    def get_pharmacy_drug_route(self, **payload):

        model_name = 'oeh.medical.drug.route'
        model = request.env[self._model].sudo().search([('model', '=', model_name)], limit=1)
        payload[
            'fields'] = "['id', 'name', 'code',]"

        if model:
            domain, fields, offset, limit, order = extract_arguments(
                payload)
            data = request.env[model.model].sudo().search_read(
                domain=domain, fields=fields, offset=offset, limit=limit, order=order)

            data_to_push = []
            for x in data:
                for k, v in x.items():
                    if str(k) == "name":
                        if v and len(v) > 0:
                            x[k] = v
                        else:
                            x[k] = ""
                    if str(k) == "code":
                        if v and len(v) > 0:
                            x[k] = v
                        else:
                            x[k] = ""

                data_to_push.append(x)
                # patient_obj
            return valid_response(data_to_push)
        return invalid_response('invalid object model', 'The model %s is not available in the registry.' % model_name)

    @authenticate_token
    @http.route(['/sehati/pharmacy-medical-dosage'], type='http', auth="none", methods=['GET'], csrf=False)
    def get_pharmacy_medical_dosage(self, **payload):

        model_name = 'oeh.medical.dosage'
        model = request.env[self._model].sudo().search([('model', '=', model_name)], limit=1)
        payload[
            'fields'] = "['id', 'name', 'code', 'abbreviation',]"

        if model:
            domain, fields, offset, limit, order = extract_arguments(
                payload)
            data = request.env[model.model].sudo().search_read(
                domain=domain, fields=fields, offset=offset, limit=limit, order=order)

            data_to_push = []
            for x in data:
                for k, v in x.items():
                    if str(k) == "name":
                        if v and len(v) > 0:
                            x[k] = v
                        else:
                            x[k] = ""
                    if str(k) == "code":
                        if v and len(v) > 0:
                            x[k] = v
                        else:
                            x[k] = ""
                    if str(k) == "abbreviation":
                        if v and len(v) > 0:
                            x[k] = v
                        else:
                            x[k] = ""

                data_to_push.append(x)
                # patient_obj
            return valid_response(data_to_push)
        return invalid_response('invalid object model', 'The model %s is not available in the registry.' % model_name)

    @authenticate_token
    @http.route(['/sehati/pharmacy/save-json-data'], type='http', auth="none", methods=['POST'], csrf=False)
    def save_json_data(self, **post):
        data = post.get('json_data')

        if not data:
            return invalid_response('json_data_not_found', 'json data not found in request ! ')

        try:
            data = json.loads(data)
        except BaseException as ex:
            print(ex)

        patient_id = consultation_id = chief = drug_allergy = drug_allergy_text = history = diagnosis_1 = diagnosis_2 = diagnosis_3 \
            = weight = heart_rate = o2_saturation = blood_sugar = blood_pressure_s = blood_pressure_d = respiration = \
            temperature = recommendations = other_prescription_1 = other_prescription_2 = other_prescription_3 = consultancy_requested = \
            consultancy_name = consultancy_age = consultancy_sex = consultancy_ssn = False
        count_medicine = 1
        for k, v in data.items():
            if str(k) == 'id':
                consultation_id = v
            if str(k) == 'patient_id':
                patient_id = v

            if type(v) == list:
                for row in range(len(v)):
                    pharmacy_medicine = strength = strength_unit = dose = dose_unit = dose_form = dose_route = common_dosage \
                        = duration = duration_unit = other_instruction = False
                    for key in v[row]:
                        if str(key) == 'pharmacy_medicine':
                            pharmacy_medicine = v[row]['pharmacy_medicine']
                        if str(key) == 'strength':
                            strength = v[row]['strength']
                        if str(key) == 'strength_unit':
                            strength_unit = v[row]['strength_unit']
                        if str(key) == 'dose':
                            dose = v[row]['dose']
                        if str(key) == 'dose_unit':
                            dose_unit = v[row]['dose_unit']
                        if str(key) == 'dose_form':
                            dose_form = v[row]['dose_form']
                        if str(key) == 'dose_route':
                            dose_route = v[row]['dose_route']
                        if str(key) == 'common_dosage':
                            common_dosage = v[row]['common_dosage']
                        if str(key) == 'duration':
                            duration = v[row]['duration']
                        if str(key) == 'duration_unit':
                            duration_unit = v[row]['duration_unit']
                        if str(key) == 'other_instruction':
                            other_instruction = v[row]['other_instruction']

                        # print(key, v[row][key])
                    # print('row: ', str(row))
                    # save medicines items to database
                    self._add_new_medicine(pharmacy_medicine, strength, strength_unit, dose, dose_unit, dose_form,
                                           dose_route, common_dosage
                                           , duration, duration_unit, consultation_id, other_instruction)
                    # print(pharmacy_medicine, strength, strength_unit, dose, dose_unit, dose_form, dose_route, common_dosage
                    #                        , duration, duration_unit, consultation_id, other_instruction)
                    count_medicine = +1
            else:
                if str(k) == 'consultancy_requested':
                    consultancy_requested = v
                if str(k) == 'consultancy_name':
                    consultancy_name = v
                if str(k) == 'consultancy_age':
                    consultancy_age = v
                if str(k) == 'consultancy_sex':
                    consultancy_sex = v
                if str(k) == 'consultancy_ssn':
                    consultancy_ssn = v
                if str(k) == 'chief':
                    chief = v
                if str(k) == 'drug_allergy':
                    drug_allergy = v
                if str(k) == 'drug_allergy_text':
                    drug_allergy_text = v
                if str(k) == 'diagnosis_1':
                    diagnosis = request.env['oeh.medical.pathology'].search([('code', '=', v)])
                    diagnosis_1 = diagnosis.id
                if str(k) == 'diagnosis_2':
                    diagnosis = request.env['oeh.medical.pathology'].search([('code', '=', v)])
                    diagnosis_2 = diagnosis.id
                if str(k) == 'diagnosis_3':
                    diagnosis = request.env['oeh.medical.pathology'].search([('code', '=', v)])
                    diagnosis_3 = diagnosis.id
                if str(k) == 'history_text':
                    history = v
                if str(k) == 'weight':
                    weight = v
                if str(k) == 'heart_rate':
                    heart_rate = v
                if str(k) == 'o2_saturation':
                    o2_saturation = v
                if str(k) == 'blood_sugar':
                    blood_sugar = v
                if str(k) == 'blood_pressure_s':
                    blood_pressure_s = v
                if str(k) == 'blood_pressure_d':
                    blood_pressure_d = v
                if str(k) == 'respiration':
                    respiration = v
                if str(k) == 'temperature':
                    temperature = v
                if str(k) == 'recommendations':
                    recommendations = v
                if str(k) == 'other_prescription_1':
                    other_prescription_1 = v
                if str(k) == 'other_prescription_2':
                    other_prescription_2 = v
                if str(k) == 'other_prescription_3':
                    other_prescription_3 = v

        if not consultation_id:
            return invalid_response('Sorry, no valid value for consultation_id in your json data')

        consultation_model = 'sm.shifa.instant.consultation'
        consultation_count = request.env[consultation_model].sudo().search_count([('id', '=', int(consultation_id))])
        if consultation_count > 0:
            consultation = request.env[consultation_model].sudo().browse(int(consultation_id))
            consultation.sudo().write({
                'cunsultancy_requested': consultancy_requested,
                'cunsultancy_name': consultancy_name,
                'cunsultancy_age': consultancy_age,
                'cunsultancy_sex': consultancy_sex,
                'cunsultancy_id': consultancy_ssn,
                'chief_complaint': chief,
                'diagnosis': diagnosis_1,
                'diagnosis_add2': diagnosis_2,
                'diagnosis_add3': diagnosis_3,
                'history': history,
                'weight': weight,
                'heart_rate': heart_rate,
                'o2_saturation': o2_saturation,
                'blood_sugar': blood_sugar,
                'blood_pressure_s': blood_pressure_s,
                'blood_pressure_d': blood_pressure_d,
                'respiration': respiration,
                'temperature': temperature,
                'recommendations': recommendations,
                'drug_allergy': drug_allergy,
                'drug_allergy_text': drug_allergy_text,
                'state': 'in_process',
                'other_prescription_1': other_prescription_1,
                'other_prescription_2': other_prescription_2,
                'other_prescription_3': other_prescription_3,

            })
            # self._update_patient(patient_id, drug_allergy, drug_allergy_text)
        else:
            return invalid_response('no_consultation_data',
                                    'Sorry, no consultation data with given consultation id %s' % consultation_id)

        # print(consultation_id, chief, drug_allergy, drug_allergy_text)
        data = {
            'consultation_id': consultation_id,
            # 'count_medicine': count_medicine,
            'message': 'Your data has been saved successfully',
        }
        return valid_response(data)

    @authenticate_token_portal
    @http.route(['/sehati/pharmacist/login'], type='http', auth="none", methods=['POST'],
                csrf=False, cors="*")
    def pharmacist_login(self, **post):
        model_name = 'sm.shifa.pharmacist'
        model = request.env[self._model].sudo().search([('model', '=', model_name)], limit=1)
        if model:
            try:
                username = post.get('username')
                password = post.get('password')
                if not username:
                    # throw error message if username is not provided
                    error_msg = 'username is missing'
                    return invalid_response('missing error', error_msg)
                if not password:
                    # throw error message if password is not provided
                    error_msg = 'password is missing'
                    return invalid_response('missing error', error_msg)

                count_pharmacist = request.env[model_name].sudo().search_count(
                    [('username', '=', username), ('password', '=', password)])

                if count_pharmacist > 0:
                    model = request.env[model_name].sudo().search([('username', '=', username)], limit=1)

                    data = {
                        'id': model.id,
                        'username': model.username,
                        'name': model.name,
                        'pharmacy_chain_id': model.pharmacy.institution.id,
                        'pharmacy_name': model.pharmacy.name,
                        'mobile': model.mobile,
                        'is_admin': model.is_admin,
                        'message': 'pharmacist logged in successfully!'
                    }

                    return valid_response(data)
                else:
                    return invalid_response('failed to login pharmacist',
                                            'No pharmacist found, please enter valid username and password.')
            except Exception as e:
                return invalid_response('failed to login pharmacist', str(e))

        return invalid_response('invalid object model', 'The model %s is not available in the registry.' % model_name)

    @authenticate_token_portal
    @http.route(['/sehati/patient/get-instant-prescription/<prescription_code>'], type='http', auth="none",
                methods=['GET'],
                csrf=False, cors="*")
    def get_patient_instant_prescription(self, prescription_code=None, **payload):
        model_name = 'sm.shifa.instant.prescriptions'
        model = request.env[self._model].sudo().search([('model', '=', model_name)], limit=1)
        payload[
            'fields'] = "['id', 'name', 'patient', 'sex', 'age', 'ssn', 'mobile', 'pharmacy_chain', 'diagnosis', 'diagnosis_add2', 'diagnosis_add3', 'other_prescription_1', 'other_prescription_1_done', 'other_prescription_2', 'other_prescription_2_done', 'other_prescription_3', 'other_prescription_3_done', 'recommendations']"
        # , 'inst_prescription_line'
        if model:
            domain, fields, offset, limit, order = extract_arguments(
                payload)
            domain = [('name', '=', str(prescription_code))]
            data = request.env[model.model].sudo().search_read(
                domain=domain, fields=fields, offset=offset, limit=limit, order=order)

            data_to_push = []
            patient_id = False
            pharmacist_name = False
            for x in data:
                for k, v in x.items():
                    if str(type(v)) in ("<class 'datetime.datetime'>", "<class 'datetime.date'>"):
                        date = v.strftime("%Y-%m-%d")  # %H:%M:%S
                        x[k] = str(date)
                    if str(k) == "patient":
                        if v and len(v) > 0:
                            patient_id = v[0]
                            x[k] = v[1]
                        else:
                            x[k] = ""
                    if str(k) == "diagnosis":
                        if v and len(v) > 0:
                            x[k] = v[1]
                        else:
                            x[k] = ""
                    if str(k) == "diagnosis_add2":
                        if v and len(v) > 0:
                            x[k] = v[1]
                        else:
                            x[k] = ""
                    if str(k) == "diagnosis_add3":
                        if v and len(v) > 0:
                            x[k] = v[1]
                        else:
                            x[k] = ""
                    if str(k) == "pharmacy_chain":
                        if v and len(v) > 0:
                            pharmacy_chain = v[0]
                            pharmacist = request.env['sm.shifa.pharmacist'].sudo().search(
                                [('institution', '=', int(pharmacy_chain))], limit=1)
                            if pharmacist:
                                pharmacist_name = pharmacist.name
                # other_prescription_1_done
                x['patient_id'] = patient_id
                x['pharmacist'] = pharmacist_name
                data_to_push.append(x)
                # patient_obj
            return valid_response(data_to_push)
        return invalid_response('invalid object model', 'The model %s is not available in the registry.' % model_name)

    @authenticate_token_portal
    @http.route(['/sehati/patient/get-instant-prescription'], type='http', auth="none",
                methods=['POST'],
                csrf=False, cors="*")
    def get_patient_instant_prescription_for_pharmacy_chain(self, **post):
        model_name = 'sm.shifa.instant.prescriptions'
        model = request.env[self._model].sudo().search([('model', '=', model_name)], limit=1)
        post[
            'fields'] = "['id', 'name', 'patient', 'sex', 'age', 'ssn', 'mobile', 'pharmacy_chain', 'diagnosis', 'diagnosis_add2', 'diagnosis_add3', 'other_prescription_1', 'other_prescription_1_done', 'other_prescription_2', 'other_prescription_2_done', 'other_prescription_3', 'other_prescription_3_done', 'recommendations']"

        prescription_code = post.get('prescription_code')
        if not prescription_code:
            return invalid_response('prescription_code_req', 'Prescription code is required ')

        pharmacy_chain_id = post.get('pharmacy_chain_id')

        if model:
            domain, fields, offset, limit, order = extract_arguments(
                post)
            # domain = [('name', '=', str(prescription_code))]
            domain = [('name', '=', str(prescription_code)), ('pharmacy_chain', 'in', [pharmacy_chain_id, False])]
            data = request.env[model.model].sudo().search_read(
                domain=domain, fields=fields, offset=offset, limit=limit, order=order)

            data_to_push = []
            patient_id = False
            pharmacist_name = False
            for x in data:
                for k, v in x.items():
                    if str(type(v)) in ("<class 'datetime.datetime'>", "<class 'datetime.date'>"):
                        date = v.strftime("%Y-%m-%d")  # %H:%M:%S
                        x[k] = str(date)
                    if str(k) == "patient":
                        if v and len(v) > 0:
                            patient_id = v[0]
                            x[k] = v[1]
                        else:
                            x[k] = ""
                    if str(k) == "diagnosis":
                        if v and len(v) > 0:
                            x[k] = v[1]
                        else:
                            x[k] = ""
                    if str(k) == "diagnosis_add2":
                        if v and len(v) > 0:
                            x[k] = v[1]
                        else:
                            x[k] = ""
                    if str(k) == "diagnosis_add3":
                        if v and len(v) > 0:
                            x[k] = v[1]
                        else:
                            x[k] = ""
                    if str(k) == "pharmacy_chain":
                        if v and len(v) > 0:
                            pharmacy_chain = v[0]
                            print("pharmacy_chain: ", str(pharmacy_chain))
                            pharmacist = request.env['sm.shifa.pharmacist'].sudo().search(
                                [('institution', '=', int(pharmacy_chain))], limit=1)
                            if pharmacist:
                                pharmacist_name = pharmacist.name

                # other_prescription_1_done
                x['patient_id'] = patient_id
                x['pharmacist'] = pharmacist_name
                data_to_push.append(x)
                # patient_obj
            return valid_response(data_to_push)
        return invalid_response('invalid object model', 'The model %s is not available in the registry.' % model_name)

    @authenticate_token_portal
    @http.route(['/sehati/patient/get-medicine-list/<prescription_id>'], type='http', auth="none", methods=['GET'],
                csrf=False, cors="*")
    def get_patient_medicine_list(self, prescription_id=None, **payload):
        model_name = 'sm.shifa.prescription.line'
        model = request.env[self._model].sudo().search([('model', '=', model_name)], limit=1)
        payload[
            'fields'] = "['pharmacy_medicines', 'pharmacy_generic', 'strength', 'strength_unit', 'dose', 'dose_unit', 'dose_form', 'dose_route', 'common_dosage', 'duration', 'frequency_unit', 'info', 'qty', 'dispensed']"

        if model:
            domain, fields, offset, limit, order = extract_arguments(
                payload)
            domain = [('inst_prescription_extra_ids', '=', int(prescription_id))]
            data = request.env[model.model].sudo().search_read(
                domain=domain, fields=fields, offset=offset, limit=limit, order=order)

            data_to_push = []
            for x in data:
                for k, v in x.items():
                    if str(k) == "dose_form":
                        if v and len(v) > 0:
                            x[k] = v[1]
                        else:
                            x[k] = ""
                    if str(k) == "common_dosage":
                        if v and len(v) > 0:
                            x[k] = v[1]
                        else:
                            x[k] = ""
                    if str(k) == "dose_unit":
                        if v and len(v) > 0:
                            x[k] = v[1]
                        else:
                            x[k] = ""
                    if str(k) == "dose_route":
                        if v and len(v) > 0:
                            x[k] = v[1]
                        else:
                            x[k] = ""
                    if str(k) == "strength_unit":
                        if v and len(v) > 0:
                            x[k] = v[1]
                        else:
                            x[k] = ""

                data_to_push.append(x)
                # patient_obj
            return valid_response(data_to_push)
        return invalid_response('invalid object model', 'The model %s is not available in the registry.' % model_name)

    @authenticate_token_portal
    @http.route(['/sehati/patient/update-medicine'], type='http', auth="none", methods=['POST'],
                csrf=False, cors="*")
    def update_prescription_medicine(self, **post):
        model_name = 'sm.shifa.prescription.line'
        m_list = post.get('medicine_list')
        prescription_id = post.get('prescription_id')

        if not m_list:
            return invalid_response('json_data_not_found', 'json data not found in request ! ')

        if not prescription_id:
            return invalid_response('prescription_id_not_found', 'prescription id not found in request ! ')

        try:
            m_list = json.loads(m_list)
            print(m_list)
            for item in m_list:
                print(item['pharmacy_medicine'])
                prescription = request.env[model_name].sudo().search(
                    [('pharmacy_medicines', '=', int(item['pharmacy_medicine']))], limit=1)
                prescription.sudo().write({
                    'dispensed': bool(item['dispensed']),
                })

            data = {
                'message': 'Your medicine list has been updated successfully',
            }
            return valid_response(data)

        except Exception as e:
            return invalid_response('error', e)
        return invalid_response('invalid object model', 'The model %s is not available in the registry.' % model_name)

    def _update_patient(self, patient_id, drug_allergy, drug_allergy_text):
        patient_model = 'oeh.medical.patient'
        patient_count = request.env[patient_model].sudo().search_count([('id', '=', int(patient_id))])
        if patient_count:
            patient = request.env[patient_model].sudo().browse(int(patient_id))
            patient.sudo().write({
                'drug_allergy': drug_allergy,
                'drug_allergy_content': drug_allergy_text,
            })

    def _add_new_medicine(self, pharmacy_medicine, strength, strength_unit, dose, dose_unit, dose_form, dose_route,
                          common_dosage, duration,
                          duration_unit, consultation_id, other_instruction):
        # pharmacy_medicine_count = request.env['sm.shifa.prescription.line'].sudo().search_count([('pharmacy_medicines', '=', int(pharmacy_medicine))])
        # if pharmacy_medicine_count == 0:
        request.env['sm.shifa.prescription.line'].sudo().create({
            'pharmacy_medicines': int(pharmacy_medicine),
            'strength': strength,
            'strength_unit': int(strength_unit),
            'dose': dose,
            'dose_unit': int(dose_unit),
            'dose_form': dose_form,
            'dose_route': dose_route,
            'common_dosage': common_dosage,
            'duration': duration,
            'frequency_unit': duration_unit,
            'prescription_extra_ids': consultation_id,
            'info': other_instruction,
        })

    def _create_jitsi_meeting(self, consultation_id):
        server_url = request.env['ir.config_parameter'].sudo().get_param('oehealth_jitsi.video_call_server_url')
        appointment = request.env['sm.shifa.instant.consultation'].sudo().browse(int(consultation_id))
        meeting_link = server_url + '/' + str(uuid.uuid4()).replace('-', '')
        invitation_text = _("<a href='%s' target='_blank'>Click here to start meeting</a>") % meeting_link
        appointment.write({
            'invitation_text_jitsi': invitation_text,
            'jitsi_link': meeting_link,
        })
        return meeting_link

    @authenticate_token
    @http.route(['/sehati/instant/update-evaluation'], type='http', auth="none", methods=['POST'],
                csrf=False, cors="*")
    def update_instant_evaluation(self, **post):
        model_name = 'sm.shifa.instant.consultation'

        if not 'consultation_id' in post:
            return invalid_response('consultation_id not found', 'consultation id not found in request ! ')

        if not 'evaluation' in post:
            return invalid_response('evaluation not found', 'evaluation not found in request ! ')

        try:
            consultation_id = post.get('consultation_id')
            evaluation = post.get('evaluation')
            consultation = request.env[model_name].sudo().search([('id', '=', int(consultation_id))], limit=1)
            model = consultation.sudo().write({
                'evaluation': str(evaluation),
                'state': 'completed',
            })
            data = {
                'evaluation': evaluation,
                'message': 'Your data has been updated successfully',
            }
            return valid_response(data)

        except Exception as e:
            return invalid_response('error', e)
        return invalid_response('invalid object model', 'The model %s is not available in the registry.' % model_name)

    @authenticate_token_portal
    @http.route(['/sehati/instant/set-done'], type='http', auth="none", methods=['POST'],
                csrf=False, cors="*")
    def set_instant_consultation_done(self, **post):
        data = post.get('json_data')
        if not data:
            return invalid_response('json_data_not_found', 'json data not found in request ! ')
        try:
            data = json.loads(data)
        except BaseException as ex:
            return invalid_response('error_json_data', ex)

        res = {}
        for i in data.items():
            res[i[0]] = i[1]

        action = False
        pres_model = 'sm.shifa.instant.prescriptions'
        prescription_code = res['prescription_code']
        pharmacist_id = res['pharmacist_id']
        print('prescription_code: ', str(prescription_code))
        print('pharmacist_id: ', str(pharmacist_id))
        print(res)
        prescription_count = request.env[pres_model].sudo().search_count([('name', '=', prescription_code)])
        if prescription_count > 0:
            prescription = request.env[pres_model].sudo().search([('name', '=', prescription_code)], limit=1)
            prescription.sudo().write({
                'done': True,
                'other_prescription_1': str(res['other_prescription_1']),
                'other_prescription_1_done': bool(res['other_prescription_1_done']),
                'other_prescription_2': str(res['other_prescription_2']),
                'other_prescription_2_done': bool(res['other_prescription_2_done']),
                'other_prescription_3': str(res['other_prescription_3']),
                'other_prescription_3_done': bool(res['other_prescription_3_done']),
                'state': 'send',
            })

            pharmacist = request.env['sm.shifa.pharmacist'].sudo().search([('id', '=', int(pharmacist_id))],
                                                                          limit=1)
            other_presc_1 = other_presc_2 = other_presc_3 = False
            # res(['other_prescription_1']).replace("False", "")
            # res(['other_prescription_2']).replace("False", "")
            # res(['other_prescription_3']).replace("False", "")

            if str(res['other_prescription_1']).strip() and str(res['other_prescription_1']) and str(
                    res['other_prescription_1']) != 'False':
                other_presc_1 = self.save_other_prescription(bool(res['other_prescription_1_done']),
                                                             str(res['other_prescription_1']), prescription.doctor.name,
                                                             pharmacist, prescription_code)

            if str(res['other_prescription_2']).strip() and str(res['other_prescription_2']) and str(
                    res['other_prescription_2']) != 'False':
                other_presc_2 = self.save_other_prescription(bool(res['other_prescription_2_done']),
                                                             str(res['other_prescription_2']), prescription.doctor.name,
                                                             pharmacist, prescription_code)

            if str(res['other_prescription_3']).strip() and str(res['other_prescription_3']) and str(
                    res['other_prescription_3']) != 'False':
                other_presc_3 = self.save_other_prescription(bool(res['other_prescription_3_done']),
                                                             str(res['other_prescription_3']), prescription.doctor.name,
                                                             pharmacist, prescription_code)
            history_medicine = []
            for ml in res['medicines']:
                medicine_model = 'sm.shifa.prescription.line'
                # update medicine
                medicine = request.env[medicine_model].sudo().browse(int(ml['id']))
                if medicine:
                    medicine.write({
                        'dispensed': bool(ml['dispensed'])
                    })
                    medicine_name = str(ml['pharmacy_medicines'])
                    self.save_history_data(medicine_name,
                                           pharmacist.name,
                                           pharmacist.pharmacy.name,
                                           pharmacist.pharmacy.institution.name,
                                           prescription.doctor.name, bool(ml['dispensed']),
                                           prescription.name)
                    history_medicine.append(medicine_name)

            history = {
                'other_prescription_1': other_presc_1,
                'other_prescription_2': other_presc_2,
                'other_prescription_3': other_presc_3,
                'medicine_list': history_medicine,
            }

            data = {
                'history': history,
                'message': 'Your data has been updated successfully',
            }
            return valid_response(data)
        else:
            return invalid_response('prescription_code not found in db',
                                    'prescription code not found in database, please select another number! ')

    @authenticate_token_portal
    @http.route(['/sehati/patient/get-instant-consultation-url/<consultation_code>'], type='http',
                auth="none",
                methods=['GET'],
                csrf=False, cors="*")
    def get_patient_instant_consultation_url(self, consultation_code=None):
        model_name = 'sm.shifa.instant.consultation'
        if consultation_code:
            found = request.env[model_name].sudo().search_count(
                [('name', '=', str(consultation_code))])
            if found:
                consultation = request.env[model_name].sudo().search(
                    [('name', '=', str(consultation_code))], limit=1)
                data = {
                    'file_url': consultation.link
                }
                return valid_response(data)
            else:
                return invalid_response('missing error',
                                        'There is no data to show for given consultation code')

        else:
            return invalid_response('missing error', 'There is no patient with given consultation code and patient id')
        return invalid_response('invalid object model', 'The model %s is not available in the registry.' % model_name)

    @authenticate_token
    @http.route(['/sehati/instant/update-fcm-token'], type='http', auth="none", methods=['POST'],
                csrf=False, cors="*")
    def update_fcm_token(self, **post):
        fcm_token = post.get('fcm_token')
        device_type = post.get('device_type')
        req_type = post.get('type')
        req_id = post.get('id')

        if not fcm_token:
            return invalid_response('missing error', 'fcm_token is missing in request')
        if not device_type:
            return invalid_response('missing error',
                                    'device_type is missing in request, must contain [ios] or [android]')
        if not req_type:
            return invalid_response('missing error',
                                    'req_type is missing in request, please put [1] for patient or [2] for doctor')
        if not req_id:
            return invalid_response('missing error', 'id missing in request')

        try:
            action = False
            if req_type == '1':
                patient = request.env['oeh.medical.patient'].sudo().browse(int(req_id))
                if patient:
                    patient.write({
                        'patient_fcm_token': fcm_token,
                        'device_type': device_type,
                    })
                    action = True
            elif req_type == '2':
                doctor = request.env['oeh.medical.physician'].sudo().browse(int(req_id))
                if doctor:
                    doctor.write({
                        'doctor_fcm_token': fcm_token,
                        'device_type': device_type,
                    })
                    action = True

            data = {}
            if action:
                data = {
                    'action': action,
                    'message': 'Your data has been updated successfully',
                }
            else:
                data = {
                    'action': action,
                    'message': 'No action has been done on your data.',
                }

            return valid_response(data)
        except Exception as e:
            return invalid_response('error', e)
        return invalid_response('invalid object model', 'The model %s is not available in the registry.' % model_name)

    @authenticate_token_portal
    @http.route(['/sehati/patient/get-history-prescription/<prescription_code>'], type='http', auth="none",
                methods=['GET'],
                csrf=False, cors="*")
    def get_patient_history_prescription(self, prescription_code=None, **payload):
        model_name = 'sm.shifa.instant.prescriptions.history'
        model = request.env[self._model].sudo().search([('model', '=', model_name)], limit=1)
        payload[
            'fields'] = "['id', 'medicine_name', 'pharmacist', 'pharmacy', 'doctor', 'dispensed', 'pharmacy_chain', 'prescription_code', 'date']"

        if model:
            domain, fields, offset, limit, order = extract_arguments(
                payload)
            domain = [('prescription_code', '=', str(prescription_code))]
            data = request.env[model.model].sudo().search_read(
                domain=domain, fields=fields, offset=offset, limit=limit, order=order)

            data_to_push = []
            patient_id = False
            pharmacist_name = False
            for x in data:
                for k, v in x.items():
                    if str(type(v)) in ("<class 'datetime.datetime'>", "<class 'datetime.date'>"):
                        date = v.strftime("%Y-%m-%d")  # %H:%M:%S
                        x[k] = str(date)

                data_to_push.append(x)
            return valid_response(data_to_push)
        return invalid_response('invalid object model', 'The model %s is not available in the registry.' % model_name)

    @authenticate_token
    @http.route(['/sehati/pharmacy-strength-unit'], type='http', auth="none", methods=['GET'], csrf=False)
    def get_pharmacy_strength_unit(self, **payload):

        model_name = 'sm.medical.strength.units'
        model = request.env[self._model].sudo().search([('model', '=', model_name)], limit=1)
        payload[
            'fields'] = "['id', 'name', 'desc',]"

        if model:
            domain, fields, offset, limit, order = extract_arguments(
                payload)
            data = request.env[model.model].sudo().search_read(
                domain=domain, fields=fields, offset=offset, limit=limit, order=order)

            data_to_push = []
            for x in data:
                for k, v in x.items():
                    if str(k) == "name":
                        if v and len(v) > 0:
                            x[k] = v
                        else:
                            x[k] = ""
                    if str(k) == "desc":
                        if v and len(v) > 0:
                            x[k] = v
                        else:
                            x[k] = ""

                data_to_push.append(x)

            return valid_response(data_to_push)
        return invalid_response('invalid object model', 'The model %s is not available in the registry.' % model_name)

    # save medicines prescription in history table
    def save_other_prescription(self, action, other_pres_name, doctor, pharmacist, pres_code):
        # if other_pres_name.strip() and other_pres_name:
        self.save_history_data(other_pres_name, pharmacist.name,
                               pharmacist.pharmacy.name, pharmacist.pharmacy.institution.name, doctor, action,
                               pres_code)

        return action

    def save_history_data(self, medicine, pharmacist, pharmacy, pharmacy_chain, doctor, dispensed, prescription_code):
        model_name = 'sm.shifa.instant.prescriptions.history'
        values = {
            'medicine_name': medicine,
            'pharmacist': pharmacist,
            'pharmacy': pharmacy,
            'pharmacy_chain': pharmacy_chain,
            'doctor': doctor,
            'dispensed': dispensed,
            'prescription_code': prescription_code,
            'date': datetime.datetime.now(),
        }
        request.env[model_name].sudo().create(values)
        return True

    # api for medicine units
    @authenticate_token
    @http.route(['/sehati/pharmacy/get-medicine-units'], type='http', auth="none", methods=['GET'],
                csrf=False)
    def get_medicine_units(self, **payload):

        object_list = {}
        # pharmacy medicines list
        medicine_row = request.env['sm.shifa.pharmacy.medicines'].sudo().search([])
        pharmacy_medicine = []
        for i in medicine_row:
            medicine = {
                'id': int(i.id),
                'pharmacy_medicines': i.pharmacy_medicines,
                'generic_medicine': i.generic_medicine,
                'code': i.code,
            }
            pharmacy_medicine.append(medicine)
        object_list['pharmacy_medicine'] = pharmacy_medicine
        # dose units list
        dose_row = request.env['oeh.medical.dose.unit'].sudo().search([])
        dose_units = []
        for i in dose_row:
            dose = {
                'id': int(i.id),
                'name': i.name,
                'desc': i.desc,
            }
            dose_units.append(dose)
        object_list['dose_unit'] = dose_units
        # strength units list
        strength_row = request.env['sm.medical.strength.units'].sudo().search([])
        strength_units = []
        for i in strength_row:
            dose = {
                'id': int(i.id),
                'name': i.name,
                'desc': i.desc,
            }
            strength_units.append(dose)
        object_list['strength_unit'] = strength_units
        # dose_route list
        dose_route_row = request.env['oeh.medical.drug.route'].sudo().search([])
        dose_route = []
        for i in dose_route_row:
            route = {
                'id': int(i.id),
                'name': i.name,
                'code': i.code,
            }
            dose_route.append(route)
        object_list['dose_route'] = dose_route
        # dose_form list
        dose_form_row = request.env['oeh.medical.drug.form'].sudo().search([])
        dose_form = []
        for i in dose_form_row:
            form = {
                'id': int(i.id),
                'name': i.name,
                'code': i.code,
            }
            dose_form.append(form)
        object_list['dose_form'] = dose_form
        # common_dosage list
        common_dosage_row = request.env['oeh.medical.dosage'].sudo().search([])
        common_dosage = []
        for i in common_dosage_row:
            dosage = {
                'id': int(i.id),
                'name': i.name,
                'code': i.code,
            }
            common_dosage.append(dosage)
        object_list['common_dosage'] = common_dosage
        return valid_response(object_list)

    @authenticate_token_portal
    @http.route(['/sehati/pharmacy/view-pharmacy-history-list'], type='http', auth="none", methods=['POST'],
                csrf=False, cors="*")
    def view_pharmacy_list(self, **post):
        model_name = 'sm.shifa.instant.prescriptions.history'
        model = request.env[self._model].sudo().search([('model', '=', model_name)], limit=1)
        post[
            'fields'] = "['id', 'medicine_name', 'pharmacist', 'pharmacy', 'pharmacy_chain', 'doctor', 'dispensed', 'prescription_code', 'date']"

        username = post.get('username')
        # password = post.get('password')
        from_date = post.get('from_date')
        to_date = post.get('to_date')

        if not username:
            return invalid_response('username_not_found', 'username field is required!')
        # if not password:
        #     return invalid_response('password_not_found', 'password field is required!')
        if not from_date:
            return invalid_response('from_date_not_found', 'from_date field is required!')
        if not to_date:
            return invalid_response('to_date_not_found', 'to_date field is required!')

        if model:
            pharmacist_domain = [('username', '=', username)]  # , ('password', '=', password)
            count = request.env['sm.shifa.pharmacist'].sudo().search_count(pharmacist_domain)
            if count > 0:
                pharmacist = request.env['sm.shifa.pharmacist'].sudo().search(pharmacist_domain, limit=1)
                domain, fields, offset, limit, order = extract_arguments(post)

                if pharmacist.is_admin:
                    print('admin')
                    domain = [('date', '>=', from_date), ('date', '<=', to_date),
                              ('pharmacy_chain', '=', pharmacist.institution.name)]
                else:
                    print('user')
                    domain = [('date', '>=', from_date), ('date', '<=', to_date),
                              ('pharmacy', '=', pharmacist.pharmacy.name)]

                data = request.env[model.model].sudo().search_read(
                    domain=domain, fields=fields, offset=offset, limit=limit, order=order)

                data_to_push = []
                for x in data:
                    for k, v in x.items():
                        if str(type(v)) in ("<class 'datetime.datetime'>", "<class 'datetime.date'>"):
                            x[k] = str(v)
                    data_to_push.append(x)
                return valid_response(data_to_push)
            else:
                return invalid_response('username_not_valid', 'username or password is not valid')
        else:
            return invalid_response('model_not_found', 'We are working on upgrade this HIS, thanks for using this service')
