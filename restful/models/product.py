# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ProductCategory(models.Model):
    _inherit = "product.category"

    revenue_recognition_account_id = fields.Many2one('account.account', string="Revenue Recognition Account", company_dependent=True)
