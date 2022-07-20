# -*- coding: utf-8 -*-
{
    'name': 'Tasys Inventory Management Dashboard',
    'version': '1.0',
    'author': 'Pham Ngoc Thach',
    'category': 'Tasys Inventory Management',
    'website': "http://tasys.vn",
    'summary': """""",
    'depends': ['bms_inventory', 'bms_lab'],
    'data': [
        "security/security.xml",
        "views/templates.xml",
        "views/inventory_management_dashboard_view.xml"
    ],
    'images': [
        'static/description/icon.png',
    ],
    'qweb': [
        # 'static/src/xml/inventory_management_dashboard.xml',
        # 'static/src/xml/value_inventory_management_dashboard.xml',
        'static/src/xml/value_inventory_management_dashboard_tung.xml',
        # 'static/src/xml/in_inventory_management_dashboard.xml',
        # 'static/src/xml/int_inventory_management_dashboard.xml',
        # 'static/src/xml/multi_location_dashboard_inventory.xml',
        # 'static/src/xml/overview_dashboard.xml',
        'static/src/xml/overview_dashboard_tung.xml',
        # 'static/src/xml/bao_cao_hao_hut_tung.xml',
    ],
    'installable': True,
    'auto_install': False,
}
