##############################################################################
#    Copyright (C) 2015 - Present, oeHealth (<https://www.oehealth.in>). All Rights Reserved
#    oeHealth, Hospital Management Solutions

# Odoo Proprietary License v1.0
#
# This software and associated files (the "Software") may only be used (executed,
# modified, executed after modifications) if you have purchased a valid license
# from the authors, typically via Odoo Apps, oeHealth.in, braincrewapps.com, or if you have received a written
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
    'name': 'Sehati - Hospital Management System',
    'version': '1.0',
    'author': "Smart Mind",
    'category': 'Generic Modules/Medical',
    'summary': 'Odoo 14 EMR & HIS based Medical, Health and Hospital Management Solutions',
    'depends': ['base', 'account', 'product', 'uom', 'hr', 'stock', 'purchase'],
    'price': 350.00,
    'currency': 'EUR',
    'description': """

About Sehati
---------------

Sehati is a multi-user, highly scalable, centralized Electronic Medical Record (EMR) and Hospital Information System for Odoo.

Manage your patients with their important details including family info, prescriptions, appointments, diseases, insurances, lifestyle,mental & social status, lab test details, invoices and surgical histories.

Administer all your doctors with their complete details, weekly consultancy schedule, prescriptions, inpatient admissions and many more.

Allow your doctors and patients to login inside your Sehati system to manage their appointments. Sehati is tightly integrated with Odoo’s calendar control so you will be always updated for your upcoming schedules.
""",
    "website": "https://www.oehealth.in",
    "data": [

        'views/oehealth.xml',
        'security/oeh_security.xml',

        'oeh_navigation.xml',

        'oeh_settings/oeh_settings_view.xml',

        'oeh_medical/views/res_partner_view.xml',
        'oeh_medical/views/product_product_view.xml',
        'oeh_medical/views/oeh_medical_medicaments_view.xml',
        'oeh_medical/views/oeh_medical_pharmacy_view.xml',
        'oeh_medical/views/oeh_medical_healthcenters_view.xml',
        'oeh_medical/views/oeh_medical_pathology_view.xml',
        'oeh_medical/views/oeh_medical_inpatient_view.xml',
        'oeh_medical/views/oeh_medical_view.xml',
        'oeh_medical/views/account_invoice_view.xml',
        'oeh_medical/views/oeh_medical_insurance_view.xml',
        'oeh_medical/views/oeh_medical_ethnic_groups_view.xml',
        'oeh_medical/views/oeh_medical_genetics_view.xml',
        'oeh_medical/reports/report_patient_label.xml',
        'oeh_medical/reports/report_patient_medicines.xml',
        'oeh_medical/reports/report_appointment_receipt.xml',
        'oeh_medical/reports/report_patient_prescriptions.xml',
        'oeh_medical/views/oeh_medical_report.xml',
        'oeh_medical/wizard/oeh_medical_inpatient_wizard_view.xml',
        'oeh_medical/wizard/oeh_medical_appointment_wizard_view.xml',

        'oeh_evaluation/views/oeh_medical_evaluation_view.xml',

        'oeh_socioeconomics/views/oeh_medical_socioeconomics_view.xml',

        'oeh_gyneco/views/oeh_medical_gyneco_view.xml',

        'oeh_lifestyle/views/oeh_medical_lifestyle_view.xml',

        'oeh_lab/views/report_patient_labtest.xml',
        'oeh_lab/views/oeh_medical_lab_report.xml',
        'oeh_lab/views/oeh_medical_lab_view.xml',

        'oeh_icu/views/oeh_icu_management_view.xml',

        'oeh_patient_examination/views/oeh_medical_injury_examination.xml',

        'oeh_patient_examination/wizard/oeh_medical_injury_wiz.xml',

        'oeh_patient_examination/reports/oeh_medical_report.xml',
        'oeh_patient_examination/reports/report_injury_examination.xml',

        'oeh_followup/views/oeh_followup_view.xml',
        'oeh_followup/wizard/oeh_followup_wizard_view.xml',

        # REST API
        'oeh_rest_api/data/api_token_data.xml',
        'oeh_rest_api/data/ir_cron_data.xml',
        'oeh_rest_api/views/api_view.xml',

        'security/oeh_menu_rights.xml',
        'security/ir.model.access.csv',
        'security/ir.rule.xml',
        'sequence/oeh_sequence.xml',

        'oeh_medical/data/oeh_physician_specialities.xml',
        'oeh_medical/data/oeh_physician_degrees.xml',
        'oeh_medical/data/oeh_insurance_types.xml',
        'oeh_medical/data/oeh_ethnic_groups.xml',
        'oeh_medical/data/oeh_who_medicaments.xml',
        'oeh_medical/data/oeh_dose_units.xml',
        'oeh_medical/data/oeh_drug_administration_routes.xml',
        'oeh_medical/data/oeh_drug_form.xml',
        'oeh_medical/data/oeh_dose_frequencies.xml',
        'oeh_medical/data/oeh_genetic_risks.xml',
        'oeh_medical/data/oeh_prescription_email_template.xml',
        'oeh_socioeconomics/data/oeh_occupations.xml',
        'oeh_lifestyle/data/oeh_recreational_drugs.xml',
        'oeh_lab/data/oeh_lab_test_units.xml',
        'oeh_lab/data/oeh_lab_test_types.xml',
        'oeh_medical/data/oeh_disease_categories.xml',
        # 'oeh_medical/data/oeh_diseases.xml',
    ],
    "images": ['images/main_screenshot.png'],
    'qweb': [
        "static/src/xml/webcam.xml",
    ],
    "active": False
}
