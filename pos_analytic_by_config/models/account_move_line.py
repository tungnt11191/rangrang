# Copyright 2020 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _post(self, soft=True):
        posted = super(AccountMove, self)._post(soft=soft)

        for invoice in posted:
            if len(invoice.pos_order_ids) > 0:
                pos_config = invoice.pos_order_ids.mapped('config_id')
                print(pos_config)
                for line in invoice.line_ids:
                    print('update analytic_account_id')
                    if line.account_id.enable_default_pos_analytic_account:
                        line.update({"analytic_account_id": pos_config.account_analytic_id.id})
        return posted


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.onchange("product_id")
    def _onchange_product_id(self):
        analytic_account_id = self.analytic_account_id
        res = super()._onchange_product_id()
        if not self.env.context.get("pos_analytic") or not analytic_account_id:
            return res
        # Odoo triggers an onchange on the product_id when creating an invoice.
        # This may cause an incompatibility with product_analytic
        if self.analytic_account_id != analytic_account_id:
            self.analytic_account_id = analytic_account_id
        return res



