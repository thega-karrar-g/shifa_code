# -*- coding: utf-8 -*-
{
    'name': "02. Smartmind Shifa Extra",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "SmartMind",
    "website": "https://smartmindsys.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Generic Modules/Medical',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'oehealth', 'oehealth_extra_addons'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'sm_medical/views/shifa_anticoagulation_management.xml',
        'sm_medical/views/shifa_anticoagulation_follow_up.xml',
        'sm_medical/views/shifa_breast_follow_up.xml',
        'sm_medical/views/shifa_breast_surgery.xml',
        'sm_medical_care/views/shifa_continence_care.xml',
        'sm_medical_care/views/shifa_continence_follow_up.xml',
        'sm_medical_care/views/shifa_diabetic_care.xml',
        'sm_medical_care/views/shifa_diabetic_follow_up.xml',
        'sm_medical/views/shifa_enteral_feeding.xml',
        'sm_medical/views/shifa_enteral_follow_up.xml',
        'sm_medical_care/views/shifa_newborn_care.xml',
        'sm_medical_care/views/shifa_newborn_follow_up.xml',
        'sm_medical_care/views/shifa_palliative_care.xml',
        'sm_medical_care/views/shifa_palliative_follow_up.xml',
        'sm_medical/views/shifa_parenteral_drugfluid.xml',
        'sm_medical/views/shifa_parenteral_follow_up.xml',
        'sm_medical_care/views/shifa_postnatal_care.xml',
        'sm_medical_care/views/shifa_postnatal_follow_up.xml',
        'sm_medical/views/shifa_pressure_ulcer.xml',
        'sm_medical/views/shifa_pressure_follow_up.xml',
        'sm_medical_care/views/shifa_stoma_care.xml',
        'sm_medical_care/views/shifa_stoma_follow_up.xml',
        'sm_medical/views/shifa_vital_signs.xml',
        'sm_medical/views/shifa_oxygen_administration.xml',
        'sm_medical/views/shifa_oxygen_follow_up.xml',
        'sm_medical_care/views/shifa_nebulization_care.xml',
        'sm_medical_care/views/shifa_nebulization_follow_up.xml',
        'sm_medical_care/views/shifa_trache_care.xml',
        'sm_medical_care/views/shifa_trache_follow_up.xml',
        'sm_medical_care/views/shifa_care_giver.xml',
        'sm_medical_care/views/shifa_care_follow_up.xml',
        'sm_medical/views/shifa_subcut_injection.xml',
        'sm_medical/views/shifa_subcut_follow_up.xml',
        'sm_medical/views/shifa_comprehensive_nurse.xml',
        'sm_medical/views/shifa_comprehensive_follow_up.xml',
        'sm_medical/views/shifa_vaccines.xml',
        'sm_medical_extra/views/shifa_cancelation_refund.xml',
        'sm_medical_extra/views/shifa_requested_payments.xml',
        'sm_pharmacy/views/shifa_instant_consultation.xml',
        'sm_pharmacy/views/shifa_instant_consultancy_charge.xml',
        'sm_pharmacy/views/shifa_time_counters.xml',
        'sm_pharmacy/views/shifa_instant_prescriptions.xml',
        'sm_pharmacy/views/shifa_pharmacist_view.xml',
        'sm_pharmacy/views/shifa_pharmacies_view.xml',
        'sm_pharmacy/views/shifa_pharmacy_chain.xml',
        'sm_pharmacy/views/shifa_app_update.xml',
        'sm_pharmacy/report/report_medical_pharmacy.xml',
        'sm_pharmacy/report/sm_shifa_medical_pharmacy_action.xml',
        'sm_pharmacy/report/report_medical_pharmacy_prescriptions.xml',
        'sm_pharmacy/views/shifa_pharmacy_medicines.xml',
        'sm_pharmacy/views/shifa_paid_amount.xml',
        'sm_pharmacy/views/shifa_penalties.xml',
        'sm_medical_extra/views/shifa_call_center_census.xml',
        'sm_pharmacy/views/shifa_instant_prescription_history_views.xml',

        'data/shifa_instant_charge.xml',
        'data/shifa_insurance_auto_actions.xml',
        'data/shifa_app_update.xml',
        'data/instant_prescription_mail_template.xml',

        'sequence/sequence.xml',
        'security/shifa_menu.xml',
        'security/ir.rule.xml',
    ],
}
