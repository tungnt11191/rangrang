# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class GiftCard(models.Model):
    _inherit = "gift.card"

    percentage = fields.Integer(_("Discount per order (Percentage)"), default=100)
    apply_for_pos = fields.Boolean(_("Apply for specific POS"))
    pos_config_ids = fields.Many2many('pos.config', 'pos_config_gift_card_rel', 'gift_card_id', 'pos_config_id')

