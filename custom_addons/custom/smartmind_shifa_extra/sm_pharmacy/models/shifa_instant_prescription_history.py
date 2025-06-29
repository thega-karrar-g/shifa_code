from odoo import models, fields, api, _
import datetime
import logging

_logger = logging.getLogger(__name__)


class InstantPrescriptions(models.Model):
    _name = 'sm.shifa.instant.prescriptions.history'
    _description = 'History of Instant Prescription Medicines'
    _rec_name = 'medicine_name'

    medicine_name = fields.Char('Medicine')# its medicine name from prescription line (pharmacy_medicine name) or from other prescription 1, 2,3
    pharmacist = fields.Char('Pharmacist Name')
    pharmacy = fields.Char('Pharmacy Name')
    pharmacy_chain = fields.Char('Pharmacy Chain')
    doctor = fields.Char('Doctor')
    dispensed = fields.Char('Dispensed')
    prescription_code = fields.Char('Prescription Code')
    date = fields.Datetime(string='Date', default=datetime.datetime.now())



