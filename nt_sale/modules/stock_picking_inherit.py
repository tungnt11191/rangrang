from odoo import fields, models, api, _

TYPE_ORDER = [
    ("market", "Market"),
    ("province", "Province"),
    ("normal", "Normal")
]

class PickingInherit(models.Model):
    _inherit = 'stock.picking'

    type_order = fields.Selection(TYPE_ORDER, string='Type order', compute='_compute_type_order')

    @api.depends('origin')
    def _compute_type_order(self):
        for rec in self:
            rec.type_order = rec.env['sale.order'].search([('name', '=', rec.origin)]).type_order

    @api.onchange('user_id')
    def link_user_pick_and_out(self):
        stock_ids = self.env['stock.picking'].search([('origin', '=', self.origin)])
        for rec in stock_ids:
            rec.user_id = self.user_id.id

