# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import base64

from odoo import fields, api, models


class POSOrder(models.Model):
    _inherit = 'pos.order'

    def _prepare_invoice_vals(self):
        vals = super()._prepare_invoice_vals()
        if self.company_id.country_id.code == 'VN':
            vals.update({'l10n_vn_confirmation_datetime': self.date_order})
        return vals


class POSOrderLine(models.Model):
    _inherit = 'pos.order.line'

    # invoice export
    # price_before_discount = fields.Float('Price before discount', store=True, compute='get_price_before_discount')
    # price_after_discount = fields.Float('Price after discount')
    # discount_per = fields.Float('Discount percentage', store=True, compute='get_discount_percentage')
    # discount_value = fields.Float('Discount')
    # price_discount = fields.Float('Price discount')
    # price_discount_tax = fields.Float('Price discount (incl VAT)')
    # vat_discount_per = fields.Float('VAT discount')
    # vat_discount_value = fields.Float('VAT discount value')
    #
    # @api.depends('price_subtotal')
    # def get_price_before_discount(self):
    #     for rec in self:
    #         rec.price_before_discount = rec.price_subtotal

    gift_card_apply_id = fields.Many2one('gift.card', compute='get_gift_card', store=True)
    session_id = fields.Many2one('pos.session', related='order_id.session_id', store=True)

    @api.depends('gift_card_id')
    def get_gift_card(self):
        for rec in self:
            if rec.gift_card_id:
                for line in rec.order_id.lines:
                    line.gift_card_apply_id = rec.gift_card_id


