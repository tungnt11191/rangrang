# Part of odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    SalesOrderUuid = fields.Char('SalesOrderUuid', index=True, copy=False)
    date_call_api = fields.Date(string="API Call Date")
    paymentType = fields.Selection(
        [('ck', 'Bank transfer'),
         ('tm', 'Cash'),
         ('tm/ck', 'Bank transfer / Cash')], string="Payment Type")
    invoiceStatus = fields.Selection(
        [('0', _(u'Không lấy hóa đơn')), ('1', _(u'Lấy hóa đơn ngay')),
         ('2', _(u'Lấy hóa đơn sau'))], string="Invoice Status")
    company_branch_id = fields.Many2one("company.branch",
                                        string="Company Branch")
    svcustomerName = fields.Char('SV Customer Name', index=True, store=True,
                                 compute="_sv_name")

    @api.depends('partner_id')
    def _sv_name(self):
        for record in self:
            name = record.partner_id.name
            if record.partner_id.company_type == 'employer':
                if record.partner_id.customerName is not False:
                    name = record.partner_id.customerName
            record.svcustomerName = name

    def find_changed_items(self, new_lines):
        self.ensure_one()

        # find deleted line
        delete_items = []
        for line in self.order_line:
            is_existed = False
            for new in new_lines:
                if new[2].get('lineID') == line.lineID:
                    is_existed = True
                    line.update(new[2])

            if not is_existed:
                delete_items.append((3, line.id))

        # find added line
        added_items = []
        for new in new_lines:
            is_existed = False
            for line in self.order_line:
                if new[2].get('lineID') == line.lineID:
                    is_existed = True

            if not is_existed:
                added_items.append(new)

        return delete_items + added_items

    @api.model
    def create(self, vals):
        print("hiiiiiiiiiiiiiiiiiiiiiiiiii")
        print(vals)
        print("hiiiiiiiiiiiiiiiiiiiiiiiiii")
        rec = super(SaleOrder, self).create(vals)
        return rec


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    lineID = fields.Integer('Line ID')
    timeDescription = fields.Char('Time Description')

    def _prepare_invoice_line(self, **optional_values):
        optional_values['lineID'] = self.lineID
        return super(SaleOrderLine, self).\
            _prepare_invoice_line(**optional_values)

    def _check_line_unlink(self):
        """
        Extend the allowed deletion policy of SO lines.

        Lines that are delivery lines can be deleted from a confirmed order.

        :rtype: recordset sale.order.line
        :returns: set of lines that cannot be deleted
        """

        undeletable_lines = super()._check_line_unlink()
        force_delete = self.env.context.get('force_delete', False)
        if force_delete:
            return False
        else:
            return undeletable_lines
