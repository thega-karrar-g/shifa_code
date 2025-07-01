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

import datetime
from datetime import date
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class oeHealthInpatientWizard(models.TransientModel):
    _name = "oeh.medical.inpatient.invoice.wizard"
    _description = "Invoice Wizard for Inpatient screen"

    INVOICE_TYPE = [
        ('1', 'Only for bed charges [charge x stay of number of days]'),
        ('2', 'Only for consumed medicines'),
        ('3', 'Both (bed charges + consumed medicine)'),
    ]

    name = fields.Selection(INVOICE_TYPE, 'Choose Invoicing Type', default='1')

    def _get_default_journal(self):
        journal = self.env['account.journal'].search([('type', '=', 'sale')], limit=1)
        return journal

    def create_invoice(self):
        inpatients = self.env['oeh.medical.inpatient'].browse(self._context.get('active_ids', []))
        invoice_type = self.name

        for inpatient in inpatients:
            invoice_lines = []
            default_journal = self._get_default_journal()

            if not default_journal:
                raise UserError(_('No accounting journal with type "Sale" defined !'))

            # Calculate Hospitalized duration
            duration = 1
            if inpatient.admission_date and inpatient.discharge_date:
                delta = inpatient.discharge_date - inpatient.admission_date
                if delta.days == 0:
                    duration = 1
                else:
                    duration = delta.days

            # Create Invoice line
            if invoice_type == '1':  # If first option "Only for bed charges [charge x stay of number of days]" selected
                if inpatient.bed:
                    invoice_lines.append((0, 0, {
                        'name': 'Bed Charges',
                        'display_type': 'line_section',
                        'account_id': False,
                        'sequence': 1,
                    }))

                    invoice_lines.append((0, 0, {
                        'display_type': False,
                        'quantity': duration,
                        'name': "Inpatient Admission charge for " + str(
                            duration) + " day(s) of " + inpatient.bed.product_id.name,
                        'product_id': inpatient.bed.product_id.id,
                        'price_unit': inpatient.bed.list_price,
                        'product_uom_id': inpatient.bed.product_id.uom_id.id,
                        'sequence': 2,
                    }))
                else:
                    raise UserError(_('Please first select bed to raise an invoice !'))

            if invoice_type == '2':     # If second option "Only for consumed medicines" selected
                if inpatient.consumed_medicines:
                    consumed_medicine_data = self.env['oeh.medical.inpatient.consumed.medicine'].read_group(
                        domain=[
                            ('inpatient_id', '=', inpatient.id)
                        ],
                        fields=['name', 'qty'],
                        groupby=['name']
                    )

                    invoice_lines.append((0, 0, {
                        'name': 'Medicines',
                        'display_type': 'line_section',
                        'account_id': False,
                        'sequence': 1,
                    }))

                    sequence = 1
                    for cmd in consumed_medicine_data:
                        total_qty = cmd.get('qty')
                        medicine = self.env['oeh.medical.medicines'].browse(cmd.get('name')[0])
                        sequence += 1

                        invoice_lines.append((0, 0, {
                            'display_type': False,
                            'quantity': int(total_qty),
                            'name': medicine.product_id.name,
                            'price_unit': medicine.list_price,
                            'product_uom_id': medicine.product_id.uom_id.id,
                            'product_id': medicine.product_id.id,
                            'sequence': sequence,
                        }))
                else:
                    raise UserError(_('No record of consumed medicines available for invoice !'))

            if invoice_type == '3':     # If third option "Both (bed charges + consumed medicine)" selected
                if inpatient.bed:
                    invoice_lines.append((0, 0, {
                        'name': 'Bed Charges',
                        'display_type': 'line_section',
                        'account_id': False,
                        'sequence': 1,
                    }))

                    invoice_lines.append((0, 0, {
                        'display_type': False,
                        'quantity': duration,
                        'name': "Inpatient Admission charge for " + str(
                            duration) + " day(s) of " + inpatient.bed.product_id.name,
                        'product_id': inpatient.bed.product_id.id,
                        'price_unit': inpatient.bed.list_price,
                        'product_uom_id': inpatient.bed.product_id.uom_id.id,
                        'sequence': 2,
                    }))

                if inpatient.consumed_medicines:
                    consumed_medicine_data = self.env['oeh.medical.inpatient.consumed.medicine'].read_group(
                        domain=[
                            ('inpatient_id', '=', inpatient.id)
                        ],
                        fields=['name', 'qty'],
                        groupby=['name']
                    )

                    invoice_lines.append((0, 0, {
                        'name': 'Medicines',
                        'display_type': 'line_section',
                        'account_id': False,
                        'sequence': 3,
                    }))

                    sequence = 3
                    for cmd in consumed_medicine_data:
                        total_qty = cmd.get('qty')
                        medicine = self.env['oeh.medical.medicines'].browse(cmd.get('name')[0])
                        sequence += 1

                        invoice_lines.append((0, 0, {
                            'display_type': False,
                            'quantity': int(total_qty),
                            'name': medicine.product_id.name,
                            'price_unit': medicine.list_price,
                            'product_uom_id': medicine.product_id.uom_id.id,
                            'product_id': medicine.product_id.id,
                            'sequence': sequence,
                        }))

            # Create Invoice
            invoice = self.env['account.move'].sudo().create({
                'move_type': 'out_invoice',
                'journal_id': default_journal.id,
                'partner_id': inpatient.patient.partner_id.id,
                'patient': inpatient.patient.id,
                'invoice_date': datetime.datetime.now().date(),
                'date': datetime.datetime.now().date(),
                'ref': "Inpatient Admission # : " + inpatient.name,
                'appointment': inpatient.id,
                'invoice_line_ids': invoice_lines
            })
            if self.env.company.stock_deduction_method == 'invoice_create':
                invoice.oeh_process_inventories()
            inpatient.write({'state': 'Invoiced', 'move_id': invoice.id})
        return True
