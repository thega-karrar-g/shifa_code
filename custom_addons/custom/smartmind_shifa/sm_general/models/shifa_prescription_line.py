from odoo import models, fields, api
import datetime


class ShifaPrescriptionLines(models.Model):
    _name = 'sm.shifa.prescription.line'
    _description = 'Prescription Lines'

    FREQUENCY_UNIT = [
        ('Seconds', 'Seconds'),
        ('Minutes', 'Minutes'),
        ('Hours', 'Hours'),
        ('Days', 'Days'),
        ('Weeks', 'Weeks'),
        ('When Required', 'When Required'),
        ('Months', 'Months'),
    ]
    DURATION_UNIT = [
        ('Minutes', 'Minutes'),
        ('Hours', 'Hours'),
        ('Days', 'Days'),
        ('Months', 'Months'),
        ('Years', 'Years'),
        ('Indefinite', 'Indefinite'),
    ]
    MEDICINE = [
        ('Brand', 'Brand'),
        ('Generic', 'Generic'),
    ]

    medicine_category = fields.Selection(MEDICINE, default='Brand')
    prescription_ids = fields.Many2one('oeh.medical.prescription', string='Prescription Reference', ondelete='cascade',
                                       index=True)
    brand_medicine = fields.Many2one('sm.shifa.brand.medicines', string='Medicines')
    generic_name = fields.Many2one('sm.shifa.generic.medicines', string='Medicines')
    indication = fields.Many2one('oeh.medical.pathology', string='Indication')
    dose = fields.Float(string='Dose')
    dose_unit = fields.Many2one('oeh.medical.dose.unit', string='Dose Unit')
    strength = fields.Float(string='Strength')
    strength_unit = fields.Many2one('sm.medical.strength.units', string='Strength Unit')
    dose_route = fields.Many2one('oeh.medical.drug.route', string='Administration Route')
    dose_form = fields.Many2one('oeh.medical.drug.form', 'Form')
    qty = fields.Integer(string='Quantity', default=lambda *a: 1.0)
    common_dosage = fields.Many2one('oeh.medical.dosage', string='Frequency')
    frequency = fields.Integer('Frequency')
    frequency_unit = fields.Selection(FREQUENCY_UNIT, 'Unit', index=True)
    admin_times = fields.Char(string='Admin hours', size=128)
    duration = fields.Integer(string='Treatment duration')
    duration_period = fields.Selection(DURATION_UNIT, string='Treatment period', index=True)
    start_treatment = fields.Datetime(string='Start of treatment')
    end_treatment = fields.Datetime('End of treatment')
    info = fields.Text('Comment')
    patient = fields.Many2one('oeh.medical.patient', 'Patient')


    @api.onchange('brand_medicine')
    def _onchange_brand_medicine(self):
        if self.brand_medicine:
            self.generic_name = None

    @api.onchange('generic_name')
    def _onchange_generic_name(self):
        if self.generic_name:
            self.brand_medicine = None

