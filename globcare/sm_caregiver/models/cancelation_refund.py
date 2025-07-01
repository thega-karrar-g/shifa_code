from odoo import models, fields
from odoo.exceptions import UserError

class CancelationRefund(models.Model):
    _inherit = 'sm.shifa.cancellation.refund'

    # Extend the existing type selection field with new options
    type = fields.Selection(selection_add=[
        ('caregiver', 'Caregiver Contract'),
        ('sleep_medicine_request', 'Sleep Medicine Request'),
    ], string="Type", readonly=False, states={})

    # New fields for caregiver and sleep_medicine_request
    caregiver_contract_id = fields.Many2one('sm.caregiver.contracts', string="Caregiver Contract")
    date_caregiver_contract = fields.Date(string='Date', related="caregiver_contract_id.date", readonly=False,
                                          states={})

    sleep_medicine_request = fields.Many2one('sm.sleep.medicine.request', string='Sleep Medicine Request',
                                             readonly=True, states={'Start': [('readonly', False)]})
    date_sleep_medicine_request = fields.Date(string='Date', related="sleep_medicine_request.date", readonly=False,
                                              states={})
    move_ids = fields.Many2many('account.move',string='Invoices')
    payment_request_id = fields.Many2one('sm.shifa.requested.payments')
    approved_refund_request = fields.Selection([('no','No'),('yes','Yes')])
    ssn = fields.Char(related="patient.ssn",store=True)

    def send_approval_request(self):
        # Reference to the medical manager group
        manager_group = self.env.ref('oehealth.group_oeh_medical_manager').sudo()
        
        # Loop through each user in the medical manager group
        for user in manager_group.users:
            # Create a mail activity for each user
            self.env['mail.activity'].sudo().create({
                'user_id': user.id,
                'res_model': self._name,
                'res_id': self.id,
                'res_model_id': self.env['ir.model'].sudo().search([('model', '=', self._name)], limit=1).id,
                'summary': f'المحاسب بانتظار الموافقة على طلب استرداد مدفوعات رقم {self.name}.'
            })



    def open_invoice_view(self):
        action = self.env['ir.actions.act_window']._for_xml_id('account.action_move_out_invoice_type')
        moves = self.move_ids.ids
        if self.caregiver_contract_id.move_ids:
            moves += self.caregiver_contract_id.move_ids.ids
        if self.package_id.move_ids:
            moves += self.package_id.move_ids.ids
        if self.hhc_appointment.move_id:
            moves += self.hhc_appointment.move_id.ids
        if self.hhc_appointment.credit_note_id:
            moves += self.hhc_appointment.credit_note_id.ids
        if self.phy_appointment.move_id:
            moves += self.phy_appointment.move_id.ids
        if self.phy_appointment.credit_note_id:
            moves += self.phy_appointment.credit_note_id.ids

        action['domain'] = [('id', 'in', moves)]
        action.update({'context': {}})
        return action

    def open_payment_view(self):
        payment_request_ids = self.payment_request_id.ids
        if self.caregiver_contract_id:
            payments = self.env['sm.shifa.requested.payments'].sudo().search([
                ('caregiver_contract_id','=',self.caregiver_contract_id.id)
            ])
            if payments:
                payment_request_ids += payments.ids
        
        if self.package_id.pay_req_id:
            payment_request_ids += self.package_id.pay_req_id.ids
        if self.hhc_appointment.pay_req_id:
            payment_request_ids += self.hhc_appointment.pay_req_id.ids
        
        if self.phy_appointment.pay_req_id:
            payment_request_ids += self.phy_appointment.pay_req_id.ids
        
        action = self.env['ir.actions.act_window']._for_xml_id(
            'smartmind_shifa_extra.sm_shifa_requested_payments_action')
        action['domain'] = [('id', 'in', payment_request_ids)]
        action.update({'context': {}})
        return action        
    
    def set_to_refund(self):
        if self.approved_refund_request != 'yes':
            raise UserError("PLease ask to admin to approve the refund request before proceeding!")
        return super().set_to_refund()
