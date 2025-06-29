{
    'name': 'Invoice report AR',
    'version': '2.0',
    'category': 'Accounting',
    'summary': 'Arabic and english invoices report',
    'depends': ['l10n_gcc_invoice', 'account'],
    'data': [
        'views/account_invoice_view.xml',
        'report/ksa_invoice_header_footer.xml',
        'report/ksa_delivery_date.xml',
        'report/ksa_invoice_report.xml',
    ],
    'installable': True,
    'assets': {},
    'license': '',
}
