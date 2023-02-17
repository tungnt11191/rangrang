# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import base64

from odoo import fields, api, models


class GiftCardGroup(models.Model):
    _name = 'gift.card.group'

    name = fields.Char('Group name', required=True)

