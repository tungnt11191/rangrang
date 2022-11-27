# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': "Gift Card: percentage discount",
    'summary': "Gift Card: percentage discount",
    'description': """Gift Card: percentage discount.""",
    'category': 'Sales/Sales',
    'version': '1.0',
    'author': 'tungnt',
    'depends': ['gift_card', 'pos_gift_card'],
    'auto_install': True,
    'data': [
        'views/gift_card_views.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            # 'pos_gift_card/static/src/css/giftCard.css',
            'tas_gift_card_percentage_discount/static/src/js/GiftCardPopup.js',
            # 'pos_gift_card/static/src/js/GiftCardButton.js',
            # 'pos_gift_card/static/src/js/GiftCardPopup.js',
            # 'pos_gift_card/static/src/js/PaymentScreen.js',
        ],
        'web.assets_qweb': [
            # 'pos_gift_card/static/src/xml/**/*',
        ],
    },
    'license': 'LGPL-3',
}
