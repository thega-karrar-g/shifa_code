# -*- coding: utf-8 -*-
{
    'name': "Warehouse Access per user",
    'category': 'Inventory',

    'summary': """ This module allows to give users specific warehouses """,

    'author': "smartmindsys",
    'website': "https://www.smartmindsys.com/",

    'version': '1.0',
    'depends': ['stock'],
    
    'data': [
        'security/groups.xml',
        'security/record_rules.xml',
        'views/res_users.xml',
    ],
}
