{
    'name': 'Assets Barcode',
    'version': '2.0',
    'category': 'Manufacturing/Manufacturing',
    'summary': 'Custom Work Center',
    'depends': ['om_account_asset'],
    'data': [
        'report/assets_barcode_report.xml',
        'security/ir.model.access.csv',
        'views/assets_barcode_view.xml',
        'views/assets_type_view.xml',
        ],
    'installable': True,
    'assets': {},
    'license': '',
}
