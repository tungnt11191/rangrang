from odoo import fields, models, api, _
# ADDRESS_FIELDS = ('street', 'street2', 'ward_id', 'district_id', 'province_id', 'country_id')


class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'

    province_id = fields.Many2one("res.country.province", string='Province', ondelete='restrict', domain="[('country_id', '=?', country_id)]")
    district_id = fields.Many2one("res.country.state.district", string='District', ondelete='restrict', domain="[('province_id', '=?', province_id)]")
    ward_id = fields.Many2one("res.ward", string='Ward', ondelete='restrict', domain="[('district_id', '=?', district_id)]")
    city = fields.Char(compute='fill_address_city')

    @api.onchange('country_id')
    def onchange_country(self):
        self.province_id = None
        self.district_id = None
        self.ward_id = None

    @api.onchange('province_id')
    def onchange_province(self):
        self.state_id = None
        self.district_id = None
        self.ward_id = None

    @api.onchange('district_id')
    def onchange_district(self):
        self.ward_id = None

    @api.depends('province_id', 'district_id', 'ward_id')
    def fill_address_city(self):
        for rec in self:
            rec.city = str(rec.ward_id.name or '') + ', ' + str(rec.district_id.name or '') + ', ' + str(rec.province_id.name or '')

    # @api.model
    # def _address_fields(self):
    #     """Returns the list of address fields that are synced from the parent."""
    #     return list(ADDRESS_FIELDS)
    #
    # @api.model
    # def _get_default_address_format(self):
    #     return "%(street)s\n%(street2)s\n%(ward_id)s %(district_id)s %(province_id)s\n%(country_name)s"