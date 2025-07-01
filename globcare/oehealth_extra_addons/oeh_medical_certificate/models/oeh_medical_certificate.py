# -*- encoding: utf-8 -*-
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
import datetime


class OeHealthPatientMedicalCert(models.Model):
    _name = 'oeh.medical.patient.medical.cert'
    _description = 'Patient Medical Certificate Management'

    def _get_duration(self):
        for history in self:
            if history.start_date and history.end_date:
                duration = history.end_date - history.start_date
                history.no_of_days = duration.days
            else:
                history.no_of_days = 0
        return True

    name = fields.Char(string='MC #', size=64, readonly=True, default=lambda *a: '/')
    start_date = fields.Date(string='From Date', required=True)
    end_date = fields.Date(string='End Date', required=True)
    no_of_days = fields.Integer(compute=_get_duration, string="No of Days")
    issue_date = fields.Datetime(string='DateTime MC is issued', required=True, default=lambda *a: datetime.datetime.now())
    patient = fields.Many2one('oeh.medical.patient', string='Patient', help="Patient Name", required=True)
    doctor = fields.Many2one('oeh.medical.physician', string='Doctor', domain=[('is_pharmacist','=',False)], help="Health professional", required=True)
    institution = fields.Many2one('oeh.medical.health.center', string='Institution', help="Institution where doctor works")
    reason = fields.Text(string='Reason', required=True)

    @api.model
    def create(self,vals):
        sequence = self.env['ir.sequence'].next_by_code('oeh.medical.patient.medical.cert')
        vals['name'] = sequence
        return super(OeHealthPatientMedicalCert, self).create(vals)


    # This function prints the patient medical cert
    def print_patient_medical_cert(self):
        return self.env.ref('oehealth_extra_addons.action_report_oeh_medical_patient_medical_cert').report_action(self)


# Inheriting Patient module to add "Medical Certificate" screen reference
class OeHealthPatient(models.Model):
    _inherit='oeh.medical.patient'
    medical_cert_ids = fields.One2many('oeh.medical.patient.medical.cert', 'patient', string='Medical Certificates')