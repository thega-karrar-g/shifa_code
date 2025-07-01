import base64
from odoo import api, fields, models, _
from datetime import date
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, UserError


class SMComplaints(models.Model):
    _name = 'sm.shifa.complaints'
    _description = "Complaints"
    STATES = [
        ('draft', 'Draft'),
        ('received', 'Received'),
        ('processed', 'Processed'),
        ('canceled', 'Canceled'),
    ]

    NATIONALITY_STATE = [
        ('KSA', 'Saudi'),
        ('NON', 'Non-Saudi')
    ]

    state = fields.Selection(STATES, string='State', default=lambda *a: 'draft', readonly=True)
    name = fields.Char('Reference', index=True, copy=False, default=lambda *a: '/')
    patient = fields.Many2one('oeh.medical.patient', string='Patient', required=True, readonly=True,
                              states={'draft': [('readonly', False)]})
    dob = fields.Date(string='Date of Birth', related='patient.dob', readonly=True,
                      states={'draft': [('readonly', False)]})
    marital_status = fields.Selection(string='Marital Status', related='patient.marital_status', readonly=True,
                                      states={'draft': [('readonly', False)]})
    sex = fields.Selection(string='Sex', related='patient.sex', readonly=True, states={'draft': [('readonly', False)]})
    ssn = fields.Char(size=256, related='patient.ssn', readonly=True, states={'draft': [('readonly', False)]})
    ksa_nationality = fields.Selection(NATIONALITY_STATE, related='patient.ksa_nationality', readonly=True,
                                       states={'draft': [('readonly', False)]})
    mobile = fields.Char(string='Mobile', related='patient.mobile', readonly=True,
                         states={'draft': [('readonly', False)]})
    age = fields.Char(string='Age', related='patient.age', readonly=True, states={'draft': [('readonly', False)]})
    date = fields.Datetime(string="Date", readonly=True, states={'draft': [('readonly', False)]})
    patient_complaints = fields.Text(readonly=True, states={'draft': [('readonly', False)]})
    operation_manager_comment = fields.Text()
    active = fields.Boolean(default=True)

    def action_archive(self):
        for rec in self:
            if rec.state != 'canceled':
                raise UserError(_("You can archive only if it canceled record"))
        return super().action_archive()

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('sm.shifa.complaints')
        return super(SMComplaints, self).create(vals)

    def set_to_received(self):
        return self.write({'state': 'received'})

    def set_to_processed(self):
        return self.write({'state': 'processed'})

    def set_to_cancel(self):
        return self.write({'state': 'canceled'})
