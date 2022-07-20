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
        self.env.cr.execute("""CREATE or REPLACE VIEW stock_move_view as (
            select 
                stock_move.id,
                stock_move.id as stock_move_id,
                stock_move.date,
                stock_move.date + INTERVAL '7 HOURS' as vn_date,
                product_product.id as product_id,
                product_template.name as product_name,
                product_product.default_code as product_code,
                product_template.id as template_id,
                -- product_template.property_cost_method,
                uom_uom.name as uom_name,
                stock_move.state,
                stock_move.location_id,
                location_from.name as location_name,
                stock_move.location_dest_id,
                location_to.name as location_dest_name,
                stock_move.product_qty product_qty,
                stock_move.product_uom_qty product_uom_qty,
                stock_move.picking_type_id,
                stock_picking_type.code as picking_type,
                (
                SELECT SUM(ABS(account_move_line.balance))
                    FROM account_move_line
                    INNER JOIN account_move on account_move.id = account_move_line.move_id
                    WHERE account_move_line.stock_move_id = stock_move.id AND account_move.state = 'posted'
                )/2 as total_amount     -- chia 2 vi no = co
            from stock_move
            inner join product_product on product_product.id = stock_move.product_id
            inner join product_template on product_template.id = product_product.product_tmpl_id
            inner join stock_location location_from on location_from.id = stock_move.location_id
            inner join stock_location location_to on location_to.id = stock_move.location_dest_id
            inner join stock_picking_type on stock_picking_type.id = stock_move.picking_type_id
            inner join stock_picking on stock_picking.id = stock_move.picking_id
            left join uom_uom on stock_move.product_uom = uom_uom.id
            where stock_move.state = 'done'
            order by stock_move.date
        )""")

    def drop_procedure_if_exists(self, procedure_name):
        self.env.cr.execute("DROP FUNCTION IF EXISTS %s" % (procedure_name,))

    def create_procedure_stock_move_by_location_and_date(self):
        self.drop_procedure_if_exists("view_stock_move_by_location_date")
        self.env.cr.execute("""
                    CREATE OR REPLACE FUNCTION view_stock_move_by_location_date(
                        from_date date,
                        to_date date,
                        location_ids int[]
                    ) RETURNS TABLE(
                        product_id integer,
                        product_code character varying, 
                        product_name character varying,
                        uom_name character varying, 
                        quantity double precision, 
                        quantity_out double precision, 
                        quantity_in double precision, 
                        quantity_end double precision, 
                        price double precision, 
                        price_out double precision, 
                        price_in double precision, 
                        price_end double precision) 
                    AS $$
                        DECLARE
                            ids INTEGER[];
                        BEGIN
                             RETURN QUERY
                                 SELECT 
                                    --stock_move_view.id, 
                                     stock_move_view.product_id,
                                     stock_move_view.product_code, 
                                     stock_move_view.product_name, 
                                     stock_move_view.uom_name, 
                                    -- stock_move_view.vn_date, 
                                    --  stock_move_view.location_id, 
                                    --  stock_move_view.location_dest_id, 
                                     CAST (SUM (stock_move_view.product_qty) AS DOUBLE PRECISION) quantity,
                                     CAST (
                                        SUM (
                                                CASE
                                                    WHEN stock_move_view.location_id = ANY(location_ids) THEN product_qty
                                                    ELSE 0
                                                END) AS DOUBLE PRECISION
                                        ) quantity_out,
                                     CAST ( 
                                        SUM (
                                            CASE
                                                WHEN stock_move_view.location_dest_id = ANY(location_ids) THEN product_qty
                                                ELSE 0
                                            END) AS DOUBLE PRECISION
                                        ) quantity_in,
                                     CAST ( 
                                        SUM (
                                            CASE
                                                WHEN stock_move_view.location_dest_id = ANY(location_ids) THEN product_qty
                                                ELSE 0
                                            END
                                            -
                                            CASE
                                                WHEN stock_move_view.location_id = ANY(location_ids) THEN product_qty
                                                ELSE 0
                                            END) AS DOUBLE PRECISION
                                        ) quantity_end,
                                     CAST ( SUM (stock_move_view.total_amount) AS DOUBLE PRECISION) price,
                                     CAST ( 
                                        SUM (
                                            CASE
                                                WHEN stock_move_view.location_id = ANY(location_ids) THEN total_amount
                                                ELSE 0
                                            END) AS DOUBLE PRECISION
                                        ) price_out,
                                     CAST (
                                        SUM (
                                            CASE
                                                WHEN stock_move_view.location_dest_id = ANY(location_ids) THEN total_amount
                                                ELSE 0
                                            END) AS DOUBLE PRECISION
                                        ) price_in,
                                    
                                     CAST ( 
                                        SUM (
                                            CASE
                                                WHEN stock_move_view.location_dest_id = ANY(location_ids) THEN total_amount
                                                ELSE 0
                                            END
                                            -
                                            CASE
                                                WHEN stock_move_view.location_id = ANY(location_ids) THEN total_amount
                                                ELSE 0
                                            END) AS DOUBLE PRECISION
                                        ) price_end	
                                     FROM public.stock_move_view
                                     WHERE date(stock_move_view.vn_date) >= from_date 
                                     AND date(stock_move_view.vn_date) <= to_date 
                                     AND ( stock_move_view.location_id = ANY(location_ids) OR stock_move_view.location_dest_id = ANY(location_ids) ) 
                                     GROUP BY
                                     --stock_move_view.id, 
                                     stock_move_view.product_id, 
                                     stock_move_view.product_code, 
                                     stock_move_view.product_name,
                                     stock_move_view.uom_name
                                    -- stock_move_view.vn_date
                                     --  stock_move_view.location_id, 
                                    --  stock_move_view.location_dest_id
                                    ;
                        END;
                    $$ LANGUAGE plpgsql;
        """)