# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class PosConfig(models.Model):
    _inherit = "pos.config"

    percentage = fields.Integer("Discount per order (Percentage)", default=100)
    gift_card_ids = fields.Many2many('gift.card', 'pos_config_gift_card_rel', 'pos_config_id', 'gift_card_id')

