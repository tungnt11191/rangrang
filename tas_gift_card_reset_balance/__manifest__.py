# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': "Gift Card: reset balance",
    'summary': "Gift Card: reset balance",
    'description': """Gift Card: reset balance.""",
    'category': 'Sales/Sales',
    'version': '1.0',
    'author': 'tungnt',
    'depends': ['gift_card'],
    'auto_install': True,
    'data': [
        'views/gift_card_views.xml',
        'data/gift_card_data.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
        ],
        'web.assets_qweb': [
        ],
    },
    'license': 'LGPL-3',
}
