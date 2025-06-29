from odoo import models, fields, api, _
import datetime
from odoo.exceptions import ValidationError, UserError


class CancellationRefund(models.Model):
    _name = 'sm.shifa.cancellation.refund'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'sequence.mixin']
    _description = 'Cancellation Refund'

    REFUND_STATE = [
        ('received', 'Received'),
        ('operation_manager', 'Operation Manager'),
        ('Reject', 'Rejected'),
        ('requestaccepted', 'Request Accepted'),
        ('Processed', 'Refund Request'),
        ('Refund', 'Refunded'),
        ('cancel', 'Cancelled'),
    ]

    """PAY_TYPE = [
        ('hhc_appointment', 'HHC Appointment'),
        ('tele_appointment', 'Tele Appointment'),
        ('hvd_appointment', 'HVD Appointment'),
        ('phy_appointment', 'Phy Appointment'),
        ('pcr_appointment', 'PCR Appointment'),
    ]"""

    PAY_TYPE = [
        ('hhc_appointment', 'HHC Appointment'),
        ('tele_appointment', 'Tele Appointment'),
        ('hvd_appointment', 'HVD Appointment'),
        ('phy_appointment', 'Phy Appointment'),
        ('pcr_appointment', 'PCR Appointment'),
        ('package', 'Package'),
        ('multipackage', 'Multi-Package'),
        ('instant', 'Instant')
    ]

    name = fields.Char('Reference', index=True, copy=False)
    state = fields.Selection(REFUND_STATE, string='State', readonly=True, default=lambda *a: 'received')
    patient = fields.Many2one('oeh.medical.patient', string='Patient', help="Patient Name", required=True,
                              readonly=True, states={'received': [('readonly', False)]})
    date = fields.Date(readonly=True, states={'received': [('readonly', False)]}, default=fields.Date.today())
    mobile = fields.Char(string='Mobile', related='patient.mobile',
                         readonly=True, states={'received': [('readonly', False)]})

    type = fields.Selection(PAY_TYPE, string="type")

    appointment_details_show = fields.Boolean()

    hhc_appointment = fields.Many2one('sm.shifa.hhc.appointment', string='HHC-App', readonly=True,
                                      domain="[('patient','=',patient)]",
                                      states={'received': [('readonly', False)]})

    date_hhc_appointment = fields.Date(string='Date', related="hhc_appointment.appointment_date_only", readonly=True,
                                       states={'received': [('readonly', False)]})

    appointment = fields.Many2one('oeh.medical.appointment', string='Tele-App', readonly=True,
                                  domain="[('patient','=',patient)]",
                                  states={'received': [('readonly', False)]})
    date_appointment = fields.Datetime(string='Date', related="appointment.appointment_date", readonly=True,
                                       states={'received': [('readonly', False)]})

    hvd_appointment = fields.Many2one('sm.shifa.hvd.appointment', string='HVD-App', readonly=True,
                                      domain="[('patient','=',patient)]",
                                      states={'received': [('readonly', False)]})
    date_hvd_appointment = fields.Datetime(string='Date', related="hvd_appointment.appointment_date", readonly=True,
                                           domain="[('patient','=',patient)]",
                                           states={'received': [('readonly', False)]})
    #
    phy_appointment = fields.Many2one('sm.shifa.physiotherapy.appointment', string='Phy-App', readonly=True,
                                      domain="[('patient','=',patient)]",
                                      states={'received': [('readonly', False)]})
    date_phy_appointment = fields.Date(string='Date', related="phy_appointment.appointment_date_only", readonly=True,
                                       states={'received': [('readonly', False)]})
    #
    pcr_appointment = fields.Many2one('sm.shifa.pcr.appointment', string='PCR-App', readonly=True,
                                      domain="[('patient','=',patient)]",
                                      states={'received': [('readonly', False)]})
    date_pcr_appointment = fields.Date(string='Date', related="pcr_appointment.appointment_date_only", readonly=True,
                                       states={'received': [('readonly', False)]})

    call_center_comments_show = fields.Boolean()
    call_center_comments = fields.Text(readonly=True, states={'received': [('readonly', False)]})

    operation_manager_comments_show = fields.Boolean()
    operation_manager_comments = fields.Text(readonly=True, states={'operation_manager': [('readonly', False)]})

    accounting_comments_show = fields.Boolean()
    accounting_comments = fields.Text(readonly=True, states={'Processed': [('readonly', False)]})
    reason = fields.Text()
    account_details = fields.Text()
    accepted_by = fields.Many2one('res.users')
    refund_by = fields.Many2one('res.users')
    active = fields.Boolean(default=True)
    package_id = fields.Many2one('sm.shifa.package.appointments', string='Package')
    package_date = fields.Date(string='Date')
    multi_package_id = fields.Many2one('sm.shifa.package.appointments.multi', string='Multi-Package')
    multi_package_date = fields.Date(string='Date')
    instant_id = fields.Many2one('sm.shifa.instant.consultation', 'Consultation')
    instant_date = fields.Date(string='Date')
    patient_balance = fields.Float(compute="_compute_patient_balance")
    # Indicates whether an appointment has been cancelled.
    # This field is typically updated when a user cancels an appointment via the mobile app or other channels.
    cancellation_requested = fields.Boolean(string='Cancellation Requested', default=lambda *a: 0)
    payment_id = fields.Many2one('account.payment', string='Payment #')

    def _compute_patient_balance(self):
        for record in self:
            record.patient_balance = 0.0
            if record.patient.partner_id:
                self.env.cr.execute("""
                    SELECT SUM(aml.balance)
                    FROM account_move_line aml
                    JOIN account_account aa ON aa.id = aml.account_id
                    WHERE aml.partner_id = %s
                    AND aml.parent_state = 'posted'
                    AND aa.user_type_id = 5
                """, (record.patient.partner_id.id,))
                result = self.env.cr.fetchone()
                record.patient_balance = result[0] if result else 0.0

    def action_open_statement(self):
        lines = self.env['account.move.line'].sudo().search([
            ('partner_id', '=', self.patient.partner_id.id),
            ('parent_state', '=', 'posted'),
            ('account_id.user_type_id', '=', 5)
        ])
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_account_moves_all")
        action['domain'] = [('id', 'in', lines.ids)]
        action['context'] = {'search_default_group_by_partner': 1, 'create': 0}
        return action

    def action_archive(self):
        for rec in self:
            if rec.state not in ['Reject', 'Processed', 'Refund']:
                raise UserError(_("You can archive only if it reject, processed or refund cancellation"))
        return super().action_archive()

    def set_to_operation_manager(self):
        return self.write({'state': 'operation_manager', 'date': datetime.datetime.now()})

    def set_to_accept(self):
        return self.write({'state': 'requestaccepted', 'accepted_by': self.env.user.id})

    def set_to_refund_request(self):
        return self.write({'state': 'Processed'})

    def set_to_reject(self):
        return self.write({'state': 'Reject'})

    def set_to_cancel(self):
        return self.write({'state': 'cancel'})

    def set_to_refund(self):

        # show payment dialog
        ctx = {
            'default_refund_request_id': self.id,
            'default_payment_type': 'outbound',
            'default_partner_id': self.patient.partner_id.id
        }

        # Create the payment record
        payment_obj = self.env['account.payment'].create({
            'payment_type': 'outbound',
            'partner_id': self.patient.partner_id.id,
            'payment_method_id': self.env.ref('account.account_payment_method_manual_out').id,
        })

        # Update the state and refund_by field with the created payment object ID
        self.write({
            'state': 'Refund',
            'refund_by': self.env.user.id,
            'payment_id': payment_obj.id
        })

        # Return the action to open the payment form view
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.payment',
            'view_mode': 'form',
            'res_id': payment_obj.id,
            'target': 'new',
            'context': ctx,
        }

    # def set_to_refund(self):
    #     # Update state and refund_by field
    #     self.write({'state': 'Refund', 'refund_by': self.env.user.id})
    #
    #     # show payment dialog
    #     ctx = {
    #         'default_refund_request_id': self.id,
    #         'default_payment_type': 'outbound',
    #         'default_partner_id': self.patient.partner_id.id,
    #         'default_payment_id': self.payment_id.id
    #     }
    #
    #     # Return the action
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'account.payment',
    #         'view_mode': 'form',
    #         'target': 'new',
    #         'context': ctx,
    #     }

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('sm.shifa.cancellation.refund')
        return super(CancellationRefund, self).create(vals)

    def open_account_payment(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.payment',
            'res_id': self.payment_id.id,
            'view_mode': 'form',
            'target': 'new',
        }


class PaymentAccount(models.Model):
    _inherit = 'account.payment'

    refund_request_id = fields.Many2one('sm.shifa.cancellation.refund', string='Refund Request#', copy=False,
                                        readonly=True)
