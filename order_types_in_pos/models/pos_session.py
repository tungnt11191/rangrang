# -*- coding: utf-8 -*-

from odoo import models, fields, api
from collections import defaultdict


class PosSession(models.Model):
    _inherit = 'pos.session'

    def _accumulate_amounts(self, data):
        output_data = super(PosSession, self)._accumulate_amounts(data)

        stock_expense = output_data['stock_expense']
        stock_return = output_data['stock_return']
        stock_output = output_data['stock_output']
        for order in self.order_ids:
            order_is_invoiced = order.is_invoiced
            if not order_is_invoiced:
                if self.company_id.anglo_saxon_accounting and order.picking_ids.ids:
                    # Combine stock lines
                    stock_moves = self.env['stock.move'].sudo().search([
                        ('picking_id', 'in', order.picking_ids.ids),
                        ('company_id.anglo_saxon_accounting', '=', True),
                        ('product_id.categ_id.property_valuation', '=', 'real_time')
                    ])
                    for move in stock_moves:
                        mapping_item = move.product_id.order_type_map_ids.filtered(lambda mapping_item: mapping_item.delivery_type.id == order.delivery_type.id)

                        if mapping_item:
                            exp_key = mapping_item.expense_account_id
                            out_key = mapping_item.income_account_id
                            amount = -sum(move.sudo().stock_valuation_layer_ids.mapped('value'))
                            stock_expense[exp_key] = self._update_amounts(stock_expense[exp_key], {'amount': amount},
                                                                          move.picking_id.date, force_company_currency=True)
                            if move.location_id.usage == 'customer':
                                stock_return[out_key] = self._update_amounts(stock_return[out_key], {'amount': amount},
                                                                             move.picking_id.date, force_company_currency=True)
                            else:
                                stock_output[out_key] = self._update_amounts(stock_output[out_key], {'amount': amount},
                                                                         move.picking_id.date, force_company_currency=True)

        output_data.update({
            'stock_expense': stock_expense,
            'stock_return': stock_return,
            'stock_output': stock_output
        })
        return output_data