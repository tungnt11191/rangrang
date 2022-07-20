# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import timedelta

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class CrossoveredBudgetLines(models.Model):
    _inherit = "crossovered.budget.lines"

    cost_driver_id = fields.Many2one('tas.cost.driver', string="Cost driver")