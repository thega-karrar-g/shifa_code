from odoo import http, _
from odoo.http import request
from datetime import datetime

from odoo.addons.oehealth.oeh_rest_api.common_methods import invalid_response, valid_response, convert_utc_to_local, extract_arguments
from odoo.addons.oehealth.oeh_rest_api.controllers.main import authenticate_token
from odoo.addons.oehealth.oeh_rest_api.shared_methods import SmartMindSharedMethods

import logging

_logger = logging.getLogger(__name__)


class SmSleepMedicineRequestController(http.Controller, SmartMindSharedMethods):
    date_format = "%Y-%m-%d"
    error_message = 'We apologize, but an unexpected error occurred. Please try again later.'

    @authenticate_token
    @http.route(['/sehati/create-sleep-medicine-request'], type='http', auth="none", methods=['POST'],
                csrf=False)
    def create_sleep_medicine_request(self, **post):
        # Check required fields
        patient_id = post.get('patient_id')
        if not patient_id:
            return invalid_response('patient_id not found', 'Patient ID not found in request!')

        date = post.get('date')
        if not date:
            return invalid_response('date not found', 'Date not found in request!')

        service_id = post.get('service_id')
        if not service_id:
            return invalid_response('service_id not found', 'Service ID not found in request!')

        try:
            patient_id = int(patient_id)
            service_id = int(service_id)
            appointment_date = datetime.strptime(date, self.date_format)

            # Validate patient
            patient = request.env['oeh.medical.patient'].sudo().browse(patient_id)
            if not patient.exists():
                return invalid_response('invalid patient_id', 'Invalid Patient ID!')

            # Validate service
            service = request.env['sm.shifa.service'].sudo().search(
                [('id', '=', service_id), ('service_type', '=', 'SM')], limit=1)
            if not service:
                return invalid_response('invalid service_id',
                                        'Invalid Service ID or service type is not Sleep Medicine!')

            values = {
                'patient_id': patient_id,
                'date': appointment_date,
                'service_id': service_id,
                'service_price': service.list_price,
                'payment_made_through': 'mobile',
                'state': 'unpaid',
            }
            # Add optional fields if provided
            house_location = post.get('house_location')
            if house_location:
                values['house_location'] = house_location

            house_number = post.get('house_number')
            if house_number:
                values['house_number'] = house_number

            branch = post.get('branch')
            if branch:
                values['branch'] = branch

            discount_id = post.get('discount_id')
            if discount_id:
                discount = request.env['sm.shifa.discounts'].sudo().browse(int(discount_id))
                if discount.exists() and discount.state == 'Active':
                    values['discount_id'] = int(discount_id)
                else:
                    return invalid_response('invalid discount_id', 'Invalid or inactive discount ID!')

            created_obj = request.env['sm.sleep.medicine.request'].sudo().create(values)
            added_to_request = self._add_service_request(patient_id, service_id, appointment_date)

            data = {
                'id': created_obj.id,
                'service request id': added_to_request.id,
                'message': 'Your data has been created successfully!',
            }
            return valid_response(data)

        except Exception as e:
            _logger.error('ERROR: %s', str(e))
            return invalid_response('Error', self.error_message)

    @authenticate_token
    @http.route(['/sehati/create-caregiver-contract'], type='http', auth="none", methods=['POST'], csrf=False)
    def create_caregiver_contract(self, **post):
        patient_id = post.get('patient_id')
        if not patient_id:
            return invalid_response('patient_id not found', 'Patient ID not found in request!')

        date = post.get('date')
        if not date:
            return invalid_response('date not found', 'Date not found in request!')

        service_id = post.get('service_id')
        if not service_id:
            return invalid_response('service_id not found', 'Service ID not found in request!')

        no_caregiver = post.get('no_caregiver')
        if not no_caregiver:
            return invalid_response('no_caregiver not found', 'Number of Caregiver not found in request!')

        additional_service_code = post.get('additional_service_id')
        try:
            patient_id = int(patient_id)
            service_id = int(service_id)
            no_caregiver = str(no_caregiver)
            appointment_date = datetime.strptime(date, self.date_format)

            # Validate patient
            patient = request.env['oeh.medical.patient'].sudo().browse(patient_id)
            if not patient.exists():
                return invalid_response('Invalid Patient', 'Patient ID not found.')

            # Validate service
            service = request.env['sm.shifa.service'].sudo().search(
                [('id', '=', service_id), ('service_type', '=', 'Car')], limit=1)
            if not service:
                return invalid_response('Invalid Service', 'Service ID not found or not of type Caregiver.')

            # Validate number of caregivers
            if no_caregiver not in ['1', '2', '3']:
                return invalid_response('Invalid Number of Caregivers',
                                        'Please select a valid number of caregivers (1, 2, or 3).')

            
            values = {
                'name': request.env.ref('sm_caregiver.sequence_caregiver_contract_request').next_by_id(),
                'patient_id': patient_id,
                'date': appointment_date,
                'service_id': service_id,
                'payment_made_through': 'mobile',
                'no_caregiver': no_caregiver,
                'state': 'unpaid',
            }

            if additional_service_code:
                values['additional_service_id'] = request.env['sm.shifa.instant.consultancy.charge'].sudo().search([
                    ('code','=',additional_service_code)
                ],limit=1).product_id.id

            # Optional fields
            house_location = post.get('house_location')
            if house_location:
                values['house_location'] = house_location

            house_number = post.get('house_number')
            if house_number:
                values['house_number'] = house_number

            branch = post.get('branch')
            if branch:
                values['branch'] = branch

            discount_id = post.get('discount_id')
            if discount_id:
                discount = request.env['sm.shifa.discounts'].sudo().browse(int(discount_id))
                if discount.exists() and discount.state == 'Active':
                    values['discount_id'] = int(discount_id)
                else:
                    return invalid_response('Invalid Discount', 'Invalid or inactive discount ID.')

            # Create the record
            created_obj = request.env['sm.caregiver.contracts'].sudo().with_context(from_api=True).create(values)
            created_obj.onchange_service()
            added_to_request = self._add_service_request(patient_id, service_id, appointment_date)

            data = {
                'id': created_obj.id,
                'service request id': added_to_request.id,
                'message': 'Your data has been created successfully!',
            }
            return valid_response(data)


        except Exception as e:
            _logger.error('ERROR: %s', str(e))
            return invalid_response('Error', self.error_message)

    def _add_service_request(self, patient_id, service, date):
        vals = {'patient': patient_id, 'service': service, 'date': date}
        return request.env['sm.shifa.service.request'].sudo().create(vals)

    @authenticate_token
    @http.route(['/sehati/sleep-medicine-request/add-questioner'], type='http', auth="none", methods=['POST'],
                csrf=False)
    def save_sleep_medicine_req_questioner(self, **post):
        model_id = post.get('id')
        if not model_id:
            return invalid_response('id not found', 'id not found in request! ')

        try:
            values = {}
            model_obj = request.env['sm.sleep.medicine.request'].sudo().browse(int(model_id))
            if not model_obj:
                return invalid_response('invalid id', 'NO data is found with the given ID.')

            weight = post.get('weight')
            if weight:
                values['weight'] = weight

            height = post.get('height')
            if height:
                values['height'] = height

            is_snore = post.get('question1')
            if is_snore:
                values['is_snore'] = is_snore

            question2 = post.get('question2')
            if question2:
                values['has_not_feeling_slept'] = question2

            question3 = post.get('question3')
            if question3:
                values['is_stop_breathing'] = question3

            question4 = post.get('question4')
            if question4:
                values['is_high_blood_pressure'] = question4

            is_male = post.get('question5')
            if is_male:
                values['is_male'] = is_male

            is_50years_older = post.get('question6')
            if is_50years_older:
                values['is_50years_older'] = is_50years_older

            comment = post.get('comment')
            if comment:
                values['comment'] = comment

            model_obj.sudo().write(values)

            data = {
                'id': model_obj.id,
                'message': 'Your data has been saved successfully!'
            }
            return valid_response(data)

        except Exception as e:
            return invalid_response('error', e)

    @authenticate_token
    @http.route(['/sehati/caregiver-contracts/add-questioner'], type='http', auth="none", methods=['POST'],
                csrf=False)
    def save_caregiver_req_questioner(self, **post):
        model_id = post.get('id')
        if not model_id:
            return invalid_response('id not found', 'id not found in request! ')

        try:
            values = {}
            model_obj = request.env['sm.caregiver.contracts'].sudo().browse(int(model_id))
            if not model_obj:
                return invalid_response('invalid id', 'NO data is found with the given ID.')

            is_snore = post.get('question1')
            if is_snore:
                values['is_patient_conscious'] = is_snore

            question2 = post.get('question2')
            ques2_yes_text = post.get('ques2_yes_text')

            if question2:
                values['have_chronic_diseases'] = question2
                if question2 == "yes":
                    values['mention_diseases'] = ques2_yes_text

            question3 = post.get('question3')
            if question3:
                values['use_insulin_needles'] = question3

            question4 = post.get('question4')
            if question4:
                values['can_move_or_seated'] = question4

            question5 = post.get('question5')
            if question5:
                values['eat_food_or_tube'] = question5

            question6 = post.get('question6')
            if question6:
                values['is_laryngeal_cleft'] = question6

            question7 = post.get('question7')
            if question7:
                values['use_oxygen_inhaled_medications'] = question7

            question8 = post.get('question8')
            if question8:
                values['have_any_catheter'] = question8

            question9 = post.get('question9')
            if question9:
                values['wounds_diabetic_bed_sores'] = question9

            question10 = post.get('question10')
            if question10:
                values['wear_diapers'] = question10

            comment = post.get('comment')
            if comment:
                values['comment'] = comment

            model_obj.sudo().write(values)

            data = {
                'id': model_obj.id,
                'message': 'Your data has been saved successfully!'
            }
            return valid_response(data)

        except Exception as e:
            return invalid_response('error', e)

    @authenticate_token
    @http.route(['/sehati/get-sleep-medicine-request-list/<patient_id>'], type='http', auth="none", methods=['GET'],
                csrf=False)
    def get_sleep_medicine_request_list(self, patient_id=None):
        if not patient_id:
            return invalid_response('patient_id not found', 'Patient ID not found in request!')
        try:
            m_list = request.env['sm.sleep.medicine.request'].sudo().search(
                [('patient_id', '=', int(patient_id)), ('state', '!=', 'draft')],
                order="date desc")
        except Exception as e:
            return invalid_response("INF_O5: {0}".format(self.error_message))

        success_data = [{
            'id': rec.id,
            'name': rec.name,
            'patient': {'id': rec.patient_id.id, 'name': rec.patient_id.name, 'mobile': rec.patient_id.mobile},
            'date': str(rec.date),
            'state': rec.state,
            'service': {'id': rec.service_id.id, 'name': rec.service_id.name, 'price': rec.service_id.list_price},
            'height': rec.height,
            'weight': rec.weight,
            'bmi': rec.bmi,
            'question1': rec.is_snore if rec.is_snore else "",
            'question2': rec.has_not_feeling_slept if rec.has_not_feeling_slept else "",
            'question3': rec.is_stop_breathing if rec.is_stop_breathing else "",
            'question4': rec.is_high_blood_pressure if rec.is_high_blood_pressure else "",
            'question5': rec.is_male if rec.is_male else "",
            'question6': rec.is_50years_older if rec.is_50years_older else "",
            'comment': rec.comment if rec.comment else "",
            'jitsi_link': rec.jitsi_link if rec.jitsi_link else "",
            'appointment_date': str(rec.appointment_date),

        } for rec in m_list]

        return valid_response(success_data)

    @authenticate_token
    @http.route(['/sehati/get-caregiver-contracts-list/<patient_id>'], type='http', auth="none", methods=['GET'],
                csrf=False)
    def get_sm_caregiver_contracts_list(self, patient_id=None):
        if not patient_id:
            return invalid_response('patient_id not found', 'Patient ID not found in request!')

        try:
            m_list = request.env['sm.caregiver.contracts'].sudo().search(
                [('patient_id', '=', int(patient_id)), ('state', '!=', 'draft')],
                order="date desc")
        except Exception as e:
            return invalid_response(f"INF_O6: {str(e)}")
        
        success_data = []
        
        for rec in m_list:
            pdf_link = self.get_attachment_pdf(rec._name, rec.id, rec.name, rec.date)
            
            success_data.append({
                'id': rec.id,
                'name': rec.name,
                'patient': {
                    'id': rec.patient_id.id, 
                    'name': rec.patient_id.name, 
                    'mobile': rec.patient_id.mobile
                },
                'date': str(rec.date),
                'starting_date': str(rec.starting_date) if rec.starting_date else "",
                'ending_date': str(rec.ending_date) if rec.ending_date else "",
                'state': rec.state,
                'service': {
                    'id': rec.service_id.id,
                    'name': rec.service_id.name,
                    'price': rec.service_id.list_price
                },
                'question1': rec.is_patient_conscious if rec.is_patient_conscious else "",
                'question2': rec.have_chronic_diseases if rec.have_chronic_diseases else "",
                'question2_text': rec.mention_diseases if rec.mention_diseases else "",
                'question3': rec.use_insulin_needles if rec.use_insulin_needles else "",
                'question4': rec.can_move_or_seated if rec.can_move_or_seated else "",
                'question5': rec.eat_food_or_tube if rec.eat_food_or_tube else "",
                'question6': rec.is_laryngeal_cleft if rec.is_laryngeal_cleft else "",
                'question7': rec.use_oxygen_inhaled_medications if rec.use_oxygen_inhaled_medications else "",
                'question8': rec.have_any_catheter if rec.have_any_catheter else "",
                'question9': rec.wounds_diabetic_bed_sores if rec.wounds_diabetic_bed_sores else "",
                'question10': rec.wear_diapers if rec.wear_diapers else "",
                'comment': rec.comment if rec.comment else "",
                'jitsi_link': rec.jitsi_link if rec.jitsi_link else "",
                'pdf_link': rec.link or "",
            })

        return valid_response(success_data)


    def get_attachment_pdf(self, mo_name, res_id, name, date):
        try:
            url_date = convert_utc_to_local(date.strftime("%Y-%m-%d %H:%M:%S"))
            domain = [('res_model', '=', mo_name), ('res_id', '=', res_id)]
            fields = ['name', 'access_token', 'res_id']
            
            data = request.env['ir.attachment'].sudo().search_read(domain=domain, fields=fields, limit=1)
            if data:
                record = data[0]
                config_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
                pdf_link = f"{config_url}/web/attachments/token/{record['access_token']}"
                return pdf_link
            return None
        except Exception as e:
            return None


    @authenticate_token
    @http.route(['/sehati/update-caregiver-contracts'], type='http', auth="none", methods=['POST'],
                csrf=False)
    def update_caregiver_contracts_state(self, **post):
        model_id = post.get('id')
        state = post.get('state')
        if not model_id:
            return invalid_response('id not found', 'id not found in request! ')
        if not state:
            return invalid_response('state not found', 'state found in request! ')

        try:
            model_obj = request.env['sm.caregiver.contracts'].sudo().browse(int(model_id))
            if not model_obj:
                return invalid_response('invalid id', 'NO data is found with the given ID.')

            model_obj.sudo().write({
                'state': state,
            })

            data = {
                'id': model_obj.id,
                'message': 'Your data has been saved successfully!'
            }
            return valid_response(data)

        except Exception as e:
            return invalid_response('error', e)

    @authenticate_token
    @http.route(['/sehati/get-cancellation-refund-list/<patient_id>'], type='http', auth="none", methods=['GET'],
                csrf=False)
    def get_cancellation_refund_list(self, patient_id=None):
        if not patient_id:
            return invalid_response('patient_id not found', 'Patient ID not found in request!')

        try:
            m_list = request.env['sm.shifa.cancellation.refund'].sudo().search(
                [('patient', '=', int(patient_id))],
                order="date desc"
            )
        except Exception as e:
            return invalid_response("INF_O6: {0}".format(self.error_message))

        success_data = []
        for rec in m_list:
            appointment_data = {}

            if rec.hhc_appointment:
                appointment_data['appointment'] = {
                    'id': rec.hhc_appointment.id,
                    'name': rec.hhc_appointment.name,
                    'date': str(rec.hhc_appointment.appointment_date_only)
                }
            if rec.phy_appointment:
                appointment_data['appointment'] = {
                    'id': rec.phy_appointment.id,
                    'name': rec.phy_appointment.name,
                    'date': str(rec.phy_appointment.appointment_date_only)
                }
            if rec.hvd_appointment:
                appointment_data['appointment'] = {
                    'id': rec.hvd_appointment.id,
                    'name': rec.hvd_appointment.name,
                    'date': str(rec.hvd_appointment.appointment_date_only)
                }
            if rec.appointment:
                appointment_data['appointment'] = {
                    'id': rec.appointment.id,
                    'name': rec.appointment.name,
                    'date': str(rec.appointment.appointment_date_only)
                }
            if rec.pcr_appointment:
                appointment_data['appointment'] = {
                    'id': rec.pcr_appointment.id,
                    'name': rec.pcr_appointment.name,
                    'date': str(rec.pcr_appointment.appointment_date_only)
                }

            data = {
                'id': rec.id,
                'name': rec.name or "",
                'type': rec.type or "",
                'patient': {
                    'id': rec.patient.id or 0,
                    'name': rec.patient.name or "",
                    'mobile': rec.patient.mobile or ""
                },
                'date': str(rec.date),
                'state': rec.state,
                'reason': rec.reason or "",
                'account_details': rec.account_details or "",
                'accepted_by': {
                    'id': rec.accepted_by.id or 0,
                    'name': rec.accepted_by.name or "",
                    'mobile': rec.accepted_by.mobile or ""
                },
                'refund_by': {
                    'id': rec.refund_by.id or 0,
                    'name': rec.refund_by.name or "",
                    'mobile': rec.refund_by.mobile or ""
                },
                'cancellation_requested': rec.cancellation_requested,
                **appointment_data
            }
            success_data.append(data)

        return valid_response(success_data)

    @authenticate_token
    @http.route(['/sehati/check-pharmacy-discount-status'], type='http', auth="none", methods=['POST'],
                csrf=False)
    def check_chain_discount_status(self, **post):
        qr_code = post.get('qr_code')
        if not qr_code:
            return invalid_response('qr_code not found', 'QR Code not found in request!')

        discount_obj = request.env['sm.shifa.pharmacy.chain'].with_user(2).search([('qr_code', '=', qr_code)], limit=1)
        is_valid = False
        if discount_obj:
            if discount_obj.state == 'Expired':
                message = 'This discount is expired'
                is_valid = False
            else:
                message = 'This discount is still available'
                is_valid = True
        else:
            message = 'No discount found for the given customer code'

        data = {
            'message': message,
            'is_valid': is_valid,
            'discount': discount_obj.discount,
        }
        return valid_response(data)
