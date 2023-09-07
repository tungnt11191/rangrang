# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import base64

from odoo import fields, api, models


class GiftCardGroup(models.Model):
    _name = 'gift.card.group'

    name = fields.Char('Group name', required=True)
    default = fields.Boolean('Default', default=False)

    _sql_constraints = [('name_unique', 'unique(name)', 'Name of group already exists!')]

    @api.constrains('default')
    def _change_default(self):
        if self.default:
            for rec in self.env['gift.card.group'].search([('id', '!=', self.id)]):
                rec.default = False
