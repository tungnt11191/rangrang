{
    'name': 'Tas VN Address',
    'summary': """Add district list at Vietnam""",

    'description': """
        Add district list at Vietnam
    """,
    'author': "TASYS",
    'website': "",
    'category': 'tasys',
    'version': '1.0',
    'sequence': 1,
    'depends': ['base', 'contacts'],
    'images': [
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/res_province_views.xml',
        'views/res_district_views.xml',
        'views/res_ward_views.xml',
        'data/province.xml',
        'data/district.xml',
        'data/ward_1.xml',
        'data/ward_2.xml',
        'views/res_partner_inherit_views.xml',
        'views/res_company_inherit_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
