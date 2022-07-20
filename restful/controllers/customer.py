# Part of odoo. See LICENSE file for full copyright and licensing details.
import logging
import json
import odoo
import werkzeug.wrappers
from odoo import http
from odoo.http import request
from odoo.addons.restful.common import invalid_response, json_response
from .main import validate_token

_logger = logging.getLogger(__name__)

expires_in = 'restful.access_token_expires_in'


class CustomerController(http.Controller):
    """."""

    @validate_token
    @http.route(['/erpapi/customer'], methods=["POST"],
                type='json', auth='none')
    def create_customer(self, **kwargs):
        logging.info(
            'Call  API create_customer with data: '
            + request.httprequest.get_data().
            decode(request.httprequest.charset))

        params = json.loads(request.httprequest.get_data().
                            decode(request.httprequest.charset))

        print(params)
        adjustmentType = params.get("adjustmentType")

        customerCode = params.get("customerCode")
        customerName = params.get("customerName")
        contactName = params.get("contactName")
        customerEmail = params.get("customerEmail")
        contactPhoneNumber = params.get("contactPhoneNumber")

        values = {
            'name': contactName,
            'customerName': customerName,
            'ref': customerCode,
            'email': customerEmail,
            'mobile': contactPhoneNumber,
        }
        customer = None
        if adjustmentType == 1:
            customer = request.env['res.partner'].search(
                [('ref', '=', customerCode)])
            if len(customer.ids) > 0:
                return json_response(
                    message='Existed Customer code. Try again',
                    status=403)
            else:
                customer = request.env['res.partner'].create(values)
                customer.company_type = 'employer'
                customer.customer_rank: 1
        elif adjustmentType == 2:
            customer = request.env['res.partner'].search(
                [('ref', '=', customerCode)])
            if len(customer.ids) > 0:
                customer.update(values)
                customer.company_type = 'employer'
                customer.customer_rank: 1
            else:
                return json_response(
                    message='Customer code is not found. Try again',
                    status=400)
        print(values)
        if customer:
            # Successful response:
            return json_response(customer.read())
        else:
            info = "Account is not valid"
            error = 'invalid_account'
            _logger.error(info)
            return invalid_response(error, info, 400)

    @validate_token
    @http.route(['/erpapi/checkcustomer/'], methods=["POST"],
                type='json', auth='none')
    def checkcustomer(self, **kwargs):
        logging.info('Call  API checkcustomer with data: ' +
                     request.httprequest.get_data().decode(
                         request.httprequest.charset))

        params = json.loads(request.httprequest.get_data().
                            decode(request.httprequest.charset))
        available_customer = []
        unavailable_customer = []
        for cs_code in params['customerCode']:
            customer = request.env['res.partner'].search(
                [('ref', '=', cs_code)])
            if len(customer) > 0:
                available_customer.append(cs_code)
            else:
                unavailable_customer.append(cs_code)
        return_info = {
            "available_customer": available_customer,
            "unavailable_customer": unavailable_customer
        }
        return json_response(data=return_info, message="", status="")
