# Copyright 2018-2019 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare, float_is_zero


class StockMove(models.Model):
    _inherit = "stock.move"

    created_purchase_request_line_id = fields.Many2one(
        comodel_name="purchase.request.line",
        string="Created Purchase Request Line",
        ondelete="set null",
        readonly=True,
        copy=False,
        index=True,
    )

    purchase_request_allocation_ids = fields.One2many(
        comodel_name="purchase.request.allocation",
        inverse_name="stock_move_id",
        copy=False,
        string="Purchase Request Allocation",
    )

    purchase_request_ids = fields.One2many(
        comodel_name="purchase.request",
        string="Purchase Requests",
        compute="_compute_purchase_request_ids",
    )

    @api.model
    def _prepare_merge_moves_distinct_fields(self):
        distinct_fields = super(StockMove, self)._prepare_merge_moves_distinct_fields()
        distinct_fields += ["created_purchase_request_line_id"]
        return distinct_fields

    @api.model
    def _prepare_merge_move_sort_method(self, move):
        move.ensure_one()
        keys_sorted = super(StockMove, self)._prepare_merge_move_sort_method(move)
        keys_sorted += [
            move.purchase_line_id.id,
            move.created_purchase_request_line_id.id,
        ]
        return keys_sorted

    def _action_cancel(self):
        for move in self:
            if move.created_purchase_request_line_id:
                try:
                    activity_type_id = self.env.ref("mail.mail_activity_data_todo").id
                except ValueError:
                    activity_type_id = False
                pr_line = move.created_purchase_request_line_id
                self.env["mail.activity"].sudo().create(
                    {
                        "activity_type_id": activity_type_id,
                        "note": _(
                            "A sale/manufacturing order that generated this "
                            "purchase request has been cancelled/deleted. "
                            "Check if an action is needed."
                        ),
                        "user_id": pr_line.product_id.responsible_id.id,
                        "res_id": pr_line.request_id.id,
                        "res_model_id": self.env.ref(
                            "purchase_request.model_purchase_request"
                        ).id,
                    }
                )
        return super(StockMove, self)._action_cancel()

    @api.depends("purchase_request_allocation_ids")
    def _compute_purchase_request_ids(self):
        for rec in self:
            rec.purchase_request_ids = rec.purchase_request_allocation_ids.mapped(
                "purchase_request_id"
            )

    def _merge_moves_fields(self):
        res = super(StockMove, self)._merge_moves_fields()
        res["purchase_request_allocation_ids"] = [
            (4, m.id) for m in self.mapped("purchase_request_allocation_ids")
        ]
        return res

    @api.constrains("company_id")
    def _check_company_purchase_request(self):
        if not self.ids:
            return
        self.env.cr.execute(
            """
            SELECT 1
            FROM purchase_request_allocation pra
            INNER JOIN stock_move sm
               ON sm.id=pra.stock_move_id
            WHERE pra.company_id != sm.company_id
                AND sm.id IN %s
            LIMIT 1
        """,
            (tuple(self.ids),),
        )
        if self.env.cr.fetchone():
            raise ValidationError(
                _(
                    "The company of the purchase request must match with "
                    "that of the location."
                )
            )

    def copy_data(self, default=None):
        if not default:
            default = {}
        if "allocation_ids" not in default:
            default["purchase_request_allocation_ids"] = []
        first_it = True
        for alloc in self.purchase_request_allocation_ids.filtered(
            lambda al: al.requested_product_uom_qty > al.allocated_product_qty
        ):
            qty_done = sum(alloc.stock_move_id.mapped("move_line_ids.qty_done"))
            if first_it:
                qty_left = qty_done
                first_it = False
            if qty_left >= alloc.open_product_qty:
                qty_left = qty_done - alloc.open_product_qty
                continue
            else:
                open_qty = alloc.open_product_qty - qty_left
            default["purchase_request_allocation_ids"].append(
                (
                    0,
                    0,
                    {
                        "purchase_request_line_id": alloc.purchase_request_line_id.id,
                        "requested_product_uom_qty": open_qty,
                    },
                )
            )
        return super(StockMove, self).copy_data(default)

# region fix performance issue when create stock valuation value
# from odoo.addons.stock_account.models.stock_move import StockMove as SecondStockMove
# from odoo.tools import float_is_zero
#
# class ThirdStockMove:
#     def _action_done(self, cancel_backorder=False):
#         valued_moves = {valued_type: self.env['stock.move'] for valued_type in self._get_valued_types()}
#         for move in self:
#             if float_is_zero(move.quantity_done, precision_rounding=move.product_uom.rounding):
#                 continue
#             for valued_type in self._get_valued_types():
#                 if getattr(move, '_is_%s' % valued_type)():
#                     valued_moves[valued_type] |= move
#             valued_moves['in'].product_price_update_before_done()
#             res = super(SecondStockMove, self)._action_done(cancel_backorder=cancel_backorder)
#             return res
# SecondStockMove._action_done = ThirdStockMove._action_done

# from odoo.addons.stock.models.stock_quant import StockQuant as SecondStockQuant
# class ThirdStockQuant:
#     def _apply_inventory(self):
#         move_vals = []
#         if not self.user_has_groups('stock.group_stock_manager'):
#             raise UserError(_('Only a stock manager can validate an inventory adjustment.'))
#         for quant in self:
#             # Create and validate a move so that the quant matches its `inventory_quantity`.
#             compare = float_compare(quant.inventory_diff_quantity, 0, precision_rounding=quant.product_uom_id.rounding)
#             if compare > 0:
#                 move_vals.append(
#                     quant._get_inventory_move_values(quant.inventory_diff_quantity,
#                                                      quant.product_id.with_company(
#                                                          quant.company_id).property_stock_inventory,
#                                                      quant.location_id))
#             elif compare < 0:
#                 move_vals.append(
#                     quant._get_inventory_move_values(-quant.inventory_diff_quantity,
#                                                      quant.location_id,
#                                                      quant.product_id.with_company(
#                                                          quant.company_id).property_stock_inventory,
#                                                      out=True))
#         moves = self.env['stock.move'].with_context(inventory_mode=False).create(move_vals)
#         moves._action_done()
#         self.location_id.write({'last_inventory_date': fields.Date.today()})
#         date_by_location = {loc: loc._get_next_inventory_date() for loc in self.mapped('location_id')}
#         for quant in self:
#             quant.inventory_date = date_by_location[quant.location_id]
#         self.write({'inventory_quantity': 0, 'user_id': False})
#         self.write({'inventory_diff_quantity': 0})
#
# SecondStockQuant._apply_inventory = ThirdStockQuant._apply_inventory

# endregion