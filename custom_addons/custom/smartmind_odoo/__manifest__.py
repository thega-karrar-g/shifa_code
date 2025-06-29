# -*- coding: utf-8 -*-
{
    'name': "Smartmind Odoo",

    'summary': """
        This module used for fit odoo modules as customer needs """,

    'description': """
        Long description of module's purpose
            """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'hr_contract', 'contacts', 'fleet', 'hr_attendance',
        'hr_holidays', 'om_credit_limit', 'global_discount_sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        # 'security/sm_menu.xml',
        'security/sm_menu_appearance.xml',
        'security/sm_menu_right.xml',
        'sm_accounting/views/account_type_view.xml',
        'sm_accounting/views/account_third_level_view.xml',
        'sm_accounting/views/sm_account_chart_view.xml',
        'sm_accounting/views/sm_account_payment_view.xml',
        'sm_general/views/ir_attachment_view.xml',
        'sm_general/views/res_user_view.xml',
        'sm_accounting/views/sm_custom_view.xml',
        # 'sm_payroll/views/hr_contracts_view.xml',
        'sm_inventory/views/stock_picking.xml',
        # 'sm_sales/views/sale_order_view.xml',
        'sm_sales/views/sale_invoice_view.xml',
        'sm_settings/package_settings_view.xml',
        'sm_settings/payment_settings_view.xml',
        'sm_settings/login_layout_inherit.xml',
        'sm_accounting/views/sm_account_group_view.xml',
    ],

    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
