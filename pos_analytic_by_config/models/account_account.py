# Copyright 2015 ACSONE SA/NV
# Copyright 2020 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class AccountAccount(models.Model):
    _inherit = "account.account"

    enable_default_pos_analytic_account = fields.Boolean('Enable Default POS analytic account')
