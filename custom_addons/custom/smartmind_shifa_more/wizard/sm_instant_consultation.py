##############################################################################
#    Copyright (C) 2021 - Present, SmartMind Sehati (<https://smartmindsys.com/>).
#    All Rights Reserved
#    Done by Developer Mukhtar Mohammed Asorori
#    Sehati, Hospital Management Solutions
##############################################################################
from odoo import models, fields, api, _


class InstantConsultationsReportWizard(models.TransientModel):
    _name = 'sm.shifa.instant.consultation.wizard'
    _description = 'Instant Consultation Report Wizard'

    name = fields.Char(string='Name')
    is_all_chains = fields.Boolean(string='All Pharmacy Chains')
    pharmacy_chain = fields.Many2one('sm.shifa.pharmacy.chain', string='Pharmacy Chain')

    is_all_doctors = fields.Boolean(string='All Doctors')
    doctor = fields.Many2one('oeh.medical.physician', string='Doctor',domain=[('active', '=', True)],)

    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')

    def action_print_report(self):
        model_name = 'sm.shifa.instant.consultation'
        domain = []
        if self.pharmacy_chain and not self.is_all_chains:
            domain += [('pharmacy_chain', '=', self.pharmacy_chain.id)]

        if self.doctor and not self.is_all_doctors:
            domain += [('doctor', '=', self.doctor.id)]

        if self.start_date:
            domain += [('date', '>=', self.start_date)]

        if self.end_date:
            domain += [('date', '<=', self.end_date)]

        consultation_list = self.env[model_name].search_read(domain)
        data = {
                'form': self.read()[0],
                'consultations': consultation_list,
            }
        # data = {}
        # for cons in consultation_list:
        #     data = {
        #         'form': self.read()[0],
        #         'consultations': cons,
        #     }
        return self.env.ref('smartmind_shifa_more.instant_consultation_report').with_context(
            landscape=True).report_action(self,  data=data)
