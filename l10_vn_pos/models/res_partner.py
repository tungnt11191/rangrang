# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import base64

from odoo import fields, api, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    barcode = fields.Char(help="Use a barcode to identify this contact.", copy=False, company_dependent=True)

    @staticmethod
    def get_barcode_customer(phone):
        phone_str = str(phone)
        phone_str = phone_str.replace("+", "")
        phone_str = phone_str.replace(" ", "")
        barcode = 'RRC' + phone_str
        return barcode

    @api.model
    def create(self, vals):
        if vals.get('mobile'):
            vals['barcode'] = self.get_barcode_customer(vals.get('mobile'))
        elif vals.get('phone'):
            vals['barcode'] = self.get_barcode_customer(vals.get('phone'))
        res = super(ResPartner, self).create(vals)
        return res

    def write(self, vals):
        res = super(ResPartner, self).write(vals)
        if vals.get("mobile"):
            self.barcode = self.get_barcode_customer(vals.get('mobile'))
        elif vals.get("phone"):
            self.barcode = self.get_barcode_customer(vals.get('phone'))
        return res


