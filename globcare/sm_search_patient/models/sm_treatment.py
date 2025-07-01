from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import UserError, ValidationError

class SMTreatments(models.Model):
    _name = 'sm.treatments'
    _description = 'Medical Service Orders'

    STATES = [
        ('draft', 'Draft'),
        ('send', 'Send'),
        ('invoiced', 'Invoiced'),
        ('cancelled', 'Cancelled '),
    ]

    PAY_METHOD = [
        ('call_center', 'Call center'),
        ('on_spot', 'On spot'),
        ('deferred', 'Deferred'),
    ]


    @api.depends('id_number', 'services_price')
    def _cal_vat(self):
        for rec in self:
            if rec.id_number and rec.id_number[0] == '2':
                final_pay = rec.services_price * 0.15
                rec.vat = final_pay
            else:
                rec.vat = 0.0


    @api.depends('services_price', 'vat')
    def _cal_net_payment(self):
        for rec in self:
            rec.amount_payable = rec.services_price + rec.vat

    @api.depends('service_ids.list_price')
    def _cal_services_price(self):
        for record in self:
            record.services_price = sum(record.service_ids.mapped('list_price'))

    name = fields.Char('Reference', index=True, copy=False, readonly=True)
    state = fields.Selection(STATES, string='State', default=lambda *a: 'draft', readonly=True)
    patient_id = fields.Many2one('oeh.medical.patient', string='Patient', help="Patient Name", required=True, readonly=True, states={'draft': [('readonly', False)]})
    id_number = fields.Char('ID', related='patient_id.ssn')
    mobile = fields.Char('Mobile', related='patient_id.mobile')
    first_service = fields.Many2one('sm.shifa.service', string="First Service", readonly=True, states={'draft': [('readonly', False)]})
    first_service_price = fields.Float(string="Service Price", related='first_service.list_price')
    second_service = fields.Many2one('sm.shifa.service', string="Second Service", readonly=True, states={'draft': [('readonly', False)]})
    second_service_price = fields.Float(string="2nd Service Price", related='second_service.list_price')
    third_service = fields.Many2one('sm.shifa.service', string="Third Service", readonly=True, states={'draft': [('readonly', False)]})
    third_service_price = fields.Float(string="3rd Service Price", related='third_service.list_price')
    fourth_service = fields.Many2one('sm.shifa.service', string="Fourth Service", readonly=True, states={'draft': [('readonly', False)]})
    fourth_service_price = fields.Float(string="4th Service Price", related='fourth_service.list_price')
    services_price = fields.Float(string='Services’ Price ', compute=_cal_services_price, store=True)
    vat = fields.Float(string='VAT (+) 15%', compute=_cal_vat)
    amount_payable = fields.Float('Amount Payable', compute=_cal_net_payment)
    payment_thru = fields.Selection(PAY_METHOD, string='Pay.Thru', default='call_center', readonly=True, states={'draft': [('readonly', False)]})
    pay_req_id = fields.Many2one('sm.shifa.requested.payments', string='Payment Request#', copy=False, readonly=True)
    move_id = fields.Many2one('account.move', string='account move', ondelete='restrict', readonly=True, copy=False)
    date = fields.Date(string='Date',  readonly=True, states={'draft': [('readonly', False)]})
    service_ids = fields.Many2many('sm.shifa.service', string="Service", readonly=True, states={'draft': [('readonly', False)]})
    caregiver_contract_id = fields.Many2one('sm.caregiver.contracts', string="Caregiver Contract")
    hhc_appointment_id = fields.Many2one('sm.shifa.hhc.appointment', string="HHC Appointment")
    phy_appointment_id = fields.Many2one('sm.shifa.physiotherapy.appointment', string="Physiotherapy Appointment")
    # archive
    active = fields.Boolean(default=True)
    pro_deferred_pay = fields.Boolean(string="Pro. Deferred Pay")

    def create_payement_request(self):
        pay_values = {
            'patient': self.patient_id.id,
            'details': "Treatment" + self.name,
            'date': self.date,
            'payment_method': 'point_of_sale',
            'state': 'Send',
            'payment_amount': self.amount_payable,
        }
        pay_req = self.env['sm.shifa.requested.payments'].create(pay_values)
        pay_req.set_to_send()
        self.pay_req_id = pay_req.id

    def _get_default_journal(self):
        journal = self.env['account.journal'].search([
                    ('type', '=', 'sale'),
                    ('analytic_account_id', '=', self.env.user.analytic_account_id.id)
                ], limit=1)
        if not journal:
            journal = self.env['account.journal'].search([
                ('type', '=', 'sale')
            ], limit=1)
        return journal

        # get the service invoice line
    def get_invoice_lines(self):
        invoice_lines = []
        if self.patient_id.ksa_nationality == 'NON':
            company = self.env.user.company_id
            tax = company.account_sale_tax_id
        else:
            tax = False
        for service in self.service_ids:
            sequence = 0
            invoice_lines.append(
                (0, 0, {
                    'product_id': service.product_id.id,
                    'price_unit': service.list_price,
                    'tax_ids': tax,
                    'sequence': sequence,
                }))
            sequence += 1
        return invoice_lines

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

        if not self.move_id:
            vals = {
                'move_type': 'out_invoice',
                'journal_id': default_journal.id,
                'partner_id': self.patient_id.partner_id.id,
                #'analytic_account_id': self.env.user.analytic_account_id.id,
                'analytic_account_id': analytical_account_id,
                'patient': self.patient_id.id,
                'invoice_date': datetime.now().date(),
                'date': datetime.now().date(),
                'ref': "Treatment",
                'invoice_line_ids': invoice_lines,
            }
            invoice = self.env['account.move'].sudo().create(vals)
            invoice.action_post()
            self.move_id = invoice

    def open_invoice_view(self):
        action = self.env['ir.actions.act_window']._for_xml_id('account.action_move_out_invoice_type')
        action['domain'] = [('id', '=', self.move_id.id)]
        action.update({'context': {}})
        return action

    def open_payment_view(self):
        action = self.env['ir.actions.act_window']._for_xml_id('smartmind_shifa_extra.sm_shifa_requested_payments_action')
        action['domain'] = [('id', '=', self.pay_req_id.id)]
        action.update({'context': {}})
        return action

    @api.model
    def create(self, vals):
        # Generate the sequence number for the treatment
        vals['name'] = self.env['ir.sequence'].next_by_code('sm.treatments')

        # Create the record using the super method
        record = super(SMTreatments, self).create(vals)

        # Assign the created record ID to the caregiver's treatment_id if the context is set
        if self.env.context.get("from_caregiver"):
            caregiver_contract_id = vals.get('caregiver_contract_id')  # Correct way to access vals
            if caregiver_contract_id:
                appointment = self.env['sm.caregiver.contracts'].search([('id', '=', int(caregiver_contract_id))],
                                                                        limit=1)
                if appointment:
                    appointment.treatment_id = record.id

        return record

    def set_to_send(self):
        # Check for deferred payment approval
        if self.payment_thru == 'deferred' and not self.pro_deferred_pay:
            raise UserError("Waiting for Admin approval!")
        self.date = datetime.now()
        self.create_payement_request()
        self.pay_req_id.generate_pay_link()
        return self.write({'state': 'send'})

    def set_to_invoiced(self):
        if self.pay_req_id and self.pay_req_id.state not in ['Paid', 'Done']:
            raise UserError("You cannot move to the next action until the payment is paid or processed!")
        self.create_invoice()
        return self.write({'state': 'invoiced'})

    def set_to_cancelled(self):
        if self.move_id:
            self.move_id.button_draft()
            self.move_id.button_cancel()
        return self.write({'state': 'cancelled'})

    def unlink(self):
        for rec in self:
            if rec.state != 'cancelled':
                raise UserError("You can only delete cancelled Treatments!")

