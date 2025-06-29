from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import UserError
from zeep.exceptions import ValidationError


class ShifaAppointmentNetbookTabs(models.Model):
    _inherit = 'sm.shifa.hvd.appointment'

    referral_ids = fields.One2many('sm.shifa.referral', 'hvd_appointment')
    lab_request_test_line = fields.One2many('sm.shifa.lab.request.line', 'hvd_appointment', string='Lab Request',
                                            readonly=False, states={'Completed': [('readonly', True)]})
    image_request_test_ids = fields.One2many('sm.shifa.imaging.request.line', 'hvd_appointment', string='Image Request',
                                             readonly=False, states={'Completed': [('readonly', True)]})
    prescription_ids = fields.One2many('oeh.medical.prescription', 'hvd_appointment', string='Prescription',
                                       readonly=False, states={'Completed': [('readonly', True)]})
    check_pres = fields.Boolean()
    labtest_line = fields.One2many('sm.shifa.lab.request', 'hvd_appointment', string='Lab Request',
                                   readonly=False, states={'Completed': [('readonly', True)]})

    home_rounding_ids = fields.One2many('sm.shifa.home.rounding', 'hvd_appointment', string='Home Rounding')
    refund_request_id = fields.Many2one('sm.shifa.cancellation.refund', string='Refund Request#', copy=False,
                                        readonly=True)
    move_type = fields.Selection(related="move_id.move_type")
    credit_note_id = fields.Many2one('account.move', 'Credit Note', copy=False)
    cancelation_reason = fields.Selection([
        ('1', 'Cancel the appointment with Creating Refund Request'),
        ('2', 'Cancel the appointment with Creating New Appointment'),
        ('3', 'Cancel the appointment (Only)'),
    ], copy=False, string='Action to do after cancel')
    reason = fields.Char()
    new_appointment = fields.Many2one('sm.shifa.hvd.appointment', store=True, readonly=True, copy=False)

    def download_pdf(self):
        for rec in self:
            if rec.pres_hvd_line:
                therapist_obj = self.env['oeh.medical.prescription']
                domain = [('hvd_appointment', '=', self.id)]
                pres_id = therapist_obj.search(domain)
                return self.env.ref('smartmind_shifa.sm_shifa_report_patient_prescriptions').report_action(pres_id)

    def set_to_completed(self):
        for rec in self:
            if not rec.pres_hvd_line:
                pass
            else:
                rec.check_pres = True
                rec.env['oeh.medical.prescription'].create({
                    'patient': rec.patient.id,
                    'doctor': rec.doctor.id,
                    'hvd_appointment': rec.id,
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
                    'prescription_line': rec.pres_hvd_line,
                })

            if not rec.lab_request_test_line:
                pass
            else:
                rec.env['sm.shifa.lab.request'].create({
                    'patient': rec.patient.id,
                    'doctor': rec.doctor.id,
                    'hvd_appointment': rec.id,
                    'lab_request_ids': rec.lab_request_test_line,
                })

            if not rec.image_request_test_ids:
                pass
            else:
                rec.env['sm.shifa.imaging.request'].create({
                    'patient': rec.patient.id,
                    'doctor': rec.doctor.id,
                    'hvd_appointment': rec.id,
                    'image_req_test_ids': rec.image_request_test_ids,
                })

        return self.write({'state': 'Completed', 'complete_process_date': datetime.now()})

    def open_cancel_reason(self):
        self.ensure_one()
        ctx = {'form_view_ref': 'smartmind_shifa_conn.sm_hvd_appointment_cancellation_form'}
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sm.shifa.hvd.appointment',
            'view_mode': 'form',
            'target': 'new',
            'context': ctx,
            'res_id': self.id,
        }

    def set_to_canceled(self):
        if not self.credit_note_id and self.move_id.move_type == 'out_invoice':
            self.create_credit_note()

        if self.cancelation_reason == '1':
            self.create_refund_request()
        elif self.cancelation_reason == '2':
            super().set_to_canceled()
            new_appointment = self.copy()
            self.new_appointment = new_appointment.id
            # Return an action to open the form view of the new appointment
            return {
                'type': 'ir.actions.act_window',
                'name': 'New Appointment',
                'res_model': 'sm.shifa.hvd.appointment',
                'res_id': new_appointment.id,
                'view_mode': 'form',
                'view_type': 'form',
                'target': 'current',  # or 'new' to open in a new window
            }

        return super(ShifaAppointmentNetbookTabs, self).set_to_canceled()

    def create_refund_request(self):
        pay_values = {
            'patient': self.patient.id,
            'type': 'hvd_appointment',
            'date': self.appointment_date,
            'hvd_appointment': self.id,
            'reason': self.reason,
        }
        refund_request = self.env['sm.shifa.cancellation.refund'].create(pay_values)
        refund_request.set_to_operation_manager()
        refund_request.set_to_accept()
        refund_request.set_to_refund_request()
        self.refund_request_id = refund_request.id

    # create an credit note for services
    def create_credit_note(self):
        if self.move_id.move_type == 'out_invoice':
            invoice_lines = self.get_invoice_lines()
            default_journal = self._get_default_journal()
            # Create Invoice
            partner = self.patient.partner_id.id
            ref = "Appointment # : " + self.name if self.name else 'Appointment #' if not self.move_id.name else self.move_id.name
            credit_note = self.env['account.move'].sudo().create({
                'move_type': 'out_refund',
                'journal_id': default_journal.id,
                'partner_id': partner,
                'patient': self.patient.id,
                'analytic_account_id': self.env.user.analytic_account_id.id,
                'invoice_date': datetime.now().date(),
                'date': datetime.now().date(),
                'ref': ref,
                'invoice_line_ids': invoice_lines,
                'reversed_entry_id': self.move_id.id,
            })
            receivable_line = self.move_id.line_ids.filtered(lambda l: l.account_id.user_type_id.id == 5)
            credit_note_line = credit_note.line_ids.filtered(lambda l: l.account_id.user_type_id.id == 5)
            credit_note.action_post()
            if receivable_line and credit_note_line:
                lines = receivable_line + credit_note_line
                lines.reconcile()
            self.credit_note_id = credit_note.id


class ShifaAppointmentSaleOrder(models.Model):
    _inherit = 'sm.shifa.hvd.appointment'

    def _compute_payment_count(self):
        oe_apps = self.env['sale.order']
        for acc in self:
            domain = [('hvd_appointment', '=', acc.id)]
            app_ids = oe_apps.search(domain)
            apps = oe_apps.browse(app_ids)
            app_count = 0
            for ap in apps:
                app_count += 1
            acc.sale_order_count = app_count
        return True

    sale_order_count = fields.Integer(compute=_compute_payment_count, string="Sale Orders")
    order_id = fields.Many2one('sale.order', string='Order #')
    pay_req_id = fields.Many2one('sm.shifa.requested.payments', string='Payment Request#', copy=False, readonly=True)

    def create_payement_request(self, appointment):
        pay_values = {
            'patient': appointment.patient.id,
            'type': 'hvd_appointment',
            'details': 'hvd appointment',
            'date': appointment.appointment_date,
            'hvd_appointment': appointment.id,
            'payment_method': 'cash',
            'state': 'Send',
            'payment_amount': appointment.amount_payable,
        }
        pay_req = self.env['sm.shifa.requested.payments'].create(pay_values)
        pay_req.set_to_send()
        appointment.pay_req_id = pay_req.id

    @api.model
    def create(self, vals):
        appointment = super(ShifaAppointmentSaleOrder, self).create(vals)
        if appointment.payment_made_through != 'mobile':
            self.create_payement_request(appointment)
        return appointment


class ShifaHVDAppointmentPayment(models.Model):
    _inherit = 'sm.shifa.hvd.appointment'

    @api.depends('doctor')
    def _compute_total_service_price(self):
        for rec in self:
            rec.total_service_price = rec.doctor.hv_price

    @api.depends('discount_name')
    def _get_discount_name(self):
        for rec in self:
            if rec.discount_name.hvd:
                rec.discount = rec.discount_name.fixed_type
                rec.discount_val = rec.total_service_price * (rec.discount_name.fixed_type / 100)
            else:
                rec.discount = 0
                rec.discount_val = 0

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

    insurance = fields.Many2one('sm.shifa.insurance', string='Insurance', help="Company Name",
                                domain=[('state', '=', 'Active')], readonly=True,
                                states={'Scheduled': [('readonly', False)]})

    add_payment_request = fields.Boolean(string="Add Payment Request", readonly=True,
                                         states={'Scheduled': [('readonly', False)]})
    payment_request = fields.One2many('sm.shifa.requested.payments', 'hvd_appointment', readonly=True,
                                      states={'Scheduled': [('readonly', False)]}, string='Payment Request')
    payment_ref = fields.Char(related="payment_request.name")
    amount_pri_dis = fields.Float('Amounts', compute='_compute_pri_dis', store=True)

    pres_hvd_line = fields.One2many('sm.shifa.prescription.line', 'prescription_hvd_ids', readonly=True,
                                    states={'Start': [('readonly', False)]})
    discount_name = fields.Many2one('sm.shifa.discounts', string='Discount Name',
                                    domain=[('state', '=', 'Active'), ('hvd', '=', 'True')],
                                    readonly=True, states={'Scheduled': [('readonly', False)]})
    discount = fields.Integer(string='Discount %', readonly=True, default=0, compute=_get_discount_name)
    discount_val = fields.Float(string='Discount', readonly=True, default=0, compute=_get_discount_name)

    def open_invoice_view(self):
        action = self.env['ir.actions.act_window']._for_xml_id('account.action_move_out_invoice_type')
        action['domain'] = [('id', '=', self.move_id.id)]
        action.update({'context': {}})
        return action

        # get default journal to invoice

    def _get_default_journal(self):
        journal = self.env['account.journal'].search([('type', '=', 'sale')], limit=1)
        return journal

        # get the service invoice line

    def get_invoice_lines(self):
        if self.patient.ksa_nationality == 'NON':
            company = self.env.user.company_id
            tax = company.account_sale_tax_id
        else:
            tax = False
        invoice_lines = [
            (0, 0, {
                'product_id': self.doctor.hv_consultancy_type.product_id.id,
                'price_unit': self.total_service_price,
                'tax_ids': tax,
                'discount': self.discount,
                'sequence': 1,
            })]
        return invoice_lines

        # create an invoice for services

    def create_invoice(self):
        invoice_lines = self.get_invoice_lines()
        if self.branch == 'riyadh':
            analytical_account_id = 2
        elif self.branch == 'dammam':
            analytical_account_id = 3
        #default_journal = self._get_default_journal()
        #default_journal = self._get_default_journal()
        default_journal = self.env['account.journal'].sudo().search([
            ('type','=','sale'),
            ('analytic_account_id','=',analytical_account_id),
            ('company_id','=',self.env.user.company_id.id),
        ],limit=1)
        # Create Invoice
        if not self.move_id:
            invoice = self.env['account.move'].sudo().create({
                'move_type': 'out_invoice',
                'journal_id': default_journal.id,
                'partner_id': self.patient.partner_id.id,
                'patient': self.patient.id,
                'analytic_account_id': analytical_account_id,
                'invoice_date': datetime.now().date(),
                'date': datetime.now().date(),
                'ref': "Appointment # : " + self.name if self.name else 'Appointment #',
                'invoice_line_ids': invoice_lines
            })
            invoice.action_post()
            self.move_id = invoice

    def set_to_start(self):
        res = super(ShifaHVDAppointmentPayment, self).set_to_start()
        self.create_invoice()
        return res

    def set_to_confirmed(self):
        res = super(ShifaHVDAppointmentPayment, self).set_to_confirmed()
        if self.payment_made_through not in ['pending', 'on_spot', 'aggregator', 'package',
                                             'aggregator_package'] and self.pay_req_id and self.pay_req_id.state not in [
            'Paid', 'Done']:
            raise UserError("You cannot move to the next action until the payment is paid or processed!")
        if self.payment_made_through == 'pending' and not self.pro_pending:
            raise UserError("Waiting for Admin approval!")
        # self.create_payement_request()
        return res


class ShifaHVDAppointmentInPayment(models.Model):
    _inherit = 'sm.shifa.requested.payments'

    hvd_appointment = fields.Many2one('sm.shifa.hvd.appointment', string="HVD Appointment #")

    # @api.onchange('add_payment_request')
    # def create_payment(self):
    #     # if self.add_payment_request:
    #     vals = {
    #         'patient': self.patient.id,
    #         'payment_amount': 0,
    #     }
    #     context = dict(self.env.context)
    #     context['form_view_initial_mode'] = 'edit'
    #     return {'type': 'ir.actions.act_window',
    #             'view_type': 'form',
    #             'view_mode': 'form',
    #             'res_model': 'sm.shifa.requested.payments',
    #             'res_id': self.env['sm.shifa.requested.payments'].create(vals).id,
    #             'context': context
    #             }


class ShifaPrescriptionLinesInherit(models.Model):
    _inherit = "sm.shifa.prescription.line"

    prescription_hvd_ids = fields.Many2one('sm.shifa.hvd.appointment', 'pres_hvd_line', ondelete='cascade', index=True)


class ShifaPrescriptionForHVDAppointment(models.Model):
    _inherit = 'oeh.medical.prescription'

    hvd_appointment = fields.Many2one("sm.shifa.hvd.appointment", string='HVD Appointment')


class ShifaLabRequestTestHVDAppointment(models.Model):
    _inherit = 'sm.shifa.lab.request.line'

    hvd_appointment = fields.Many2one("sm.shifa.hvd.appointment", string='HVD Appointment')


class ShifaImagingRequestTestHVDAppointment(models.Model):
    _inherit = 'sm.shifa.imaging.request.line'

    hvd_appointment = fields.Many2one("sm.shifa.hvd.appointment", string='HVD Appointment')


class ShifaReferralInherit(models.Model):
    _inherit = 'sm.shifa.referral'

    hvd_appointment = fields.Many2one("sm.shifa.hvd.appointment", string='HVD Appointment',
                                      ondelete='cascade')


class ShifaHVDAppointmentInvestigation(models.Model):
    _inherit = "sm.shifa.hvd.appointment"

    lab_test_ids = fields.One2many('sm.shifa.lab.request', 'hvd_appointment', string='Lab Request')
    image_test_ids = fields.One2many('sm.shifa.imaging.request', 'hvd_appointment', string='Image Request')
    investigation_ids = fields.One2many('sm.shifa.investigation', 'hvd_appointment', string='HVD Appointment')


class ShifaLabTestForHVDAppointment(models.Model):
    _inherit = 'sm.shifa.lab.request'

    hvd_appointment = fields.Many2one("sm.shifa.hvd.appointment", string='HVD Appointment')


class ShifaImagingTestForHVDAppointment(models.Model):
    _inherit = 'sm.shifa.imaging.request'

    hvd_appointment = fields.Many2one("sm.shifa.hvd.appointment", string='HVD Appointment')


class ShifaHomeRoundingForHVDAppointment(models.Model):
    _inherit = 'sm.shifa.home.rounding'

    hvd_appointment = fields.Many2one("sm.shifa.hvd.appointment", string='HVD Appointment')
