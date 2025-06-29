import base64
from odoo.exceptions import ValidationError
from odoo import models, fields, api, _
from odoo.tools import config
import datetime
from werkzeug.urls import url_encode
import requests
import logging

_logger = logging.getLogger(__name__)


class ShifaExternalPrescription(models.Model):
    _name = "sm.shifa.external.prescription"

    STATES = [
        ('Start', 'Start'),
        ('PDF Created', 'PDF Created'),
        ('send', 'Send'),
    ]

    YES_NO = [

        ('yes', 'Yes'),
        ('no', 'No'),
    ]

    DURATION_UNIT = [
        ('Minutes', 'Minutes'),
        ('Hours', 'Hours'),
        ('Days', 'Days'),
        ('Months', 'Months'),
        ('Years', 'Years'),
        ('Indefinite', 'Indefinite'),
    ]

    name = fields.Char(string='Prescription #', size=64, readonly=True, required=True, default=lambda *a: '/')
    state = fields.Selection(STATES, 'State', readonly=True, default=lambda *a: 'Start')
    patient = fields.Many2one('oeh.medical.patient', string='Patient', help="Patient Name", required=True,
                              readonly=True, states={'Start': [('readonly', False)]})
    # add_by = fields.Many2one('oeh.medical.patient', string='Added By')
    add_by = fields.Many2one('oeh.medical.physician', string='Added By', domain=[('active', '=', True)])
    date = fields.Datetime(string='Date', readonly=True, states={'Start': [('readonly', False)]},
                           default=datetime.datetime.now())
    info = fields.Text(string='Prescription Notes', readonly=True, states={'Start': [('readonly', False)]})
    prescription_line = fields.One2many('sm.shifa.prescription.line', 'ex_prescription_ids',
                                        string='Prescription Lines',
                                        readonly=True, states={'Start': [('readonly', False)]})

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('sm.shifa.external.prescription')
        rec = super(ShifaExternalPrescription, self).create(vals)
        rec.set_to_pdf_create()
        return rec

    def set_to_pdf_create(self):

        medication_profile_obj = self.env["sm.shifa.medication.profile"]

        patient = self.patient.id
        date = self.date
        for rec in self.prescription_line:
            medication_profile = medication_profile_obj.sudo().create({
                'patient': patient,
                'p_generic_name': rec.generic_name.id,
                'p_brand_medicine': rec.brand_medicine.id,
                'p_indication': rec.indication.id,
                'p_dose': rec.dose,
                'p_dose_unit': rec.dose_unit.id,
                'p_dose_form': rec.dose_form.id,
                'p_common_dosage': rec.common_dosage.id,
                'p_duration': rec.duration,
                'p_qty': rec.qty,
                'p_duration_period': rec.frequency_unit,
                'p_dose_route': rec.dose_route.id,
                'state_app': 'active',
                'pre_exter_type': 'external',
                'comment': " ",
                'date': date
            })


class ExternalPrescriptionLine(models.Model):
    _inherit = 'sm.shifa.prescription.line'

    ex_prescription_ids = fields.Many2one('sm.shifa.external.prescription', string='Prescription Line')
