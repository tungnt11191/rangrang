# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockMove(models.Model):
    _inherit = 'stock.move'

    def get_origin_product_of_bom(self):
        self.ensure_one()
        if self.bom_line_id and self.bom_line_id.bom_id and self.bom_line_id.bom_id.product_id:
            return self.bom_line_id.bom_id.product_id
        return False