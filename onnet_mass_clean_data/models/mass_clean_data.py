from odoo import fields, models, api, _



class MassCleanData(models.TransientModel):
    _name = "mass.clean.data"
    _description = "Mass Clean Data"

    clean_modules = {
        'chk_sales_and_transfers': ['sale_order_line', 'sale.order', 'stock.picking', 'stock.valuation.layer', 'stock.move', 'stock.move.line', 'stock.scrap', 'stock.inventory'],
        # 'stock.picking'
        'chk_purchases_and_transfers': ['purchase_order_line', 'purchase.order', 'stock.picking', 'stock.valuation.layer', 'stock.move', 'stock.move.line', 'stock.scrap', 'stock.inventory'],
        'chk_only_transfer': ['stock.picking', 'stock.valuation.layer', 'stock.valuation.layer', 'stock.move', 'stock.move.line', 'stock.scrap', 'stock.inventory'],
        'chk_invoice_payment_journal': ['account.move.line', 'account.move', 'account.payment'],
        'chk_journal_entries': ['account.move.line', 'account.move'],
        'chk_customers_and_vendors': ['res.partner'],
        'chk_accounting_data': ['account.move.line', 'account.move', 'account.journal', 'account.payment' ],
        'chk_clean_all': ['sale.order', 'purchase.order', 'stock.picking', 'account.move.line', 'account.move',
                          'account.payment', 'res.partner', 'stock.valuation.layer', 'stock.move', 'stock.move.line', 'stock.scrap', 'stock.inventory']
    }

    chk_sales_and_transfers = fields.Boolean(string=_("Sales & All Transfers"), default=False)
    chk_purchases_and_transfers = fields.Boolean(string=_("Purchases & All Transfers"), default=False)
    chk_only_transfer = fields.Boolean(string=_("Only Transfers"), default=False)
    chk_invoice_payment_journal = fields.Boolean(string=_("All Invoicing, Payments & Journal Entries"), default=False)
    chk_journal_entries = fields.Boolean(string=_("Only Journal Entries"), default=False)
    chk_customers_and_vendors = fields.Boolean(string=_("Customers & Vendors"), default=False)
    chk_accounting_data = fields.Boolean(string=_("Chart Of Accounts & All Accounting Data"), default=False)
    chk_clean_all = fields.Boolean(string=_("All Data"), default=False)

    def clean_data(self):
        for attr in dir(self):
            if attr.startswith('chk_'):
                if(self[attr] == True):
                    self._delete_record(attr, self.clean_modules[attr])

    def _delete_record(self,attr, tables):
        for table in tables:
            tbl = table.replace('.', '_')
            domain = []
            if table == 'account.move':
                if attr == 'chk_invoice_payment_journal':
                    domain = [('journal_id', '!=', False),('payment_id', '!=', False)]
                elif attr == 'chk_journal_entries':
                    domain = [('journal_id', '!=', False)]
            elif table == 'res.partner':
                domain = [('create_uid', '!=', '1'), '|', ('customer_rank', '!=' , 0), ('supplier_rank', '!=', 0)]
                ids = self.env[table].search(domain).mapped('id')
                if ids:
                    self.env.cr.execute('delete from sale_order where partner_id = any(array%s)' % ids)
                    self.env.cr.execute('delete from purchase_order where partner_id = any(array%s)' % ids)
            if domain:
                params = self.env[table].search(domain).mapped('id')
                if params:
                    self.env.cr.execute('delete from ' + tbl + ' where id = any(array%s)' % params)
            else:
                self.env.cr.execute('delete from ' + tbl)
