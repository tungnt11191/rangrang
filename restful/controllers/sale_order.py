# Part of odoo. See LICENSE file for full copyright and licensing details.
import logging
import json
import time

import odoo
import werkzeug.wrappers
from odoo import http
from odoo.http import request
from odoo.addons.restful.common import json_response
from odoo.addons.restful.common import SaleOrderLog
from .main import validate_token

_logger = logging.getLogger(__name__)

expires_in = 'restful.access_token_expires_in'


class SaleOrderController(http.Controller):
    """."""

    @validate_token
    @http.route(['/erpapi/createsalesorder',
                 '/erpapi/createsalesorder/<string:CustomerCode>'],
                methods=["POST"], type='json', auth='none')
    def create_sale_order(self, CustomerCode='', **kwargs):
        logging.info('Call  API create_sale_order with data: '
                     + request.httprequest.get_data().
                     decode(request.httprequest.charset))

        SaleOrderLog.info('Receive API call ')

        if CustomerCode == '':
            info = "Customer Code is empty"
            error = 'invalid_account'
            _logger.error(info)
            # return invalid_response(400, error, info)
            return json_response(message=info, status="ERR_10")

        SaleOrderLog.info('Receive API call: customer code - ' + CustomerCode + ' - data: ' + request.httprequest.get_data().
                     decode(request.httprequest.charset))
        params = json.loads(request.httprequest.get_data().
                            decode(request.httprequest.charset))

        print("Haloooooooooooooooo")
        print(params)
        print("Haloooooooooooooooo")

        values = {
            'SalesOrderUuid': params.get('generalInvoiceInfo').
            get('SalesOrderUuid') if params.get('generalInvoiceInfo').
            get('SalesOrderUuid') else '',
            'date_order': params.get('generalInvoiceInfo').
            get('SalesOrderConfirmDate') if
            params.get('generalInvoiceInfo').
            get('SalesOrderConfirmDate') else '',
            'date_call_api': params.get('generalInvoiceInfo').
            get('SalesOrderConfirmDate') if params.get('generalInvoiceInfo').
            get('SalesOrderConfirmDate') else '',
            'state': 'sale' if params.get('generalInvoiceInfo').get('status')
            == 'confirm' else params.get('generalInvoiceInfo').get('status'),
            'paymentType': (params.get('generalInvoiceInfo').get('paymentType')
                            if params.get('generalInvoiceInfo').
                            get('paymentType') else '').lower(),
            'note': params.get('otherInfo') if params.get('otherInfo') else '',
        }

        if params.get('generalInvoiceInfo'):
            if params.get('generalInvoiceInfo').get('currencyCode'):
                currency = params.get('generalInvoiceInfo').get('currencyCode')
                currency_id = request.env['res.currency'].sudo().search(
                    [('name', '=ilike', currency)])
                if len(currency_id.ids) > 0:
                    values['currency_id'] = currency_id.id
                else:
                    info = "Currency is not valid"
                    error = 'invalid_account'
                    _logger.error(info)
                    SaleOrderLog.error(info)
                    return json_response(message=info, status="ERR_09")

            if params.get('generalInvoiceInfo').get('paymentTermTypeCode'):
                payment_term = params.get('generalInvoiceInfo').\
                    get('paymentTermTypeCode')
                term_id = request.env['account.payment.term'].sudo().search(
                    [('code', '=ilike', payment_term), ])
                if len(term_id.ids) > 0:
                    values['payment_term_id'] = term_id.id
                else:
                    info = "Payment term code is not valid"
                    error = 'invalid_account'
                    _logger.error(info)
                    SaleOrderLog.error(info)
                    return json_response(message=info, status="ERR_08")

        if CustomerCode != '':
            partner = request.env['res.partner'].sudo()\
                .search([('ref', '=ilike', CustomerCode)])
            print(">>>>>>>>>>>>>>>>>>>>")
            print(partner)
            print(">>>>>>>>>>>>>>>>>>>>")
            if len(partner.ids) > 0:
                values['partner_id'] = partner.id
            else:
                info = "Customer code is not valid"
                error = 'invalid_account'
                _logger.error(info)
                SaleOrderLog.error(info)
                return json_response(message=info, status="ERR_07")

        if params.get('buyerInvoiceInfo'):
            print("***********")
        else:
            buyer = partner
            print("xxxxxxxxxxxxxxxxxxxxxxxxxx")

        if params.get('sellerInfo'):
            companyCode = params.get('sellerInfo').get('companyCode')
            company = request.env['res.company'].sudo().search(
                [('companyCode', '=ilike', companyCode)])
            print("??????????????")
            print(company)
            print("??????????????")
            if len(company.ids) > 0:
                values['company_id'] = company.id
            else:
                info = "Company code is not valid"
                _logger.error(info)
                SaleOrderLog.error(info)
                return json_response(message=info, status="ERR_02")

            sellerCode = params.get('sellerInfo').get('sellerCode')
            seller = request.env['res.users'].sudo().search(
                [('sellerCode', '=ilike', sellerCode),
                 ("active", "in", [True, False])], limit=1)
            print("<<<<<<<<<<<<<<<<<<<<<<<<<")
            print(seller)
            print("<<<<<<<<<<<<<<<<<<<<<<<<<")
            if len(seller.ids) > 0:
                values['user_id'] = seller.id
                team = seller.sale_team_id
                values['team_id'] = False
                if team:
                    if team.company_id and team.company_id.id:
                        if len(company.ids) > 0 and company.id == team.company_id.id:
                            values['team_id'] = team.id
                    else:
                        values['team_id'] = team.id

            else:
                info = "Seller code is not valid"
                error = 'invalid_account'
                _logger.error(info)
                SaleOrderLog.error(info)
                return json_response(message=info, status="ERR_01")



            branchCode = params.get('sellerInfo').get('branchCode')
            branch_id = request.env['company.branch'].sudo().search(
                [('code', '=ilike', branchCode)])

            if len(branch_id.ids) == 1:
                values['company_branch_id'] = branch_id.id

        if params.get('buyerInvoiceInfo'):
            values['invoiceStatus'] = str(params.get('buyerInvoiceInfo').
                                          get('invoiceStatus'))
            print("cococococococococococo")
            print(params.get('buyerInvoiceInfo'))
            print("cococococococococococo")
            if params.get('buyerInvoiceInfo').get('buyerTaxCode'):
                buyerTaxCode = params.get('buyerInvoiceInfo').\
                    get('buyerTaxCode')
                buyer = request.env['res.partner'].sudo().\
                    search([('vat', '=ilike', buyerTaxCode),
                            ('active', 'in', [True, False]),
                            ('partner_share', '=', True)], limit=1)

                print("+++++++++++++++++++++++")
                print(len(buyer))
                print("+++++++++++++++++++++++")

                if len(buyer) > 1:
                    info = "More than one Partner has buyerTaxCode"
                    _logger.error(info)
                    SaleOrderLog.error(info)
                    return json_response(message=info, status="ERR_11")

                buyer_values = {
                    'name': params.get('buyerInvoiceInfo').
                    get('buyerLegalName'),
                    'street': params.get('buyerInvoiceInfo').
                    get('buyerAddressLine'),
                    'phone': params.get('buyerInvoiceInfo').
                    get('buyerPhoneNumber'),
                    'email': params.get('buyerInvoiceInfo').get('buyerEmail'),
                    'vat': params.get('buyerInvoiceInfo').get('buyerTaxCode'),
                    'company_type': 'company',
                    'customer_rank': 1
                }
                if len(buyer.ids) == 0:
                    buyer = request.env['res.partner'].sudo().\
                        create(buyer_values)
                    print("buyer info >>>>>>>>>>>>>>>")
                    print(buyer)
                    print("buyer info >>>>>>>>>>>>>>>")
                else:
                    buyer.update(buyer_values)
            else:
                buyer = partner

        items = []
        if params.get('itemInfo'):
            for item in params.get('itemInfo'):
                item_values = {
                    'lineID': item.get('lineID'),
                    'name': item.get('itemInvoiceName'),
                    'price_unit': item.get('unitPriceWithTax'),
                    'product_uom_qty': item.get('quantity'),
                    'price_total': item.get('itemTotalAmountWithTax'),
                    'timeDescription': item.get('timeDescription'),
                    'qty_invoiced': item.get('quantity'),
                    'qty_to_invoice': item.get('quantity')
                }

                if item.get('itemCode'):
                    product_code = item.get('itemCode')
                    product_id = request.env['product.product'].sudo().search(
                        [('default_code', '=ilike', product_code)])
                    print("---------------")
                    print(product_id)
                    print("---------------")
                    if len(product_id.ids) > 0:
                        item_values['product_id'] = product_id.id
                    else:
                        info = "Product code is not valid"
                        _logger.error(info)
                        SaleOrderLog.error(info)
                        return json_response(message=info, status="ERR_03")
                if item.get('unitName'):
                    unit_code = item.get('unitName')
                    unit_id = request.env['uom.uom'].sudo()\
                        .with_context(lang='vi_VN').search([
                            ('name', '=ilike', unit_code)])
                    if len(unit_id.ids) > 0:
                        item_values['product_uom'] = unit_id.id
                    else:
                        info = "Unit of measure is not valid"
                        _logger.error(info)
                        SaleOrderLog.error(info)
                        return json_response(message=info, status="ERR_04")

                if item.get('taxPercentage'):
                    tax_code = item.get('taxPercentage')
                    tax_id = request.env['account.tax'].sudo().search(
                        [('amount', '=', tax_code),
                         ('type_tax_use', '=', 'sale'),
                         ('company_id', '=', company.id)])
                    print("&&&&&&&&&&&&&&")
                    print(tax_id)
                    print("&&&&&&&&&&&&&&")
                    if len(tax_id.ids) > 0:
                        item_values['tax_id'] = [(4, tax_id.id)]

                items.append((0, 0, item_values))

        SalesOrderUuid = params.get('generalInvoiceInfo').get('SalesOrderUuid')
        saleOrder = None
        adjustmentType = params.get('generalInvoiceInfo').get('adjustmentType')
        if adjustmentType == 1:
            saleOrder = request.env['sale.order'].search(
                [('SalesOrderUuid', '=', SalesOrderUuid)])
            if len(saleOrder.ids) > 0:
                info = "Existed Sale Order"
                SaleOrderLog.error(info)
                return json_response(message=info, status="ERR_05")
            else:
                values['order_line'] = items
                print("we are here >>>>>>>>>>>>>")
                print(values)
                print("we are here >>>>>>>>>>>>>")

                def createOrder():
                    saleOrder = request.env['sale.order'].create(values)
                    SaleOrderLog.success("Created sale order "
                                         + saleOrder.name)

                    # have to set Invoicing Policy	Ordered
                    # quantities at product.template
                    saleOrder.action_confirm()
                    saleOrder.update({
                        'date_order': values['date_order'],
                    })
                    SaleOrderLog.success("Confirmed sale order "
                                         + saleOrder.name)
                    moves = saleOrder._create_invoices()
                    moves.update({
                        'partner_id': buyer.id,
                        'date': values['date_order'],
                        'invoice_date': values['date_order'],
                        'so_id': saleOrder.id,
                        'invoice_user_id': saleOrder.user_id.id
                    })
                    for move_line_id in moves.line_ids:
                        move_line_id.partner_id = buyer.id
                    SaleOrderLog.success("Create invoice from sale order " + saleOrder.name)
                    return saleOrder
                try:
                    saleOrder = createOrder()
                except Exception as e:
                    info = "Cannot create order " + e.args[0]
                    _logger.error(info)
                    if 'could not serialize access due to concurrent update' in e.args[0]:
                        # transaction này tạm nghỉ
                        time.sleep(30)
                        _logger.error("Recreate sale order")
                        saleOrder = createOrder()
                    else:
                        SaleOrderLog.error(info)
                        return json_response(message=info, status=400)
        elif adjustmentType == 2:
            saleOrder = request.env['sale.order'].search(
                [('SalesOrderUuid', '=', SalesOrderUuid)])
            if len(saleOrder.ids) > 0 and len(items) > 0:
                try:
                    # if saleOrder.state == "done":
                    saleOrder.sudo().action_unlock()
                    # saleOrder.sudo().with_context({'disable_cancel_warning': True}).action_cancel()
                    saleOrder.sudo().action_draft()
                    # changedItems = saleOrder.find_changed_items(items)
                    order_invoice_lines = saleOrder.invoice_ids
                    saleOrder.order_line.with_context({'force_delete': True}).unlink()
                    values['order_line'] = [(5, 0, 0)] + items
                    saleOrder.update(values)
                    order_invoice_lines.update({
                        'invoice_date': values['date_order'],
                        'date': values['date_order'],
                    })
                    saleOrder.sudo().action_confirm()
                    # update invoice
                    for invoice in order_invoice_lines:
                        # previous_state = invoice.state
                        invoice.button_draft()
                        invoice_lines = [(5, 0, 0)]
                        for order_line in saleOrder.order_line:
                            invoice_line_values = order_line._prepare_invoice_line()
                            # invoice_line_values['quantity'] = order_line.qty_invoiced
                            invoice_lines.append((0, 0, invoice_line_values))
                        invoice.update({'invoice_line_ids': invoice_lines, 'so_id': saleOrder.id})
                        # if previous_state == 'posted':
                        #     invoice.action_post()
                except Exception as e:
                    info = "Cannot update " + e.args[0]
                    _logger.error(info)
                    SaleOrderLog.error(info)
                    return json_response(message=info, status=400)
            else:
                return json_response(message="Cannot found order " + SalesOrderUuid + " Or do not have order line", status=400)

        if saleOrder:
            # Successful response:
            info = ""
            SaleOrderLog.success("Call API success")
            return json_response(message=info, status="")
        else:
            info = "Cannot create sale order"
            _logger.error(info)
            SaleOrderLog.error(info)
            return json_response(message=info, status=400)
