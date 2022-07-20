# -*- coding: utf-8 -*-

from odoo import models, api, fields

class BmsInventoryValuationLine(models.Model):
    _name = 'bms.inventory.valuation.line'

    inventory_valuation_id = fields.Many2one(comodel_name="bms.inventory.valuation", string="", required=False, )
    quantity = fields.Float("SL đầu ngày")
    price = fields.Float("Giá trị dư đầu ngày")
    quantity_in = fields.Float("SL nhập trong ngày")
    quantity_out = fields.Float("SL xuất trong ngày")
    price_in = fields.Float("Giá trị nhập trong ngày")
    price_out = fields.Float("Giá trị xuất trong ngày")
    product_id = fields.Many2one(comodel_name="product.product", string="Sản phẩm", required=False)
    date = fields.Date("Ngày")
    quantity_end = fields.Float("SL cuối ngày")
    price_end = fields.Float("Giá trị dư cuối ngày")
