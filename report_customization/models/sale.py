from vietnam_number import n2w
from odoo import api, fields, models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # @api.multi
    def _compute_amount_in_word(self):
        for rec in self:
            total = rec.amount_total / 10
            rec.num_word = n2w(str(total)).capitalize() + ' đồng.'
            string1 = rec.num_word
            string2 = 'không trăm nghìn không trăm đồng.'
            print(len(string1))
            print(len(string2))
            if string1.endswith(string2, len(string1) - len(string2), len(string1)) is True:
                string1 = string1.rstrip(string2)
                print(string1)
                string1 += ' đồng chẵn.'
                rec.num_word = string1

    num_word = fields.Char('Amount In Words:', compute='_compute_amount_in_word')
    x_delivery_place = fields.Char('Delivery Place')
    x_expected_arrival_date = fields.Datetime('Expected Arrival Date')
    x_internal_so = fields.Char('Internal Sales Order')
    x_method_of_delivery = fields.Char('Method of Delivery')

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    x_po_ref = fields.Char('Customer PO')