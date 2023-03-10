# -*- coding: utf-8 -*-
from odoo import api, fields, models
from datetime import date, timedelta, datetime
import pytz

import logging
_logger = logging.getLogger(__name__)


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    picking_type_id = fields.Many2one('stock.picking.type', related='picking_id.picking_type_id', string="Picking type", store=True)