# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ProductProduct(models.Model):
    _inherit = "product.template"

    vietnamese_name = fields.Char(string="Vietnamese name")
    width = fields.Char(string="Width", digits='Product Unit of Measure')
    high = fields.Char(string="High", digits='Product Unit of Measure')
    onp_ht = fields.Char(string="H/T", digits='Product Unit of Measure')
