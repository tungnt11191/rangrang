# -*- coding: utf-8 -*-

from odoo import api, fields, models


class CountryStateDistrict(models.Model):
    _description = "Country state district"
    _name = 'res.country.state.district'
    _order = 'code'

    province_id = fields.Many2one('res.country.province', string='Province', required=True)
    name = fields.Char(string='District Name', required=True)
    code = fields.Char(string='District Code', help='The district code.', required=True)