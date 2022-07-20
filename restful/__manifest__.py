{
    "name": "Odoo RESTFUL API",
    "version": "1.0.0",
    "category": "API",
    "author": "",
    "website": "",
    "summary": "Odoo RESTFUL API",
    "support": "",
    "description": """ RESTFUL API For Odoo
====================
With use of this module user can enable REST API
in any Odoo applications/modules

""",
    "depends": ["base", "web", "sale", "account", "sv_account_revenue"],
    "data": [
        "data/ir_config_param.xml",
        "views/ir_model.xml",
        "views/res_users.xml",
        "views/res_company.xml",
        "views/res_partner.xml",
        "views/sale_order.xml",
        "views/account_move.xml",
        "views/account_payment.xml",
        "views/product_views.xml",
        "views/sale_order_log.xml",
        "views/templates.xml",
        "security/ir.model.access.csv",
    ],

    'qweb': [
        'static/xml/tas_revenue_template.xml',
        'static/xml/tas_revenue_seller.xml',
    ],
    "images": ["static/description/main_screenshot.png"],
    "license": "LGPL-3",
    "installable": True,
    "auto_install": False,
}
