{
    'name': "Insurance Integration",
    'author': "Smart Mind",
    'category': 'Generic Modules/Medical',

    'summary': """
             """,

    'description': """
        """,
    'website': "https://my-care.io/",
    'version': '2.0',

    # any module necessary for this one to work correctly
    'depends': ['base' , 'oehealth'],

    # always loaded
    'data': [
        'sequence/insurance_sequence.xml',
        # 'security/insurance.xml',
        'security/ir.model.access.csv',
        'views/sm_eligibility_check_requests_views.xml',
        'views/sm_pre_authorization_diagnosis_views.xml',
        'views/sm_pre_authorization_request_views.xml',
        # 'views/sm_dashboard_views.xml',
        # 'views/sm_clinic_appointment.xml',


    ],

    'assets': {
        'web.assets_backend': [
            # 'sm_insurance_integration/static/src/js/sm_dashboard.js',
            # 'sm_radiology_referral/static/src/js/autorefresh_dashboard_view.js',
            # 'sm_insurance_integration/static/src/xml/sm_insurance_dashboard.xml',
            # 'https://pixinvent.com/stack-responsive-bootstrap-4-admin-template/app-assets/css/bootstrap.min.css',
            # 'sm_insurance_integration/static/src/css/sm_dashboard.css',
            # 'sm_insurance_integration/static/src/css/sm_font_icons.css',
        ],
    },
}



