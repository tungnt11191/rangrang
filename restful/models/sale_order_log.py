# Part of odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _


class SaleOrderLog(models.Model):
    _name = "sale.order.log"
    _description = "Log of sale order"

    name = fields.Char(string='Name')
    log_status = fields.Char(string='Log Status')



