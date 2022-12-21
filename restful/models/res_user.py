
from odoo import fields, models, api


class ResUser(models.Model):
    _inherit = "res.users"

    sellerCode = fields.Char('Seller Code')

    _sql_constraints = [
        ('ta_unique_sellerCode', 'unique (sellerCode)', 'Code already exists')
    ]
