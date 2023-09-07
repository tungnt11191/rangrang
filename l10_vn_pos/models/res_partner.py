# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import base64

from odoo import fields, api, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    barcode = fields.Char(help="Use a barcode to identify this contact.", copy=False, company_dependent=True)
    gift_card_count = fields.Integer('Gift card count', compute='_compute_num_of_gift_card')

    def _compute_num_of_gift_card(self):
        for rec in self:
            rec.gift_card_count = self.env['gift.card'].search_count([('partner_id', '=', rec.id)])

    def action_view_gift_card(self):
        self.ensure_one()
        return {
            "name": "Gift Card",
            "view_mode": "tree,form",
            "res_model": "gift.card",
            "type": "ir.actions.act_window",
            "domain": [("partner_id", "=", self.id)],
            "context": dict(self._context, create=False),
        }

    @staticmethod
    def get_barcode_customer(phone):
        phone_str = str(phone)
        phone_str = phone_str.replace("+", "")
        phone_str = phone_str.replace(" ", "")
        barcode = 'RRC' + phone_str
        return barcode

    @api.model
    def create(self, vals):
        if vals.get('mobile'):
            vals['barcode'] = self.get_barcode_customer(vals.get('mobile'))
        elif vals.get('phone'):
            vals['barcode'] = self.get_barcode_customer(vals.get('phone'))

        res = super(ResPartner, self).create(vals)
        # Auto create gift card for new customer
        if vals.get('customer_rank'):
            gift_card = {
                'initial_amount': 90000,
                'partner_id': res.id,
            }
            print(gift_card, vals)
            self.env['gift.card'].create(gift_card)
        return res

    def write(self, vals):
        res = super(ResPartner, self).write(vals)
        if vals.get("mobile"):
            self.barcode = self.get_barcode_customer(vals.get('mobile'))
        elif vals.get("phone"):
            self.barcode = self.get_barcode_customer(vals.get('phone'))
        return res


