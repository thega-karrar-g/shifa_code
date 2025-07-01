from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime


class ShifaHHCPhysiotherapy(models.Model):
    _inherit = 'sm.shifa.physiotherapy.appointment'
    _description = 'Physiotherapy Appointment Management'

    def _get_default_hvf(self):
        miscellaneous_obj = self.env['sm.shifa.miscellaneous.charge.service']
        domain = [('code', '=', 'PHY-HVF')]
        hvf = miscellaneous_obj.search(domain, limit=1)
        if hvf:
            return hvf.id or False
        else:
            return False

    @api.depends('discount_name')
    def _compute_discount_value(self):
        for rec in self:
            if rec.discount_name.physiotherapy:
                rec.discount = rec.discount_name.fixed_type
            # else:
            #     rec.discount = 0

    # calculate discount amount depending on discount percentage
    @api.depends('discount_name', 'discount', 'total_service_price', 'miscellaneous_price')
    def _calculate_discount(self):
        for rec in self:
            if rec.discount_name.physiotherapy:
                rec.discount_val = (rec.total_service_price + rec.miscellaneous_price) * (
                        rec.discount_name.fixed_type / 100)
            else:
                rec.discount_val = (rec.total_service_price + rec.miscellaneous_price) * (rec.discount / 100)

    # compute service price
    @api.depends('service_price')
    def _compute_service_price(self):
        for rec in self:
            rec.total_service_price = rec.service_price

    @api.depends('total_service_price', 'tax', 'miscellaneous_price', 'discount')
    def _compute_amount_payable(self):
        self.amount_payable = self.total_service_price - self.discount_val + self.miscellaneous_price + self.tax

    @api.depends('total_service_price', 'discount')
    def _compute_pri_dis(self):
        for rec in self:
            if rec.total_service_price > 0 and rec.discount >= 0:
                rec.amount_pri_dis = (rec.total_service_price - rec.discount)

    # calculate tax
    @api.depends('total_service_price', 'discount_val', 'miscellaneous_price', 'ksa_nationality',
                 'payment_made_through')
    def _set_tax_value(self):
        for rec in self:
            rec.tax = 0
            if rec.payment_made_through in ['aggregator', 'aggregator_package']:
                rec.tax = (rec.total_service_price + rec.miscellaneous_price - rec.discount_val) * 0.15
            else:
                if rec.patient.ksa_nationality == 'KSA':
                    rec.tax = 0
                else:
                    rec.tax = (rec.total_service_price + rec.miscellaneous_price - rec.discount_val) * 0.15

    miscellaneous_charge = fields.Many2one('sm.shifa.miscellaneous.charge.service', string='Other Charges Type',
                                           required=True, readonly=True, default=_get_default_hvf)
    miscellaneous_price = fields.Float(string='Home Visit Fee', readonly=True)

    total_service_price = fields.Integer('Service Price', compute='_compute_service_price', readonly=True, default=0)
    tax = fields.Float('VAT(+) 15%', compute='_set_tax_value')

    # instance = fields.Many2one('sm.shifa.instant.consultancy.charge', string='Instance', default=_default_home_visi_fee)
    # home_visit_fee = fields.Integer(string='Home Visit Fee', readonly=True)
    amount_payable = fields.Float('Amount Payable', compute=_compute_amount_payable)

    physician_physiotherapy_line = fields.One2many('sm.shifa.physiotherapy.assessment', 'physiotherapy',
                                                   string="Physiotherapy Assessment", readonly=True,
                                                   states={'in_progress': [('readonly', False)],
                                                           'visit_done': [('readonly', False)]})
    physician_physiotherapy_followup_line = fields.One2many('sm.shifa.physiotherapy.followup', 'physiotherapy',
                                                            string="Physiotherapy Assessment Follow up", readonly=True,
                                                            states={'in_progress': [('readonly', False)],
                                                                    'visit_done': [('readonly', False)]})

    add_payment_request = fields.Boolean(string="Add Payment Request", readonly=True,
                                         states={'scheduled': [('readonly', False)]})

    payment_request = fields.One2many('sm.shifa.requested.payments', 'phy_appointment', readonly=False,
                                      states={'canceled': [('readonly', True)]}, string='Payment Request')
    payment_ref = fields.Char(related="payment_request.name")

    discount_name = fields.Many2one('sm.shifa.discounts', string='Discount Name',
                                    domain=[('state', '=', 'Active'), ('physiotherapy', '=', 'True')],
                                    readonly=True, states={'scheduled': [('readonly', False)]})
    discount = fields.Float(string='Discount %', readonly=True, default=0, compute=_compute_discount_value, store=True)
    discount_val = fields.Float(string='Discount', readonly=True, default=0, compute=_calculate_discount, store=True)

    amount_pri_dis = fields.Float('Amounts', compute='_compute_pri_dis', store=True)
    physiotherapy_ass_id = fields.Many2one('sm.shifa.physiotherapy.assessment', string='physiotherapy Assessment',
                                           copy=False, readonly=True)
    physiotherapy_ass_followup_id = fields.Many2one('sm.shifa.physiotherapy.followup',
                                                    string='physiotherapy Assessment Followup',
                                                    copy=False, readonly=True)
    pay_req_id = fields.Many2one('sm.shifa.requested.payments', string='Payment Request#', copy=False, readonly=True)

    move_id = fields.Many2one('account.move', string='accounting #', ondelete='restrict', copy=False)
    aggregator = fields.Many2one('sm.aggregator', string='Aggregator', readonly=False,
                                 states={'scheduled': [('readonly', False)],
                                         'head_physiotherapist': [('readonly', False)],
                                         'operation_manager': [('readonly', False)]})

    move_type = fields.Selection(related="move_id.move_type")
    credit_note_id = fields.Many2one('account.move', 'Credit Note', copy=False)
    cancelation_reason = fields.Selection([
        ('1', 'Cancel the appointment with Creating Refund Request'),
        ('2', 'Cancel the appointment with Creating New Appointment'),
        ('3', 'Cancel the appointment (Only)'),
    ], copy=False, strig='Action to do after cancel')
    reason = fields.Char()
    new_appointment = fields.Many2one('sm.shifa.physiotherapy.appointment', store=True, readonly=True, copy=False)

    def open_cancel_reason(self):
        # if not self.move_id.move_type == 'out_invoice':
        #     return super(ShifaHHCPhysiotherapy, self).set_to_canceled()
        self.ensure_one()
        ctx = {'form_view_ref': 'smartmind_shifa_conn.sm_physiotherapy_appointment_cancellation_form'}
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sm.shifa.physiotherapy.appointment',
            'view_mode': 'form',
            'target': 'new',
            'context': ctx,
            'res_id': self.id,
        }

    def set_to_canceled(self):
        if not self.credit_note_id and self.move_id.move_type == 'out_invoice' and self.payment_made_through != 'pending':
            self.create_credit_note()
        if self.state == 'operation_manager' or self.state == 'scheduled':
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
                    'res_model': 'sm.shifa.physiotherapy.appointment',
                    'res_id': new_appointment.id,
                    'view_mode': 'form',
                    'view_type': 'form',
                    'target': 'current',  # or 'new' to open in a new window
                }
        else:
                if self.cancelation_reason == '1':
                    self.create_refund_request()
                elif self.cancelation_reason == '2':
                    new_appointment = self.copy()
                    self.new_appointment = new_appointment.id
                    # Return an action to open the form view of the new appointment
                    return {
                        'type': 'ir.actions.act_window',
                        'name': 'New Appointment',
                        'res_model': 'sm.shifa.physiotherapy.appointment',
                        'res_id': new_appointment.id,
                        'view_mode': 'form',
                        'view_type': 'form',
                        'target': 'current',  # or 'new' to open in a new window
                    }
        return super().set_to_canceled()

    # create a journal entry for appointment
    def create_journal(self):
        amount = self.total_service_price + self.miscellaneous_price
        ic = self.env['ir.config_parameter'].sudo()
        journal_id = int(ic.get_param('smartmind_odoo.journal_id'))
        debit_account_id = int(ic.get_param('smartmind_odoo.debit_account_id'))
        credit_account_id = int(ic.get_param('smartmind_odoo.credit_account_phy_id'))
        credit_discount_account_id = int(ic.get_param('smartmind_odoo.credit_discount_id'))
        debit_discount_account_id = int(ic.get_param('smartmind_odoo.debit_discount_id'))
        if self.payment_made_through == 'package':
            name = 'package'
        elif self.payment_made_through == 'aggregator_package':
            name = 'Aggregator Package'
        if journal_id and credit_account_id and debit_account_id:
            debit_line_vals = {
                'name': name or ' ',
                'debit': amount,
                'credit': 0,
                'account_id': debit_account_id,
            }
            credit_line_vals = {
                'name': name or ' ',
                'debit': 0,
                'credit': amount,
                'account_id': credit_account_id,
            }
            debit_discount_vals = {
                'name': name + "Discount" or ' ',
                'debit': self.discount_val,
                'credit': 0,
                'account_id': debit_discount_account_id,
            }
            credit_discount_vals = {
                'name': name + "Discount" or ' ',
                'debit': 0,
                'credit': self.discount_val,
                'account_id': credit_discount_account_id,
            }
            # check if there is a discount or not
            if self.discount_val == 0:
                line_ids = [(0, 0, debit_line_vals), (0, 0, credit_line_vals)]
            else:
                line_ids = [(0, 0, debit_line_vals), (0, 0, credit_line_vals),
                            (0, 0, debit_discount_vals), (0, 0, credit_discount_vals)]

            vals = {
                'patient': self.patient.id,
                'state': 'draft',
                'ref': self.name,
                'journal_id': journal_id,
                'line_ids': line_ids
            }
            journal = self.env['account.move'].create(vals)
            journal.action_post()
            self.move_id = journal
        else:
            raise UserError(_('Set  journal , debit account and credit account from settings'))

    def open_journal_view(self):
        action = self.env['ir.actions.act_window']._for_xml_id('account.action_move_journal_line')
        action['domain'] = [('id', '=', self.move_id.id)]
        action.update({'context': {}})
        return action
    
    def write(self, vals):
        res = super().write(vals)
        if self.payment_made_through in ['mobile','call_center'] and 'state' in vals and vals['state'] == 'head_physiotherapist':
            self.create_invoice()
        return res

    def set_to_head_physiotherapist(self):
        # Check if payment method is not allowed
        if self.payment_made_through in ['mobile', 'package', 'aggregator_package']:
            raise UserError("You are not allowed to save this type of payment method. Please select another value.")

        # Check if payment method is not in the allowed list and payment request is not processed
        if self.payment_made_through not in ['pending', 'on_spot', 'aggregator', 'package', 'aggregator_package']:
            if self.pay_req_id and self.pay_req_id.state not in ['Paid', 'Done']:
                raise UserError("You cannot move to the next action until the payment is paid or processed!")

        # Check for pending payment approval
        if self.payment_made_through == 'pending' and not self.pro_pending:
            raise UserError("Waiting for Admin approval!")
        # Check for deferred payment approval
        if self.payment_made_through == 'deferred' and not self.pro_deferred_pay:
            raise UserError("Waiting for Admin approval!")

        return super().set_to_head_physiotherapist()

    # def set_to_head_physiotherapist(self):
    #     if self.payment_made_through in ['mobile', 'package', 'aggregator_package']:
    #         raise UserError("You are not allowed to save this type of payment method. Please select another value.")
    #     if self.payment_made_through not in ['pending', 'on_spot', 'aggregator', 'package',
    #                                          'aggregator_package'] and self.pay_req_id and self.pay_req_id.state not in [
    #         'Paid', 'Done']:
    #         raise UserError("You cannot move to the next action until the payment is paid or processed!")
    #     if self.payment_made_through == 'pending' and not self.pro_pending:
    #         raise UserError("Waiting for Admin approval!")
    #     return super().set_to_head_physiotherapist()

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
        invoice_lines = []
        if self.payment_made_through != "aggregator":
            if self.patient.ksa_nationality == 'NON':
                company = self.env.user.company_id
                tax = company.account_sale_tax_id
            else:
                tax = False
        else:
            company = self.env.user.company_id
            tax = company.account_sale_tax_id
        for line in self:
            sequence = 0
            if line.service:
                sequence += 1
                invoice_lines.append(
                    (0, 0, {
                        'product_id': self.service.product_id.id,
                        'price_unit': self.service_price,
                        'tax_ids': tax,
                        'discount': self.discount,
                        'sequence': sequence,
                    }))
            if line.miscellaneous_charge:
                sequence += 1
                invoice_lines.append(
                    (0, 0, {
                        'product_id': self.miscellaneous_charge.product_id.id,
                        'price_unit': self.miscellaneous_price,
                        'tax_ids': tax,
                        'discount': self.discount,
                        'sequence': sequence,
                    }))

        return invoice_lines

    # create an invoice for services
    def create_invoice(self):
        if self.branch == 'riyadh':
            analytical_account_id = 2
        elif self.branch == 'dammam':
            analytical_account_id = 3
        invoice_lines = self.get_invoice_lines()
        #default_journal = self._get_default_journal()
        default_journal = self.env['account.journal'].sudo().search([
            ('type','=','sale'),
            ('analytic_account_id','=',analytical_account_id),
            ('company_id','=',self.env.user.company_id.id),
        ],limit=1)
        # Create Invoice
        if self.payment_made_through == 'aggregator':
            partner = self.aggregator.partner_id.id
        else:
            partner = self.patient.partner_id.id
        if not self.move_id:
            invoice = self.env['account.move'].sudo().create({
                'move_type': 'out_invoice',
                'journal_id': default_journal.id,
                'partner_id': partner,
                'patient': self.patient.id,
                'analytic_account_id': analytical_account_id,
                'invoice_date': datetime.now().date(),
                'date': datetime.now().date(),
                'ref': "Appointment # : " + self.name if self.name else "Appointment #",
                'invoice_line_ids': invoice_lines
            })
            invoice.action_post()
            self.move_id = invoice

    # create an credit note for services
    def create_credit_note(self):
        if self.move_id.move_type == 'out_invoice':
            invoice_lines = self.get_invoice_lines()
            default_journal = self._get_default_journal()
            # Create Invoice
            if self.payment_made_through == 'aggregator':
                partner = self.aggregator.partner_id.id
            else:
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

    def set_to_start(self):
        if not self.service_type_choice and not self.physiotherapist and not self.service:
            raise UserError(_('service name and physiotherapist should be added to start!'))
        if self.payment_made_through == 'on_spot' and self.pay_req_id and self.pay_req_id.state not in ['Paid', 'Done']:
            raise UserError("You cannot move to the next action until the payment is paid or processed!")
        if self.service_type_choice == 'main':
            self.physiotherapy_assessment_link()
        elif self.service_type_choice == 'followup':
            self.physiotherapy_assessment_followup_link()

        if self.payment_made_through in ['package', 'aggregator_package']:
            self.create_journal()
        elif self.payment_made_through == 'pending':
            pass
        else:
            self.create_invoice()

        return self.write({'state': 'in_progress', 'start_process_date': datetime.now()})

    def physiotherapy_assessment_link(self):
        for rec in self:
            physio_values = {
                'patient': rec.patient.id,
                'doctor': rec.physiotherapist.id,
                'service': rec.service.id,
                'physiotherapy': rec.id,
                'phys_appointment': rec.id,
            }
            physio_assessments = self.env['sm.shifa.physiotherapy.assessment'].create(physio_values)
            rec.physiotherapy_ass_id = physio_assessments.id

    def physiotherapy_assessment_followup_link(self):
        for rec in self:
            physio_followup_values = {
                'patient': rec.patient.id,
                'physiotherapist': rec.physiotherapist.id,
                'service': rec.service.id,
                'physiotherapy': rec.id,
                'phys_appointment': rec.id,
            }
            physio_assessments = self.env['sm.shifa.physiotherapy.followup'].create(physio_followup_values)
            rec.physiotherapy_ass_followup_id = physio_assessments.id

    def open_payment_request_dialog(self):
        self.ensure_one()
        ctx = {
            'form_view_ref': 'smartmind_shifa_extra.view_shifa_requested_payments_form',
            'default_patient': self.patient.id,
            'default_type': 'phy_appointment',
            'default_phy_appointment': self.id,
            'default_date_phy_appointment': self.appointment_date_only,
        }
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sm.shifa.requested.payments',
            'view_mode': 'form',
            'target': 'new',
            'context': ctx,
        }

    def open_treatment_view(self):
        action = self.env['ir.actions.act_window']._for_xml_id('sm_search_patient.sm_treatments_action')
        action['domain'] = [('phy_appointment_id', '=', self.id)]
        action.update({'context': {}})
        return action


class ShifaPHYSAppointmentInPhysiotherapyAssessmentFollowup(models.Model):
    _inherit = 'sm.shifa.physiotherapy.followup'

    physiotherapy = fields.Many2one('sm.shifa.physiotherapy.appointment', string="Physiotherapy #")


class ShifaPHYSAppointmentInPhysiotherapyAssessment(models.Model):
    _inherit = 'sm.shifa.physiotherapy.assessment'

    physiotherapy = fields.Many2one('sm.shifa.physiotherapy.appointment', string="Physiotherapy #")


class ShifaAppointmentSaleOrder(models.Model):
    _inherit = 'sm.shifa.physiotherapy.appointment'

    refund_request_id = fields.Many2one('sm.shifa.cancellation.refund', string='Refund Request#', copy=False,
                                        readonly=True)

    @api.onchange('miscellaneous_charge')
    def _get_miscellaneous_price(self):
        for rec in self:
            if rec.miscellaneous_charge.list_price:
                rec.miscellaneous_price = rec.miscellaneous_charge.list_price
            else:
                rec.miscellaneous_price = 1

    def create_payement_request(self, appointment):
        pay_values = {
            'patient': appointment.patient.id,
            'type': 'phy_appointment',
            'details': 'Physiotherapy appointment',
            'date': appointment.appointment_date,
            'phy_appointment': appointment.id,
            'payment_method': 'cash',
            'state': 'Send',
            'payment_amount': appointment.amount_payable,
        }
        pay_req = self.env['sm.shifa.requested.payments'].create(pay_values)
        pay_req.set_to_send()
        appointment.pay_req_id = pay_req.id

    def create_refund_request(self):
        pay_values = {
            'patient': self.patient.id,
            'type': 'phy_appointment',
            'date': self.appointment_date,
            'phy_appointment': self.id,
            'reason': self.reason,
        }
        refund_request = self.env['sm.shifa.cancellation.refund'].create(pay_values)
        refund_request.set_to_operation_manager()
        refund_request.set_to_accept()
        refund_request.set_to_refund_request()
        self.refund_request_id = refund_request.id

    def create_payment(self):
        pay_values = {
            'patient': self.patient.id,
            'type': 'phy_appointment',
            'details': 'Physiotherapy appointment',
            'date': self.appointment_date,
            'phy_appointment': self.id,
            'payment_method': 'cash',
            'state': 'Send',
            'payment_amount': self.amount_payable,
        }
        pay_req = self.env['sm.shifa.requested.payments'].create(pay_values)
        pay_req.set_to_send()
        self.pay_req_id = pay_req.id

    @api.model
    def create(self, vals):
        appointment = super(ShifaAppointmentSaleOrder, self).create(vals)
        payment_method = appointment.payment_made_through
        if payment_method == 'mobile':
            patient = vals.get('patient')
        if payment_method == 'call_center' or payment_method == 'on_spot':
            self.create_payement_request(appointment)
        return appointment
