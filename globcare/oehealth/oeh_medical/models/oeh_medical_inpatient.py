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

from odoo import api, fields, models, _
import datetime
from odoo import tools
from datetime import date
from odoo.exceptions import UserError


# Inpatient Prescriped Medicines details
class OeHealthInpatientPrescribedMedicaments(models.Model):
    _name = 'oeh.medical.inpatient.prescribed.medicine'
    _description = 'Inpatient Admissions Prescribed Medicines'

    FREQUENCY_UNIT = [
        ('Seconds', 'Seconds'),
        ('Minutes', 'Minutes'),
        ('Hours', 'Hours'),
        ('Days', 'Days'),
        ('Weeks', 'Weeks'),
        ('When Required', 'When Required'),
    ]

    DURATION_UNIT = [
        ('Minutes', 'Minutes'),
        ('Hours', 'Hours'),
        ('Days', 'Days'),
        ('Months', 'Months'),
        ('Years', 'Years'),
        ('Indefinite', 'Indefinite'),
    ]

    inpatient_id = fields.Many2one('oeh.medical.inpatient', string='Inpatient Admission Reference', required=True, ondelete='cascade', index=True)
    name = fields.Many2one('oeh.medical.medicines', string='Medicines', help="Prescribed Medicines",
                           domain=[('medicament_type', '=', 'Medicine')], required=True)
    indication = fields.Many2one('oeh.medical.pathology', string='Indication',
                                 help="Choose a disease for this medicament from the disease list. It can be an existing disease of the patient or a prophylactic.")
    dose = fields.Integer(string='Dose', help="Amount of medicines (eg, 250 mg ) each time the patient takes it")
    dose_unit = fields.Many2one('oeh.medical.dose.unit', string='Dose Unit',
                                help="Unit of measure for the medication to be taken")
    dose_route = fields.Many2one('oeh.medical.drug.route', string='Administration Route',
                                 help="HL7 or other standard drug administration route code.")
    dose_form = fields.Many2one('oeh.medical.drug.form', 'Form', help="Drug form, such as tablet or gel")
    qty = fields.Integer(string='Quantity', help="Quantity of units (eg, 2 capsules) of the medicament",
                         default=lambda *a: 1.0)
    common_dosage = fields.Many2one('oeh.medical.dosage', string='Frequency',
                                    help="Common / standard dosage frequency for this medicines")
    frequency = fields.Integer('Frequency')
    frequency_unit = fields.Selection(FREQUENCY_UNIT, 'Unit', index=True)
    admin_times = fields.Char(string='Admin hours', size=128,
                              help='Suggested administration hours. For example, at 08:00, 13:00 and 18:00 can be encoded like 08 13 18')
    duration = fields.Integer(string='Treatment duration')
    duration_period = fields.Selection(DURATION_UNIT, string='Treatment period',
                                       help="Period that the patient must take the medication. in minutes, hours, days, months, years or indefinately",
                                       index=True)
    start_treatment = fields.Datetime(string='Start of treatment')
    end_treatment = fields.Datetime('End of treatment')
    info = fields.Text('Comment')
    patient = fields.Many2one('oeh.medical.patient', 'Patient', help="Patient Name")


# Inpatient Consumed Medicines details
class OeHealthInpatientConsumedMedicaments(models.Model):
    _name = 'oeh.medical.inpatient.consumed.medicine'
    _description = 'Inpatient Admissions Consumed Medicines'

    inpatient_id = fields.Many2one('oeh.medical.inpatient', string='Inpatient Admission Reference', required=True, ondelete='cascade', index=True)
    name = fields.Many2one('oeh.medical.medicines', string='Consumed Medicine', required=True)
    date_time = fields.Datetime(string='Date & Time', required=True, default=datetime.datetime.now())
    user_id = fields.Many2one('res.users', string='Given By', default=lambda self: self.env.user)
    dose_no = fields.Integer('Dose #')
    dose = fields.Float('Dose', help='Amount of medication (eg, 250 mg) per dose')
    dose_unit = fields.Many2one('oeh.medical.dose.unit', 'Dose unit',
                                help='Unit of measure for the medication to be taken')
    qty = fields.Integer(string='Quantity', help="Quantity of units (eg, 2 capsules) of the medicament",
                         default=lambda *a: 1.0)
    remarks = fields.Text('Remarks')


# Inpatient Hospitalization Management
class OeHealthInpatient(models.Model):
    _name = 'oeh.medical.inpatient'
    _description = "Information about the Patient administration"

    ADMISSION_TYPE = [
        ('Routine', 'Routine'),
        ('Maternity', 'Maternity'),
        ('Elective', 'Elective'),
        ('Urgent', 'Urgent'),
        ('Emergency', 'Emergency'),
        ('Other', 'Other'),
    ]

    INPATIENT_STATES = [
        ('Draft', 'Draft'),
        ('Hospitalized', 'Hospitalized'),
        ('Discharged', 'Discharged'),
        ('Invoiced', 'Invoiced'),
        ('Cancelled', 'Cancelled'),
    ]

    # Automatically detect logged in physician
    def _get_physician(self):
        """Return default physician value"""
        therapist_obj = self.env['oeh.medical.physician']
        domain = [('oeh_user_id', '=', self.env.uid)]
        user_ids = therapist_obj.search(domain, limit=1)
        if user_ids:
            return user_ids.id or False
        else:
            return False

    company_id = fields.Many2one(
        'res.company', store=True, default=lambda self: self.env.company
    )
    name = fields.Char(string='Inpatient #', size=128, readonly=True, required=True, default=lambda *a: '/')
    patient = fields.Many2one('oeh.medical.patient', string='Patient', help="Patient Name", required=True,
                              readonly=True, states={'Draft': [('readonly', False)]})
    institution = fields.Many2one('oeh.medical.health.center', string='Health Center', readonly=True,
                                  states={'Draft': [('readonly', False)]})
    admission_type = fields.Selection(ADMISSION_TYPE, string='Admission Type', required=True, readonly=True,
                                      states={'Draft': [('readonly', False)]})
    admission_reason = fields.Many2one('oeh.medical.pathology', string='Reason for Admission',
                                       help="Reason for Admission", required=True, readonly=True,
                                       states={'Draft': [('readonly', False)]})
    admission_date = fields.Datetime(string='Hospitalization Date', readonly=True,
                                     states={'Draft': [('readonly', False)]})
    discharge_date = fields.Datetime(string='Discharge Date', readonly=False,
                                     states={'Discharged': [('readonly', True)], 'Invoiced': [('readonly', True)]})
    attending_physician = fields.Many2one('oeh.medical.physician', string='Attending Doctor', readonly=True,
                                          states={'Draft': [('readonly', False)]}, default=_get_physician)
    operating_physician = fields.Many2one('oeh.medical.physician', string='Operating Doctor', readonly=True,
                                          states={'Draft': [('readonly', False)]})
    ward = fields.Many2one('oeh.medical.health.center.ward', string='Ward', required=True, readonly=True,
                           states={'Draft': [('readonly', False)]}, domain="[('institution', '=', institution)]")
    bed = fields.Many2one('oeh.medical.health.center.beds', string='Bed', required=True, readonly=True,
                          states={'Draft': [('readonly', False)]})
    nursing_plan = fields.Text(string='Nursing Plan', readonly=False, states={'Invoiced': [('readonly', True)]})
    discharge_plan = fields.Text(string='Discharge Plan', readonly=False, states={'Invoiced': [('readonly', True)]})
    admission_condition = fields.Text(string='Condition before Admission', readonly=False,
                                      states={'Invoiced': [('readonly', True)]})
    info = fields.Text(string='Extra Info', readonly=False, states={'Invoiced': [('readonly', True)]})
    state = fields.Selection(INPATIENT_STATES, string='State', default=lambda *a: 'Draft')
    prescribed_medicines = fields.One2many('oeh.medical.inpatient.prescribed.medicine', 'inpatient_id',
                                           string='Prescribed Medicines', readonly=True,
                                           states={'Hospitalized': [('readonly', False)]})
    consumed_medicines = fields.One2many('oeh.medical.inpatient.consumed.medicine', 'inpatient_id',
                                         string='Consumed Medicines', readonly=True,
                                         states={'Hospitalized': [('readonly', False)]})
    move_id = fields.Many2one('account.move', string='Invoice #', copy=False)

    @api.model
    def create(self, vals):
        company = self.env['res.company']._company_default_get('oeh.medical.inpatient')
        search_sequence = self.env['ir.sequence'].search(
            [('code', '=', 'oeh.medical.inpatient'), ('company_id', 'in', [company.id, False])], order='company_id')
        if not search_sequence:
            values = {
                'name': 'Inpatient (' + str(company.name) + ')',
                'code': 'oeh.medical.inpatient',
                'company_id': company.id,
                'prefix': 'IN',
                'padding': 6,
            }
            self.env['ir.sequence'].sudo().create(values)
            vals['name'] = self.env['ir.sequence'].next_by_code('oeh.medical.inpatient')
            inpatient = models.Model.create(self, vals)
            return inpatient
        else:
            sequence = self.env['ir.sequence'].next_by_code('oeh.medical.inpatient')
            vals['name'] = sequence or '/'
            return super(OeHealthInpatient, self).create(vals)

    def _default_account(self):
        journal = self.env['account.journal'].search([('type', '=', 'sale')], limit=1)
        return journal.default_credit_account_id.id

    def set_to_hospitalized(self):
        hospitalized_date = False
        for ina in self:
            if ina.admission_date:
                hospitalized_date = ina.admission_date
            else:
                hospitalized_date = datetime.datetime.now()

            if ina.bed:
                query = _("update oeh_medical_health_center_beds set state='Occupied' where id=%s") % (str(ina.bed.id))
                self.env.cr.execute(query)
        return self.write({'state': 'Hospitalized', 'admission_date': hospitalized_date})

    def set_to_invoiced(self):
        view_id = self.env.ref('oehealth.view_oeh_medical_inpatient_wizard').id
        return {'type': 'ir.actions.act_window',
                'name': _('Create Invoice'),
                'res_model': 'oeh.medical.inpatient.invoice.wizard',
                'target': 'new',
                'view_mode': 'form',
                'views': [[view_id, 'form']],
                }

    def set_to_discharged(self):
        discharged_date = False
        for ina in self:
            if ina.discharge_date:
                discharged_date = ina.discharge_date
            else:
                discharged_date = datetime.datetime.now()

            if ina.bed:
                query = _("update oeh_medical_health_center_beds set state='Free' where id=%s") % (str(ina.bed.id))
                self.env.cr.execute(query)
        return self.write({'state': 'Discharged', 'discharge_date': discharged_date})

    def set_to_cancelled(self):
        for ina in self:
            if ina.bed:
                query = _("update oeh_medical_health_center_beds set state='Free' where id=%s") % (str(ina.bed.id))
                self.env.cr.execute(query)
        return self.write({'state': 'Cancelled'})

    def set_to_draft(self):
        return self.write({'state': 'Draft'})

    def unlink(self):
        for inpatient in self.filtered(lambda inpatient: inpatient.state not in ['Draft']):
            raise UserError(_('You can not delete an admission record which is not in "Draft" state !!'))
        return super(OeHealthInpatient, self).unlink()
