{
    'name': 'Caregiver Modules',
    'version': '1.0',
    'author': "Smart Mind",
    'category': 'Generic Modules/Medical',
    'summary': 'Odoo 14 EMR & HIS based Medical, Health and Hospital Management Solutions',
    'description': """Hospital Management System Customization for Shifa Hospital - from Smart Mind Co.""

About Sehati
---------------


Sehati is a multi-user, highly scalable, centralized Electronic Medical Record (EMR) and Hospital Information System for Odoo.

Manage your patients with their important details including family info, prescriptions, appointments, diseases, insurances, lifestyle,mental & social status, lab test details, invoices and surgical histories.

Administer all your doctors with their complete details, weekly consultancy schedule, prescriptions, inpatient admissions and many more.

Allow your doctors and patients to login inside your Sehati system to manage their appointments. Sehati is tightly integrated with Odoo’s calendar control so you will be always updated for your upcoming schedules.
""",

    "website": "https://smartmindsys.com/",
    'depends': ['oehealth', 'oehealth_extra_addons', 'smartmind_shifa', 'smartmind_shifa_extra', 'sm_search_patient'],

    "data": [
        'security/security_groups.xml',
        'security/ir.model.access.csv',
        'sequence/shifa_more_sequence.xml',

        'views/sm_patient_medicines_view.xml',
        'views/sm_caregiver_views.xml',
        'views/sm_medicines_frequencies_view.xml',
        'views/sm_medicine_schedule_view.xml',
        'views/sm_sleep_medicine_request_view.xml',
        'views/sm_caregiver_contracts_view.xml',
        'views/requested_payment_view.xml',
        'views/cancelation_refund_view.xml',
        'views/call_center_census.xml',
        'views/sm_patient_views.xml',
        'views/sm_instant.xml',
        'views/sm_slider.xml',
        'data/schedual_action.xml',
    ],
    # # "images": ['images/main_screenshot.png'],
    # "active": False
}
