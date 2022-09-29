{
    'name': 'Account Report Aged Receivable By Seller',
    'summary': """Account Report Aged Receivable By Seller """,

    'description': """
        Account Report Aged Receivable By Seller
    """,
    'author': "LongDT",
    'website': "https://on.net.vn",
    'category': 'account',
    'version': '1.0',
    'depends': ['account_reports'],
    'images': [
    ],
    'license': 'OEEL-1',
    'data': [
        'security/ir.model.access.csv',
        'views/account_aged_seller.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
