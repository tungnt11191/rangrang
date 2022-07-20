# Part of odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api


class AccountPaymentTerm(models.Model):
    _inherit = "account.payment.term"

    code = fields.Char('Code')


