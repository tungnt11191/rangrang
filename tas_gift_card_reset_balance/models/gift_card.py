# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
import base64
from datetime import datetime, timedelta
from calendar import monthrange


class GiftCard(models.Model):
    _inherit = "gift.card"

    reset_balance = fields.Boolean(_("Reset balance"), help=_("Reset balance every month"))
    balance = fields.Monetary(store=True)

    def _cron_reset_balance(self):
        first_day_of_month = (datetime.now().replace(day=1)).date()
        today = (datetime.now()).date()

        if first_day_of_month == today:
            cards = self.search([])
            cards._compute_balance()
            # cards = self.search([('reset_balance', '=', True)])
            # for card in cards:
            #     if card.reset_balance:
            #         card.balance = card.initial_amount

    @api.onchange('reset_balance')
    def _onchange_reset_balance(self):
        self._compute_balance()

    def recompute_balance(self):
        for record in self:
            record._compute_balance()

    @api.depends("redeem_pos_order_line_ids", "redeem_line_ids")
    def _compute_balance(self):
        for record in self:
            if not record.reset_balance:
                record._compute_balance()
            else:
                first_day_of_month = (datetime.now().replace(hour=0, minute=0))

                days_in_month = monthrange(first_day_of_month.year, first_day_of_month.month)[1]
                first_day_of_next_month = (datetime.now().replace(hour=0, minute=0)) + timedelta(days=days_in_month)

                # sale order
                confirmed_line = record.redeem_line_ids.filtered(
                    lambda l: l.state in ('sale', 'done')
                                and l.create_date >= first_day_of_month
                                and l.create_date < first_day_of_next_month
                )
                balance = record.initial_amount
                if confirmed_line:
                    balance -= sum(confirmed_line.mapped(
                        lambda line: line.currency_id._convert(line.price_unit, record.currency_id, record.env.company,
                                                               line.create_date) * -1
                    ))
                record.balance = balance

                # pos order
                confirmed_line = record.redeem_pos_order_line_ids.sudo().filtered(
                    lambda l: l.order_id.state in ('paid', 'done', 'invoiced')
                              and l.create_date >= first_day_of_month
                              and l.create_date < first_day_of_next_month
                )
                balance = record.balance
                if confirmed_line:
                    balance -= sum(
                        confirmed_line.mapped(
                            lambda line: line.currency_id._convert(
                                line.price_unit,
                                record.currency_id,
                                record.env.company,
                                line.create_date,
                            )
                            * -1
                        )
                    )
                record.balance = balance