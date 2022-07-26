import json
import time
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from time import mktime
import json
from datetime import datetime, timedelta


TYPE_ORDER = [
    ("market", "Market"),
    # ("express", "Express"),
    ("province", "Province"),
    ("normal", "Normal")
]

class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    SalesOrderUuid = fields.Char('SalesOrderUuid', index=True, copy=False)
    type_order = fields.Selection(TYPE_ORDER, string='Type order', default='normal', compute='_compute_type_order')
    # delivery_express = fields.Boolean(string='Express', default=False)
    # readonly_express = fields.Boolean(default=True)
    delivery_time = fields.Float(string='Delivery time', default=8.0)
    delivery_date = fields.Date(default=fields.Date.today(), string='Delivery date')
    paymentType = fields.Selection(
        [('ck', 'Bank transfer'),
         ('tm', 'Cash'),
         ('tm/ck', 'Bank transfer / Cash')], string="Payment Type")
    invoiceStatus = fields.Selection(
        [('0', _(u'Không lấy hóa đơn')), ('1', _(u'Lấy hóa đơn ngay')),
         ('2', _(u'Lấy hóa đơn sau'))], string="Invoice Status")
    company_branch_id = fields.Many2one("company.branch",
                                        string="Company Branch")
    svcustomerName = fields.Char('SV Customer Name', index=True, store=True,
                                 compute="_sv_name")

    @api.depends('partner_id')
    def _sv_name(self):
        for record in self:
            name = record.partner_id.name
            if record.partner_id.company_type == 'employer':
                if record.partner_id.customerName is not False:
                    name = record.partner_id.customerName
            record.svcustomerName = name

    @api.depends('partner_invoice_id', 'commitment_date')
    def _compute_type_order(self):
        for rec in self:
            if rec.partner_invoice_id.province_id.id != self.env.company.province_id.id:
                rec.type_order = 'province'
            else:
                if rec.commitment_date:
                    date = rec.commitment_date - timedelta(hours=17)
                    now = datetime.now()
                    time = date.strftime("%H:%M:%S")
                    begin = now.replace(hour=4, minute=0, second=0).strftime("%H:%M:%S")
                    end = now.replace(hour=6, minute=0, second=0).strftime("%H:%M:%S")
                    print(f"begin: {begin}, commit {time}, end{end}")
                    if time < begin or time > end:
                        rec.type_order = 'normal'
                    else:
                        rec.type_order = 'market'
                else:
                    rec.type_order = 'normal'

    @api.onchange('delivery_time', 'delivery_date')
    def _onchange_delivery_datetime(self):
        if self.delivery_time and self.delivery_date:
            commitment_date = datetime.combine(self.delivery_date, datetime.min.time()) + timedelta(hours=self.delivery_time - 7)
            self.commitment_date = commitment_date

    # @api.depends('partner_shipping_id', 'commitment_date', 'delivery_express')
    # def _compute_type_order(self):
    #     for rec in self:
    #         print(rec.partner_shipping_id.state_id.name)
    #         print("+++++++++++++++++++++")
    #         print(self.env.company.state_id.name)
    #         if rec.partner_shipping_id.state_id.id != self.env.company.state_id.id:
    #             rec.type_order = 'province'
    #             rec.delivery_express = True
    #             rec.readonly_express = True
    #         else:
    #             if rec.commitment_date:
    #                 date = rec.commitment_date - timedelta(hours=17)
    #                 now = datetime.now()
    #                 time = date.strftime("%H:%M:%S")
    #                 begin = now.replace(hour=4, minute=0, second=0).strftime("%H:%M:%S")
    #                 end = now.replace(hour=6, minute=0, second=0).strftime("%H:%M:%S")
    #                 print(f"begin: {begin}, commit {time}, end{end}")
    #                 if time < begin or time > end and rec.delivery_express is True:
    #                     rec.type_order = 'express'
    #                     rec.readonly_express = False
    #                 elif time < begin or time > end and rec.delivery_express is False:
    #                     rec.type_order = 'normal'
    #                     rec.readonly_express = False
    #                 else:
    #                     rec.type_order = 'market'
    #                     rec.readonly_express = True
    #                     rec.delivery_express = False
    #             else:
    #                 rec.delivery_express = False
    #                 rec.readonly_express = False
    #                 rec.type_order = 'normal'


