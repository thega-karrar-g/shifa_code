import datetime

from odoo.exceptions import ValidationError
from odoo import models, fields, api, _


class ShifaInvestigation(models.Model):
    _name = "sm.shifa.investigation"
    _description = 'Investigation'
    _inherit = ['mail.thread']

    STATES = [
        ('Draft', 'Draft'),
        ('Call Center', 'Call Center'),
        ('Team', 'Team'),
        ('Test In Progress', 'Test In Progress'),
        ('Uploaded', 'Uploaded'),
        ('Cancelled', 'Cancelled'),
    ]

    name = fields.Char('Reference', index=True, copy=False)
    patient = fields.Many2one('oeh.medical.patient', string='Patient', help="Patient Name", required=True,
                              readonly=True, states={'Draft': [('readonly', False)]})
    requester_id = fields.Many2one('oeh.medical.physician', string='Doctor',
                                   help="Doctor", readonly=True,  domain=[('role_type', 'in', ['HD', 'HHCD', 'TD']), ('active', '=', True)],
                                   states={'Draft': [('readonly', False)]})
    diagnosis = fields.Text(string='Diagnosis', readonly=True,
                            states={'Call Center': [('readonly', False)], 'Team': [('readonly', False)],
                                    'Test In Progress': [('readonly', False)]})
    date_requested = fields.Datetime(string='Date requested', readonly=True)
    date_analysis = fields.Datetime(string='Date of the Analysis', readonly=True)
    result = fields.Text(string='Result', readonly=True,
                         states={'Draft': [('readonly', False)], 'Call Center': [('readonly', False)], 'Team': [('readonly', False)],
                                 'Test In Progress': [('readonly', False)]})
    investigation_document = fields.Binary(string="Document", readonly=True,
                                           states={'Draft': [('readonly', False)], 'Call Center': [('readonly', False)], 'Team': [('readonly', False)],
                                                   'Test In Progress': [('readonly', False)]})
    investigation_image = fields.Binary(readonly=True,
                                        states={'Draft': [('readonly', False)], 'Call Center': [('readonly', False)], 'Team': [('readonly', False)],
                                                'Test In Progress': [('readonly', False)]})
    investigation_analysis = fields.Char(string="Analysis", readonly=True,
                                         states={'Draft': [('readonly', False)], 'Call Center': [('readonly', False)], 'Team': [('readonly', False)],
                                                 'Test In Progress': [('readonly', False)]})
    investigation_conclusion = fields.Char(string="Conclusion", readonly=True,
                                           states={'Draft': [('readonly', False)], 'Call Center': [('readonly', False)], 'Team': [('readonly', False)],
                                                   'Test In Progress': [('readonly', False)]})

    tele_appointment = fields.Char() # temp field only. we will remove it latter.

    # tele_appointment = fields.Many2one('sm.telemedicine.appointment', string='Tele-Appointment',
    #                                    readonly=True, states={'Draft': [('readonly', False)]})

    appointment = fields.Many2one('oeh.medical.appointment', string='Tele-Appointment',
                                       readonly=True, states={'Draft': [('readonly', False)]})
    hhc_appointment = fields.Many2one('sm.shifa.hhc.appointment', string='HHC Appointment',
                                      readonly=True, states={'Draft': [('readonly', False)]})
    hvd_appointment = fields.Many2one('sm.shifa.hvd.appointment', string='HVD Appointment', readonly=True,
                                      states={'Draft': [('readonly', False)]})
    register_walk_in = fields.Many2one('sm.shifa.hhc.appointment', string='HHC Appointment')
    icuAdmission = fields.Many2one('oeh.medical.icu.admission', string='Home Admission #')
    physician_Admission = fields.Many2one('sm.shifa.physician.admission', string='Physician Admission #')
    state = fields.Selection(STATES, string='State', readonly=True, default=lambda *a: 'Draft')
    price = fields.Integer(readonly=True)

    # the investigation type will be joined to other module
    # type = fields.Selection([
    #     ('Test', 'Test')
    # ], readonly=True, states={'Draft': [('readonly', False)]})
    investigation_name = fields.Many2one('sm.shifa.investigation.name', readonly=True, states={'Draft': [('readonly', False)]})
    attachment_ids = fields.Many2many('ir.attachment', string="Results", states={'Done': [('readonly', True)]})
    attachment_count = fields.Integer(compute="_compute_attachment_count")

    def _compute_attachment_count(self):
        for record in self:
            record['attachment_count'] = len(record.attachment_ids)


    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('sm.shifa.investigation')
        return super(ShifaInvestigation, self).create(vals)


    # def print_patient_labtest(self):
    #     return self.env.ref('oehealth.action_report_patient_labtest').report_action(self)

    def set_to_call_center(self):
        return self.write({'state': 'Call Center', 'date_requested': datetime.datetime.now()})

    def set_to_upload(self):
        return self.write({'state': 'Uploaded'})

    def set_to_cancel(self):
        return self.write({'state': 'Cancelled'})

    def set_to_team(self):
        return self.write({'state': 'Team'})

    def set_to_investigation_start(self):
        return self.write({'state': 'Test In Progress', 'date_analysis': datetime.datetime.now()})

    # connect the patient details with appointment
    @api.onchange('hvd_appointment')
    def _onchange_hvd_appointment(self):
        if self.hvd_appointment:
            self.patient = self.hvd_appointment.patient
            self.hhc_appointment = None
            self.appointment = None
            # self.tele_appointment = None

    @api.onchange('hhc_appointment')
    def _onchange_hhc_appointment(self):
        if self.hhc_appointment:
            self.patient = self.hhc_appointment.patient
            self.hvd_appointment = None
            self.appointment = None
            # self.tele_appointment = None

    @api.onchange('appointment')
    def _onchange_tele_appointment(self):
        if self.appointment:
            self.patient = self.appointment.patient
            self.hhc_appointment = None
            self.hvd_appointment = None

    # @api.onchange('tele_appointment')
    # def _onchange_tele_appointment(self):
    #     if self.tele_appointment:
    #         self.patient = self.tele_appointment.patient
    #         self.hhc_appointment = None
    #         self.hvd_appointment = None

    # the invoiced is depend on the service itself
    # def action_investigation_invoice_create(self):
    #     invoice_obj = self.env["account.move"]
    #     invoice_lines = []
    #
    #     for acc in self:
    #         # Create Invoice
    #         if acc.service:
    #             default_journal = self._get_default_journal()
    #
    #             sequence_count = 1
    #             invoice_lines.append((0, 0, {
    #                 'name': 'HHC Appointment consultancy invoice',
    #                 'display_type': 'line_section',
    #                 'account_id': False,
    #                 'sequence': sequence_count,
    #             }))
    #
    #             sequence_count += 1
    #
    #             invoice_lines.append((0, 0, {
    #                 'display_type': False,
    #                 'name': acc.service.product_id.name,
    #                 'price_unit': acc.service.list_price,
    #                 'quantity': 1,
    #                 'sequence': sequence_count,
    #             }))
    #
    #             invoice = invoice_obj.sudo().create({
    #                 'move_type': 'out_invoice',
    #                 'journal_id': default_journal.id,
    #                 'partner_id': acc.patient.partner_id.id,
    #                 'patient': acc.patient.id,
    #                 'invoice_date': datetime.datetime.now().date(),
    #                 'date': acc.appointment_date,
    #                 'payment_reference': acc.payment_reference,
    #                 'ref': "# : " + acc.service.product_id,
    #                 'investigation': acc.id,
    #                 'invoice_line_ids': invoice_lines,
    #             })
    #
    #             self.write({'state': 'Invoiced', 'move_id': invoice.id})
    #
    #         else:
    #             raise UserError(_('Configuration error!\nCould not find any physician to create the invoice !'))
    #
    #     return True

#
# class ShifaInvestigationInAccountMove(models.Model):
#     _inherit = 'account.move'
#
#     investigation = fields.Many2one('sm.shifa.investigation', string="Investigation")
