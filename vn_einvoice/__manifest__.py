{
    'name': "E-Invoice",

    'summary': """
            E-Invoice Intergration
        """,

    'description': """
        TASYS
    """,
    "data": [
        'security/ir.model.access.csv',
        # 'security/group.xml',
        'security/ir_rule.xml',
        'data/data.xml',
        'view/invoice_viettel.xml',
        'view/account_move.xml',
    ],
    "license": "LGPL-3",
    "depends": ['base', 'sale', 'account', 'sv_account_revenue', 'nt_sale'],
    'author': "TASYS",
    'category': 'Accounting',
    'version': '1.0.1',
    'installable': True,
}
