{
    'name': 'Customize POS report',
    'summary': """Customize POS report """,

    'description': """
        Customize POS report
    """,
    'author': "TASYS",
    'website': "",
    'category': 'tasys',
    'version': '1.0',
    'depends': ['mrp', 'mrp_mps', 'account_budget'],
    'images': [
        'static/description/icon.png',
    ],
    'data': [
        'data/data.xml',
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'views/pos_order_report_view.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'OEEL-1',
}
