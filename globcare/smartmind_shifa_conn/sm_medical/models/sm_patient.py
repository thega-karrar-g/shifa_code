from odoo import models, fields


class ShifaPatientComprehensive(models.Model):
    _inherit = 'oeh.medical.patient'

    def _instant_consultation_count(self):
        oe_apps = self.env['sm.shifa.instant.consultation']
        for pa in self:
            domain = [('patient', '=', pa.id)]
            app_ids = oe_apps.search(domain)
            apps = oe_apps.browse(app_ids)
            app_count = 0
            for ap in apps:
                app_count += 1
            pa.instant_consultation_count = app_count
        return True
    def _compute_package_count(self):
        package = self.env['sm.shifa.package.appointments']
        for pa in self:
            domain = [('patient', '=', pa.id)]
            app_ids = package.search(domain)
            apps = package.browse(app_ids)
            app_count = 0
            for ap in apps:
                app_count += 1
            pa.package_count = app_count
        return True

    nursing_comprehensive_ids = fields.One2many('sm.shifa.comprehensive.nurse', 'patient',
                                                string='Comprehensive Nursing Assessment')
    nursing_comprehensive_fu_ids = fields.One2many('sm.shifa.comprehensive.nurse.follow.up', 'patient',
                                                string='Comprehensive Nursing Assessment Follow up')

    vaccines_line = fields.One2many('sm.shifa.vaccines', 'patient',
                                                string='Vaccines')
    requested_payments_line = fields.One2many('sm.shifa.requested.payments', 'patient',
                                                string='Requested Payments')
    cancellation_refund_line = fields.One2many('sm.shifa.cancellation.refund', 'patient',
                                              string='Cancellation Refund')
    instant_prescription_line = fields.One2many('sm.shifa.instant.prescriptions', 'patient',
                                               string='Instant prescription')
    anticoagulation_management_line = fields.One2many('sm.shifa.anticoagulation.management', 'patient',
                                                string='Anticoagulation Management')
    comprehensive_nurse_line = fields.One2many('sm.shifa.comprehensive.nurse', 'patient',
                                                string='Comprehensive Nurse')
    diabetic_care_line = fields.One2many('sm.shifa.diabetic.care', 'patient',
                                                string='Diabetic Care')
    drain_tube_line = fields.One2many('sm.shifa.drain.tube', 'patient',
                                                string='Drain Tube Care')
    enteral_feeding_line = fields.One2many('sm.shifa.enteral.feeding', 'patient',
                                                string='Enteral Feeding')
    newborn_care_line = fields.One2many('sm.shifa.newborn.care', 'patient',
                                                string='Newborn Care')
    oxygen_administration_line = fields.One2many('sm.shifa.oxygen.administration', 'patient',
                                                string='Oxygen Administration')
    palliative_care_line = fields.One2many('sm.shifa.palliative.care', 'patient',
                                                string='Palliative Care')
    parenteral_drugfluid_line = fields.One2many('sm.shifa.parenteral.drugfluid', 'patient',
                                                string='Parenteral Drugfluid')
    parenteral_drugfluid_fu_line = fields.One2many('sm.shifa.parenteral.drugfluid.follow.up', 'patient',
                                                string='Parenteral Drug fluid Follow up')

    postnatal_care_line = fields.One2many('sm.shifa.postnatal.care', 'patient',
                                                string='Postnatal Care')
    pressure_ulcer_line = fields.One2many('sm.shifa.pressure.ulcer', 'patient',
                                                string='Pressure Ulcer')
    stoma_care_line = fields.One2many('sm.shifa.stoma.care', 'patient',
                                                string='Stoma Care')
    subcut_injection_line = fields.One2many('sm.shifa.subcut.injection', 'patient',
                                                string='Subcut Injection')
    continence_care_line = fields.One2many('sm.shifa.continence.care', 'patient',
                                                string='Continence Care')
    trache_care_line = fields.One2many('sm.shifa.trache.care', 'patient',
                                                string='Trache Care')
    nebulization_care_line = fields.One2many('sm.shifa.nebulization.care', 'patient',
                                                string='Nebulization Care')

    wound_assessment_line = fields.One2many('sm.shifa.wound.assessment', 'patient',
                                                string='Wound Assessment')
    wound_assessment_fu_line = fields.One2many('sm.shifa.wound.care.followup', 'patient',
                                                string='Wound Assessment Follow up')
    physician_admission_fu_line = fields.One2many('sm.physician.admission.followup', 'patient',
                                                string='Physician Admission Follow up')
    physician_assessment_line = fields.One2many('sm.shifa.physician.assessment', 'patient',
                                                string='Physician Assessment')
    nurse_assessment_line = fields.One2many('sm.shifa.nurse.assessment', 'patient',
                                                string='Nurse Assessment')

    instant_consultation_count = fields.Integer(compute=_instant_consultation_count, string="Instant Consultation")

    multidisciplinary_line = fields.One2many('sm.shifa.multidisciplinary.team.meeting', 'patient',  string='Multidisciplinary Team Meeting')


    report_line = fields.One2many('sm.medical.report', 'patient',  string='Report')

    house_location = fields.Char(string='House Location')
    package_count = fields.Integer(compute=_compute_package_count, string='Package')

     # open package form
    def open_package_view(self):
        action = self.env['ir.actions.act_window']._for_xml_id('smartmind_shifa_more.sm_shifa_package_appointments_action_tree')
        action['domain'] = [('patient', '=', self.id)]
        action.update({'context': {}})
        return action




