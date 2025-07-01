from odoo import api, fields, models,_
from odoo.exceptions import UserError


class ShRequestedPayment(models.Model):
    _inherit = "sm.shifa.requested.payments"
    _description = "inherit from smartmind_shifa_extra/sm_medical_extra/models/shifa_requested_payment"

    def create_account_payment(self):
        ic = self.env['ir.config_parameter'].sudo()
        journal_cash = ic.get_param('smartmind_odoo.journal_cash')
        journal_bank = ic.get_param('smartmind_odoo.journal_bank')
        journal_point_sale = ic.get_param('smartmind_odoo.journal_point_sale')
        journal_mobile = ic.get_param('smartmind_odoo.journal_mobile')
        journal_portal = ic.get_param('smartmind_odoo.journal_portal')
        journal = False
        if self.payment_method == 'cash':
            journal = journal_cash
        elif self.payment_method == 'bank_transfer':
            journal = journal_bank
            if self.journal_id:
                journal = self.journal_id
        elif self.payment_method == 'mobile':
            journal = journal_mobile
        elif self.payment_method == 'point_of_sale':
            journal = journal_point_sale
        elif self.payment_method == 'portal':
            journal = journal_portal
        else:
            journal = False
        if journal:
            payment = self.env['account.payment'].create({
            'payment_type' : 'inbound',
            'partner_type' : 'customer',
            'partner_id' : self.patient.partner_id.id,
            #'destination_account_id' : self.get_property_account_receivable_id(self.patient.id),
            'amount' : self.deduction_amount,
            # 'date' : self.date,
            'date':fields.Datetime.today(),
            'requested_payment' : self.id,
            'ref': self.memo,
            'journal_id': int(journal),
            })
            # payment is draft
            payment.action_post()
            self.payment_id = payment.id
        else:
            raise UserError(_(' you should add journal from settings first'))
