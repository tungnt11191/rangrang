from odoo import api, fields, models

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    origin_source = fields.Char(compute='_compute_origin_source')

    @api.depends('origin')
    def _compute_origin_source(self):
        for record in self:
            record.origin_source = ''
            if record.origin and record.origin.startswith('WH/MO'):
                mo = self.env['mrp.production'].search([('name', '=', self.origin)], limit=1)
                if mo:
                    record.origin_source = mo.origin

