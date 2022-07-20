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


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    onp_bom_type = fields.Selection([
        ('engineering', 'Engineering Bom'),
        ('manufacturing', 'Manufacturing Bom')
    ], string='ONP Type')

    engineering_bom = fields.Many2one('mrp.bom', string="Engineering Bom", domain="[('onp_bom_type', '=', 'engineering')]")
    manufacturing_bom = fields.Many2one('mrp.bom', string="Manufacturing Bom", domain="[('onp_bom_type', '=', 'manufacturing')]")

    effective_date = fields.Date('Effective Date')
    revision = fields.Char('Revision')
    reason = fields.Char('reason')
    pcs_pallet = fields.Float('Pcs/Pallet')
    pallet_cont = fields.Float('Pallet/Cont')
    product_cont = fields.Float('Product/Cont')


class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    sub_quantity = fields.Float(string="Sub quantity", digits='Product Unit of Measure')
    width = fields.Char(string="Width", related='product_id.width', digits='Product Unit of Measure')
    high = fields.Char(string="High", related='product_id.high', digits='Product Unit of Measure')
    onp_ht = fields.Char(string="H/T", related='product_id.onp_ht', digits='Product Unit of Measure')
    qty_per_sheet = fields.Float(string="Qty per sheet", digits='Product Unit of Measure')
    fin_sur = fields.Float(string="Fin.Sur", digits='Product Unit of Measure')
    waste_factor = fields.Float(string="Waste factor", digits='Product Unit of Measure')
