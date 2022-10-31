# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Product(models.Model):
    _inherit = "product.template"

    order_type_map_ids = fields.One2many('product.product.order.type.map', 'product_id', string='Maps')


class ProductProductOrderTypeMap(models.Model):
    _name = "product.product.order.type.map"

    product_id = fields.Many2one('product.product', string="Product", required=True)
    delivery_type = fields.Many2one('delivery.type', string='Order Type', required=True)
    income_account_id = fields.Many2one('account.account', string="Income", required=True)
    expense_account_id = fields.Many2one('account.account', string="Expense", required=True)

    _sql_constraints = [
        ('product_type_unique', 'unique (product_id, delivery_type)', 'The combination product/type already exists!'),
    ]