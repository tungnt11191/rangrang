# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from collections import defaultdict
from odoo.exceptions import AccessError, UserError, ValidationError


class PosSession(models.Model):
    _inherit = 'pos.session'

    def _prepare_line(self, order_line):
        """ Derive from order_line the order date, income account, amount and taxes information.

        These information will be used in accumulating the amounts for sales and tax lines.
        """

        # region tungnt
        def get_income_account(order_line):
            product = order_line.product_id
            mapping_item = product.order_type_map_ids.filtered(lambda mapping_item: mapping_item.delivery_type.id == order_line.order_id.delivery_type.id)
            if mapping_item:
                income_account = mapping_item.income_account_id
            else:
                income_account = product.with_company(order_line.company_id)._get_product_accounts()['income']
            if not income_account:
                raise UserError(_('Please define income account for this product: "%s" (id:%d).')
                                % (product.name, product.id))
            return order_line.order_id.fiscal_position_id.map_account(income_account)

        # end region
        tax_ids = order_line.tax_ids_after_fiscal_position\
                    .filtered(lambda t: t.company_id.id == order_line.order_id.company_id.id)
        sign = -1 if order_line.qty >= 0 else 1
        price = sign * order_line.price_unit * (1 - (order_line.discount or 0.0) / 100.0)
        # The 'is_refund' parameter is used to compute the tax tags. Ultimately, the tags are part
        # of the key used for summing taxes. Since the POS UI doesn't support the tags, inconsistencies
        # may arise in 'Round Globally'.
        check_refund = lambda x: x.qty * x.price_unit < 0
        is_refund = check_refund(order_line)
        tax_data = tax_ids.with_context(force_sign=sign).compute_all(price_unit=price, quantity=abs(order_line.qty), currency=self.currency_id, is_refund=is_refund)
        taxes = tax_data['taxes']
        # For Cash based taxes, use the account from the repartition line immediately as it has been paid already
        for tax in taxes:
            tax_rep = self.env['account.tax.repartition.line'].browse(tax['tax_repartition_line_id'])
            tax['account_id'] = tax_rep.account_id.id
        date_order = order_line.order_id.date_order
        taxes = [{'date_order': date_order, **tax} for tax in taxes]
        return {
            'date_order': order_line.order_id.date_order,
            'income_account_id': get_income_account(order_line).id,
            'amount': order_line.price_subtotal,
            'taxes': taxes,
            'base_tags': tuple(tax_data['base_tags']),
        }


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
                            old_exp_key = move.product_id._get_product_accounts()['expense']
                            old_out_key = move.product_id.categ_id.property_stock_account_output_categ_id
                            if old_exp_key in stock_expense:
                                stock_expense.pop(old_exp_key)
                            if old_out_key in stock_return:
                                stock_return.pop(old_out_key)
                            if old_out_key in stock_output:
                                stock_output.pop(old_out_key)

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