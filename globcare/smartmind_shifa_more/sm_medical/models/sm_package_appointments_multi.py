import logging
import math
from datetime import timedelta, datetime
from odoo import models, fields, api ,_
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

class ShifaAppointmentsPackages(models.Model):
    _name = 'sm.shifa.package.appointments.multi'
    _description = 'Multi Package Service Appointments'

    PACKAGE_STATES = [
        ('draft', 'Draft'),
        ('send', 'Send for payment'),
        ('schedule', 'Schedule'),
        ('generated', 'Generated'),
        ('cancel', 'Cancelled'),

    ]
    PAY_THRU = [
        ('pending', 'Free Service'),
        ('package', 'Package'),
        ('aggregator_package', 'Aggregator Package'),
    ]

    patient = fields.Many2one('oeh.medical.patient', string='Patient', required=True, readonly=False,states={'generated': [('readonly', True)], 'cancel': [('readonly', True)]})
    ssn = fields.Char(string='ID Number', readonly=True, related='patient.ssn',store=True)
    branch = fields.Selection([
        ('riyadh', 'Riyadh'),
        ('dammam', 'Dammam'),
        ('jeddah', 'Jeddah'),
    ], string="Branch", readonly=False, states={'generated': [('readonly', True)], 'cancel': [('readonly', True)]})
    state = fields.Selection(PACKAGE_STATES, string='State', default='draft',compute="_compute_state",store=True)
    package_appointments_ids = fields.One2many('sm.shifa.package.appointments','package_appointment_id','Packages', states={'generated': [('readonly', True)], 'cancel': [('readonly', True)]})
    name = fields.Char(string='Reference', readonly=True, states={'draft': [('readonly', False)]}, default=lambda self: _('New'))
    package_name = fields.Char(string='Package Name', readonly=True, states={'draft': [('readonly', False)], 'schedule': [('readonly', False)], 'send': [('readonly',False)]})
    move_id = fields.Many2one('account.move', string='account move', ondelete='restrict',copy=False)
    active = fields.Boolean('Archive', default=True)
    pay_thru = fields.Selection(PAY_THRU, string='Pay made thru', readonly=False,
                                states={'generated': [('readonly', True)], 'cancel': [('readonly', True)]}
                                , required=True)
    aggregator = fields.Many2one('sm.aggregator', string='Aggregator', readonly=False,
                                 states={'generated': [('readonly', True)], 'cancel': [('readonly', True)]})
    pay_req_id = fields.Many2one('sm.shifa.requested.payments', string='Payment Request#', copy=False, readonly=True)
    pro_pending = fields.Boolean(string="Pro. Free Service")
    move_ids = fields.One2many('account.move','multi_package_id')
    cancellation_reason = fields.Char()
    refund_req = fields.Many2one('sm.shifa.cancellation.refund', string='Refund Request')

    def create_refund_request(self):
        pay_values = {
            # 'patient': self.patient_id.id,
            'patient': self.patient.id,
            'state': 'Processed',
            'type': 'multipackage',
            'reason': '',
            'payment_request_id': self.pay_req_id.id if self.pay_req_id else False,
            'multi_package_id': self.id,
            'move_ids': [(6, 0, self.move_ids.ids)] if self.move_ids else [(5, 0, 0)]
        }
        refund_req = self.env['sm.shifa.cancellation.refund'].create(pay_values)
        self.refund_req = refund_req.id

    def open_cancel_request(self):
        action = self.env['ir.actions.act_window']._for_xml_id(
            'smartmind_shifa_extra.sm_shifa_cancellation_refund_action')
        action['domain'] = [('multi_package_id', '=', self.id)]
        action.update({'context': {}})
        return action

    def cancel(self):
        ctx = {
            'form_view_ref': 'smartmind_shifa_more.sm_shifa_package_appointment_cancel_multi',
        }
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_mode': 'form',
            'target': 'new',
            'res_id': self.id,
            'context': ctx,
        }

    def create_payment(self, amount):
        pay_values = {
            'patient': self.patient.id,
            'type': 'multipackage',
            'details': 'multi package appointment',
            'payment_method': 'cash',
            'state': 'Send',
            'payment_amount': amount,
            'multi_package_id': self.id,
        }
        pay_req = self.env['sm.shifa.requested.payments'].create(pay_values)
        pay_req.set_to_send()
        self.pay_req_id = pay_req.id
    def action_archive(self):
        for rec in self:
            if rec.state != 'cancel':
                raise UserError(_("You can archive only if it cancelled Appointments or visit done"))
        return super().action_archive()

    @api.depends('package_appointments_ids.state')
    def _compute_state(self):
        for record in self:
            has_cancel = False
            has_generated = False
            has_draft = False
            has_send = False
            has_schedule = False
            state = 'draft'
            for rec in record.package_appointments_ids:
                if rec.state == 'draft':
                    has_draft = True
                elif rec.state == 'cancel':
                    has_cancel = True
                elif rec.state == 'generated':
                    has_generated = True
                elif rec.state == 'send':
                        has_send = True
                elif rec.state == 'schedule':
                        has_schedule = True

            if has_cancel and not has_generated and not has_draft:
                state = 'cancel'
            elif has_generated and not has_cancel and not has_draft:
                state = 'generated'
            elif has_draft and not has_generated and not has_cancel:
                state = 'draft'
            elif has_send and not has_draft and not has_schedule:
                state ='send'
            elif has_schedule and not has_draft and not has_send:
                state ='schedule'

            record.state = state

    @api.model
    def create(self, vals):
        vals['name'] = self.env.ref('smartmind_shifa_more.sequence_package_multi').next_by_id()
        return super().create(vals)
    

    def set_to_generate(self):
        appointments = self.package_appointments_ids.filtered(lambda l: l.state == 'schedule')
        if appointments:
            for appointment in appointments:
                appointment.set_to_generate()
        if self.pay_thru == 'package':
            self.notification(self.pay_req_id)
        if self.pay_thru != 'pending':
            self.create_invoice()
        self._compute_state()

    def set_to_payment(self):
        appointments = self.package_appointments_ids.filtered(lambda l: l.state == 'draft')
        if appointments:
            amount = 0
            for appointment in appointments:
                appointment.set_to_payment()
                amount += appointment.amount_payable
            if self.pay_thru == 'package':
                self.create_payment(amount)
                self.notification(self.pay_req_id)
        else:
            raise UserError(_('Please add a package appointment first'))

    def open_payment(self):
        action = self.env['ir.actions.act_window']._for_xml_id('smartmind_shifa_extra.sm_shifa_requested_payments_action')
        action['domain'] = [('id', '=', self.pay_req_id.id)]
        action.update({'context': {}})
        return action
    def set_to_scheduling(self):
        appointments = self.package_appointments_ids.filtered(lambda l: l.state == 'send')
        if appointments:
            for appointment in appointments:
                appointment.set_to_scheduling()
        self._compute_state()

    def notification(self, payment_id):
        msg = "payment request is  [ %s ]" % (payment_id.state)
        msg_vals = {"message": msg, "title": "Payment Request", "sticky": True}
        admin_group_ids = [self.env.ref('oehealth.group_oeh_medical_manager').id,
                           self.env.ref('smartmind_shifa.group_oeh_medical_operation_manager').id,
                           self.env.ref('smartmind_shifa.group_oeh_medical_call_center').id]
        for group_id in admin_group_ids:
            group_users = self.env['res.users'].search([('groups_id', 'in', group_id)])
            for user in group_users:
                user.notify_success(**msg_vals)

    def action_cancel(self):
        #if self.move_ids.filtered(lambda l: l.move_type == 'out_invoice' and l.state == 'posted'):
            #self.create_credit_note()
        receivable_line = discount_lines = False
        discount_amount = 0
        if self.move_ids.filtered(lambda l: l.move_type == 'out_invoice'):
            receivable_line = self.move_ids.filtered(lambda l: l.move_type == 'out_invoice')[0].line_ids.filtered(
                lambda l: l.account_id.user_type_id.id == 5)
            discount_lines = self.move_ids.filtered(lambda inv: inv.move_type == 'out_invoice').mapped('invoice_line_ids').filtered(lambda l: l.price_unit < 0)
            discount_amount = sum(discount_lines.mapped('price_subtotal'))

        for rec in self.package_appointments_ids:
            rec.with_context(from_multi=True, from_package=True).action_cancel()
            for move in rec.move_ids.filtered(lambda l: l.move_type in ['out_refund','entry']):
                move.sudo().write({"package_id": False, 'multi_package_id': self.id})
        

        if discount_amount != 0:
            if self.move_ids.filtered(lambda l: l.move_type == 'out_refund' and l.amount_total > discount_amount):
                credit_note = self.move_ids.filtered(lambda l: l.move_type == 'out_refund' and l.amount_total > discount_amount)[0]
                credit_note.button_draft()
                self.env['account.move.line'].sudo().create({
                    'account_id': discount_lines[0].account_id.id,
                    'move_id': credit_note.id,
                    'price_unit': discount_amount,
                    'name': 'Discount',
                }).with_context(check_move_validity=False)._onchange_price_subtotal()
                credit_note.with_context(check_move_validity=False)._onchange_invoice_line_ids()
                credit_note.with_context(check_move_validity=False)._recompute_dynamic_lines(True,True)
                credit_note.with_context(check_move_validity=False)._compute_amount()
                credit_note.action_post()
        credit_note_line = self.move_ids.filtered(lambda l: l.move_type == 'out_refund').mapped('line_ids').filtered(lambda l: l.account_id.user_type_id.id == 5)
        if receivable_line and credit_note_line:
            lines = receivable_line + credit_note_line
            lines.reconcile()
        
        self.create_refund_request()

    def create_invoice(self):
        if self.branch == 'riyadh':
            analytical_account_id = 2
        elif self.branch == 'dammam':
            analytical_account_id = 3
        if not self.package_appointments_ids.filtered(lambda p: p.state == 'generated'):
            return
        
        invoice_lines = []
        #default_journal = self._get_default_journal()
        default_journal = self.env['account.journal'].sudo().search([
            ('type','=','sale'),
            ('analytic_account_id','=',analytical_account_id),
            ('company_id','=',self.env.user.company_id.id),
        ],limit=1)           
        # Create Invoice

        discount_type = False
        discount_amount = 0

        for rec in self.package_appointments_ids.filtered(lambda p: p.state == 'generated'):
            invoice_lines.append(rec.get_invoice_lines())
            if rec.discount or rec.admin_discount:
                discount_type = 'percentage'
                discount_amount += rec.discount_amount
        
        if not self.move_id and invoice_lines:
            vals = {
                'move_type': 'out_invoice',
                'journal_id': default_journal.id,
                'partner_id': self.patient.partner_id.id if self.pay_thru == 'package' else self.aggregator.partner_id.id,
                'analytic_account_id': analytical_account_id,
                'patient': self.patient.id,
                'invoice_date': datetime.now().date(),
                'date': datetime.now().date(),
                'ref': "Multi Package Appointment " + self.name,
                'discount_type': discount_type,
                'discount_amount': discount_amount,
                'multi_package_id': self.id
            }
            
            invoice = self.env['account.move'].sudo().create(vals)
            if self.package_name:
                section = self.env['account.move.line'].sudo().create({
                    'display_type': 'line_section',
                    'name': self.package_name,
                    'move_id': invoice.id,
                    'sequence': 0,
                })
            for line in invoice_lines:
                line = line[0][2]
                inv_line = self.env['account.move.line'].with_context(check_move_validity=False).sudo().create({
                    'account_id': self.env['account.account'].search([('code','=','2121002')]).id,
                    'product_id': line['product_id'],
                    'price_unit': line['price_unit'],
                    'tax_ids': [(6, 0, line['tax_ids'].ids)] if line['tax_ids'] else False,
                    'sequence': line['sequence'],
                    'move_id': invoice.id,
                    'name': self.env['product.product'].browse(line['product_id']).name,
                })

                inv_line.with_context(check_move_validity=False)._onchange_price_subtotal()


            line = invoice.invoice_line_ids.filtered(lambda l: l.name == 'Discount')
            if line:
                line[0].sudo().with_context(check_move_validity=False).write({"price_unit": -discount_amount})
                line.with_context(check_move_validity=False)._onchange_price_subtotal()
            
            invoice.with_context(check_move_validity=False)._onchange_invoice_line_ids()
            invoice.with_context(check_move_validity=False)._recompute_dynamic_lines(True,True)
            invoice.with_context(check_move_validity=False)._compute_amount()
            invoice.with_context(check_move_validity=False).action_post()
            self.move_id = invoice

    def create_credit_note(self):
        if not self.package_appointments_ids.filtered(lambda p: p.state == 'generated'):
            return
        
        invoice_lines = []
        default_journal = self._get_default_journal()
        # Create Invoice

        discount_type = False
        discount_amount = 0

        for rec in self.package_appointments_ids.filtered(lambda p: p.state == 'generated'):
            invoice_lines.append(rec.get_invoice_lines())
            if rec.discount or rec.admin_discount:
                discount_type = 'percentage'
                discount_amount += rec.discount_amount
        
        if not self.move_id and invoice_lines:
            vals = {
                'move_type': 'out_invoice',
                'journal_id': default_journal.id,
                'partner_id': self.patient.partner_id.id if self.pay_thru == 'package' else self.aggregator.partner_id.id,
                'analytic_account_id': self.env.user.analytic_account_id.id,
                'patient': self.patient.id,
                'invoice_date': datetime.now().date(),
                'date': datetime.now().date(),
                'ref': "Multi Package Appointment " + self.name,
                'discount_type': discount_type,
                'discount_amount': discount_amount
            }
            
            invoice = self.env['account.move'].sudo().create(vals)
            if self.package_name:
                section = self.env['account.move.line'].sudo().create({
                    'display_type': 'line_section',
                    'name': self.package_name,
                    'move_id': invoice.id,
                    'sequence': 0,
                })
            for line in invoice_lines:
                line = line[0][2]
                inv_line = self.env['account.move.line'].with_context(check_move_validity=False).sudo().create({
                    'account_id': default_journal.default_account_id.id,
                    'product_id': line['product_id'],
                    'price_unit': line['price_unit'],
                    'tax_ids': [(6, 0, line['tax_ids'].ids)] if line['tax_ids'] else False,
                    'sequence': line['sequence'],
                    'move_id': invoice.id,
                    'name': self.env['product.product'].browse(line['product_id']).name,
                })

                inv_line.with_context(check_move_validity=False)._onchange_price_subtotal()


            line = invoice.invoice_line_ids.filtered(lambda l: l.name == 'Discount')
            if line:
                line[0].sudo().with_context(check_move_validity=False).write({"price_unit": -discount_amount})
                line.with_context(check_move_validity=False)._onchange_price_subtotal()
            
            invoice.with_context(check_move_validity=False)._onchange_invoice_line_ids()
            invoice.with_context(check_move_validity=False)._recompute_dynamic_lines(True,True)
            invoice.with_context(check_move_validity=False)._compute_amount()
            invoice.with_context(check_move_validity=False).action_post()
            raise UserError(invoice)

     # open invoice
    def open_invoice_view(self):
        action = self.env['ir.actions.act_window']._for_xml_id('account.action_move_out_invoice_type')
        action['domain'] = ['|',('id', '=', self.move_id.id),('id', 'in', self.move_ids.ids)]
        action.update({'context': {}})
        return action

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

    def unlink(self):
        for rec in self:
            if rec.state != 'cancel':
                raise UserError("You can only delete cancelled packages!")
        
        return super().unlink()

class AccountMove(models.Model):
    _inherit = 'account.move'
    multi_package_id = fields.Many2one('sm.shifa.package.appointments.multi')