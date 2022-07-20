from odoo import api, fields, models

class ProductTemplate(models.Model):
    _inherit = "product.template"

    x_purchase_description = fields.Text('Purchase Description')

class ProductUom(models.Model):
    _inherit = "uom.uom"

    x_purchase_name = fields.Char('Purchase UoM')