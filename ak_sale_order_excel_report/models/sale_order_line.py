from odoo import fields, models, api, _


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    po_ref = fields.Char(string=_('Customer PO'))
    finishing_color = fields.Char(string=_('Finishing Color'))