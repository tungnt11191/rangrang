{
    'name': 'Sale quota',
    'summary': """Sale quota """,

    'description': """
        Sale quota
    """,
    'author': "TASYS",
    'website': "",
    'category': 'tasys',
    'version': '1.0',
    'depends': ['sale'],
    'images': [
        'static/description/icon.png',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/product_template.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
