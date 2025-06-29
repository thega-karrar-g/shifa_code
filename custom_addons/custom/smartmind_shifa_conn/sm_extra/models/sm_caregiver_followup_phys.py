from odoo import models, fields


class ShifaAnticoagulationManagement(models.Model):
    _inherit = 'sm.shifa.care.giver.follow.up'

    phy_asse = fields.Many2one('sm.shifa.physician.assessment', string='Phy_Assessment#', required=True,
                              readonly=True, states={'Draft': [('readonly', False)]},
                              domain="[('patient','=',patient), ('state', 'in', ('Admitted', 'Start'))]")

    provisional_diagnosis = fields.Many2one('oeh.medical.pathology', related='phy_asse.provisional_diagnosis')
    provisional_diagnosis_add = fields.Many2one('oeh.medical.pathology', related='phy_asse.provisional_diagnosis_add')
    provisional_diagnosis_add2 = fields.Many2one('oeh.medical.pathology', related='phy_asse.provisional_diagnosis_add2')
    provisional_diagnosis_add3 = fields.Many2one('oeh.medical.pathology', related='phy_asse.provisional_diagnosis_add3')
    medical_care_plan = fields.Text(related='phy_asse.medical_care_plan')
