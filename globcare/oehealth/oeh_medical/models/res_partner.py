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
from odoo.exceptions import UserError


class oeHealthPartner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'
    _description = 'Partner'

    is_insurance_company = fields.Boolean(string='Insurance Company', help='Check if the party is an Insurance Company')
    is_institution = fields.Boolean(string='Institution', help='Check if the party is a Medical Center')
    is_doctor = fields.Boolean(string='Health Professional', help='Check if the party is a health professional')
    is_patient = fields.Boolean(string='Patient', help='Check if the party is a patient')
    is_person = fields.Boolean(string='Person', help='Check if the party is a person.')
    is_pharmacy = fields.Boolean(string='Pharmacy', help='Check if the party is a Pharmacy')
    ref = fields.Char(size=256, string='SSN', help='Patient Social Security Number or equivalent')

    def add_as_patient(self):
        for res in self:
            patient_obj = self.env['oeh.medical.patient']
            partner_id = res.id

            find_patient = patient_obj.sudo().search([('partner_id', '=', int(partner_id))], limit=1)
            if find_patient:
                raise UserError(_('%s is already added as a patient!') % str(res.name))
            else:
                values = {
                    'partner_id': partner_id,
                }
                patient_obj.sudo().create(values)
        return True

    def add_as_company(self):
        for res in self:
            health_center_obj = self.env['oeh.medical.health.center']
            partner_id = res.id

            find_healthcenter = health_center_obj.sudo().search([('partner_id', '=', int(partner_id))], limit=1)
            if find_healthcenter:
                raise UserError(_('%s is already added as a clinic!') % str(res.name))
            else:
                values = {
                    'partner_id': partner_id,
                    'health_center_type': 'Clinic'
                }
                health_center_obj.sudo().create(values)
        return True


class Employee(models.Model):
    _inherit = "hr.employee"

    added_as_physician = fields.Boolean(string='Added as Doctor', default=False)

    def action_add_as_physician(self):
        for rec in self:
            physician_obj = self.env['oeh.medical.physician']
            employee_id = rec.id
            user_id = rec.user_id

            find_physician = physician_obj.sudo().search([('employee_id', '=', int(employee_id))], limit=1)
            if not find_physician:
                values = {
                    'employee_id': employee_id,
                    'oeh_user_id': user_id.id

                }
                physician = physician_obj.sudo().create(values)
                if physician:
                    rec.write({'added_as_physician': True})

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
