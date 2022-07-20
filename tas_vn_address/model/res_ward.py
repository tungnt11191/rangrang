# -*- coding: utf-8 -*-

from odoo import api, fields, models


class CountryStateDistrictWard(models.Model):
    _description = "Country state district ward"
    _name = 'res.ward'
    _order = 'code'

    district_id = fields.Many2one('res.country.state.district', string='Province', required=True)
    name = fields.Char(string='District Name', required=True)
    code = fields.Char(string='District Code', help='The district code.', required=True)