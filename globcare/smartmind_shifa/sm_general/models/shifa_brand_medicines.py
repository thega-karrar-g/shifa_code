from odoo import models, fields, api
import datetime


class ShifaBrandMedicines(models.Model):
    _name = 'sm.shifa.brand.medicines'
    _description = 'Brand Medicines'

    #  Brand Medicines
    name = fields.Char(string="Brand Medicine", required=True)
    brand_image = fields.Binary()
    generic_name = fields.Many2one('sm.shifa.generic.medicines', string='Generic', help="Generic Medicine", required=True)
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
