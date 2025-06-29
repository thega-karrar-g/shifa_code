from odoo import models, fields, api
import datetime


class ShifaGenericVaccines(models.Model):
    _name = 'sm.shifa.generic.vaccines'
    _description = 'Generic Vaccines'

    #  Generic Vaccines
    name = fields.Char(string="Generic Vaccines", required=True)
    therapeutic_action = fields.Char(string='Therapeutic effect', size=128, help="Therapeutic action")

    pregnancy_warning = fields.Boolean(string='Pregnancy Warning',
                                       help="Check when the drug can not be taken during pregnancy or lactancy")

    adverse_reaction = fields.Text(string='Adverse Reactions')

    info = fields.Text(string='Extra Info')
    active = fields.Boolean(default=True)
