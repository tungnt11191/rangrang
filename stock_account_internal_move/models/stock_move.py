# Copyright (C) 2018 by Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models
from odoo.tools import float_round


class StockMove(models.Model):
    _inherit = 'stock.move'

    # @override
    def _action_done(self, cancel_backorder=False):
        """Call _account_entry_move for internal moves as well."""
        res = super(StockMove, self)._action_done(cancel_backorder)
        for move in res:
            # first of all, define if we need to even valuate something
            # if move.product_id.valuation != 'real_time':
            #     continue
            # we're customizing behavior on moves between internal locations
            # only, thus ensuring that we don't clash w/ account moves
            # created in `stock_account`
            if not move._is_internal():
                continue
            if move._is_internal():
                # corrected_value = float_round(
                #     value=move.product_id.standard_price * move.quantity_done,
                #     precision_rounding=move.company_id.currency_id.rounding,
                # )
                #
                # vals = {
                #     'product_id': move.id,
                #     'value': corrected_value,
                #     'unit_cost': 0,
                #     'quantity': 0,
                #     'remaining_qty': 0,
                #     'stock_move_id': move.id,
                #     'company_id': move.company_id.id,
                # }
                # vacuum_svl = self.env['stock.valuation.layer'].sudo().create(vals)
                #
                # vacuum_svl.stock_move_id._account_entry_move(
                #     vacuum_svl.quantity, vacuum_svl.description, vacuum_svl.id, vacuum_svl.value
                # )
                stock_valuation_layers = self.env['stock.valuation.layer']
                stock_valuation_layers |= move._create_in_svl(forced_quantity=abs(move.quantity_done))
                # stock_valuation_layers.stock_move_id._account_entry_move(
                #     stock_valuation_layers.quantity, stock_valuation_layers.description, stock_valuation_layers.id, stock_valuation_layers.value
                # )
        return res

    # # @override
    # def _sanity_check_for_valuation(self):
    #     # Extend `_run_valuation` to make it work on internal moves.
    #     self.ensure_one()
    #     res = super()._sanity_check_for_valuation()
    #     if self._is_internal() and not self.value:
    #         # TODO: recheck if this part respects product valuation method
    #         self.value = float_round(
    #             value=self.product_id.standard_price * self.quantity_done,
    #             precision_rounding=self.company_id.currency_id.rounding,
    #         )
    #     return res

    # @override
    def _account_entry_move(self, qty, description, svl_id, cost):
        self.ensure_one()
        res = super()._account_entry_move(qty, description, svl_id, cost)
        if res is not None and not res:
            # `super()` tends to `return False` as an indicator that no
            # valuation should happen in this case
            return res

        # treated by `super()` as a self w/ negative qty due to this hunk:
        # quantity = self.product_qty or context.get('forced_quantity')
        # quantity = quantity if self._is_in() else -quantity
        # so, self qty is flipped twice and thus preserved
        self = self.with_context(forced_quantity=-self.product_qty)

        location_from = self.location_id
        location_to = self.location_dest_id
        # get valuation accounts for product
        if self._is_internal():
            product_valuation_accounts \
                = self.product_id.product_tmpl_id.get_product_accounts()
            stock_valuation = product_valuation_accounts.get('stock_valuation')
            stock_journal = product_valuation_accounts.get('stock_journal')

            if location_from.force_accounting_entries \
                    and location_to.force_accounting_entries:
                self._create_account_move_line(
                    location_from.valuation_out_account_id.id,
                    location_to.valuation_in_account_id.id,
                    stock_journal.id, qty, description, svl_id, cost)
            elif location_from.force_accounting_entries:
                self._create_account_move_line(
                    location_from.valuation_out_account_id.id,
                    stock_valuation.id,
                    stock_journal.id, qty, description, svl_id, cost)
            elif location_to.force_accounting_entries:
                self._create_account_move_line(
                    stock_valuation.id,
                    location_to.valuation_in_account_id.id,
                    stock_journal.id, qty, description, svl_id, cost)
            else:
                if location_from.auto_create_move_entries and location_to.auto_create_move_entries:
                    self._create_account_move_line(
                        stock_valuation.id,
                        stock_valuation.id,
                        stock_journal.id, qty, description, svl_id, cost)

        return res

    def _is_internal(self):
        self.ensure_one()
        return self.location_id.usage == 'internal' \
            and self.location_dest_id.usage == 'internal'

    def _get_accounting_data_for_valuation(self):
        self.ensure_one()
        journal_id, acc_src, acc_dest, acc_valuation \
            = super()._get_accounting_data_for_valuation()
        # intercept account valuation, use account specified on internal
        # location as a local valuation

        if self._is_in() and self.location_dest_id.force_accounting_entries:
            # (acc_src if not dest.usage == 'customer') => acc_valuation
            acc_valuation \
                = self.location_dest_id.valuation_in_account_id.id
        if self._is_out() and self.location_id.force_accounting_entries:
            # acc_valuation => (acc_dest if not dest.usage == 'supplier')
            acc_valuation \
                = self.location_id.valuation_out_account_id.id
        return journal_id, acc_src, acc_dest, acc_valuation
