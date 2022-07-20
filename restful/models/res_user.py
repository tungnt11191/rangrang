
from odoo import fields, models, api


class ResUser(models.Model):
    _inherit = "res.users"

    sellerCode = fields.Char('Seller Code')

    @api.model
    @api.depends('name', 'sellerCode')
    def name_get(self):
        res = []
        for record in self:
            if record.sellerCode is not False:
                if record.name is not False:
                    name = record.name + '-' + record.sellerCode
                else:
                    name = record.sellerCode
            else:
                if record.name is not False:
                    name = record.name
                else:
                    name = ""
            res.append((record.id, name))
        return res

    _sql_constraints = [
        ('ta_unique_sellerCode', 'unique (sellerCode)', 'Code already exists')
    ]
