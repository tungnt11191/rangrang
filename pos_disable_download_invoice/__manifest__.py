# -*- coding: utf-8 -*-

{
    'name': "POS Disable Download invoice",
    'version': '15.0.1.0.0',
    'summary': """POS Disable Download invoice""",
    'description': """POS Disable Download invoice.""",
    'author': "tung nguyen thanh",
    'company': 'Tasys',
    'category': 'Point of Sale',
    'depends': ['pos_restaurant', 'point_of_sale'],
    'website': 'https://tasys.com.vn',
    'data': [
    ],
    'assets': {
        'web.assets_qweb': [
        ],
        'point_of_sale.assets': [
            'pos_disable_download_invoice/static/src/js/pos.js'
        ]
    },
    'images': ['static/description/banner.png'],
    'license': 'OPL-1',
    'price': 0.00,
    'currency': 'EUR',
    'installable': True,
    'auto_install': False,
    'application': False,
}
