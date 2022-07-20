{
    'name': 'Nu Sale & Purchase',
    'summary': """Nu Sale Inherit""",

    'description': """
        Nutree sale and purchase
    """,
    'author': "TASYS",
    'website': "",
    'category': 'tasys',
    'version': '1.0',
    'sequence': 1,
    'depends': ['sale_management'],
    'images': [
    ],
    'data': [
        'views/sale_order_inherit_view.xml',
        'views/purchase_order_inherit_view.xml',
        'views/stock_picking_inherit_views.xml',
        # 'views/res_partner_inherit_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
