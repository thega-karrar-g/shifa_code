# -*- coding: utf-8 -*-
{
    'name': 'Shifa Report Customization',
    'version': '1.0',
    'summary': 'Shifa Customization software',
    'sequence': -100,
    'description': """Odoo 14 Development""",
    'category': 'Generic Modules',
    'author': 'Shifa',
    'license': 'AGPL-3',
    'maintainer': 'Shifa',
    'website': '',
    'depends': ['mail','smartmind_shifa','sm_caregiver'],
    'data': [
    'views/contract_report.xml',
    'security/ir.model.access.csv',
    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
