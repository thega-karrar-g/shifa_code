from odoo import models, fields


class ShifaPhysicianAdmission(models.Model):
    _inherit = 'sm.shifa.physician.admission'

    nursing_comprehensive_ids = fields.One2many('sm.shifa.comprehensive.nurse', 'phy_adm', string='Nursing Assessment')
    caregiver_followup_line = fields.One2many('sm.shifa.care.giver.follow.up', 'phy_adm')
    physiotherapy_line = fields.One2many('sm.shifa.physiotherapy.assessment', 'phy_adm')
    parenteral_drug_fluid_line = fields.One2many('sm.shifa.parenteral.drugfluid', 'phy_adm')
    pres_phy_line = fields.One2many('sm.shifa.prescription.line', 'prescription_phy_ids')


class ShifaNursingInherit(models.Model):
    _inherit = 'sm.shifa.comprehensive.nurse'

    physician_admission = fields.Many2one('sm.shifa.physician.admission', string='physician', ondelete='cascade')


class ShifaPhysicianAdmissionInCaregiverFollowup(models.Model):
    _inherit = 'sm.shifa.care.giver.follow.up'

    physician_admission = fields.Many2one('sm.shifa.physician.admission', string="physician_admission")


class ShifaPhysicianAdmissionInPhysiotherapyAssessment(models.Model):
    _inherit = 'sm.shifa.physiotherapy.assessment'

    physician_admission = fields.Many2one('sm.shifa.physician.admission', string="physician_admission")

#  This is for physician assessment and prescription tab
class ShifaPrescriptionPhyLinesInherit(models.Model):
    _inherit = "sm.shifa.prescription.line"

    prescription_phy_ids = fields.Many2one('sm.shifa.physician.admission', 'pres_phy_line', ondelete='cascade', index=True)


class ShifaPrescriptionPhALinesInherit(models.Model):
    _inherit = "sm.shifa.prescription.line"

    prescription_phA_ids = fields.Many2one('sm.shifa.physician.assessment', 'pres_phA_line', ondelete='cascade', index=True)


class ShifaPhysicianAssessment(models.Model):
    _inherit = "sm.shifa.physician.assessment"
    complate = {
        'Draft': [('readonly', True)],
        'Admitted': [('readonly', True)],
        'Discharged': [('readonly', True)]
    }
    pres_phA_line = fields.One2many('sm.shifa.prescription.line', 'prescription_phA_ids', readonly=False, states=complate)
    physiotherapy_phA_line = fields.One2many('sm.shifa.physiotherapy.assessment', 'physician_assessment', readonly=False, states=complate)


class PhysicianAssessmentPhysiotherapyAssessment(models.Model):
    _inherit = 'sm.shifa.physiotherapy.assessment'

    physician_assessment = fields.Many2one('sm.shifa.physician.assessment', string="PhA")






