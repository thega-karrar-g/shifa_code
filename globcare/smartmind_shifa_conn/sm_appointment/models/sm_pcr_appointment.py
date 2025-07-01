from odoo import models, fields, api, _
import datetime
from odoo.exceptions import UserError, ValidationError


class ShifaPCRAppointmentPayment(models.Model):
    _inherit = 'sm.shifa.pcr.appointment'

    # getting default bank id from bank accounts
    @api.model
    def _default_home_visi_fee(self):
        return self.env['sm.shifa.instant.consultancy.charge'].search([('code', '=', 'HVF')], limit=1)

    # @api.onchange('service')
    # def _onchange_service(self):
    #     self.total_service_price = self.service_price * self.swabs_count

    @api.onchange('swabs_count')
    def compute_price(self):
        if self.swabs_count <= 0:
            raise ValidationError("It should be more than 0")
        else:
            self.total_service_price = self.swabs_count * self.service_price

    @api.onchange('service')
    def _get_service_price(self):
        for rec in self:
            rec.service_price = rec.service.list_price
            rec.home_visit_fee = rec.instance.charge

    @api.onchange('discount_name')
    def _onchange_discount_name(self):
        for rec in self:
            if rec.discount_name.pcr:
                rec.discount = rec.discount_name.fixed_type
                rec.discount_val = rec.total_service_price * (rec.discount_name.fixed_type / 100)
            else:
                rec.discount = 0

    @api.depends('total_service_price', 'tax', 'home_visit_fee', 'discount')
    def _compute_amount_payable(self):
        self.amount_payable = ((self.total_service_price - self.discount_val) + self.home_visit_fee) + self.tax

    @api.depends('total_service_price', 'discount')
    def _compute_pri_dis(self):
        for rec in self:
            if rec.total_service_price > 0 and rec.discount >= 0:
                rec.amount_pri_dis = (rec.total_service_price - rec.discount)

    @api.depends('amount_pri_dis', 'ksa_nationality')
    def _set_tax_value(self):
        percent = ((self.total_service_price - self.discount_val) + self.home_visit_fee) * 0.15
        if self.ksa_nationality == 'NON':
            self.tax = percent
        else:
            self.tax = 0

    @api.depends('instance')
    def _set_home_visit_fee(self):
        self.home_visit_fee = self.instance.charge

    total_service_price = fields.Integer('Service Price', readonly=True, computed="compute_price")
    swabs_count = fields.Integer('Swabs Number', readonly=False, default=1)
    tax = fields.Float('VAT(+) 15%', compute='_set_tax_value')
    instance = fields.Many2one('sm.shifa.instant.consultancy.charge', string='Instance', default=_default_home_visi_fee)
    home_visit_fee = fields.Integer(string='Home Visit Fee', compute='_set_home_visit_fee')
    amount_payable = fields.Float('Amount Payable', compute='_compute_amount_payable')

    add_payment_request = fields.Boolean(string="Add Payment Request", readonly=True, states={'scheduled': [('readonly', False)]})
    payment_request = fields.One2many('sm.shifa.requested.payments', 'pcr_appointment', readonly=True,
                                      states={'scheduled': [('readonly', False)]}, string='Payment Request')
    payment_ref = fields.Char(related="payment_request.name")
    amount_pri_dis = fields.Float('Amounts', compute='_compute_pri_dis', store=True)

    discount_name = fields.Many2one('sm.shifa.discounts', string='Discount Name',
                                    readonly=True, states={'scheduled': [('readonly', False)]})
    discount = fields.Integer(string='Discount %', readonly=True, default=0)
    discount_val = fields.Float(string='Discount', readonly=True, default=0)
    pay_req_id = fields.Many2one('sm.shifa.requested.payments', string='Payment Request#', copy=False, readonly=True)

    def create_payement_request(self, appointment):
        pay_values = {
            'patient': appointment.patient.id,
            'type': 'pcr_appointment',
            'details': 'pcr appointment',
            'date': appointment.appointment_date,
            'pcr_appointment': appointment.id,
            'payment_method': 'cash',
            'state': 'Send',
            'payment_amount': appointment.amount_payable,
        }
        pay_req = self.env['sm.shifa.requested.payments'].create(pay_values)
        appointment.pay_req_id = pay_req.id

    @api.model
    def create(self, vals):
        appointment = super(ShifaPCRAppointmentPayment, self).create(vals)
        payment_method = appointment.payment_made_through
        if payment_method == 'mobile':
            patient = vals.get('patient')
        if payment_method == 'call_center' or payment_method == 'on_spot':
            self.create_payement_request(appointment)
        return appointment



class ShifaPCRAppointmentInPayment(models.Model):
    _inherit = 'sm.shifa.requested.payments'

    pcr_appointment = fields.Many2one('sm.shifa.pcr.appointment', string="PCR Appointment #")

