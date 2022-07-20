# -*- coding: utf-8 -*-
from odoo import models, fields, api


class InvoiceViettelLine(models.Model):
    _name = "invoice.viettel.line"

    product_id = fields.Many2one("product.product", string="Sản phẩm")
    price_unit = fields.Float(string="Giá")
    quantity = fields.Float("Số lượng")
    name = fields.Char("Tên SP trên HĐĐT")
    invoice_line_tax_ids = fields.Many2one("account.tax", string="Thuế")
    invoice_id = fields.Many2one('invoice.viettel')
    price_total = fields.Integer("Tiền trước thuế", compute="_sub_total")
    price_subtotal = fields.Integer("Tổng tiền", compute="_sub_total")
    uom_id = fields.Many2one('uom.uom', string="Đơn vị")
    invoice_uom_id = fields.Char("ĐVT trên HĐĐT")
    vat_rate = fields.Integer("VAT Rate", compute="_sub_total")
    vat_amount = fields.Integer("VAT Amount", compute="_sub_total")

    @api.depends('product_id', 'quantity', 'invoice_line_tax_ids', 'price_unit')
    def _sub_total(self):
        for rec in self:
            rec.price_total = round(rec.price_unit * rec.quantity)
            rec.vat_rate = int(rec.invoice_line_tax_ids.amount)
            rec.vat_amount = int(rec.price_unit * rec.quantity * rec.invoice_line_tax_ids.amount / 100)
            rec.price_subtotal = rec.price_unit * rec.quantity + rec.vat_amount

    @api.onchange('product_id')
    def onchange_price(self):
        self.price_unit = self.product_id.lst_price
        self.name = self.product_id.name
        self.uom_id = self.product_id.uom_id
        self.invoice_uom_id = self.product_id.uom_id.name
