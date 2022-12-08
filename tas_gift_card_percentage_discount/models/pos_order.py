# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class PosOrder(models.Model):
    _inherit = "pos.order"

    @api.model
    def create_from_ui(self, orders, draft=False):
        order_ids = super(PosOrder, self).create_from_ui(orders, draft)
        for order in self.sudo().browse([o["id"] for o in order_ids]):
            gift_card_config = order.config_id.gift_card_settings
            for line in order.lines:
                if not line.gift_card_id:
                    if gift_card_config == "create_set":
                        new_card = line._create_gift_cards()
                        new_card.partner_id = order.partner_id or False
                        line.generated_gift_card_ids = new_card
                    else:
                        gift_card = self.env["gift.card"].search(
                            [("id", "=", line.generated_gift_card_ids.id)]
                        )
                        gift_card.buy_pos_order_line_id = line.id
                        gift_card.expired_date = fields.Date.add(
                            fields.Date.today(), years=1
                        )
                        gift_card.partner_id = order.partner_id or False

                        if gift_card_config == "scan_set":
                            gift_card.initial_amount = line.price_unit

        return order_ids