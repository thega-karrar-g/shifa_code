from odoo import models, fields, api


class ShifaRegisterForEvaluation(models.Model):
    _inherit = "oeh.medical.evaluation"

    treatment_line = fields.One2many('oeh.medical.treatment', 'appointment', string='Treatment Lines',
                                     readonly=False, states={'Invoiced': [('readonly', True)]})

    working_diagnosis = fields.Many2one('oeh.medical.pathology', string='Working Diagnosis', help="Choose a disease for this medicament from the disease list. It can be an existing disease of the patient or a prophylactic.")
    differential_diagnosis_1 = fields.Many2one('oeh.medical.pathology', string='Differential Diagnosis 1', help="Choose a disease for this medicament from the disease list. It can be an existing disease of the patient or a prophylactic.")
    differential_diagnosis_2 = fields.Many2one('oeh.medical.pathology', string='Differential Diagnosis 2', help="Choose a disease for this medicament from the disease list. It can be an existing disease of the patient or a prophylactic.")
    differential_diagnosis_3 = fields.Many2one('oeh.medical.pathology', string='Differential Diagnosis 3', help="Choose a disease for this medicament from the disease list. It can be an existing disease of the patient or a prophylactic.")
    differential_diagnosis_4 = fields.Many2one('oeh.medical.pathology', string='Differential Diagnosis 4', help="Choose a disease for this medicament from the disease list. It can be an existing disease of the patient or a prophylactic.")

    @api.model
    def default_get(self, fields):
        rec = models.Model.default_get(self, fields)
        rec['evaluation_type'] = 'Telemedicine'
        return rec

