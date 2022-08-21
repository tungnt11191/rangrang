from odoo import fields, models, api
import logging
logger = logging.getLogger(__name__)


class TasProductCostReport(models.Model):
    _name = "tas.product.cost.report"
    _description = " Product Cost report "

    name = fields.Char('Name', default="Bao Cao Gia Thanh")
    date_from = fields.Date("From", required=True)
    date_end = fields.Date("End", required=True)
    line_ids = fields.One2many("tas.product.cost.report.line", "report_id", string="Lines")
    budget_id = fields.Many2one('crossovered.budget', string="Budget", required=True)

    @api.onchange('date_from', 'date_end', 'budget_id')
    def onchange_date_budget(self):
        if self.date_from and self.date_end and self.budget_id:
            mrp_productions = self.env['mrp.production'].search([('date_planned_start', '>=', self.date_from), ('date_planned_start', '<=', self.date_end), ('state', 'in', ('progress', 'done'))])

            line_ids = [(5, 0, 0)]
            for mo in mrp_productions:
                line_ids.append((0, 0, {
                    'mrp_production_id': mo.id
                }))
            self.line_ids = line_ids


class TasProductCostReportLine(models.Model):
    _name = "tas.product.cost.report.line"
    _description = " Product Cost report line "

    report_id = fields.Many2one('tas.product.cost.report', string="Report", ondelete='cascade')
    bom_id = fields.Many2one('mrp.bom', string="Bom", related='mrp_production_id.bom_id', store=True)
    mrp_production_id = fields.Many2one('mrp.production', string="Manufacturing Order", required=True)
    total_amount = fields.Float("Total amount", related='mrp_production_id.product_qty', store=True)
    complete_amount = fields.Float("Complete", compute='_compute_operation_quantity', store=True)
    scrap_amount = fields.Float("Scrap", compute='_compute_operation_quantity', store=True)
    wip_amount = fields.Float("Wip", compute='_compute_operation_quantity', store=True)
    cost_of_structure = fields.Float("Cost of structure", compute='_compute_cost_of_structure_operation', store=True)
    cost_of_operation = fields.Float("Cost of operation", compute='_compute_cost_of_structure_operation', store=True)
    activity_ids = fields.One2many("tas.product.cost.report.line.activity", "line_id", string="Lines", compute='_compute_activity_ids', store=True)
    total_cost_of_process = fields.Float("Total cost of process", compute='_total_cost_of_process')
    actual_cost_per_unit = fields.Float("Actual Cost Per Unit")

    @api.depends('activity_ids')
    def _total_cost_of_process(self):
        for record in self:
            total_cost_of_process = record.cost_of_structure
            for activity in record.activity_ids:
                total_cost_of_process += activity.cost_of_activity
            record.total_cost_of_process = total_cost_of_process

    @api.depends('mrp_production_id')
    def _compute_operation_quantity(self):
        for record in self:
            record.mrp_production_id._compute_operation_quantity()
            record.complete_amount = record.mrp_production_id.complete_amount
            record.scrap_amount = record.mrp_production_id.scrap_amount
            record.wip_amount = record.mrp_production_id.wip_amount

    @api.depends('mrp_production_id')
    def _compute_cost_of_structure_operation_bak(self):
        for record in self:
            # include cost of structure and cost of operation
            total_cost = 0
            stock_valuation_layer_ids = record.mrp_production_id.move_finished_ids.stock_valuation_layer_ids
            cost_of_component = 0
            cost_of_operation = 0
            for line in stock_valuation_layer_ids:
                cost_of_component += line.value

            record.cost_of_structure = cost_of_component
            record.cost_of_operation = cost_of_operation

    @api.depends('mrp_production_id')
    def _compute_cost_of_structure_operation(self):
        for record in self:
            lines = self.env['report.mrp_account_enterprise.mrp_cost_structure'].get_lines(record.mrp_production_id)
            cost_of_component = 0
            cost_of_operation = 0
            if len(lines) == 1:
                cost_of_component = lines[0].get('total_cost')
                for operation in lines[0].get('operations'):
                    cost_of_operation += operation[3] * operation[4]

            record.cost_of_structure = cost_of_component
            record.cost_of_operation = cost_of_operation

    @api.depends('mrp_production_id', 'report_id.budget_id')
    def _compute_activity_ids(self):
        cost_driver = {}
        for record in self:
            budget = record.report_id.budget_id
            for budget_line in budget.crossovered_budget_line:
                if budget_line.cost_driver_id:
                    cost_driver[budget_line.cost_driver_id.code] = {
                        'id': budget_line.cost_driver_id.id,
                        'data': [],
                        'cost_of_activity': abs(budget_line.practical_amount),
                        'complete_amount': 0,
                        'complete_unit_amount': 0,
                        'wip_amount': 0,
                        'wip_unit_amount': 0
                    }

            for mo in record.report_id.line_ids:
                for bom_cost_driver in mo.mrp_production_id.production_cost_line_ids:
                    if bom_cost_driver.cost_driver_id.code in cost_driver:
                        cost_driver[bom_cost_driver.cost_driver_id.code]['data'].append(mo.mrp_production_id)
                        cost_driver[bom_cost_driver.cost_driver_id.code]['complete_amount'] += mo.mrp_production_id.complete_amount
                        cost_driver[bom_cost_driver.cost_driver_id.code]['complete_unit_amount'] += (mo.mrp_production_id.complete_amount * bom_cost_driver.actual_count)
                        cost_driver[bom_cost_driver.cost_driver_id.code]['wip_amount'] += mo.mrp_production_id.wip_amount
                        cost_driver[bom_cost_driver.cost_driver_id.code]['wip_unit_amount'] += (mo.mrp_production_id.wip_amount * bom_cost_driver.actual_count)

        for record in self:
            activity_lines = [(5, 0, 0)]
            if record.bom_id:
                # value = (0, 0, {
                #     'activity_type': self.env.ref('tas_bao_cao_gia_thanh.tas_cost_driver_working_hour').id,
                #     'cost_of_activity': record.cost_of_operation,
                #     # 'cost_per_activity': record.cost_of_operation / record.complete_amount,
                #     'cost_per_unit': record.cost_of_operation / record.complete_amount if record.complete_amount > 0 else 0
                # })
                # activity_lines.append(value)
                logger.debug("activity_type 1 " + str(self.env.ref('tas_bao_cao_gia_thanh.tas_cost_driver_nvl').id))
                value = (0, 0, {
                    'activity_type': self.env.ref('tas_bao_cao_gia_thanh.tas_cost_driver_nvl').id,
                    'cost_of_activity': record.cost_of_structure,
                    # 'cost_per_activity': record.cost_of_structure / record.complete_amount,
                    'cost_per_unit': record.cost_of_structure / record.complete_amount if record.complete_amount > 0 else 0
                })
                activity_lines.append(value)

                for bom_cost_driver in record.mrp_production_id.production_cost_line_ids:
                    if bom_cost_driver.cost_driver_id.code in cost_driver:
                        cost_per_uom_unit = (cost_driver[bom_cost_driver.cost_driver_id.code]['cost_of_activity'] / (cost_driver[bom_cost_driver.cost_driver_id.code]['complete_unit_amount'])) if (cost_driver[bom_cost_driver.cost_driver_id.code]['complete_unit_amount']) > 0 else 0
                        cost_per_bom_unit = bom_cost_driver.actual_count * cost_per_uom_unit
                        cost_of_activity = record.complete_amount * bom_cost_driver.actual_count * cost_per_bom_unit
                        # cost_of_activity = record.complete_amount * cost_per_activity
                        logger.debug(
                            "activity_type 2 " + str(cost_driver[bom_cost_driver.cost_driver_id.code]['id']))

                        value = (0, 0, {
                            'activity_type': cost_driver[bom_cost_driver.cost_driver_id.code]['id'],
                            'cost_of_activity': cost_of_activity,
                            # 'cost_per_activity': cost_per_activity,
                            'cost_per_unit': cost_per_bom_unit
                        })
                        activity_lines.append(value)
            record.update({'activity_ids': activity_lines})


class TasProductCostReportLineActivity(models.Model):
    _name = "tas.product.cost.report.line.activity"

    line_id = fields.Many2one('tas.product.cost.report.line', string="Line")
    activity_type = fields.Many2one('tas.cost.driver', string="Cost Driver", required=True)
    cost_of_activity = fields.Float("Cost of activity")
    cost_per_activity = fields.Float("Cost per activity")
    cost_per_unit = fields.Float("Cost per unit")