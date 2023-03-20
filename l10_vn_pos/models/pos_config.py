# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import base64

from odoo import fields, api, models


class PosConfig(models.Model):
    _inherit = 'pos.config'
    _order = 'sequence'

    sequence = fields.Integer('Sequence')

