# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
import base64
from datetime import datetime


class GiftCard(models.Model):
    _inherit = "gift.card"

    reset_balance = fields.Boolean(_("Reset balance"), help=_("Reset balance every month"))
    balance = fields.Monetary(store=True)

    def _cron_reset_balance(self):
        first_day_of_month = (datetime.now().replace(day=1)).date()
        today = (datetime.now()).date()

        if first_day_of_month == today:
            cards = self.search([('reset_balance', '=', True)])
            for card in cards:
                if card.reset_balance:
                    card.balance = card.initial_amount
