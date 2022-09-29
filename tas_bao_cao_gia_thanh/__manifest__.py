{
    'name': 'Báo cáo giá thành',
    'summary': """Báo cáo giá thành """,

    'description': """
        Báo cáo giá thành
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
        'views/mrp_bom.xml',
        'views/account_budget_view.xml',
        'views/product_cost_report_view.xml',
        'views/cost_driver_view.xml',
        'views/mrp_production.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'OEEL-1',
}
