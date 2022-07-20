# -*- coding: utf-8 -*-
from odoo import api, models
from datetime import datetime


import logging
_logger = logging.getLogger(__name__)


class TasRevenueReport(models.Model):
    _name = 'tas.revenue.report'

    @api.model
    def get_start_datetime(self):
        data = {
            'start_date': datetime.today().replace(day=1).date(),
            'end_date': (datetime.today()).date(),
        }
        return data

    def get_revenue_so(self, so_id):
        revenue_recognize_ids = self.env['revenue.recognize'].sudo().search([
            ('sale_order_id', '=', int(so_id))])
        total_amount = 0
        for revenue_recognize_id in revenue_recognize_ids:
            total_amount += revenue_recognize_id.revenue
        return total_amount

    def get_move_by_so(self, so_id):
        moves = self.env['account.move'].sudo().search([
            ('so_id', '=', int(so_id)), ('journal_id.code', '=', '3387R')])
        total_amount = 0
        for move in moves:
            total_amount += move.amount_total
        return total_amount

    def get_revenue_seller(self, seller_id, start_date, end_date, company_id):
        revenue_recognize_ids = self.env['revenue.recognize'].sudo().\
            search([
                ('seller_id', '=', int(seller_id)),
                ('revenue_date', '>=', start_date),
                ('revenue_date', '<=', end_date),
                ('company_id', '=', int(company_id))
            ])
        total_amount = 0
        for revenue_recognize_id in revenue_recognize_ids:
            total_amount += revenue_recognize_id.revenue
        return total_amount

    @api.model
    def get_revenue_data(self, start_date, end_date):
        result = []
        invoice_ids = self.env['account.move'].sudo().search([
            ('date', '>=', start_date), ('date', '<=', end_date),
            ('company_id', '=', self.env.company.id),
            ('state', '=', 'posted'),
            ('move_type', '=', 'out_invoice'),
            ('payment_state', '!=', 'reversed')
        ], order='date asc')

        print(">>>>>>>>>>>>>>>")
        print(invoice_ids)
        print(">>>>>>>>>>>>>>>")

        for invoice_id in invoice_ids:
            amount_5113 = 0
            if invoice_id.so_id\
                and len(invoice_id.so_id.revenue_recognize_ids.ids) > 0:
                # and (invoice_id.so_id.invoice_status == 'invoiced' \
                #      or invoice_id.so_id.invoice_status == 'sale' \
                #      or invoice_id.so_id.invoice_status == 'done' \
                #      or invoice_id.so_id.invoice_status == 'to invoice') \
                # amount_5113 = self.get_revenue_so(invoice_id.so_id.id)
                amount_5113 = invoice_id.so_id.with_context(start_date=start_date, end_date=end_date).revenue_total

            revenue_has_money = invoice_id.with_context(start_date=start_date, end_date=end_date)._compute_revenue_has_money()

            dataline = {
                "invoice": invoice_id.name,
                "einvoice": invoice_id.vsi_number or 'Chưa Cập Nhật',
                "sale_team": invoice_id.team_id.name or 'Chưa Cập Nhật',
                "seller": invoice_id.invoice_user_id.name,
                "sale_order": invoice_id.so_id.SalesOrderUuid or 'Chưa Cập Nhật',
                "customer_id":  invoice_id.partner_id.ref,
                "customer_name": invoice_id.partner_id.sv_calculated_name,
                "total_3387": invoice_id.amount_untaxed,
                "3387_to_5113": revenue_has_money,
                "5113_total": amount_5113,
                "remainnng_amount": invoice_id.amount_untaxed - amount_5113
            }
            print(dataline)
            result.append(dataline)

        return result

    @api.model
    def get_doanh_so_data(self, start_date, end_date):
        result = []
        seller_ids = self.env['res.users'].sudo().search([
            ('sellerCode', '!=', False), ('active', 'in', [True, False])
        ])

        for seller_id in seller_ids:
            amount_5113 = self.get_revenue_seller(seller_id.id, start_date,
                                                  end_date,
                                                  self.env.user.company_id.id)
            if amount_5113 > 0:
                dataline = {
                    "seller": seller_id.name,
                    "seller_code": seller_id.sellerCode or 'Chưa Cập Nhật',
                    "5113_total": amount_5113,
                }
                print(dataline)
                result.append(dataline)

        return result
