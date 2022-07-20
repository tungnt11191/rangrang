from odoo import fields, models


class Product(models.Model):
    _inherit = "product.product"

    x_dongia = fields.Char('DonGia')
    x_thanhtien = fields.Char('ThanhTien')
