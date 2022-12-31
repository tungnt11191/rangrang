# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
import base64


class GiftCard(models.Model):
    _inherit = "gift.card"

    percentage = fields.Integer(_("Discount per order (Percentage)"), default=100)
    apply_for_pos = fields.Boolean(_("Apply for specific POS"))
    pos_config_ids = fields.Many2many('pos.config', 'pos_config_gift_card_rel', 'gift_card_id', 'pos_config_id')
    gift_card_product_id = fields.Many2one(
        comodel_name='product.product',
        string='Gift Card Product',
        compute='_compute_gift_card_product_id',
        store=True,
        inverse='_inverse_gift_card_product_id'
    )

    def _inverse_revenue_accrual_account(self):
        for record in self:
            test = True

    @api.depends('percentage')
    def _compute_gift_card_product_id(self):
        for record in self:
            if record.percentage < 50:
                record.gift_card_product_id = self.env.ref("gift_card.pay_with_gift_card_product")
            else:
                record.gift_card_product_id = self.env.ref("tas_gift_card_percentage_discount.pay_with_gift_card_product_50_percentage")

    def generate_barcode(self, value, type, **kwargs):
        barcode = self.env['ir.actions.report'].barcode(type, value, **kwargs)
        return base64.encodestring(barcode)