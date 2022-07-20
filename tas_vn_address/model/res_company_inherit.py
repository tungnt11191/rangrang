from odoo import fields, models, api, _


class ResCompanyInherit(models.Model):
    _inherit = 'res.company'

    province_id = fields.Many2one("res.country.province", string='Province', ondelete='restrict', domain="[('country_id', '=?', country_id)]")
    district_id = fields.Many2one("res.country.state.district", string='District', ondelete='restrict', domain="[('province_id', '=?', province_id)]")
    ward_id = fields.Many2one("res.ward", string='Ward', ondelete='restrict', domain="[('district_id', '=?', district_id)]")
