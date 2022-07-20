from odoo import fields, models


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    cost_driver_ids = fields.One2many("tas.mrp.bom.cost.driver", "mrp_bom_id", string="Cost driver")