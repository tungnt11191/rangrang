# -*- coding: utf-8 -*-

from odoo import api, fields, models


class CountryProvince(models.Model):
    _description = "Country province"
    _name = 'res.country.province'
    _order = 'code'

    country_id = fields.Many2one('res.country', string='State', required=True)
    name = fields.Char(string='Province Name', required=True)
    code = fields.Char(string='Province Code', help='The province code.', required=True)