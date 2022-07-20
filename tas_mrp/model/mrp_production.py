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


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def unlink(self):
        if self.env.user.login == 'delete_mo':
            for record in self:
                workorders_to_delete = record.workorder_ids
                if workorders_to_delete:
                    workorders_to_delete.unlink()
            return models.Model.unlink(self)
        else:
            return super(MrpProduction, self).unlink()
