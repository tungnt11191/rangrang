# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import base64

from odoo import fields, api, models


class GiftCard(models.Model):
    _inherit = 'gift.card'

    gift_card_group_id = fields.Many2one('gift.card.group', string='Group')

    def action_sent_gift_card(self):
        selected_ids = self.env.context.get('active_ids', [])
        selected_records = self.env['gift.card'].browse(selected_ids)
        for rec in selected_records:
            mail_template = self.env.ref('sale_gift_card.mail_template_gift_card')
            mail_template.send_mail(rec.id, force_send=True)

