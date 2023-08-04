# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PosOrder(models.Model):
    _inherit = 'pos.order'

    delivery_type = fields.Many2one('delivery.type', string='Order Type')

    @api.model
    def _order_fields(self, ui_order):
        order_fields = super(PosOrder, self)._order_fields(ui_order)
        order_fields['delivery_type'] = ui_order.get('delivery_type', False)
        return order_fields

    @api.model
    def create_from_ui(self, orders, draft=False):
        order_ids = super(PosOrder, self).create_from_ui(orders, draft)
        for order in self.sudo().browse([o['id'] for o in order_ids]):
            print(order)
        return order_ids


class DeliveryMethods(models.Model):
    _inherit = 'pos.config'

    @api.model
    def default_get(self, default_fields):
        res = super(DeliveryMethods, self).default_get(default_fields)
        location_ids = self.env['delivery.type'].sudo().search([])
        res.update({
            'delivery_methods': location_ids,
        })
        return res

    enable_delivery = fields.Boolean(string='Enable Order Types', default=True)
    delivery_methods = fields.Many2many('delivery.type', string='Order Types')
    default_order_type_id = fields.Many2one('delivery.type', string='Default Order Types')


class DeliveryTypes(models.Model):
    _name = 'delivery.type'

    name = fields.Char('Order Type')
    active = fields.Boolean(string='active', default=True)
