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
# -*- encoding: utf-8 -*-

from odoo import fields, models, _
from odoo.exceptions import UserError
import datetime

class OeHealthImagingTypeManagementSmartMind(models.Model):
    _inherit = 'oeh.medical.imaging'

    appointment = fields.Many2one('oeh.medical.appointment', string='Appointment')

class OeHealthAppointmentSmartMind(models.Model):
    _inherit = 'oeh.medical.appointment'

    PATIENT_STATUS = [
                ('Ambulatory', 'Ambulatory'),
                ('Outpatient', 'Outpatient'),
                ('Inpatient', 'Inpatient'),
            ]

    APPOINTMENT_STATUS = [
            ('Scheduled', 'Scheduled'),
            ('Confirmed', 'Confirmed'),
            ('Start', 'Start'),
            ('Completed', 'Completed'),
            ('Invoiced', 'Invoiced'),
        ]

    state = fields.Selection(APPOINTMENT_STATUS, string='State', readonly=True, default=lambda *a: 'Scheduled')
    image_test_ids = fields.One2many('oeh.medical.imaging','appointment',string='Image Test')
    apt_invoice_count = fields.Integer(string='Invoice Count', compute='_get_apt_invoiced', readonly=True)

    def _get_apt_invoiced(self):
        for apt in self:
            inv = self.env['account.move'].search([('appointment','=',apt.id)])
            apt.apt_invoice_count = len(inv)

    def action_view_apt_invoice(self):
        return {
            'name': _('Invoice(s)'),
            'view_mode': 'tree,form',
            'domain': [('appointment', 'in', self.ids)],
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'context': {'create': False},
        }

    def set_to_invoiced(self):
        for acc in self:
            invoice_lines = []
            default_journal = self._get_default_journal()
            sequence = 0

            if not default_journal:
                raise UserError(_('No accounting journal with type "Sale" defined !'))

            if acc.treatment_line:
                sequence += 1
                invoice_lines.append((0, 0, {
                    'name': 'Treatment',
                    'display_type': 'line_section',
                    'account_id': False,
                    'sequence': sequence,
                }))
                for treat_line in acc.treatment_line:
                    if treat_line.treatment_items:
                        for item in treat_line.treatment_items:
                            sequence += 1
                            invoice_lines.append((0, 0, {
                                'display_type': False,
                                'quantity': item.qty,
                                'name': item.name.name,
                                'price_unit': item.name.list_price,
                                'product_id': item.name.id,
                                'product_uom_id': item.name.uom_id and item.name.uom_id.id or False,
                                'sequence': sequence,
                            }))

            # Create Invoice lines for Labs
            if acc.labtest_line:
                sequence += 1
                invoice_lines.append((0, 0, {
                    'name': 'Lab Tests',
                    'display_type': 'line_section',
                    'account_id': False,
                    'sequence': sequence,
                }))

                for lab in acc.labtest_line:
                    lab_test_name = lab.test_type.name + ' (' + lab.name + ')'

                    invoice_lines.append((0, 0, {
                        'display_type': False,
                        'name': lab_test_name,
                        'price_unit': lab.test_type.test_charge,
                        'quantity': 1,
                        'product_uom_id': self.env.ref('uom.product_uom_unit') and self.env.ref(
                            'uom.product_uom_unit').id or False,
                        'sequence': sequence,
                    }))

            # Create Invoice lines for Prescription
            if acc.prescription_line:
                sequence += 1
                invoice_lines.append((0, 0, {
                    'name': 'Medicines',
                    'display_type': 'line_section',
                    'account_id': False,
                    'sequence': sequence,
                }))

                for pres_line in acc.prescription_line:
                    if pres_line.prescription_line:
                        for pres in pres_line.prescription_line:
                            sequence += 1
                            invoice_lines.append((0, 0, {
                                'display_type': False,
                                'quantity': pres.qty,
                                'name': pres.name.product_id.name,
                                'product_id': pres.name.product_id.id,
                                'product_uom_id': pres.name.product_id.uom_id and pres.name.product_id.uom_id.id or False,
                                'price_unit': pres.name.product_id.list_price,
                                'sequence': sequence,
                            }))
                        pres_line.write({'state': 'Invoiced'})

            # Create Invoice
            invoice = self.env['account.move'].sudo().create({
                'move_type': 'out_invoice',
                'journal_id': default_journal.id,
                'partner_id': acc.patient.partner_id.id,
                'patient': acc.patient.id,
                'invoice_date': datetime.datetime.now().date(),
                'date': datetime.datetime.now().date(),
                'ref': "Appointment # : " + acc.name,
                'appointment': acc.id,
                'invoice_line_ids': invoice_lines
            })
            if self.env.company.stock_deduction_method == 'invoice_create':
                invoice.oeh_process_inventories()
            acc.write({'state': 'Invoiced', 'move_id': invoice.id})
        return True

    def set_to_confirmed(self):
        for acc in self:
            invoice_lines = []
            consultancy_invoice_lines = []
            default_journal = self._get_default_journal()

            if not default_journal:
                raise UserError(_('No accounting journal with type "Sale" defined !'))

            price = acc.doctor.consultancy_price

            # Prepare Invoice lines
            consultancy_invoice_lines.append((0, 0, {
                    'name': 'Consultancy',
                    'display_type': 'line_section',
                    'account_id': False,
                    'sequence': 1,
                }))
            consultancy_invoice_lines.append((0, 0, {
                    'display_type': False,
                    'quantity': 1.0,
                    'name': 'Consultancy Charge for ' + acc.name,
                    'price_unit': price,
                    'product_uom_id': self.env.ref('uom.product_uom_unit') and self.env.ref('uom.product_uom_unit').id or False,
                    'sequence': 2,
                }))

            # Create Invoice
            invoice = self.env['account.move'].sudo().create({
                'move_type': 'out_invoice',
                'journal_id': default_journal.id,
                'partner_id': acc.patient.partner_id.id,
                'patient': acc.patient.id,
                'invoice_date': datetime.datetime.now().date(),
                'date': datetime.datetime.now().date(),
                'ref': "Appointment # : " + acc.name,
                'appointment': acc.id,
                'invoice_line_ids': consultancy_invoice_lines
            })
            if self.env.company.stock_deduction_method == 'invoice_create':
                invoice.oeh_process_inventories()
            acc.write({'state': 'Confirmed', 'move_id': invoice.id})
        return True

    def set_to_start(self):
        self.write({'state': 'Start'})