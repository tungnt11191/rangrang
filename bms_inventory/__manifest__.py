# -*- coding: utf-8 -*-
{
    'name': "BMS INVENTORY",
    'summary': """""",
    'description': """ """,
    'author': "Phạm Ngọc Thạch",
    'website': "www.tasys.vn",
    'category': 'TASYS APPS',
    'version': '1.0',
    'depends': ['base', 'account', 'stock'],
    'images': [
        'static/description/icon.png',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/inventory_valuation.xml',
        'views/inventory_valuation_line.xml',
        'views/cronjob_inventory_valuation.xml',
        'views/inventory_valuation_excel.xml',
        'views/bms_inventory_cron_check.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': True,
}
