# -*- coding: utf-8 -*-
{
    'name': "Discharge Report",

    'summary': """
     SM-Medical-Reports
    """,

    'description': """
       SM-Medical-Reports model captures a wide array of medical information associated with patients,
        facilitating the documentation and tracking of various medical services
        and interventions.   
        """,
    'category': 'SM HIS/Medical',
    'version': '1.0',

    'author': "SmartMind",
    'website': "https://my-care.io/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'oehealth', 'oehealth_extra_addons', 'oehealth_smartmind', 'smartmind_shifa', 'utm', 'mail'],

    # always loaded
    'data': [
        'sequence/sm_medical_report_sequence.xml',
        'security/ir.model.access.csv',

        'reports/sm_medical_report_action.xml',
        'reports/sm_discharge_report_template.xml',

        'views/sm_discharge_report_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [],
}
