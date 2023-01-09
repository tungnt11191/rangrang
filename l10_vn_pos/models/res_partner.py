# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import base64

from odoo import fields, api, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    barcode = fields.Char(help="Use a barcode to identify this contact.", copy=False, company_dependent=True)

    @api.model
    def create(self, vals):
        if vals.get('mobile'):
            vals['barcode'] = 'RRC' + vals.get("mobile")
        res = super(ResPartner, self).create(vals)
        return res

    def write(self, vals):
        res = super(ResPartner, self).write(vals)
        if vals.get("mobile"):
            self.barcode = 'RRC' + vals.get("mobile")
        return res


