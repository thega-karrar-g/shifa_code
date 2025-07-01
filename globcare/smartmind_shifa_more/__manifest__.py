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
    'name': '03. Shifa More Modules',
    'version': '1.0',
    'author': "Smart Mind",
    'category': 'Generic Modules/Medical',
    'summary': 'Odoo 14 EMR & HIS based Medical, Health and Hospital Management Solutions',
    'depends': ['oehealth', 'oehealth_extra_addons', 'oehealth_jitsi'],
    'description': """Hospital Management System Customization for Shifa Hospital - from Smart Mind Co.""

About Sehati
---------------


Sehati is a multi-user, highly scalable, centralized Electronic Medical Record (EMR) and Hospital Information System for Odoo.

Manage your patients with their important details including family info, prescriptions, appointments, diseases, insurances, lifestyle,mental & social status, lab test details, invoices and surgical histories.

Administer all your doctors with their complete details, weekly consultancy schedule, prescriptions, inpatient admissions and many more.

Allow your doctors and patients to login inside your Sehati system to manage their appointments. Sehati is tightly integrated with Odoo’s calendar control so you will be always updated for your upcoming schedules.
""",
    "website": "https://smartmindsys.com/",

    "data": [
        'security/ir.model.access.csv',
        'security/actions_windows.xml',
        'sm_medical/data/sequence.xml',
        'sm_extra/views/sm_discounts_views.xml',
        'sm_extra/views/sm_multidisciplinary_team_meeting_views.xml',
        'reports/report_action.xml',
        'reports/consent_report_template.xml',
        'reports/multidisciplinary_report_template.xml',
        'reports/sm_medical_report_module.xml',
        'sm_extra/views/sm_consent_views.xml',
        'sm_extra/views/sm_medical_report.xml',
        'sm_extra/views/sm_nurse_assessment_views.xml',
        'sm_extra/views/sm_physician_assessment_views.xml',
        'sm_extra/views/sm_complaint_views.xml',

        'sm_medical/views/sm_package_appointments_view.xml',
        'sm_medical/views/sm_package_appointments_view_multi.xml',
        'sm_medical/views/sm_aggregator_view.xml',
        'sm_extra/views/sm_app_notification_view.xml',

        'data/schedual_action.xml',
        'sequence/shifa_more_sequence.xml',

        'reports/period_report_template.xml',
        'reports/period_report.xml',
        'wizard/sm_instant_prescription_history_views.xml',
        'wizard/sm_instant_consultation_views.xml',
        'security/more_menu.xml',
        'security/other_menus.xml',
    ],
    # # "images": ['images/main_screenshot.png'],
    # "active": False
}
