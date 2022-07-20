# Part of odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, api, fields, _, _lt
from odoo.tools.misc import format_date
from dateutil.relativedelta import relativedelta
from itertools import chain
import json
from datetime import datetime


class AccountMove(models.Model):
    _inherit = "account.move"


    def _compute_revenue_has_money(self):
        start_date = self.env.context.get('start_date', False)
        end_date = self.env.context.get('end_date', False)

        invoice = self
        revenue_has_money = 0
        invoice_payments_content = invoice.invoice_payments_widget
        invoice_payments = json.loads(invoice_payments_content)
        if invoice_payments:
            for payment in invoice_payments.get('content'):
                if datetime.strptime(payment.get('date'), '%Y-%m-%d').date() >= datetime.strptime(start_date, '%Y-%m-%d').date() \
                        and datetime.strptime(payment.get('date'), '%Y-%m-%d').date() <= datetime.strptime(end_date, '%Y-%m-%d').date():
                    revenue_has_money += payment.get('amount')
        return revenue_has_money


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    lineID = fields.Integer('Line ID')
    price_without_tax = fields.Float('Giá Trước Thuế', compute="_compute_price_without_tax")
    sv_calculated_name = fields.Char("Tên Kế Toán",
                                     related="partner_id.sv_calculated_name")


    @api.depends('move_id.move_type')
    def _compute_move_type(self):
        for record in self:
            if record.move_id and record.move_id.move_type:
                record.move_type = record.move_id.move_type

    @api.depends('price_unit', 'quantity')
    def _compute_price_without_tax(self):
        for rec in self:
            if len(rec.tax_ids) > 0:
                for tax_id in rec.tax_ids:
                    rec.price_without_tax = rec.price_unit / \
                        (100+tax_id.amount) * 100
            else:
                rec.price_without_tax = rec.price_unit
