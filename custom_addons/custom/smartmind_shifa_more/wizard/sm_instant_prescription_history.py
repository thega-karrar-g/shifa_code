##############################################################################
#    Copyright (C) 2021 - Present, SmartMind Sehati (<https://smartmindsys.com/>).
#    All Rights Reserved
#    Done by Developer Mukhtar Mohammed Asorori
#    Sehati, Hospital Management Solutions
##############################################################################
from odoo import models, fields, api, _


class InstantPrescriptionsReportWizard(models.TransientModel):
    _name = 'sm.shifa.instant.prescriptions.history.wizard'
    _description = 'History of Instant Prescription Medicines Report Wizard'

    name = fields.Char(string='Name')
    is_all = fields.Boolean(string='All Pharmacy Chains')
    pharmacy_chain = fields.Many2one('sm.shifa.pharmacy.chain', string='Pharmacy Chain')
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')

    def action_print_report(self):
        model_name = 'sm.shifa.instant.prescriptions.history'
        domain = []
        if self.pharmacy_chain and not self.is_all:
            domain += [('pharmacy_chain', '=', self.pharmacy_chain.name)]

        if self.start_date:
            domain += [('date', '>=', self.start_date)]

        if self.end_date:
            domain += [('date', '<=', self.end_date)]

        history_list = self.env[model_name].search_read(domain)
        data = {
            'form': self.read()[0],
            'medicines': history_list,
        }
        return self.env.ref('smartmind_shifa_more.instant_prescription_history_report').with_context(
            landscape=True).report_action(self,  data=data)
