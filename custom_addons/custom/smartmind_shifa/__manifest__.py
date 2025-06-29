##############################################################################
#    Copyright (C) 2021 - Present, SmartMind Sehati (<https://smartmindsys.com/>). All Rights Reserved
#    Sehati, Hospital Management Solutions

# Odoo Proprietary License v1.0
#
# This software and associated files (the "Software") may only be used (executed,
# modified, executed after modifications) if you have purchased a valid license
# from the authors, typically via Odoo Apps, Sehati, smartmindsys.com, or if you have received a written
# agreement from the authors of the Software.
#
# You may develop Odoo modules that use the Software as a library (typically
# by depending on it, importing it and using its resources), but without copying
# any source code or material from the Software. You may distribute those
# modules under the license of your choice, provided that this license is
# compatible with the terms of the Odoo Proprietary License (For example:
# LGPL, MIT, or proprietary licenses similar to this one).
#
# It is forbidden to publish, distribute, sublicense, or sell copies of the Software
# or modified copies of the Software.
#
# The above copyright notice and this permission notice must be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

##############################################################################
{
    'name': '01. Shifa HIS',
    'version': '1.0',
    'author': "Smart Mind",
    'category': 'Generic Modules/Medical',
    'summary': 'Odoo 14 EMR & HIS based Medical, Health and Hospital Management Solutions',
    'depends': ['oehealth', 'oehealth_extra_addons', 'oehealth_jitsi', 'calendar', 'social_media'],
    'description': """Hospital Management System Customization for Shifa Hospital - from Sehati""

About Sehati
---------------

Sehati is a multi-user, highly scalable, centralized Electronic Medical Record (EMR) and Hospital Information System for Odoo.

Manage your patients with their important details including family info, prescriptions, appointments, diseases, insurances, lifestyle,mental & social status, lab test details, invoices and surgical histories.

Administer all your doctors with their complete details, weekly consultancy schedule, prescriptions, inpatient admissions and many more.

Allow your doctors and patients to login inside your Sehati system to manage their appointments. Sehati is tightly integrated with Odoo’s calendar control so you will be always updated for your upcoming schedules.
""",
    "website": "https://smartmindsys.com/",

    "data": [
        'security/shifa_security.xml',
        'security/shifa_parent_menu.xml',
        'security/shifa_navigation.xml',
        'sm_general/views/shifa_appointment_views.xml',
        # 'sm_general/views/sm_hvd_appointment_views.xml',
        'sm_general/views/shifa_evaluation_views.xml',
        'sm_general/views/shifa_icu_admission_views.xml',
        'sm_general/views/shifa_physician_views.xml',
        'sm_general/views/shifa_strength_units_view.xml',
        'sm_general/views/shifa_prespection_inhert_views.xml',
        'sm_general/views/shifa_lab_test_view.xml',
        'sm_general/views/shifa_image_test_view.xml',
        'sm_general/views/shifa_generic_medicines_view.xml',
        'sm_general/views/shifa_prescription_line_view.xml',
        'sm_general/views/shifa_physician_views.xml',
        'sm_general/views/sehati_odoo_views.xml',
        'sm_general/views/shifa_patient_views.xml',
        'sm_general/views/shifa_brand_medicines_view.xml',
        'sm_general/views/shifa_generic_vaccines_view.xml',
        # 'sm_general/views/template.xml',
        'sm_general/views/shifa_external_prescription_views.xml',
        'sm_general/views/shifa_medication_profile_views.xml',

        'sm_extra_info/views/sm_home_visit_screening_views.xml',
        'sm_extra_info/views/sm_investigation_views.xml',
        'sm_extra_info/views/sm_insurance_view.xml',

        'sm_appointment/views/sm_hhc_appointment_views.xml',
        'sm_appointment/views/sm_physiotherapy_views.xml',
        'sm_appointment/views/sm_pcr_appointment_views.xml',
        'sm_appointment/views/sm_service_request_views.xml',
        # 'sm_appointment/views/sm_telemedicine_appointment_views.xml',
        'sm_appointment/views/sm_hvd_appointment_views.xml',

        # 'smartmind_shifa_more/views/sm_discounts_views.xml',
        # 'smartmind_shifa_more/views/sm_multidisciplinary_team_meeting_views.xml',

        'sm_physiotherapy/views/sm_physiotherapy_assessment_views.xml',
        'sm_physiotherapy/views/sm_physiotherapy_followup_views.xml',

        'sm_health_care/views/sm_wound_assessment_views.xml',
        'sm_health_care/views/sm_wound_assessment_values_views.xml',
        'sm_health_care/views/sm_wound_care_followup_view.xml',
        'sm_health_care/views/sm_nursing_assessment_views.xml',
        'sm_health_care/views/sm_physician_admission_views.xml',
        'sm_health_care/views/sm_physician_admission_followup_view.xml',
        'sm_health_care/views/sm_home_rounding_views.xml',
        'sm_health_care/views/sm_patient_treatment_views.xml',
        'sm_health_care/views/sm_medical_views.xml',
        'sm_health_care/views/sm_referral_views.xml',
        'sm_health_care/views/sm_notification_views.xml',
        'sm_health_care/views/shifa_lab_request_view.xml',
        'sm_health_care/views/shifa_imaging_request_view.xml',

        # report action
        'sm_general/reports/sm_shifa_medical_report.xml',
        'sm_general/reports/report_patient_prescriptions.xml',
        'sm_general/reports/header_footer.xml',
        'sm_general/reports/report_lab_test_template.xml',
        'sm_general/reports/report_imaging_template.xml',

        'sm_general/views/shifa_medicines_view.xml',
        'sm_health_care/reports/image_request_report.xml',
        'sm_health_care/reports/lab_request_report.xml',
        'sm_health_care/reports/sm_shifa_health_care_report_action.xml',

        'sm_extra_info/views/sm_investigation_name_view.xml',
        'sm_extra_info/views/sm_investigation_views.xml',
        'sm_extra_info/views/sm_basic_info_views.xml',
        'sm_extra_info/views/sm_contactus_view.xml',
        'sm_extra_info/views/sm_facility_contract_module_view.xml',
        'sm_extra_info/views/sm_doctor_schedule_view.xml',
        'sm_extra_info/views/sm_web_request_views.xml',

        'security/shifa_menu.xml',
        'security/ir.model.access.csv',
        'security/ir.rule.xml',
        'security/shifa_menu_appearance.xml',
        'security/shifa_action_appearance.xml',
        'security/shifa_menu_right.xml',
        'sequence/shifa_sequence.xml',

        'data/languages.xml',
        'data/shifa_insurance_auto_actions.xml',
        'data/mail_template_data.xml',
        'data/service_module_data.xml',

        'sm_settings/shifa_stamp_view.xml',
        'sm_settings/shifa_user_stamp_view.xml',
        'sm_settings/shifa_settings_view.xml',
    ],
    # "images": ['images/main_screenshot.png'],
    'qweb': [
        "static/src/xml/webcam.xml",
    ],
    "active": False
}
