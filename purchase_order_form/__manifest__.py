# -*- coding: utf-8 -*-
# Part of Aktiv Software
# See LICENSE file for full copyright & licensing details.

{
    'name': "Purchase Order Form",
    'summary': """Custom Purchase Order""",
    'description': """""",
    'author': "PTSon",
    'category': 'Purchase',
    'depends': [
        'base', 'purchase',
    ],
    'data': [
        'views/purchase_order_form_view.xml',
        'views/res_partner_form_view.xml',
    ],
    'images': [
    ],
    'auto_install': False,
    'installable': True,
    'application': False,
    'license': 'OEEL-1',
}
