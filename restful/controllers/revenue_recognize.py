# Part of odoo. See LICENSE file for full copyright and licensing details.
import logging
import json
import odoo
import werkzeug.wrappers
from odoo import http
from odoo.http import request
from odoo.addons.restful.common import json_response
from odoo.addons.restful.common import RevenueRecognizeLog
from .main import validate_token

_logger = logging.getLogger(__name__)

expires_in = 'restful.access_token_expires_in'


class RevenueRecognizeController(http.Controller):
    """."""

    @validate_token
    @http.route(['/erpapi/revenue'], methods=["POST"],
                type='json', auth='none')
    def create_revenue(self, **kwargs):
        logging.info('Call  API create_revenue with data: ' +
                     request.httprequest.get_data().
                     decode(request.httprequest.charset))
        print("aaaaaaaaaaaaaa")
        RevenueRecognizeLog.info('Receive API call')

        params = json.loads(request.httprequest.get_data().
                            decode(request.httprequest.charset))

        if params.get('data'):
            revenueRecogizeData = params.get('data')

            print("bbbbbbbbbbbbbbbbbb")
            err01_list = []  # Sale Order Code - idSO was not found
            err02_list = []  # Sale Order Line - idItem was not found
            err03_list = []  # Existed Revenue uID
            err04_list = []  # Missing idSO in data parameter
            err07_list = []  # not found uid when update
            err08_list = []
            # update success but update journal entry fail (notice accountant)
            err09_list = []  # unrecognize update error to Revenue Recognize
            err10_list = []  # khong tao duoc but toan
            err11_list = []  # unrecognize create error
            success = []
            update_success = []

            for revenueData in revenueRecogizeData:
                print("cccccccccccccccccccc")
                adjustmentType = revenueData.get("adjustmentType")
                uid = revenueData.get("uID")
                idSO = revenueData.get("idSO")
                idItem = revenueData.get("idItem")
                idSubItem = revenueData.get("idSubItem")
                revenue = revenueData.get("revenue")
                revenue_date = revenueData.get("revenue_date")
                currencyCode = revenueData.get("currencyCode")

                values = {
                    'name': uid,
                    'idSO': idSO,
                    'idItem': idItem,
                    'idSubItem': idSubItem,
                    'currencyCode': currencyCode,
                    'revenue_date': revenue_date,
                    'revenue': revenue
                }

                if not revenueData.get("idSO")\
                        or revenueData.get("idSO") == '':
                    info = "Missing idSO in data parameter"
                    _logger.error(info)
                    RevenueRecognizeLog.error(info)
                    err04_list.append(uid)
                    continue

                init_so = [
                    'tvn_60000001',
                    'vl24h_60000002',
                    'mw_60000003',
                    'vtn_60000004'
                ]



                saleOrder = request.env['sale.order'].sudo().\
                    search([('SalesOrderUuid', '=ilike', idSO)])
                print("check sooooooooooooooooooooooooooooooooo")
                print(saleOrder)
                print("check sooooooooooooooooooooooooooooooooo")
                if len(saleOrder.ids) > 0:
                    values['sale_order_id'] = saleOrder.id
                    values['company_id'] = saleOrder.company_id.id
                    values['seller_id'] = saleOrder.user_id.id
                else:
                    info = "Sale Order Code - idSO was not found"
                    _logger.error(info)
                    RevenueRecognizeLog.error(info)
                    err01_list.append(uid)
                    print("ffff")
                    continue

                if idSO not in init_so:
                    finded_Item = False
                    for saleOrderLine in saleOrder.order_line:
                        print("solineeeeeeeeeeeeeeeeeeeeee")
                        print(saleOrderLine)
                        print(saleOrderLine.lineID)
                        print("solineeeeeeeeeeeeeeeeeeeeee")
                        if saleOrderLine.lineID == idItem:
                            values['sale_order_line_id'] = saleOrderLine.id
                            values['product_id'] = saleOrderLine.product_id.id
                            finded_Item = True
                            break

                    if not finded_Item:
                        info = "Sale Order Line - idItem was not found"
                        _logger.error(info)
                        RevenueRecognizeLog.error(info)
                        err02_list.append(uid)
                        continue

                else:
                    # xu ly du lieu SO dau ky
                    if len(saleOrder.ids) > 0:
                        values['sale_order_id'] = saleOrder.id
                        values['company_id'] = saleOrder.company_id.id
                        values['seller_id'] = saleOrder.user_id.id

                    print(2)

                print("ddd")
                if adjustmentType == 1:
                    try:
                        currentRevenue = request.env['revenue.recognize'].\
                            search([('name', '=ilike', uid)])
                        if len(currentRevenue.ids) > 0:
                            info = "Existed Revenue uID"
                            RevenueRecognizeLog.error(info)
                            print("99999999")
                            err03_list.append(uid)
                            print("888888888")
                        else:
                            newRevenue = request.env["revenue.recognize"].\
                                create(values)
                            isCreatedAccountMove = newRevenue.\
                                create_journal_entry()

                            if isCreatedAccountMove:
                                RevenueRecognizeLog.success(
                                    "Created account move " + newRevenue.name)
                                success.append(uid)
                                continue
                            else:
                                _logger.error(isCreatedAccountMove)
                                RevenueRecognizeLog.error(isCreatedAccountMove)
                                err10_list.append(uid)
                                continue
                    except Exception as e:
                        info = "Cannot create revenue recognize " + e.args[0]
                        _logger.error(info)
                        RevenueRecognizeLog.error(info, e)
                        err11_list.append(uid)
                        print("3333333333333")
                        continue
                        # return json_response(message=info, status=400)
                elif adjustmentType == 2:
                    currentRevenue = request.env['revenue.recognize'].search(
                        [('name', '=ilike', uid)])
                    print("22222222222222222")
                    if len(currentRevenue.ids) > 0:
                        try:
                            currentRevenue.update(values)
                            isUpdatedAccountMove = currentRevenue.\
                                create_journal_entry()
                            if isUpdatedAccountMove:
                                RevenueRecognizeLog.success(
                                    "Update account move " +
                                    currentRevenue.name)
                                update_success.append(uid)
                                continue
                            else:
                                _logger.error(isUpdatedAccountMove)
                                RevenueRecognizeLog.error(isUpdatedAccountMove)
                                err08_list.append(uid)
                                continue

                            RevenueRecognizeLog.success("Updated revenue " +
                                                        currentRevenue.name)
                        except Exception as e:
                            info = "Cannot update revenue " + e.args[0]
                            _logger.error(info)
                            RevenueRecognizeLog.error(info)
                            err09_list.append(uid)
                            continue
                            # return json_response(message=info, status=400)
                    else:
                        err07_list.append(uid)
                        continue

            print("44444444444444")
            xdata = {
                "ERR_01": err01_list,
                "ERR_02": err02_list,
                "ERR_03": err03_list,
                "ERR_04": err04_list,
                "ERR_07": err07_list,
                "ERR_08": err08_list,
                "ERR_09": err09_list,
                "ERR_10": err10_list,
                "ERR_11": err11_list,
                "create_success": success,
                "update_success": update_success
            }
            print(xdata)
            return json_response(message=xdata, status="")
        else:
            info = "Invalid data information"
            _logger.error(info)
            RevenueRecognizeLog.error(info)
            return json_response(message=info, status="ERR_05")

    @validate_token
    @http.route(['/erpapi/checkrevenue'], methods=["POST"],
                type='json', auth='none')
    def checksaleorder(self, **kwargs):
        logging.info('Call  API checksaleorder with data: ' +
                     request.httprequest.get_data().
                     decode(request.httprequest.charset))
        params = json.loads(request.httprequest.get_data().
                            decode(request.httprequest.charset))

        available_revenue_uid = []
        unavailable_revenue_uid = []
        for revenue_uid in params['uID']:
            revenue_recognize_id = request.env['revenue.recognize'].search(
                [('name', '=', revenue_uid)])
            if len(revenue_recognize_id) > 0:
                available_revenue_uid.append(revenue_uid)
            else:
                unavailable_revenue_uid.append(revenue_uid)
        return_info = {
            "available_revenue_uid": available_revenue_uid,
            "unavailable_revenue_uid": unavailable_revenue_uid
        }
        return json_response(data=return_info, message="", status="")
