{
    'name': 'HR Attendance UI Enhancement',
    'version': '14.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Places Check In/Out button in upper right like Odoo 17',
    'depends': ['hr_attendance'],
    'data': [
        'views/hr_attendance.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'hr_attendance_ui/static/src/css/hr_attendance_ui.css',
        ],
    },
    'installable': True,
    'application': False,
}
