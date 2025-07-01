
{
    'name': '06. Sm Search patient',
    'version': '1.0',
    'author': "Smart Mind",
    'category': 'Generic Modules/Medical',
    'summary': 'Odoo 14 EMR & HIS based Medical, Health and Hospital Management Solutions',
    'depends': ['smartmind_shifa'],
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
        'security/ir.model.access.csv',
        "sequence/sm_sequence.xml",
        "views/sm_patient_search_views.xml",
        "views/sm_treatments_views.xml",
    ],
    'qweb': [

    ],
    "active": False
}
