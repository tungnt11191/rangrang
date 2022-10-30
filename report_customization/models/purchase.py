import n2w
from odoo import api, fields, models

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    x_annex_related = fields.Char('Annex')
    x_contract_related = fields.Char('Contract')
    x_purpose_using = fields.Char('Purpose using')
    x_using_time = fields.Char('Using time')

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

    num_word = fields.Char(string="Amount In Words:", compute='_compute_amount_in_word')

class OrderLine(models.Model):
    _inherit = "purchase.order.line"

    x_remark = fields.Char('Remark')