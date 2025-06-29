from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import UserError, ValidationError


class ShifaTeleAppointment(models.Model):
    _inherit = 'sm.telemedicine.appointment'

    pres_tele_line = fields.One2many('sm.shifa.prescription.line', 'prescription_tele_ids')
    lab_request_test_line = fields.One2many('sm.shifa.lab.request.line', 'telemedicine_appointment',
                                            string='Lab Request',
                                            readonly=False, states={'completed': [('readonly', True)]})
    image_request_test_ids = fields.One2many('sm.shifa.imaging.request.line', 'telemedicine_appointment',
                                             string='Image Request',
                                             readonly=False, states={'completed': [('readonly', True)]})
    investigation_ids = fields.One2many('sm.shifa.investigation', 'tele_appointment',
                                        string='Telemedicine Appointment')
    referral_ids = fields.One2many('sm.shifa.referral', 'telemedicine_appointment')


class ShifaAppointmentSaleOrder(models.Model):
    _inherit = 'sm.telemedicine.appointment'

    def _compute_payment_count(self):
        oe_apps = self.env['sale.order']
        for acc in self:
            domain = [('tele_appointment', '=', acc.id)]
            app_ids = oe_apps.search(domain)
            apps = oe_apps.browse(app_ids)
            app_count = 0
            for ap in apps:
                app_count += 1
            acc.sale_order_count = app_count
        return True

    sale_order_count = fields.Integer(compute=_compute_payment_count, string="Sale Orders")
    order_id = fields.Many2one('sale.order', string='Order #')

    def action_create_sale_order(self):
        for acc in self:
            if acc.insurance:
                partner_val = acc.insurance.partner_id.id
            else:
                partner_val = acc.patient.partner_id.id

            sale_order = self.env["sale.order"].sudo().create({
                'partner_id': partner_val,
                'client_order_ref': "Tele Appointment # : " + acc.name,
                'tele_appointment': acc.id,
                'state': 'sale',
            })

            self.create_sale_order_line(acc.doctor.consultancy_type.name,
                                        acc.doctor.consultancy_type.product_id.id, acc.total_service_price,
                                        acc.discount,
                                        acc.ksa_nationality, sale_order.id)

            self.write({'state': 'start', 'order_id': sale_order.id, 'complete_process_date': datetime.now()})
        return True

    @api.model
    def create(self, vals):
        appointment = super(ShifaAppointmentSaleOrder, self).create(vals)
        payment_method = vals['payment_made_through']
        if payment_method == 'mobile':
            patient = vals.get('patient')
            print('patient', patient)
            # self.create_payment(vals)
        return appointment

    def create_sale_order_line(self, name, product_id, price, discount, ksa, order_id):
        sale_order_line = self.env['sale.order.line'].create({
            'name': name,
            'product_id': product_id,
            'product_uom_qty': 1,
            'price_unit': price,
            'discount': discount,
            'order_id': order_id,
        })
        if ksa == 'NON':
            sale_order_line.product_id_change()


class ShifaTeleAppointmentPayment(models.Model):
    _inherit = "sm.telemedicine.appointment"

    @api.onchange('doctor')
    def _compute_total_service_price(self):
        for rec in self:
            rec.total_service_price = rec.doctor.tele_price

    @api.onchange('discount_name')
    def _onchange_discount_name(self):
        for rec in self:
            if rec.discount_name.tele:
                rec.discount = rec.discount_name.fixed_type
                rec.discount_val = rec.total_service_price * (rec.discount_name.fixed_type / 100)
            else:
                rec.discount = 0

    @api.depends('total_service_price', 'tax', 'discount')
    def _compute_amount_payable(self):
        for rec in self:
            rec.amount_payable = (rec.total_service_price - rec.discount_val) + rec.tax

    @api.depends('total_service_price', 'discount')
    def _compute_pri_dis(self):
        for rec in self:
            if rec.total_service_price > 0 and rec.discount >= 0:
                rec.amount_pri_dis = (rec.total_service_price - rec.discount)

    @api.depends('amount_pri_dis', 'ksa_nationality')
    def _set_tax_value(self):
        for rec in self:
            percent = (rec.total_service_price - rec.discount_val) * 0.15
            if rec.ksa_nationality == 'NON':
                rec.tax = percent
            else:
                rec.tax = 0

    total_service_price = fields.Integer('Service Price', compute='_compute_total_service_price', store=True)
    tax = fields.Float('VAT(+) 15%', compute='_set_tax_value')
    amount_payable = fields.Float('Amount Payable', compute='_compute_amount_payable', store=True)
    add_payment_request = fields.Boolean(string="Add Payment Request", readonly=True,
                                         states={'Scheduled': [('readonly', False)]})
    payment_request = fields.One2many('sm.shifa.requested.payments', 'telemedicine_appointment', readonly=False,
                                      states={'canceled': [('readonly', True)]}, string='Payment Request')
    payment_ref = fields.Char(related="payment_request.name")
    amount_pri_dis = fields.Float('Amounts', compute='_compute_pri_dis', store=True)
    discount_name = fields.Many2one('sm.shifa.discounts', string='Discount Name', readonly=False,
                                    states={'start': [('readonly', True)], 'Confirmed': [('readonly', True)],
                                            'Completed': [('readonly', True)], 'canceled': [('readonly', True)]})
    discount = fields.Integer(string='Discount %', readonly=True, default=0)
    discount_val = fields.Float(string='Discount', readonly=True, default=0)

    pay_req_id = fields.Many2one('sm.shifa.requested.payments', string='Payment Request#', copy=False, readonly=True)

    def pay_req_link(self):
        for rec in self:
            pay_values = {
                'patient': rec.patient.id,
                'type': 'tele_appointment',
                'details': 'tele appointment',
                'date': rec.appointment_date_only,
                # in payment module the new telemedicine field is not exist
                # 'tele_appointment': rec.id,
                'payment_amount': rec.amount_payable,
            }
        pay_req = self.env['sm.shifa.requested.payments'].create(pay_values)
        for pay_value in pay_req:
            self.pay_req_id = pay_value

    # price details
    @api.model
    def create(self, vals):
        if not vals.get('total_service_price'):
            raise UserError(
                _('Service price is required!, you can setup the price from Configuration->Services Management->Consultancy Charges'))
        return super(ShifaTeleAppointmentPayment, self).create(vals)

    def set_to_start(self):
        # res = super(ShifaTeleAppointmentPayment, self).set_to_start()
        self.action_create_sale_order()
        return True

    def set_to_completed(self):
        if self.pres_tele_line.id:
            for rec in self:
                if not rec.pres_tele_line:
                    pass
                else:
                    rec.env['oeh.medical.prescription'].create({
                        'patient': rec.patient.id,
                        'doctor': rec.doctor.id,
                        'tele_appointment': rec.id,
                        'provisional_diagnosis': rec.provisional_diagnosis.id,
                        'provisional_diagnosis_add_other': rec.provisional_diagnosis_add_other,
                        'provisional_diagnosis_add': rec.provisional_diagnosis_add.id,
                        'provisional_diagnosis_add_other2': rec.provisional_diagnosis_add_other2,
                        'provisional_diagnosis_add2': rec.provisional_diagnosis_add2.id,
                        'provisional_diagnosis_add_other3': rec.provisional_diagnosis_add_other3,
                        'provisional_diagnosis_add3': rec.provisional_diagnosis_add3.id,
                        'allergies_show': rec.allergies_show,
                        'has_drug_allergy': rec.has_drug_allergy,
                        'drug_allergy': rec.drug_allergy,
                        'drug_allergy_content': rec.drug_allergy_content,
                        'has_food_allergy': rec.has_food_allergy,
                        'food_allergy': rec.food_allergy,
                        'food_allergy_content': rec.food_allergy_content,
                        'has_other_allergy': rec.has_other_allergy,
                        'other_allergy': rec.other_allergy,
                        'other_allergy_content': rec.other_allergy_content,
                        'prescription_line': rec.pres_tele_line,
                    })
                if not rec.lab_request_test_line:
                    pass
                else:
                    print("Lab")
                    rec.env['sm.shifa.lab.request'].create({
                        'patient': rec.patient.id,
                        'doctor': rec.doctor.id,
                        'tele_appointment': rec.id,
                        'lab_request_ids': rec.lab_request_test_line,
                    })

                if not rec.image_request_test_ids:
                    pass
                else:
                    print("Image")
                    rec.env['sm.shifa.imaging.request'].create({
                        'patient': rec.patient.id,
                        'doctor': rec.doctor.id,
                        'tele_appointment': rec.id,
                        'image_req_test_ids': rec.image_request_test_ids,
                    })
        return self.write({'state': 'completed', 'complete_process_date': datetime.now()})


class ShifaAppointmentRequestedPayment(models.Model):
    _inherit = 'sm.telemedicine.appointment'

    def _compute_requested_payment_count(self):
        oe_apps = self.env['sm.shifa.requested.payments']
        for acc in self:
            domain = [('tele_appointment', '=', acc.id)]
            app_ids = oe_apps.search(domain)
            apps = oe_apps.browse(app_ids)
            app_count = 0
            for ap in apps:
                app_count += 1
            acc.requests_payment_count = app_count
        return True

    requests_payment_count = fields.Integer(compute=_compute_requested_payment_count, string="Req. Payments")


class ShifaTeleAppointmentInPayment(models.Model):
    _inherit = 'sm.shifa.requested.payments'

    telemedicine_appointment = fields.Many2one('sm.telemedicine.appointment', string="Tele Appointment #")


class ShifaLabRequestTestTeleAppointment(models.Model):
    _inherit = 'sm.shifa.lab.request.line'

    telemedicine_appointment = fields.Many2one("sm.telemedicine.appointment", string='tele Appointment')


class ShifaImagingRequestTestTeleAppointment(models.Model):
    _inherit = 'sm.shifa.imaging.request.line'

    telemedicine_appointment = fields.Many2one("sm.telemedicine.appointment", string='tele Appointment')


class ShifaPrescriptionTeleLinesInherit(models.Model):
    _inherit = "sm.shifa.prescription.line"

    prescription_telemedicine_ids = fields.Many2one('sm.telemedicine.appointment', 'pres_tele_line', ondelete='cascade',
                                                    index=True)



class ShifaReferralInherit(models.Model):
    _inherit = 'sm.shifa.referral'

    telemedicine_appointment = fields.Many2one("sm.telemedicine.appointment", string='Telemedicine Appointment',
                                               ondelete='cascade')


class ShifaLabRequestTestTeleAppointment(models.Model):
    _inherit = 'sm.shifa.lab.request.line'

    tele_appointment = fields.Many2one("sm.telemedicine.appointment", string='Tele Appointment')


class ShifaImagingRequestTestTeleAppointment(models.Model):
    _inherit = 'sm.shifa.imaging.request.line'

    tele_appointment = fields.Many2one("sm.telemedicine.appointment", string='Tele Appointment')


class ShifaPrescriptionTeleLinesInherit(models.Model):
    _inherit = "sm.shifa.prescription.line"

    prescription_tele_ids = fields.Many2one('sm.telemedicine.appointment', 'pres_tele_line', ondelete='cascade',
                                            index=True)


class ShifaImagingTestForTeleAppointment(models.Model):
    _inherit = 'sm.shifa.imaging.request'

    tele_appointment = fields.Many2one("sm.telemedicine.appointment", string='Tele Appointment')


class ShifaLabTestForTeleAppointment(models.Model):
    _inherit = 'sm.shifa.lab.request'

    tele_appointment = fields.Many2one("sm.telemedicine.appointment", string='Tele Appointment')


class ShifaAssessmentForTeleAppointment(models.Model):
    _inherit = 'sm.shifa.physician.assessment'

    tele_appointment = fields.Many2one("sm.telemedicine.appointment", string='Tele Appointment')


class ShifaAdmissionFollowupForTeleAppointment(models.Model):
    _inherit = 'sm.physician.admission.followup'

    tele_appointment = fields.Many2one("sm.telemedicine.appointment", string='Tele Appointment')


class ShifaAdmissionForTeleAppointment(models.Model):
    _inherit = 'sm.shifa.physician.admission'

    tele_appointment = fields.Many2one("sm.telemedicine.appointment", string='Tele Appointment')
