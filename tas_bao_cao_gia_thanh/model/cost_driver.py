from odoo import fields, models


class TasCostDriver(models.Model):
    _name = "tas.cost.driver"
    _description = " Cost driver "

    name = fields.Char('Name', required=True)
    code = fields.Char('code', required=True)
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure')
    debit_account_id = fields.Many2one('account.account', string="Debit Account")
    credit_account_id = fields.Many2one('account.account', string="Credit Account")
    computation = fields.Selection([('manual', 'Manual Input'),
                                    ('equal_plan', 'Equal Plan'),
                                    ('base_on_some_last_mo', 'Base on 10 last MO')], string='Computation method', default='equal_plan')
    work_center_id = fields.Many2one('mrp.workcenter', string='Work Center')


class TasMrpBomCostDriver(models.Model):
    _name = "tas.mrp.bom.cost.driver"
    _description = "Mrp BOM Cost driver "

    mrp_bom_id = fields.Many2one('mrp.bom', string="BOM")
    cost_driver_id = fields.Many2one('tas.cost.driver', string="Cost driver", required=True)
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure', related='cost_driver_id.uom_id')
    planned_count = fields.Float("Planned Count")
    planned_cost_per_unit = fields.Float("Planned Cost Per Uom Unit")
    actual_count = fields.Float("Actual Count")
    actual_cost_per_unit = fields.Float("Actual Cost Per Uom Unit")
    complete_percentage = fields.Float("Tỷ lệ hoàn thành")