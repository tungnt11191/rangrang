{
    'name': 'Tas mrp',
    'summary': """Tas mrp """,

    'description': """
        Tas mrp
    """,
    'author': "TASYS",
    'website': "",
    'category': 'tasys',
    'version': '1.0',
    'depends': ['mrp', 'mrp_mps'],
    'images': [
        'static/description/icon.png',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'data/data.xml',
        'views/mrp_bom.xml',
        'views/product.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'OEEL-1',
}
