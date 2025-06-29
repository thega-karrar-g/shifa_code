from odoo import models, fields, api, _
from odoo.exceptions import UserError

class HVDAppointment(models.Model):
    _inherit = 'sm.shifa.hvd.appointment'
    branch = fields.Selection(required=True,default='riyadh')

class MedecineAppointment(models.Model):
    _inherit = 'oeh.medical.appointment'
    branch = fields.Selection(required=True,default='riyadh')

class SleepMedecineAppointment(models.Model):
    _inherit = 'sm.sleep.medicine.request'
    branch = fields.Selection(required=True,default='riyadh')

class ShifaInstantPresceiption(models.Model):
    _inherit = 'sm.shifa.instant.prescriptions'
    branch = fields.Selection([('riyadh','Riyadh'),('dammam','Dammam'),('jeddah','Jeddah')],required=True,default='riyadh')

class ShifaInstantConsultation(models.Model):
    _inherit = 'sm.shifa.instant.consultation'
    branch = fields.Selection([('riyadh','Riyadh'),('dammam','Dammam'),('jeddah','Jeddah')],required=True,default='riyadh')

class SmTreatments(models.Model):
    _inherit = 'sm.treatments'
    branch = fields.Selection([('riyadh','Riyadh'),('dammam','Dammam'),('jeddah','Jeddah')],required=True,default='riyadh')