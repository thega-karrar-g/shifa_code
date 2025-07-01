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
import time
import datetime
from odoo.exceptions import UserError


# Lab Units Management
class OeHealthLabTestUnits(models.Model):
    _name = 'oeh.medical.lab.units'
    _description = 'Lab Test Units'

    name = fields.Char(string='Unit Name', size=25, required=True)
    code = fields.Char(string='Code', size=25, required=True)

    _sql_constraints = [('name_uniq', 'unique(company_id,name)', 'The Lab unit name must be unique')]


# Lab Test Department
class OeHealthLabTestDepartment(models.Model):
    _name = 'oeh.medical.labtest.department'
    _description = 'Lab Test Departments'

    company_id = fields.Many2one(
        'res.company', store=True, default=lambda self: self.env.company
    )
    name = fields.Char(string='Name', size=128, required=True)


# Lab Test Types Management
class OeHealthLabTestCriteria(models.Model):
    _name = 'oeh.medical.labtest.criteria'
    _description = 'Lab Test Criteria'

    company_id = fields.Many2one(
        'res.company', store=True, default=lambda self: self.env.company
    )
    name = fields.Char(string='Tests', size=128, required=True)
    normal_range = fields.Text(string='Normal Range')
    units = fields.Many2one('oeh.medical.lab.units', string='Units')
    sequence = fields.Integer(string='Sequence')
    medical_type_id = fields.Many2one('oeh.medical.labtest.types', string='Lab Test Types')

    _order="sequence"


class OeHealthLabTestTypes(models.Model):
    _name = 'oeh.medical.labtest.types'
    _description = 'Lab Test Types'

    company_id = fields.Many2one(
        'res.company', store=True, default=lambda self: self.env.company
    )
    name = fields.Char(string='Lab Test Name', size=128, required=True, help="Test type, eg X-Ray, Hemogram, Biopsy...")
    code = fields.Char(string='Code', size=128, help="Short code for the test")
    info = fields.Text(string='Description')
    test_charge = fields.Float(string='Test Charge', default=lambda *a: 0.0)
    lab_criteria = fields.One2many('oeh.medical.labtest.criteria', 'medical_type_id', string='Lab Test Cases')
    lab_department = fields.Many2one('oeh.medical.labtest.department', string='Department')


class OeHealthLabTests(models.Model):
    _name = 'oeh.medical.lab.test'
    _description = 'Lab Tests'
    _inherit = ['mail.thread']

    LABTEST_STATE = [
        ('Draft', 'Draft'),
        ('Test In Progress', 'Test In Progress'),
        ('Completed', 'Completed'),
        ('Invoiced', 'Invoiced'),
    ]

    company_id = fields.Many2one(
        'res.company', store=True, default=lambda self: self.env.company
    )
    name = fields.Char(string='Lab Test #', size=16, readonly=True, required=True, help="Lab result ID", default=lambda *a: '/')
    lab_department = fields.Many2one('oeh.medical.labtest.department', string='Department', readonly=True, states={'Draft': [('readonly', False)]})
    test_type = fields.Many2one('oeh.medical.labtest.types', string='Test Type', domain="[('lab_department', '=', lab_department)]", required=True, readonly=True, states={'Draft': [('readonly', False)]}, help="Lab test type")
    # test_type = fields.Many2one('oeh.medical.labtest.types', string='Test Type', required=True, readonly=True, states={'Draft': [('readonly', False)]}, help="Lab test type")
    patient = fields.Many2one('oeh.medical.patient', string='Patient', help="Patient Name", required=True, readonly=True, states={'Draft': [('readonly', False)]})
    pathologist = fields.Many2one('oeh.medical.physician', string='Pathologist', help="Pathologist", readonly=True, states={'Draft': [('readonly', False)]})
    requestor_id = fields.Many2one('oeh.medical.physician', string='Doctor who requested the test', help="Doctor who requested the test", required=True, readonly=True, states={'Draft': [('readonly', False)]})
    # requestor = fields.Many2one('oeh.medical.physician', string='Doctor who requested the test', help="Doctor who requested the test", required=True, readonly=True, states={'Draft': [('readonly', False)]})
    requestor = fields.Char(string='Doctor who requested the test', help="Doctor who requested the test", readonly=True, states={'Draft': [('readonly', False)]})
    results = fields.Text(string='Results', readonly=True, states={'Draft': [('readonly', False)], 'Test In Progress': [('readonly', False)]})
    diagnosis = fields.Text(string='Diagnosis', readonly=True, states={'Draft': [('readonly', False)], 'Test In Progress': [('readonly', False)]})
    lab_test_criteria = fields.One2many('oeh.medical.lab.resultcriteria', 'medical_lab_test_id', string='Lab Test Result', readonly=True, states={'Draft': [('readonly', False)], 'Test In Progress': [('readonly', False)]})
    date_requested = fields.Datetime(string='Date requested', readonly=True, states={'Draft': [('readonly', False)]}, default=lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'))
    date_analysis = fields.Datetime(string='Date of the Analysis', readonly=True, states={'Draft': [('readonly', False)], 'Test In Progress': [('readonly', False)]})
    state = fields.Selection(LABTEST_STATE, string='State', readonly=True, default=lambda *a: 'Draft')
    institution = fields.Many2one('oeh.medical.health.center', string='Health Center', help="Medical Center", readonly=True, states={'Draft': [('readonly', False)]})
    appointment = fields.Many2one('oeh.medical.appointment', string='Appointment #')
    move_id = fields.Many2one('account.move', string='Invoice #', copy=False)

    @api.model
    def create(self, vals):
        company = self.env['res.company']._company_default_get('oeh.medical.lab.test')
        search_sequence = self.env['ir.sequence'].search(
            [('code', '=', 'oeh.medical.lab.test'), ('company_id', 'in', [company.id, False])],
            order='company_id')
        if not search_sequence:
            values = {
                'name': 'Lab Tests (' + str(company.name) + ')',
                'code': 'oeh.medical.lab.test',
                'company_id': company.id,
                'prefix': 'LT',
                'padding': 6,
            }
            self.env['ir.sequence'].sudo().create(values)
            vals['name'] = self.env['ir.sequence'].next_by_code('oeh.medical.lab.test')
            homecare = models.Model.create(self, vals)
            return homecare
        else:
            sequence = self.env['ir.sequence'].next_by_code('oeh.medical.lab.test')
            vals['name'] = sequence or '/'
            return super(OeHealthLabTests, self).create(vals)

    # Fetching lab test types
    @api.onchange('test_type')
    def onchange_test_type_id(self):
        lab_test_criteria = []
        if self.test_type and self.test_type.lab_criteria:
            self.lab_test_criteria = False
            for criteria in self.test_type.lab_criteria:
                lab_test_criteria.append((0, 0, {
                    'name': criteria.name,
                    'normal_range': criteria.normal_range,
                    'units': criteria.units and criteria.units.id or False,
                    'sequence': criteria.sequence,
                }))
            self.lab_test_criteria = lab_test_criteria
        else:
            self.lab_test_criteria = False

    # This function prints the lab test
    def print_patient_labtest(self):
        return self.env.ref('oehealth.action_report_patient_labtest').report_action(self)

    def set_to_test_inprogress(self):
        return self.write({'state': 'Test In Progress', 'date_analysis': datetime.datetime.now()})

    def set_to_test_complete(self):
        return self.write({'state': 'Completed'})

    def unlink(self):
        # for labtest in self.filtered(lambda labtest: labtest.state not in ['Draft']):
        #     raise UserError(_('You can not delete a lab test which is not in "Draft" state !!'))
        return super(OeHealthLabTests, self).unlink()

    def _get_default_journal(self):
        journal = self.env['account.journal'].search([('type', '=', 'sale')], limit=1)
        return journal

    def action_lab_invoice_create(self):
        res = {}
        for lab in self:
            # Create Invoice
            if lab.patient:
                invoice_lines = []
                default_journal = self._get_default_journal()

                if not default_journal:
                    raise UserError(_('No accounting journal with type "Sale" defined !'))

                sequence_count = 1
                invoice_lines.append((0, 0, {
                    'name': 'Lab Test',
                    'display_type': 'line_section',
                    'account_id': False,
                    'sequence': sequence_count,
                }))

                sequence_count += 1

                invoice_lines.append((0, 0, {
                    'display_type': False,
                    'name': lab.test_type.name,
                    'price_unit': lab.test_type.test_charge,
                    'quantity': 1,
                    'product_uom_id': self.env.ref('uom.product_uom_unit') and self.env.ref('uom.product_uom_unit').id or False,
                    'sequence': sequence_count,
                }))

                invoice = self.env['account.move'].sudo().create({
                    'move_type': 'out_invoice',
                    'journal_id': default_journal.id,
                    'partner_id': lab.patient.partner_id.id,
                    'patient': lab.patient.id,
                    'invoice_date': datetime.datetime.now().date(),
                    'date': datetime.datetime.now().date(),
                    'ref': "Lab Test # : " + lab.name,
                    'labtest': lab.id,
                    'invoice_line_ids': invoice_lines
                })
                if self.env.company.stock_deduction_method == 'invoice_create':
                    invoice.oeh_process_inventories()
                res = lab.write({'state': 'Invoiced', 'move_id': invoice.id})
        return res


class OeHealthLabTestsResultCriteria(models.Model):
    _name = 'oeh.medical.lab.resultcriteria'
    _description = 'Lab Test Result Criteria'

    name = fields.Char(string='Tests', size=128, required=True)
    result = fields.Text(string='Result')
    normal_range = fields.Text(string='Normal Range')
    units = fields.Many2one('oeh.medical.lab.units', string='Units')
    sequence = fields.Integer(string='Sequence')
    medical_lab_test_id = fields.Many2one('oeh.medical.lab.test', string='Lab Tests')

    _order="sequence"

# Inheriting Patient module to add "Lab" screen reference
class OeHealthPatient(models.Model):
    _inherit='oeh.medical.patient'

    def _labtest_count(self):
        oe_labs = self.env['oeh.medical.lab.test']
        for ls in self:
            domain = [('patient', '=', ls.id)]
            lab_ids = oe_labs.search(domain)
            labs = oe_labs.browse(lab_ids)
            labs_count = 0
            for lab in labs:
                labs_count+=1
            ls.labs_count = labs_count
        return True

    lab_test_ids = fields.One2many('oeh.medical.lab.test', 'patient', string='Lab Test IDs')
    labs_count = fields.Integer(compute=_labtest_count, string="Lab Tests")