from odoo import models, fields


class ShifaAnticoagulationManagement(models.Model):
    _inherit = 'sm.shifa.anticoagulation.management'

    consent_ids = fields.One2many('sm.shifa.consent','anticoagulation_id', string='Consent')

class ShifaComprehensiveNurse(models.Model):
    _inherit = 'sm.shifa.comprehensive.nurse'

    consent_ids = fields.One2many('sm.shifa.consent','comprehensive_id', string='Consent')
class ShifaContinenceCare(models.Model):
    _inherit = 'sm.shifa.continence.care'

    consent_ids = fields.One2many('sm.shifa.consent','continence_id', string='Consent')

class ShifaDiabetiCare(models.Model):
    _inherit = 'sm.shifa.diabetic.care'

    consent_ids = fields.One2many('sm.shifa.consent','diabetic_id', string='Consent')

class ShifaDrainTube(models.Model):
    _inherit = 'sm.shifa.drain.tube'

    consent_ids = fields.One2many('sm.shifa.consent', 'drain_id', string='Consent')


class ShifaEnteralFeeding(models.Model):
    _inherit = 'sm.shifa.enteral.feeding'

    consent_ids = fields.One2many('sm.shifa.consent','enteral_id', string='Consent')


class ShifaNebulizationCare(models.Model):
    _inherit = 'sm.shifa.nebulization.care'

    consent_ids = fields.One2many('sm.shifa.consent','nebulization_id', string='Consent')


class ShifaNewbornCare(models.Model):
    _inherit = 'sm.shifa.newborn.care'

    consent_ids = fields.One2many('sm.shifa.consent','newborn_id', string='Consent')


class ShifaAdministration(models.Model):
    _inherit = 'sm.shifa.oxygen.administration'

    consent_ids = fields.One2many('sm.shifa.consent','oxygen_id',string='Consent')


class ShifaPalliativeCare(models.Model):
    _inherit = 'sm.shifa.palliative.care'

    consent_ids = fields.One2many('sm.shifa.consent','palliative_id',string='Consent')


class ShifaParenteralDrugfluid(models.Model):
    _inherit = 'sm.shifa.parenteral.drugfluid'

    consent_ids = fields.One2many('sm.shifa.consent','parenteral_id',string='Consent')


class ShifaPressureUlcer(models.Model):
    _inherit = 'sm.shifa.pressure.ulcer'

    consent_ids = fields.One2many('sm.shifa.consent','pressure_id',string='Consent')


class ShifaPostnatalCare(models.Model):
    _inherit = 'sm.shifa.postnatal.care'

    consent_ids = fields.One2many('sm.shifa.consent','postnatal_id',string='Consent')


class ShifaStomaCare(models.Model):
    _inherit = 'sm.shifa.stoma.care'

    consent_ids = fields.One2many('sm.shifa.consent','stoma_id',string='Consent')


class ShifaSubcutInjection(models.Model):
    _inherit = 'sm.shifa.subcut.injection'

    consent_ids = fields.One2many('sm.shifa.consent','subcut_id',string='Consent')


class ShifaTracheCare(models.Model):
    _inherit = 'sm.shifa.trache.care'

    consent_ids = fields.One2many('sm.shifa.consent','trache_id',string='Consent')


class ShifaVaccines(models.Model):
    _inherit = 'sm.shifa.vaccines'

    consent_ids = fields.One2many('sm.shifa.consent','vaccines_id',string='Consent')


class ShifaVitalSigns(models.Model):
    _inherit = 'sm.shifa.vital.signs'

    consent_ids = fields.One2many('sm.shifa.consent','vital_id',string='Consent')


class ShifaWoundAssessment(models.Model):
    _inherit = 'sm.shifa.wound.assessment'

    consent_ids = fields.One2many('sm.shifa.consent','wound_id',string='Consent')


class ShifaPhysicianAdmission(models.Model):
    _inherit = 'sm.shifa.physician.admission'

    consent_ids = fields.One2many('sm.shifa.consent','physician_admission_id',string='Consent')


class ShifaPhysiotherapyAssessment(models.Model):
    _inherit = 'sm.shifa.physiotherapy.assessment'

    consent_ids = fields.One2many('sm.shifa.consent','physiotherapy_assessment_id',string='Consent')


class ShifaSafeHomeVisitScreening(models.Model):
    _inherit = 'sm.shifa.safe.home.visit.screening'

    consent_ids = fields.One2many('sm.shifa.consent','safe_home_id',string='Consent')


class ShifaCaregiverFollowupConsent(models.Model):
    _inherit = 'sm.shifa.care.giver.follow.up'

    consent_ids = fields.One2many('sm.shifa.consent', 'caregiver_fu_id', string='Consent')


class ShifaComprehensiveFollowupConsent(models.Model):
    _inherit = 'sm.shifa.comprehensive.nurse.follow.up'

    consent_ids = fields.One2many('sm.shifa.consent', 'comprehensive_nurse_fu_id', string='Consent')

class ShifaNurseAssessmentConsent(models.Model):
    _inherit = 'sm.shifa.nurse.assessment'

    consent_ids = fields.One2many('sm.shifa.consent', 'nurse_assessment_fu_id', string='Consent')

class ShifaPhysicianAssessmentConsent(models.Model):
    _inherit = 'sm.shifa.physician.assessment'
    complate = {
        'Draft': [('readonly', True)],
        'Admitted': [('readonly', True)],
        'Discharged': [('readonly', True)]
    }
    consent_ids = fields.One2many('sm.shifa.consent', 'physician_assessment_fu_id', string='Consent', readonly=False, states=complate)


class ShifaConsentIds(models.Model):
    _inherit = 'sm.shifa.consent'

    drain_id = fields.Many2one('sm.shifa.drain.tube', string='Consent')
    anticoagulation_id = fields.Many2one('sm.shifa.anticoagulation.management', string='Consent')
    comprehensive_id = fields.Many2one('sm.shifa.comprehensive.nurse', string='Consent')
    diabetic_id = fields.Many2one('sm.shifa.diabetic.care', string='Consent')
    enteral_id = fields.Many2one('sm.shifa.enteral.feeding', string='Consent')
    nebulization_id = fields.Many2one('sm.shifa.nebulization.care', string='Consent')
    continence_id = fields.Many2one('sm.shifa.continence.care', string='Consent')
    newborn_id = fields.Many2one('sm.shifa.newborn.care', string='Consent')
    oxygen_id = fields.Many2one('sm.shifa.oxygen.administration', string='Consent')
    palliative_id = fields.Many2one('sm.shifa.palliative.care', string='Consent')
    parenteral_id = fields.Many2one('ssm.shifa.parenteral.drugfluid', string='Consent')
    pressure_id = fields.Many2one('sm.shifa.pressure.ulcer', string='Consent')
    postnatal_id = fields.Many2one('sm.shifa.postnatal.care', string='Consent')
    stoma_id = fields.Many2one('sm.shifa.stoma.care', string='Consent')
    subcut_id = fields.Many2one('sm.shifa.subcut.injection', string='Consent')
    trache_id = fields.Many2one('sm.shifa.postnatal.care', string='Consent')
    vaccines_id = fields.Many2one('sm.shifa.vaccines', string='Consent')
    vital_id = fields.Many2one('sm.shifa.vital.signs', string='Consent')
    wound_id = fields.Many2one('sm.shifa.wound.assessment', string='Consent')
    physician_admission_id = fields.Many2one('sm.shifa.physician.admission', string='Consent')
    physiotherapy_assessment_id = fields.Many2one('sm.shifa.physiotherapy.assessment', string='Consent')
    safe_home_id = fields.Many2one('sm.shifa.safe.home.visit.screening', string='Consent')
    caregiver_fu_id = fields.Many2one('sm.shifa.care.giver.follow.up', string='Consent')
    comprehensive_nurse_fu_id = fields.Many2one('sm.shifa.comprehensive.nurse.follow.up', string='Consent')
    nurse_assessment_fu_id = fields.Many2one('sm.shifa.nurse.assessment', string='Consent')
    physician_assessment_fu_id = fields.Many2one('sm.shifa.physician.assessment', string='Consent')


