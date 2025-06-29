# -*- coding: utf-8 -*-
{
    'name': "Analytical Account On Journal And Purchase",
    'category': "Accounting",

    'summary': """ This module allows to select analytical account on journal level""",

    'author': "smartmindsys",
    'website': "https://www.smartmindsys.com/",

    'version': '1.0',
    'depends': ['account','purchase_stock','sm_user_warehouse_access'],
    
    'data': [
        'security/record_rules.xml',
        'views/res_users.xml',
        'views/account_journal.xml',
        'views/account_move.xml',
        'views/purchase.xml',
        'views/stock_warehouse.xml',
    ],
}
