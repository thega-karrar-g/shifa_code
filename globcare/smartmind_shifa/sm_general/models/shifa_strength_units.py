from odoo import models, fields, api


class StrengthUnits(models.Model):
    _name = "sm.medical.strength.units"
    _description = "Medical Dose Unit"

    name = fields.Char(string='Unit', size=32, required=True)
    desc = fields.Char(string='Description', size=64)
    active = fields.Boolean(default=True)

class MedicalDosage(models.Model):
    _inherit ='oeh.medical.dosage'
    active = fields.Boolean(default=True)


class MedicalDoseUnit(models.Model):
    _inherit ='oeh.medical.dose.unit'
    active = fields.Boolean(default=True)

class MedicalDrugForm(models.Model):
    _inherit ='oeh.medical.drug.form'
    active = fields.Boolean(default=True)

class MedicalDrugRoute(models.Model):
    _inherit ='oeh.medical.drug.route'
    active = fields.Boolean(default=True)

