# Part of odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, api, fields, _, _lt
from odoo.tools.misc import format_date
from dateutil.relativedelta import relativedelta
from itertools import chain
import io
from odoo.tools.misc import xlsxwriter
import pytz
from odoo.exceptions import ValidationError, UserError
import warnings
import logging

_logger = logging.getLogger(__name__)


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.onchange('product_template_id', 'product_uom_qty')
    def _onchange_product_template_id(self):
        if self.product_template_id and self.product_id:
            internal_locations = self.env['stock.location'].search([('usage', '=', 'internal')])

            available_quantity = 0
            for location in internal_locations:
                available_qty = self.env['stock.quant']._get_available_quantity(self.product_id, location, allow_negative=True)
                available_quantity += available_qty

            if self.product_uom_qty > (available_quantity + self.product_template_id.sale_quota):
                raise UserError(_("Quantity greater than quota"))



