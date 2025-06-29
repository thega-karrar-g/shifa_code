{
    'name': "Insurance",
    'author': "Smart Mind",
    'category': 'Generic Modules/Medical',

    'summary': """
             """,

    'description': """
        """,
    'website': "https://my-care.io/",
    'version': '2.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'utm', 'smartmind_shifa','oehealth'],

    # always loaded
    'data': [
        'data/schedual_action.xml',
        'sequence/insurance_sequence.xml',
        'security/ir.model.access.csv',
        # 'security/insurance.xml',
        'views/sm_medical_insurance_companies_views.xml',
        'views/sm_service_price.xml',
        'views/sm_insurance_policy.xml',
        'views/sm_medical_insurance_classes_views.xml',
        'views/sm_insured_companies.xml',
        # 'views/sm_patient.xml',


    ],
}



