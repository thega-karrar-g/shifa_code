from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class InheritclinicAppointment(models.Model):
    _inherit = 'sm.clinic.appointment'

    eligibility_request_count = fields.Integer(string="Eligibility request", compute='get_eligibility_request_count')
    pre_auth_request_count = fields.Integer(string="pre_auth request", compute='get_pre_auth_request_count')

    @api.depends()
    def get_eligibility_request_count(self):
        for record in self:  # Iterate over each record in the recordset
            eligibility = self.env['sm.eligibility.check.request'].sudo().search(
                [('clinic_appointment_id', '=', record.id)])
            if eligibility:
                record.eligibility_request_count = len(eligibility)  # Store the count
            else:
                record.eligibility_request_count = 0

    @api.depends()
    def get_pre_auth_request_count(self):
        for record in self:  # Iterate over each record in the recordset
            pre_auth_request = self.env['sm.pre.authorization.request'].sudo().search(
                [('clinic_appointment_id', '=', record.id)])
            if pre_auth_request:
                record.pre_auth_request_count = len(pre_auth_request)
            else:
                record.pre_auth_request_count = 0

    def set_to_confirmed(self):
        # Call the original set_to_confirmed logic
        super_result = super().set_to_confirmed()

        for appointment in self:
            if appointment.pay_made_thru == 'insurance':
                # Call the eligibility check request creation method
                appointment.create_eligibility_check_request()

        return super_result
    def create_eligibility_check_request(self):
        for appointment in self:

            # Create the sm.eligibility.check.request record
            self.env['sm.eligibility.check.request'].create({
                'patient_id': appointment.patient_id.id,
                'department_id': appointment.department_id.id,
                'clinic_appointment_id': appointment.id,
                'insured_company_id': appointment.insured_company_id.id,
                'insured_policy': appointment.insured_policy.id,
                'insurance_company_id': appointment.insurance_company_id.id,
                'expiration_date': appointment.expiration_date,
                'class_company_id': appointment.class_company_id.id,
                'serv_patient_deduct': appointment.serv_patient_deduct,
                'pt_deduct_visit': appointment.pt_deduct_visit,
                'approval_limit': appointment.approval_limit,
                'insurance_state': appointment.insurance_state,
                'state': 'sent',
            })

    def set_to_completed(self):
        # Call the original set_to_confirmed logic
        super_result = super().set_to_completed()

        if self.pay_made_thru == 'insurance':
            action = self.create_pre_authorization_request()
            return action

        return super_result

    def open_eligibility_request_view(self):
        action = self.env['ir.actions.act_window']._for_xml_id(
            'sm_insurance_integration.action_eligibility_check_request')
        action['domain'] = [('clinic_appointment_id', '=', self.id)]
        return action

    def open_pre_auth_request_view(self):
        action = self.env['ir.actions.act_window']._for_xml_id(
            'sm_insurance_integration.sm_pre_authorization_request_action')
        action['domain'] = [('clinic_appointment_id', '=', self.id)]
        return action

    def create_pre_authorization_request(self):
        for record in self:
            # Create the pre-authorization request
            pre_auth_request = self.env['sm.pre.authorization.request'].create({
                'patient_id': record.patient_id.id,
                'department_id': record.department_id.id,
                'physician_id': record.physician_id.id,
                'clinic_appointment_id': record.id,
                'insured_company_id': record.insured_company_id.id,
                'insured_policy': record.insured_policy.id,
                'insurance_company_id': record.insurance_company_id.id,
                'expiration_date': record.expiration_date,
                'class_company_id': record.class_company_id.id,
                'serv_patient_deduct': record.serv_patient_deduct,
                'pt_deduct_visit': record.pt_deduct_visit,
                'approval_limit': record.approval_limit,
                'insurance_state': record.insurance_state,
                'state': 'draft',
                'temperature': record.temperature,
                'weight': record.weight,
                'prescription_line_ids': record.prescription_line_ids,
            })

            # Add service lines
            for lab_request_line in record.lab_request_line_ids:
                self.env['sm.physician.order.line'].create({
                    'authorization_request_id': pre_auth_request.id,
                    'type': 'lab',
                    'test_type_id': lab_request_line.test_type_id.id,
                    'lab_section_id': lab_request_line.lab_section_id.id,
                    'from_consultation': True,
                    'service_id': False,
                })

            for image_request_line in record.image_request_line_ids:
                self.env['sm.physician.order.line'].create({
                    'authorization_request_id': pre_auth_request.id,
                    'type': 'image',
                    'image_test_type_id': image_request_line.test_type_id.id,
                    'image_procedure_id': image_request_line.procedure_id.id,
                    'reason_of_exam': image_request_line.reason_of_exam,
                    'brief_history': image_request_line.brief_history,
                    'protocol_of_scan': image_request_line.protocol_of_scan,
                    'comment': image_request_line.comment,
                    'from_consultation': True,
                    'service_id': False,
                })

            for invest_line in record.investigation_request_line_ids:
                self.env['sm.physician.order.line'].create({
                    'authorization_request_id': pre_auth_request.id,
                    'type': 'investigation',
                    'invest_section_id': invest_line.section_id.id,
                    'from_consultation': True,
                })

            for procedure_line in record.procedure_request_line_ids:
                self.env['sm.physician.order.line'].create({
                    'authorization_request_id': pre_auth_request.id,
                    'type': 'procedure',
                    'procedure_id': procedure_line.procedure_id.id,
                    'from_consultation': True,
                })

            # Notify success
            self.env.user.notify_success(message="Authorization request created successfully!", title="Success",
                                         sticky=False)
        form_view_id = self.env.ref('sm_insurance_integration.sm_pre_authorization_request_form_views').id
        action = self.env["ir.actions.actions"]._for_xml_id("sm_insurance_integration.sm_pre_authorization_request_action")
        action['views'] = [(form_view_id, 'form')]
        action['res_id'] = pre_auth_request.id
        action['target'] = 'current'
        return action