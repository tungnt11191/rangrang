# Copyright 2018-2019 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare, float_is_zero

# for fixing performance issue
# class AccountMove(models.Model):
#     _inherit = "account.move"
#
#     @api.model
#     def create(self, data):
#         return super(AccountMove, self.with_context(tracking_disable=True)).create(data)