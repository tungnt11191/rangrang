from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    production_cost_line_ids = fields.One2many("tas.mrp.production.cost.line", "mrp_production_id", string="Cost Lines")
    total_other_cost = fields.Float('Other cost')

    def create_account_move(self, cost_line):
        move_ids = self.env['account.move'].create({
            'ref': cost_line.mrp_production_id.name + ' - ' + cost_line.mrp_production_id.product_id.name,
            'line_ids': [
                (0, 0, {
                    'account_id': cost_line.cost_driver_id.debit_account_id.id,
                    'debit': cost_line.planned_cost_of_activity,
                    'name': cost_line.mrp_production_id.name + ' - ' + cost_line.cost_driver_id.name,
                }),
                (0, 0, {
                    'account_id': cost_line.cost_driver_id.credit_account_id.id,
                    'credit': cost_line.planned_cost_of_activity,
                    'name': cost_line.mrp_production_id.name + ' - ' + cost_line.cost_driver_id.name,
                }),
            ]
        })
        move_ids.action_post()

    def button_mark_done(self):

        for order in self:
            total_other_cost = 0
            for cost_line in order.production_cost_line_ids:
                # self.create_account_move(cost_line)
                if cost_line.actual_count == 0 or cost_line.actual_cost_per_uom_unit == 0:
                    raise ValidationError('Please input actual count')
                else:
                    total_other_cost += cost_line.actual_cost_of_activity
            self.total_other_cost = total_other_cost
        res = super(MrpProduction, self).button_mark_done()
        return res

    def action_confirm(self):
        res = super(MrpProduction, self).action_confirm()

        if self.bom_id:
            production_cost_line_ids = []
            for cost_driver in self.bom_id.cost_driver_ids:
                planned_cost_per_bom_unit = cost_driver.planned_cost_per_unit * cost_driver.planned_count

                cost_line_value = {
                    'cost_driver_id': cost_driver.cost_driver_id.id,
                    'uom_id': cost_driver.uom_id.id,
                    'planned_count': cost_driver.planned_count,
                    'planned_cost_per_uom_unit': cost_driver.planned_cost_per_unit,
                    'planned_cost_per_bom_unit': planned_cost_per_bom_unit,
                    'planned_cost_of_activity': planned_cost_per_bom_unit * self.product_qty,
                    'actual_count': cost_driver.planned_count,
                    'complete_percentage': cost_driver.complete_percentage
                }

                if cost_driver.cost_driver_id.computation == 'equal_plan':
                    cost_line_value['actual_count'] = cost_driver.planned_count
                    cost_line_value['actual_cost_per_uom_unit'] = cost_driver.planned_cost_per_unit
                elif cost_driver.cost_driver_id.computation == 'manual':
                    cost_line_value['actual_count'] = 0
                    cost_line_value['actual_cost_per_uom_unit'] = 0
                elif cost_driver.cost_driver_id.computation == 'base_on_some_last_mo':
                    number_of_mo = 10
                    last_mrp_productions = self.env['mrp.production'].search([('product_id', '=', self.product_id.id), ('state', '=', 'done' )], limit=number_of_mo, order='date_planned_start desc')
                    total_actual_count = 0
                    total_actual_cost_per_uom_unit = 0
                    for last_mo in last_mrp_productions:
                        for last_cost_line in last_mo.production_cost_line_ids:
                            if last_cost_line.cost_driver_id.id == cost_driver.cost_driver_id.id:
                                total_actual_count += last_cost_line.actual_count
                                total_actual_cost_per_uom_unit += last_cost_line.actual_cost_per_uom_unit
                    cost_line_value['actual_count'] = total_actual_count/number_of_mo
                    cost_line_value['actual_cost_per_uom_unit'] = total_actual_cost_per_uom_unit/number_of_mo

                production_cost_line_ids.append((0, 0, cost_line_value))

            self.production_cost_line_ids = production_cost_line_ids
        return res

    complete_amount = fields.Float("Complete", compute='_compute_operation_quantity')
    scrap_amount = fields.Float("Scrap", compute='_compute_operation_quantity')
    wip_amount = fields.Float("Wip", compute='_compute_operation_quantity')

    def _compute_operation_quantity(self):
        for record in self:
            stock_picking = self.env['stock.picking'].search(
                [('state', '=', 'done'), ('origin', '=', record.name)])
            stock_move_lines = self.env['stock.move.line'].search(
                [('state', '=', 'done'), ('picking_id', 'in', stock_picking.ids)])

            scrap = 0
            complete = 0
            for line in stock_move_lines:
                if line.move_id.scrapped:
                    scrap += line.qty_done
                elif line.location_id.barcode == 'WH-POSTPRODUCTION' and line.location_dest_id.barcode == 'WH-STOCK':
                    complete += line.qty_done

            record.complete_amount = complete
            record.scrap_amount = scrap
            record.wip_amount = record.product_qty - (record.complete_amount + record.scrap_amount)

    def _cal_price(self, consumed_moves):
        """Set a price unit on the finished move according to `consumed_moves`.
        """
        res = super(MrpProduction, self)._cal_price(consumed_moves)
        work_center_cost = 0
        finished_move = self.move_finished_ids.filtered(lambda x: x.product_id == self.product_id and x.state not in ('done', 'cancel') and x.quantity_done > 0)
        if finished_move:
            finished_move.ensure_one()
            for work_order in self.workorder_ids:
                time_lines = work_order.time_ids.filtered(lambda x: x.date_end and not x.cost_already_recorded)
                duration = sum(time_lines.mapped('duration'))
                work_center_cost += (duration / 60.0) * work_order.workcenter_id.costs_hour
            if finished_move.product_id.cost_method in ('fifo', 'average'):
                qty_done = finished_move.product_uom._compute_quantity(finished_move.quantity_done, finished_move.product_id.uom_id)

                # tungnt: them chi phi khac
                extra_cost = self.extra_cost * qty_done + self.total_other_cost
                # end tungnt: them chi phi khac

                finished_move.price_unit = (sum([-m.stock_valuation_layer_ids.value for m in consumed_moves.sudo()]) + work_center_cost + extra_cost) / qty_done
        return res


class TasMrpBomCostDriver(models.Model):
    _name = "tas.mrp.production.cost.line"
    _description = "Mrp BOM production cost line "

    mrp_production_id = fields.Many2one('mrp.production', string="MO")
    cost_driver_id = fields.Many2one('tas.cost.driver', string="Cost driver", required=True)
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure', related='cost_driver_id.uom_id')
    planned_count = fields.Float("Planned Count")
    planned_cost_per_uom_unit = fields.Float("Planned Cost Per UOM Unit")
    planned_cost_per_bom_unit = fields.Float("Planned Cost Per Bom Unit")
    planned_cost_of_activity = fields.Float("Planned Cost Of Activity")
    actual_count = fields.Float("Actual Count", default=0)
    actual_cost_per_uom_unit = fields.Float("Actual Cost Per Unit", default=0)
    actual_cost_per_bom_unit = fields.Float("Actual Cost Per Bom Unit", compute="_compute_actual_cost", store=True)
    actual_cost_of_activity = fields.Float("Actual Cost Of Activity", compute="_compute_actual_cost", store=True)
    complete_percentage = fields.Float("Tỷ lệ hoàn thành")

    @api.depends('actual_count', 'actual_cost_per_uom_unit', 'mrp_production_id.qty_producing')
    def _compute_actual_cost(self):
        for record in self:
            record.actual_cost_per_bom_unit = record.actual_count * record.actual_cost_per_uom_unit
            record.actual_cost_of_activity = record.actual_cost_per_bom_unit * record.mrp_production_id.qty_producing

    # @api.model
    # def create(self, vals):
    #     self._onchange_actual_count()
    #     rec = super(TasMrpBomCostDriver, self).create(vals)
    #     return rec