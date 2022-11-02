# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'TASYS - Point of Sale',
    'author': 'TASYS VN',
    'category': 'Accounting/Localizations/Point of Sale',
    'description': """
TASYS POS Localization
=======================================================
    """,
    'license': 'LGPL-3',
    'depends': ['point_of_sale'],
    'data': [
    ],
    'assets': {
        'web.assets_qweb': [
            'l10_vn_pos/static/src/xml/OrderReceipt.xml',
        ],
        'point_of_sale.assets': [
            'web/static/lib/zxing-library/zxing-library.js',
            'l10_vn_pos/static/src/js/models.js',
        ]
    },
    'auto_install': True,
}
