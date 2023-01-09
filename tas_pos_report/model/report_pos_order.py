from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError


class PosOrderReport(models.Model):
    _inherit = "report.pos.order"

    delivery_type = fields.Many2one('delivery.type', string='Order Type')
    payment_method = fields.Many2one('pos.payment.method', string='Payment method')
    guest_number = fields.Integer(string='Guest')

    def _select(self):
        select = super(PosOrderReport, self)._select()
        select += ',s.delivery_type AS delivery_type'
        select += ',pos_payment_method.id AS payment_method'
        select += """,CASE
                        WHEN s.partner_id = 1272 THEN 1   -- khach le
                        ELSE 0
                    END AS guest_number
                """
        return select

    def _from(self):
        from_sql = super(PosOrderReport, self)._from()
        from_sql += """LEFT JOIN pos_payment pos_payment ON pos_payment.pos_order_id = (
                        SELECT pos_order_id
                        FROM pos_payment pp 
                        WHERE pp.pos_order_id = s.id
                        LIMIT 1
                    )"""

        from_sql += """LEFT JOIN pos_payment_method pos_payment_method ON pos_payment_method.id = pos_payment.payment_method_id
                    """

        return from_sql

    def _group_by(self):
        group_by = super(PosOrderReport, self)._group_by()
        group_by += ',s.delivery_type'
        group_by += ',payment_method'
        group_by += ',guest_number'
        return group_by