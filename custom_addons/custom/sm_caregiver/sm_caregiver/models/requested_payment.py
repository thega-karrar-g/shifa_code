from odoo import models, fields, api, _
from odoo.exceptions import UserError

class RequestedPayments(models.Model):
    _inherit = 'sm.shifa.requested.payments'

    # Extend the existing type selection field with new options
    type = fields.Selection(selection_add=[
        ('caregiver', 'Caregiver Contract'),
        ('sleep_medicine_request', 'Sleep Medicine Request'),
    ], string="Type", readonly=True, states={'Start': [('readonly', False)]})

    # New fields for caregiver and sleep_medicine_request
    caregiver_contract_id = fields.Many2one('sm.caregiver.contracts', string="Caregiver Contract")
    date_caregiver_contract = fields.Date(string='Date', related="caregiver_contract_id.date", readonly=True,
                                          states={'Start': [('readonly', False)]})

    sleep_medicine_request = fields.Many2one('sm.sleep.medicine.request', string='Sleep Medicine Request',
                                             readonly=True, states={'Start': [('readonly', False)]})
    date_sleep_medicine_request = fields.Date(string='Date', related="sleep_medicine_request.date", readonly=True,
                                              states={'Start': [('readonly', False)]})

    ssn = fields.Char(related="patient.ssn",store=True)

    @api.model
    def create(self, vals):
        # Call the parent create method to create the record
        vals['name'] = self.env['ir.sequence'].next_by_code('sm.shifa.requested.payments')
        record = super(RequestedPayments, self).create(vals)

        # Assign the created record ID to the caregiver's request_payment_id
        if 'caregiver' in vals:
            appointment = self.env['sm.caregiver.contracts'].browse(vals['caregiver'])
            appointment.request_payment_id = record.id

        return record


    """def write(self, vals):
        payment_document = self.payment_document
        if 'payment_document' in vals:
            payment_document = vals['payment_document']
        payment_method = self.payment_method
        if 'payment_method' in vals:
            payment_method = vals['payment_method']
        if self.state == 'Send' and not payment_document and payment_method in ['bank_transfer','point_of_sale']:
            raise UserError("Document upload is required here!")
        return super().write(vals)"""


    def set_to_pay(self):
        res = super().set_to_pay()
        if self.payment_document:
            self.env['ir.attachment'].sudo().create({
                'res_model': 'account.payment',
                'res_id': self.payment_id.id,
                'datas': self.payment_document,
                'name': self.payment_id.name,
            })
        return res


    def unlink(self):
        for rec in self:
            if rec.state not in ['Reject','cancel']:
                raise UserError("You can only delete rejected or cancelled payments!")
        return super().unlink()