from odoo import models, fields, api, _
import datetime
import logging

_logger = logging.getLogger(__name__)


class ShifaMedicationProfile(models.Model):
    _name = "sm.shifa.medication.profile"


    STATES = [
        ('Start', 'Start'),
        ('PDF Created', 'PDF Created'),
        ('send', 'Send'),
    ]

    YES_NO = [
        ('yes', 'Yes'),
        ('no', 'No'),
    ]
    TYPE = [
        ('prescribed', 'Prescribed'),
        ('external', 'External'),
    ]
    DURATION_UNIT = [
        ('Seconds', 'Seconds'),
        ('Minutes', 'Minutes'),
        ('Hours', 'Hours'),
        ('Days', 'Days'),
        ('Weeks', 'Weeks'),
        ('Months', 'Months'),
        ('Years', 'Years'),
        ('Indefinite', 'Indefinite'),
    ]

    STATE_PR = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]
    state = fields.Selection(STATES, 'State', readonly=True, default=lambda *a: 'Start')
    patient = fields.Many2one('oeh.medical.patient', string='Patient', help="Patient Name", required=True,
                              readonly=True, states={'Start': [('readonly', False)]})

    date = fields.Datetime(string='Date', readonly=True, states={'Start': [('readonly', False)]},
                           default=datetime.datetime.now())
    info = fields.Text(string='Prescription Notes', readonly=True, states={'Start': [('readonly', False)]})
    comment = fields.Char(string="Comment")
    pre_exter_type = fields.Selection(TYPE, string="Prescribed/External")
    state_app = fields.Selection(STATE_PR, string="State")
    patient_line = fields.Char()
    p_generic_name = fields.Many2one('sm.shifa.generic.medicines')
    p_brand_medicine = fields.Many2one('sm.shifa.brand.medicines')
    p_indication = fields.Many2one('oeh.medical.pathology')
    p_dose = fields.Float()
    p_dose_unit = fields.Many2one('oeh.medical.dose.unit')
    p_dose_form = fields.Many2one('oeh.medical.drug.form')
    p_common_dosage = fields.Many2one('oeh.medical.dosage')
    p_duration = fields.Integer()
    p_qty = fields.Integer()
    p_dose_route = fields.Many2one('oeh.medical.drug.route', string='Administration Route')
    p_duration_period = fields.Selection(DURATION_UNIT, string='Duration Period')

    def get_generic(self):
        medicine = self.search([
            ('state', '=', 'Start'),
        ])
        if medicine:
            for rec in medicine:
                if rec.p_brand_medicine:
                    rec.p_generic_name = rec.p_brand_medicine.generic_name
                    rec.state = "send"
