{
    'name': 'Warehouse restrict',
    'summary': """Manage access Warehouse and Location follow user""",

    'description': """
       Restrict access Warehouse
    """,
    'author': "TASYS",
    'website': "",
    'category': 'Inventory',
    'version': '1.0',
    'depends': ['stock'],
    'images': [
    ],
    'data': [
        'security/security.xml',
        'views/res_user_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'OEEL-1',
}
