import base64
from odoo.exceptions import ValidationError
from odoo import models, fields, api, _
import datetime
from werkzeug.urls import url_encode
import logging

_logger = logging.getLogger(__name__)


class PhysicianAssessmentPrescription(models.Model):
    _inherit = "oeh.medical.prescription"

    phy_assessment = fields.Many2one('sm.shifa.physician.assessment', string='Phy Assessment',
                                     readonly=True, states={'Start': [('readonly', False)]},
                                     domain=[('state', 'in', ['Draft', 'Start', 'Admitted'])],
                                     ondelete='cascade')

    diagnosis_show = fields.Boolean(default=True)
    provisional_diagnosis = fields.Many2one('oeh.medical.pathology', related='phy_assessment.provisional_diagnosis',
                                            string='Disease', readonly=False, store=True,
                                            states={'PDF Created': [('readonly', True)],'send': [('readonly', True)]})
    provisional_diagnosis_add_other = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    provisional_diagnosis_add = fields.Many2one('oeh.medical.pathology',
                                                related='phy_assessment.provisional_diagnosis_add', string='Disease',
                                                readonly=False, store=True,
                                                states={'PDF Created': [('readonly', True)],
                                                        'send': [('readonly', True)]})
    provisional_diagnosis_add_other2 = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    provisional_diagnosis_add2 = fields.Many2one('oeh.medical.pathology',
                                                 related='phy_assessment.provisional_diagnosis_add2', string='Disease',
                                                 readonly=False, store=True,
                                                 states={'PDF Created': [('readonly', True)],
                                                         'send': [('readonly', True)]})
    provisional_diagnosis_add_other3 = fields.Boolean(readonly=True, states={'Start': [('readonly', False)]})
    provisional_diagnosis_add3 = fields.Many2one('oeh.medical.pathology', store=True,
                                                 related='phy_assessment.provisional_diagnosis_add3', string='Disease',
                                                 readonly=False,
                                                 states={'PDF Created': [('readonly', True)],
                                                         'send': [('readonly', True)]})

    @api.onchange('phy_assessment')
    def _onchange_phy_assessment(self):
        if self.phy_assessment:
            self.patient = self.phy_assessment.patient
            self.hvd_appointment = None
            # self.tele_appointment = None

    @api.onchange('hvd_appointment')
    def _onchange_hvd_appointment(self):
        if self.hvd_appointment:
            self.patient = self.hvd_appointment.patient
            self.phy_assessment = False
            # self.tele_appointment = None

    @api.onchange('appointment')
    def _onchange_tele_appointment(self):
        if self.appointment:
            self.patient = self.appointment.patient
            self.phy_assessment = False
            self.hvd_appointment = None

    # @api.onchange('tele_appointment')
    # def _onchange_tele_appointment(self):
    #     if self.tele_appointment:
    #         self.patient = self.tele_appointment.patient
    #         self.phy_assessment = False
    #         self.hvd_appointment = None
