from odoo import models, api, fields, _, _lt


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def plus_qty(self):
        self.ensure_one()
        self.product_uom_qty += 1

    def minus_qty(self):
        self.ensure_one()
        if self.product_uom_qty > 0:
            self.product_uom_qty -= 1


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def save_record(self):
        return True