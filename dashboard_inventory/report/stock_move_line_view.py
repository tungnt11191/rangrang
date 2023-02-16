# -*- coding: utf-8 -*-

from odoo import tools
from odoo import models, fields, api


class StockMoveLineView(models.Model):
    _name = "stock.move.line.view"
    _description = "Stock move line view"
    _auto = False
    _rec_name = 'date'
    _order = 'date asc'

    @api.depends('state')
    def _compute_test_computes_field(self):
        for record in self:
            record.test_computes_field = "test"

    stock_move_id = fields.Many2one('stock.move', readonly=True, string="Stock move")
    date = fields.Datetime(readonly=True, string="Date")
    vn_date = fields.Datetime(readonly=True, string="VietNam date")
    product_id = fields.Many2one('product.product', readonly=True, string="product_id")
    product_code = fields.Char(readonly=True, string="Ma VT")
    product_name = fields.Char(readonly=True, string="Ten VT")
    reference = fields.Char(readonly=True, string="Reference")
    product_uom_id = fields.Many2one('uom.uom', readonly=True, string="Don vi tinh")
    uom_name = fields.Char(readonly=True, string="Don vi tinh")
    test_computes_field = fields.Char(readonly=True, string="Test", compute='_compute_test_computes_field')
    template_id = fields.Many2one('product.template', readonly=True, string="Product category")
    picking_id = fields.Many2one('stock.picking', readonly=True, string="Stock picking")
    state = fields.Selection(related='stock_move_id.state', readonly=False)
    location_id = fields.Many2one('stock.location', readonly=True, string="From")
    location_name = fields.Char(readonly=True, string="From Name")
    location_type = fields.Char(readonly=True, string="Location Type")
    location_dest_id = fields.Many2one('stock.location', readonly=True, string="To")
    location_dest_name = fields.Char(readonly=True, string="To Name")
    location_dest_type = fields.Char(readonly=True, string="Location Dest Type")
    product_qty = fields.Float(readonly=True, string="Product qty")
    picking_type_id = fields.Many2one('stock.picking.type', readonly=True, string="Picking type id")
    picking_type = fields.Selection(related='picking_type_id.code', readonly=False, string="Picking type code")
    # property_cost_method = fields.Selection(related='template_id.property_cost_method', readonly=False, string="Cost method")
    company_id = fields.Many2one('res.company', readonly=True, string="Company", related='stock_move_id.company_id')
    total_amount = fields.Float('Total amount')
    has_manufacture_order = fields.Boolean('Has manufacture order', default=False)
    has_purchase_order = fields.Boolean('Has purchase order', default=False)
    has_sale_order = fields.Boolean('Has sale order', default=False)


    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW stock_move_line_view as (
            select
                stock_move_line.id,
                stock_move_line.id as stock_move_line_id,
                stock_move_line.date as date,
                (stock_move_line.date + INTERVAL '7 HOURS') as vn_date,
                product_product.id as product_id,
                product_template.name as product_name,
                product_product.default_code as product_code,
                product_template.id as template_id,
                stock_move_line.reference as reference,
                stock_picking.id as picking_id,
                stock_move_line.product_uom_id as product_uom_id,
                uom_uom.name as uom_name,
                stock_move_line.state,
                stock_move_line.location_id,
                location_from.name as location_name,
                location_from.usage as location_type,
                stock_move_line.location_dest_id,
                location_to.name as location_dest_name,
                location_to.usage as location_dest_type,
                stock_move_line.qty_done product_qty,
                stock_move_line.picking_type_id,
                stock_picking_type.code as picking_type,
                stock_move.company_id as company_id,
                stock_move.id as stock_move_id,
                CASE
                   WHEN exists (
                      SELECT 1
                      FROM mrp_production
                      INNER JOIN stock_move as stock_move2 ON stock_move2.group_id = mrp_production.procurement_group_id
                      WHERE stock_move2.id = stock_move.id
                   )
                   THEN true
                   ELSE false
                END as has_manufacture_order,
                CASE
                   WHEN exists (
                      SELECT 1
                      FROM purchase_order
                      INNER JOIN stock_move as stock_move2 ON stock_move2.group_id = purchase_order.group_id
                      WHERE stock_move2.id = stock_move.id
                   )
                   THEN true
                   ELSE false
                END as has_purchase_order,
                CASE
                   WHEN exists (
                      SELECT 1
                      FROM sale_order
                      INNER JOIN stock_move as stock_move2 ON stock_move2.group_id = sale_order.procurement_group_id
                      WHERE stock_move2.id = stock_move.id
                   )
                   THEN true
                   ELSE false
                END as has_sale_order,
                (
                SELECT (SUM(ABS(stock_valuation_layer.value)) / SUM(ABS(stock_valuation_layer.quantity)) )
                    FROM stock_valuation_layer
                    WHERE stock_valuation_layer.stock_move_id = stock_move.id
                ) * stock_move_line.qty_done as total_amount,
            uom_uom.id uom_id
            from stock_move_line
            inner join stock_move on stock_move.id = stock_move_line.move_id
            inner join product_product on product_product.id = stock_move_line.product_id
            inner join product_template on product_template.id = product_product.product_tmpl_id
            inner join stock_location location_from on location_from.id = stock_move_line.location_id
            inner join stock_location location_to on location_to.id = stock_move_line.location_dest_id
            left join stock_picking_type on stock_picking_type.id = stock_move_line.picking_type_id
            left join stock_picking on stock_picking.id = stock_move_line.picking_id
            left join uom_uom on stock_move_line.product_uom_id = uom_uom.id
            where stock_move_line.state = 'done'
            and product_template.detailed_type not in ('consu', 'gift') 
            order by stock_move_line.date
        )""")

        self.create_procedure_stock_move_line_by_location_and_date()

    def drop_procedure_if_exists(self, procedure_name):
        self.env.cr.execute("DROP FUNCTION IF EXISTS %s" % (procedure_name,))

    def create_procedure_stock_move_line_by_location_and_date(self):
        self.drop_procedure_if_exists("view_stock_move_line_by_location_date")
        self.env.cr.execute("""
                    CREATE OR REPLACE FUNCTION view_stock_move_line_by_location_date(
                        from_date date,
                        to_date date,
                        _company_id int,
                        location_ids int[]
                    ) RETURNS TABLE(
                        product_id integer,
                        product_code character varying,
                        product_name character varying,
                        uom_name character varying,
                        uom_id integer,
                        quantity double precision,
                        quantity_out double precision,
                        quantity_in double precision,
                        quantity_end double precision,
                        price double precision,
                        price_out double precision,
                        price_in double precision,
                        price_end double precision
                        )
                    AS $$
                        DECLARE
                            ids INTEGER[];
                        BEGIN
                             RETURN QUERY
                                 SELECT
                                     stock_move_line_view.product_id,
                                     stock_move_line_view.product_code,
                                     stock_move_line_view.product_name,
                                     stock_move_line_view.uom_name,
                                     stock_move_line_view.uom_id,
                                     CAST (SUM (stock_move_line_view.product_qty) AS DOUBLE PRECISION) quantity,
                                     CAST (
                                        SUM (
                                                CASE
                                                    WHEN stock_move_line_view.location_id = ANY(location_ids) THEN product_qty
                                                    ELSE 0
                                                END) AS DOUBLE PRECISION
                                        ) quantity_out,
                                     CAST (
                                        SUM (
                                            CASE
                                                WHEN stock_move_line_view.location_dest_id = ANY(location_ids) THEN product_qty
                                                ELSE 0
                                            END) AS DOUBLE PRECISION
                                        ) quantity_in,
                                     CAST (
                                        SUM (
                                            CASE
                                                WHEN stock_move_line_view.location_dest_id = ANY(location_ids) THEN product_qty
                                                ELSE 0
                                            END
                                            -
                                            CASE
                                                WHEN stock_move_line_view.location_id = ANY(location_ids) THEN product_qty
                                                ELSE 0
                                            END) AS DOUBLE PRECISION
                                        ) quantity_end,
                                     CAST (
                                        SUM (
                                            CASE
                                                WHEN stock_move_line_view.total_amount IS NOT NULL THEN total_amount
                                                ELSE 0
                                            END) AS DOUBLE PRECISION) price,
                                     CAST (
                                        SUM (
                                            CASE
                                                WHEN stock_move_line_view.location_id = ANY(location_ids) AND stock_move_line_view.total_amount IS NOT NULL THEN total_amount
                                                ELSE 0
                                            END) AS DOUBLE PRECISION
                                        ) price_out,
                                     CAST (
                                        SUM (
                                            CASE
                                                WHEN stock_move_line_view.location_dest_id = ANY(location_ids) AND stock_move_line_view.total_amount IS NOT NULL THEN total_amount
                                                ELSE 0
                                            END) AS DOUBLE PRECISION
                                        ) price_in,

                                     CAST (
                                        SUM (
                                            CASE
                                                WHEN stock_move_line_view.location_dest_id = ANY(location_ids) AND stock_move_line_view.total_amount IS NOT NULL THEN total_amount
                                                ELSE 0
                                            END
                                            -
                                            CASE
                                                WHEN stock_move_line_view.location_id = ANY(location_ids) AND stock_move_line_view.total_amount IS NOT NULL THEN total_amount
                                                ELSE 0
                                            END) AS DOUBLE PRECISION
                                        ) price_end
                                     FROM public.stock_move_line_view
                                     WHERE date(stock_move_line_view.vn_date) >= from_date
                                     AND date(stock_move_line_view.vn_date) <= to_date
                                     AND ( stock_move_line_view.location_id = ANY(location_ids) OR stock_move_line_view.location_dest_id = ANY(location_ids) )
                                     AND stock_move_line_view.company_id = _company_id
                                     GROUP BY
                                     stock_move_line_view.product_id,
                                     stock_move_line_view.product_code,
                                     stock_move_line_view.product_name,
                                     stock_move_line_view.uom_name,
                                     stock_move_line_view.uom_id
                                    ;
                        END;
                    $$ LANGUAGE plpgsql;
        """)
