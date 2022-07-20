# Part of odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api


class AccountPaymentTerm(models.Model):
    _inherit = "res.company"

    companyCode = fields.Char('Company Code')

    _sql_constraints = [
        ('unique_companyCode', 'unique (companyCode)', 'Code already exists')
    ]


