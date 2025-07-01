from odoo import models, fields, api
import datetime


class ShifaGenericMedicines(models.Model):
    _name = 'sm.shifa.generic.medicines'
    _description = 'Generic Medicines'

    #  Generic Medicines
    name = fields.Char(string="Medicines", required=True)
    therapeutic_action = fields.Char(string='Therapeutic effect', size=128, help="Therapeutic action")
    composition = fields.Text(string='Composition', help="Components")
    indications = fields.Text(string='Indication', help="Indications")
    dosage = fields.Text(string='Dosage Instructions', help="Dosage / Indications")
    overdosage = fields.Text(string='Overdosage', help="Overdosage")
    pregnancy_warning = fields.Boolean(string='Pregnancy Warning',
                                       help="Check when the drug can not be taken during pregnancy or lactancy")
    pregnancy = fields.Text(string='Pregnancy and Lactancy', help="Warnings for Pregnant Women")
    adverse_reaction = fields.Text(string='Adverse Reactions')
    storage = fields.Text(string='Storage Conditions')
    info = fields.Text(string='Extra Info')
    active = fields.Boolean(default=True)


class ShifaPatientMedicines(models.Model):
    _name = 'sm.shifa.patient.medicines'
    _description = 'Patient Medicines'

    name = fields.Char(string="Medicines", required=True)
    medicine_image = fields.Binary()
    active = fields.Boolean(default=True)
