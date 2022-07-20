# -*- coding: utf-8 -*-

from odoo import tools
from odoo import models, fields, api


class StockMoveView(models.Model):
    _name = "stock.move.view"
    _description = "Stock move view"
    _auto = False
    _rec_name = 'date'
    _order = 'date asc'

    @api.depends('state')
    def _compute_test_computes_field(self):
        for record in self:
            record.test_computes_field = "test"

    stock_move_id = fields.Many2one('stock.move', readonly=True, string="Stock move")
    date = fields.Date(readonly=True, string="Date")
    vn_date = fields.Date(readonly=True, string="VietNam date")
    product_id = fields.Many2one('product.product', readonly=True, string="product_id")
    product_code = fields.Char(readonly=True, string="Ma VT")
    product_name = fields.Char(readonly=True, string="Ten VT")
    uom_name = fields.Char(readonly=True, string="Don vi tinh")
    test_computes_field = fields.Char(readonly=True, string="Test", compute='_compute_test_computes_field')
    picking_id = fields.Many2one('stock.picking', readonly=True, string="Stock picking")
    template_id = fields.Many2one('product.template', readonly=True, string="Product category")
    state = fields.Selection(related='picking_id.state', readonly=False)
    location_id = fields.Many2one('stock.location', readonly=True, string="From")
    location_name = fields.Char(readonly=True, string="From Name")
    location_dest_id = fields.Many2one('stock.location', readonly=True, string="To")
    location_dest_name = fields.Char(readonly=True, string="To Name")
    product_qty = fields.Float(readonly=True, string="Product qty")
    product_uom_qty = fields.Float(readonly=True, string="Product Uom qty")
    picking_type_id = fields.Many2one('stock.picking.type', readonly=True, string="Picking type id")
    picking_type = fields.Selection(related='picking_type_id.code', readonly=False, string="Picking type code")
    # property_cost_method = fields.Selection(related='template_id.property_cost_method', readonly=False, string="Cost method")

    def init(self):
        self.create_procedure_stock_move_by_location_and_date()
        tools.drop_view_if_exists(self.env.cr, self._table)

    def drop_procedure_if_exists(self, procedure_name):
        self.env.cr.execute("DROP FUNCTION IF EXISTS %s" % (procedure_name,))

    def create_procedure_stock_move_by_location_and_date(self):
        self.drop_procedure_if_exists("view_stock_move_by_location_date")
