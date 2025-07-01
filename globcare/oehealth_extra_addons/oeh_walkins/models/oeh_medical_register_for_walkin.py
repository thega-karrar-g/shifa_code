##############################################################################
#    Copyright (C) 2015 - Present, oeHealth (<https://www.oehealth.in>). All Rights Reserved
#    oeHealth, Hospital Management Solutions

# Odoo Proprietary License v1.0
#
# This software and associated files (the "Software") may only be used (executed,
# modified, executed after modifications) if you have purchased a valid license
# from the authors, typically via Odoo Apps, oeHealth.in, braincrewapps.com, or if you have received a written
# agreement from the authors of the Software.
#
# You may develop Odoo modules that use the Software as a library (typically
# by depending on it, importing it and using its resources), but without copying
# any source code or material from the Software. You may distribute those
# modules under the license of your choice, provided that this license is
# compatible with the terms of the Odoo Proprietary License (For example:
# LGPL, MIT, or proprietary licenses similar to this one).
#
# It is forbidden to publish, distribute, sublicense, or sell copies of the Software
# or modified copies of the Software.
#
# The above copyright notice and this permission notice must be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

##############################################################################

from odoo import fields, api, models, _
from odoo.exceptions import UserError
import datetime

class OeHealthAppointmentWalkin(models.Model):
    _name = "oeh.medical.appointment.register.walkin"
    _description = 'Patient Walk-ins Management'

    MARITAL_STATUS = [
        ('Single', 'Single'),
        ('Married', 'Married'),
        ('Widowed', 'Widowed'),
        ('Divorced', 'Divorced'),
        ('Separated', 'Separated'),
    ]

    SEX = [
        ('Male', 'Male'),
        ('Female', 'Female'),
    ]

    BLOOD_TYPE = [
        ('A', 'A'),
        ('B', 'B'),
        ('AB', 'AB'),
        ('O', 'O'),
    ]

    RH = [
        ('+','+'),
        ('-','-'),
    ]

    WALKIN_STATUS = [
        ('Scheduled', 'Scheduled'),
        ('Completed', 'Completed'),
        ('Invoiced', 'Invoiced'),
    ]

    def _get_physician(self):
        """Return default physician value"""
        therapist_obj = self.env['oeh.medical.physician']
        domain = [('oeh_user_id', '=', self.env.uid)]
        user_ids = therapist_obj.search(domain)
        if user_ids:
            return user_ids.id or False
        else:
            return False

    company_id = fields.Many2one(
        'res.company', store=True, default=lambda self: self.env.company
    )

    name = fields.Char(string='Queue #', size=128, required=True, readonly=True, default=lambda *a: '/')
    patient = fields.Many2one('oeh.medical.patient', string='Patient', help="Patient Name", required=True, readonly=True, states={'Scheduled': [('readonly', False)]})
    dob = fields.Date(string='Date of Birth', readonly=True, states={'Scheduled': [('readonly', False)]})
    sex = fields.Selection(SEX, string='Sex', index=True, readonly=True, states={'Scheduled': [('readonly', False)]})
    marital_status = fields.Selection(MARITAL_STATUS, string='Marital Status', readonly=True, states={'Scheduled': [('readonly', False)]})
    blood_type = fields.Selection(BLOOD_TYPE, string='Blood Type', readonly=True, states={'Scheduled': [('readonly', False)]})
    rh = fields.Selection(RH, string='Rh', readonly=True, states={'Scheduled': [('readonly', False)]})
    doctor = fields.Many2one('oeh.medical.physician', string='Responsible Doctor', readonly=False, states={'Scheduled': [('readonly', True)]}, default=_get_physician)
    state = fields.Selection(WALKIN_STATUS, string='State', readonly=True, states={'Scheduled': [('readonly', False)]}, default=lambda *a: 'Scheduled')
    comments = fields.Text(string='Comments', readonly=True, states={'Scheduled': [('readonly', False)]})
    date = fields.Datetime(string='Date', required=True, readonly=True, states={'Scheduled': [('readonly', False)]}, default=lambda *a: datetime.datetime.now())
    evaluation_ids = fields.One2many('oeh.medical.evaluation', 'walkin', string='Evaluation') # , readonly=True, states={'Scheduled': [('readonly', False)]}
    prescription_ids = fields.One2many('oeh.medical.prescription','walkin', string='Prescriptions') # , readonly=True, states={'Scheduled': [('readonly', False)]}
    lab_test_ids = fields.One2many('oeh.medical.lab.test', 'walkin', string='Lab Tests') # , readonly=True, states={'Scheduled': [('readonly', False)]}
    inpatient_ids = fields.One2many('oeh.medical.inpatient', 'walkin', string='Inpatient Admissions', readonly=True, states={'Scheduled': [('readonly', False)]})
    vaccine_ids = fields.One2many('oeh.medical.vaccines', 'walkin', string='Vaccines', readonly=True, states={'Scheduled': [('readonly', False)]})
    move_id = fields.Many2one('account.move', string='Invoice #')

    _sql_constraints = [
        ('full_name_uniq', 'unique (company_id,name)', 'The Queue Number must be unique')
    ]


    @api.model
    def create(self, vals):
        company = self.env['res.company']._company_default_get('oeh.medical.appointment.register.walkin')
        search_sequence = self.env['ir.sequence'].search(
            [('code', '=', 'oeh.medical.appointment.register.walkin'), ('company_id', 'in', [company.id, False])], order='company_id')
        if not search_sequence:
            values = {
                'name': 'Walkin (' + str(company.name) + ')',
                'code': 'oeh.medical.appointment.register.walkin',
                'company_id': company.id,
                'prefix': 'WI/' + datetime.datetime.now().strftime('%m-%d-%Y') + '/',
                'padding': 5,
            }
            self.env['ir.sequence'].sudo().create(values)
            vals['name'] = self.env['ir.sequence'].next_by_code('oeh.medical.appointment.register.walkin')
            medical_surgery = models.Model.create(self, vals)
            return medical_surgery
        else:
            sequence = self.env['ir.sequence'].next_by_code('oeh.medical.appointment.register.walkin')
            vals['name'] = sequence
            return super(OeHealthAppointmentWalkin, self).create(vals)

    @api.onchange(patient)
    def onchange_patient(self):
        if self.patient:
            self.dob = self.patient.dob
            self.sex = self.patient.sex
            self.marital_status = self.patient.marital_status
            self.blood_type = self.patient.blood_type
            self.rh = self.patient.rh

    def _get_default_journal(self):
        journal = self.env['account.journal'].search([('type', '=', 'sale')], limit=1)
        return journal

    def action_walkin_invoice_create(self):
        invoice_obj = self.env["account.move"]
        invoice_lines = []

        for acc in self:
            # Create Invoice
            if acc.doctor:
                default_journal = self._get_default_journal()

                sequence_count = 1
                invoice_lines.append((0, 0, {
                    'name': 'Walkin consultancy invoice',
                    'display_type': 'line_section',
                    'account_id': False,
                    'sequence': sequence_count,
                }))

                sequence_count += 1

                invoice_lines.append((0, 0, {
                    'display_type': False,
                    'name': acc.name,
                    'price_unit': acc.doctor.consultancy_price,
                    'quantity': 1,
                    'sequence': sequence_count,
                }))

                invoice = invoice_obj.sudo().create({
                    'move_type': 'out_invoice',
                    'journal_id': default_journal.id,
                    'partner_id': acc.patient.partner_id.id,
                    'patient': acc.patient.id,
                    'invoice_date': acc.date,
                    'date': acc.date,
                    'ref': "Walkin # : " + acc.name,
                    'invoice_line_ids': invoice_lines,
                })

                self.write({'state': 'Invoiced', 'move_id': invoice.id})

            else:
                raise UserError(_('Configuration error!\nCould not find any physician to create the invoice !'))

        return True

    def set_to_completed(self):
        return self.write({'state': 'Completed'})


# Physician schedule management for Walkins
class OeHealthPhysicianWalkinSchedule(models.Model):
    _name = "oeh.medical.physician.walkin.schedule"
    _description = "Information about walkin schedule"

    name = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True)
    physician_id = fields.Many2one('oeh.medical.physician', string='Doctor', index=True, ondelete='cascade')

    _order = 'name desc'


# Inheriting Physician screen to add walkin schedule lines

class OeHealthPhysician(models.Model):
    _inherit = "oeh.medical.physician"
    walkin_schedule_lines = fields.One2many('oeh.medical.physician.walkin.schedule', 'physician_id', string='Walkin Schedule')

# Inheriting Inpatient module to add "Walkin" screen reference
class OeHealthInpatient(models.Model):
    _inherit = 'oeh.medical.inpatient'
    walkin = fields.Many2one('oeh.medical.appointment.register.walkin', string='Queue #', readonly=True, states={'Draft': [('readonly', False)]})


# Inheriting Prescription module to add "Walkin" screen reference
class OeHealthPrescription(models.Model):
    _inherit = 'oeh.medical.prescription'
    walkin = fields.Many2one('oeh.medical.appointment.register.walkin', string='Queue #', readonly=True, states={'Draft': [('readonly', False)]})


# Inheriting Evaluation module to add "Walkin" screen reference
class OeHealthPatientEvaluation(models.Model):
    _inherit = 'oeh.medical.evaluation'
    walkin = fields.Many2one('oeh.medical.appointment.register.walkin', string='Queue #')


# Inheriting Evaluation module to add "Walkin" screen reference
class OeHealthLabTests(models.Model):
    _inherit = 'oeh.medical.lab.test'
    walkin = fields.Many2one('oeh.medical.appointment.register.walkin', string='Queue #', readonly=True, states={'Draft': [('readonly', False)]})


# Inheriting Evaluation module to add "Walkin" screen reference
class OeHealthVaccines(models.Model):
    _inherit = 'oeh.medical.vaccines'
    walkin = fields.Many2one('oeh.medical.appointment.register.walkin', string='Queue #')
