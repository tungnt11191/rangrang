import logging
import datetime
import json
import ast
from odoo.http import request
import traceback
import werkzeug.wrappers

_logger = logging.getLogger(__name__)


def default(o):
    if isinstance(o, (datetime.date, datetime.datetime)):
        return o.isoformat()
    if isinstance(o, bytes):
        return str(o)


def valid_response(data, status=200):
    """Valid Response
    This will be return when the http request was successfully processed."""
    data = {"count": len(data) if not isinstance(data, str) else 1, "data": data}
    return werkzeug.wrappers.Response(
        status=status, content_type="application/json; charset=utf-8", response=json.dumps(data, default=default),
    )

def json_response(data=None, message='', status=200):
    return {
        'data': data,
        'errorCode': status,
        'description': message
    }

def invalid_response(typ, message=None, status=401):
    """Invalid Response
    This will be the return value whenever the server runs into an error
    either from the client or the server."""
    # return json.dumps({})
    return werkzeug.wrappers.Response(
        status=status,
        content_type="application/json; charset=utf-8",
        response=json.dumps(
            {"type": typ, "message": str(message) if str(message) else "wrong arguments (missing validation)",},
            default=datetime.datetime.isoformat,
        ),
    )


def extract_arguments(payloads, offset=0, limit=0, order=None):
    """Parse additional data  sent along request."""
    payloads = payloads.get("payload", {})
    fields, domain, payload = [], [], {}

    if payloads.get("domain", None):
        domain = ast.literal_eval(payloads.get("domain"))
    if payloads.get("fields"):
        fields = ast.literal_eval(payloads.get("fields"))
    if payloads.get("offset"):
        offset = int(payloads.get("offset"))
    if payloads.get("limit"):
        limit = int(payloads.get("limit"))
    if payloads.get("order"):
        order = payloads.get("order")
    filters = [domain, fields, offset, limit, order]

    return filters


class SaleOrderLog:

    @staticmethod
    def success(message):
        request.env['sale.order.log'].sudo().create({'name': message, 'log_status': 'success'})

    @staticmethod
    def error(message):
        request.env['sale.order.log'].sudo().create({'name': message, 'log_status': 'error'})

    @staticmethod
    def info(message):
        request.env['sale.order.log'].sudo().create({'name': message, 'log_status': 'info'})


class RevenueRecognizeLog:

    @staticmethod
    def success(message):
        request.env['revenue.recognize.log'].sudo().create({'name': message, 'log_status': 'success'})

    @staticmethod
    def error(message, e=None):
        data = {'name': message, 'log_status': 'error'}
        if e:
            data['traceback'] = traceback.format_exc()
        request.env['revenue.recognize.log'].sudo().create(data)

    @staticmethod
    def info(message):
        request.env['revenue.recognize.log'].sudo().create({'name': message, 'log_status': 'info'})