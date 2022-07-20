# -*- coding: utf-8 -*-
import time

import requests
from datetime import datetime
from num2words import num2words
from dicttoxml import dicttoxml
from bs4 import BeautifulSoup

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class InvoiceViettel(models.Model):
    _name = "invoice.viettel"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char("Số Hóa Đơn", default="New")
    vsi_status = fields.Selection([
        ('draft', 'Đã Tạo Dự Thảo'),
        ('creating', 'Đang Phát Hành'),
        ('created', 'Đã Phát Hành'),
        ('canceled', 'Đã Hủy'),
    ], string=u'Trạng thái HĐĐT', default='draft', copy=False, tracking=True)
    date_invoice = fields.Date("Ngày hoá đơn")
    payment_term_id = fields.Many2one('account.payment.term')
    partner_id = fields.Many2one("res.partner", string="Tên doanh nghiệp")
    reference = fields.Char()
    company_id = fields.Many2one('res.company', string="Công ty",
                                 default=lambda self: self.env.user.company_id)
    company_branch_id = fields.Many2one('company.branch', string="Chi nhánh")
    currency_id = fields.Many2one('res.currency')
    journal_id = fields.Many2one('account.journal')
    invoice_line_ids = fields.One2many(
        'invoice.viettel.line', 'invoice_id', string="Sản phẩm")

    amount_tax = fields.Integer("Tiền thuế")
    amount_total = fields.Integer("Tiền sau thuế")
    residual = fields.Integer("Tổng tiền")
    access_token = fields.Char("Token")
    user_id = fields.Many2one('res.users')
    buyerName = fields.Char('Người mua hàng')

    account_move_ids = fields.Many2many(
        "account.move", string="Hoá đơn nội bộ")

    tax_company = fields.Char(
        "Mã số thuế", related="company_branch_id.vsi_tin")
    street_company = fields.Char(
        "Địa chỉ công ty", related="company_id.street")
    VAT = fields.Char("VAT", related="partner_id.vat")
    street_partner = fields.Char("Địa chỉ ", related="partner_id.street")
    email_partner = fields.Char("Email ", related="partner_id.email")
    phone_partner = fields.Char("Điện thoại ", related="partner_id.phone")
    vsi_tin = fields.Char("Loại Hóa Đơn	", related="company_branch_id.vsi_tin")
    vsi_template = fields.Char(
        "Mẫu Hóa Đơn	 ", related="company_branch_id.vsi_template")
    vsi_series = fields.Char(
        "Ký hiệu hóa đơn	 ", related="company_branch_id.vsi_series")
    additionalReferenceDesc = fields.Char("Văn bản thoả thuận")
    additionalReferenceDate = fields.Datetime("Ngày thỏa thuận")
    invoiceStatus = fields.Selection(
        [('0', _(u'Không lấy hóa đơn')), ('1', _(u'Lấy hóa đơn ngay')),
         ('2', _(u'Lấy hóa đơn sau'))], string="Invoice Status")
    origin_invoice = fields.Many2one(
        "invoice.viettel", "Hóa đơn cần điều chỉnh")
    is_adjustment_invoice = fields.Boolean(string="Hóa đơn điều chỉnh")
    adjustment_type = fields.Selection(
        [('2', _('Điều chỉnh tăng')),
         ('3', _('Điều chỉnh giảm')),
         ('4', ('Điều chỉnh thông tin'))],
        string="Loại chỉnh sửa")
    fkey = fields.Char("Mã Kỹ Thuật")
    pdf_file = fields.Many2one("ir.attachment", "File Hóa Đơn PDF")

    # Các trường này trên Invoice Viettel
    invoiceId = fields.Char("Viettel InvoiceID")
    invoiceType = fields.Char('invoiceType')
    adjustmentType = fields.Char('adjustmentType')

    total = fields.Char('total')
    issueDate = fields.Char('issueDate')
    issueDateStr = fields.Char('issueDateStr')
    requestDate = fields.Char('requestDate')
    description = fields.Char('description')
    buyerCode = fields.Char('buyerCode')
    paymentStatus = fields.Char('paymentStatus')
    viewStatus = fields.Char('viewStatus')
    exchangeStatus = fields.Char('exchangeStatus')
    numOfExchange = fields.Char('numOfExchange')
    createTime = fields.Char('createTime')
    contractId = fields.Char('contractId')
    contractNo = fields.Char('contractNo')
    totalBeforeTax = fields.Char('totalBeforeTax')
    taxRate = fields.Char('taxRate')
    paymentMethod = fields.Char('paymentMethod')
    taxAmount = fields.Char('taxAmount')
    paymentTime = fields.Char('paymentTime')

    paymentStatusName = fields.Char('paymentStatusName')
    grossvalue = fields.Float(string="Tổng tiền trước thuế")
    grossvalue0 = fields.Float(string="Tổng tiền không thuế 0")
    grossvalue5 = fields.Float(string="Tổng tiền không thuế 5")
    grossvalue10 = fields.Float(string="Tổng tiền không thuế 10")
    vatamount5 = fields.Float(string="Tổng tiền thuế 5")
    amount_untaxed = fields.Integer("Tiền trước thuế")
    vatamount10 = fields.Float(string="Tổng tiền thuế 10")
    amountinwords = fields.Char(string="Tiền bằng chữ",
                                compute="_sub_amount_total")
    svcustomerName = fields.Char('Tên xuất hóa đơn',
                                 index=True, store=True, compute="_sv_name")
    paymentType = fields.Selection(
        [('ck', 'CK'),
         ('tm', 'TM'),
         ('tm/ck', 'TM/CK')],
        string="Hình thức thanh toán", default='tm/ck')

    @ api.onchange('invoice_line_ids')
    def _sub_total(self):
        for rec in self:
            tax = 0
            tax5 = 0
            tax10 = 0
            gross5 = 0
            gross10 = 0
            amount_untaxed = 0
            for line in rec.invoice_line_ids:
                amount_untaxed += line.price_total
                tax += line.vat_amount
                if line.vat_rate == 5:
                    tax5 += line.vat_amount
                    gross5 += line.price_total
                if line.vat_rate == 10:
                    tax10 += line.vat_amount
                    gross10 += line.price_total

            rec.amount_untaxed = amount_untaxed
            rec.amount_tax = rec.amount_total - rec.amount_untaxed
            rec.grossvalue5 = gross5
            rec.grossvalue10 = gross10
            rec.vatamount5 = tax5
            rec.vatamount10 = tax10

    @ api.depends('amount_total')
    def _sub_amount_total(self):
        for rec in self:
            rec.amount_total = rec.amount_tax + rec.amount_untaxed
            try:
                rec.amountinwords = num2words(
                    int(rec.amount_total), lang='vi_VN').capitalize() + " đồng chẵn."
            except NotImplementedError:
                rec.amountinwords = num2words(
                    int(rec.amount_total), lang='en').capitalize() + " VND."

    @ api.depends('partner_id')
    def _sv_name(self):
        for record in self:
            name = record.partner_id.name
            if record.partner_id.company_type == 'employer':
                if record.partner_id.customerName is not False:
                    name = record.partner_id.customerName
            record.svcustomerName = name

    # def cap_nhat_sellercode(self):
    #     for record in self:
            # no_seller_so_ids = self.env['sale.order'].sudo().search([('user_id', '=', False)])
            # for so_id in no_seller_so_ids:
            #     so_id.user_id = self.env['res.users'].browse(598)

            # no_seller_account_move_ids = self.env['account.move'].sudo().search(
            #     [('invoice_user_id', '=', False), ('move_type', '=', 'out_invoice')])
            # for account_move_id in no_seller_account_move_ids:
            #     account_move_id.invoice_user_id = self.env['res.users'].browse(598)

            # so_598_ids = self.env['sale.order'].sudo().search([('user_id', '=', 598)])
            # for so_598_id in so_598_ids:
            #     revenue_recognize_ids = self.env['revenue.recognize'].sudo().search(
            #         [('sale_order_id', '=', so_598_id.id)])
            #     # print("<<<<<<<<---------------")
            #     # print(revenue_recognize_ids)
            #     # print("<<<<<<<<---------------")
            #     for revenue_recognize_id in revenue_recognize_ids:
            #         revenue_recognize_id.seller_id = so_598_id.user_id
            # print("xxxxxxxxxxxxxxxxxxxx")
            # print(revenue_recognize_id.seller_id)
            # print("xxxxxxxxxxxxxxxxxxxx")

            # print(">>>>>>>>>>>>>>>>")
            # # print(no_seller_so_ids)
            # print(so_598_ids)
            # # print(no_seller_account_move_ids)
            # print(">>>>>>>>>>>>>>>>")

    def download_file_pdf(self):
        # Check config
        if len(self.company_branch_id) == 0:
            raise UserError(
                "Chưa chọn Cấu hình phát hành hóa đơn Company Branch")

        # cau hinh xml body gui API
        xmlformdata = """<?xml version="1.0" encoding="utf-8"?>
        <soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xmlns:xsd="http://www.w3.org/2001/XMLSchema"
         xmlns:soap12="http://www.w3.org/2003/05/soap-envelope">
                    <soap12:Body>
                        <downloadInvPDFFkeyNoPay xmlns="http://tempuri.org/">
                            <Account>"""
        xmlformdata += self.company_branch_id.account + \
            "</Account><ACpass>" + self.company_branch_id.acpass
        xmlformdata += "</ACpass><fkey>" + self.fkey + \
            "</fkey><userName>" + self.company_branch_id.vsi_username
        xmlformdata += "</userName><userPass>" + self.company_branch_id.vsi_password + """</userPass>
                            </downloadInvPDFFkeyNoPay>
                    </soap12:Body>
                </soap12:Envelope>
                """

        headers = {"Content-Type": "text/xml;charset=utf-8"}
        api_url = self.company_branch_id.portal_service_domain
        result = requests.post(
            api_url, data=xmlformdata.encode('utf-8'), headers=headers)
        result_soup = BeautifulSoup(result.content.decode("utf- 8"), 'xml')
        b64_pdf = result_soup.downloadInvPDFFkeyNoPayResult.text
        # print(">>>>>>>>>>>>>>>>>>>>")
        # print(b64_pdf)
        # print(">>>>>>>>>>>>>>>>>>>>")
        # if "ERR:" in b64_pdf:
        #     raise UserError("Có lỗi khi hủy hóa đơn hiện tại %s", b64_pdf)
        # else:
        ATTACHMENT_NAME = self.fkey + '_' + self.name
        ir_attachment_id = self.env['ir.attachment'].create({
            'name': ATTACHMENT_NAME + '.pdf',
            'type': 'binary',
            'datas': b64_pdf,
            'store_fname': ATTACHMENT_NAME + '.pdf',
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/x-pdf'
        })
        self.pdf_file = ir_attachment_id

    # def delete_company_partner(self):
    #     print("delete")
    #     res_parter_ids = self.env['res.partner'].search(
    #         [("company_type", "=", "company")], limit=10000)
    #     for res_parter_id in res_parter_ids:
    #         if res_parter_id.id not in [1, 285279, 285272, 285277, 285275]:
    #             res_parter_id.unlink()

    # def update_company_partner(self):
    #     print("update")
    #     invoice_ids = self.env['account.move'].sudo().search(
    #         [("move_type", "!=", "entry")])
    #     for invoice_id in invoice_ids:
    #         for account_move_line_id in invoice_id.line_ids:
    #             account_move_line_id.partner_id = invoice_id.partner_id

    # def update_account_journal_date(self):
    #     print("update")
    #     invoice_ids = self.env['account.move'].sudo().search(
    #         [("move_type", "=", "out_invoice")])
    #     for invoice_id in invoice_ids:
    #         invoice_id.date = invoice_id.invoice_date

    # Huy hoa don
    def cancel_invoice_comfirm(self):
        self.insert_log("Click Huỷ hoá đơn")
        # Check config
        if len(self.company_branch_id) == 0:
            raise UserError(
                "Chưa chọn Cấu hình phát hành hóa đơn Company Branch")

        xmlformdata = """<?xml version="1.0" encoding="utf-8"?>
<soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
 xmlns:xsd="http://www.w3.org/2001/XMLSchema"
 xmlns:soap12="http://www.w3.org/2003/05/soap-envelope">
    <soap12:Body>
        <cancelInvNoPay xmlns="http://tempuri.org/">
            <Account>"""
        xmlformdata += self.company_branch_id.account + \
            "</Account><ACpass>" + self.company_branch_id.acpass
        xmlformdata += "</ACpass><fkey>" + self.fkey + \
            "</fkey><userName>" + self.company_branch_id.vsi_username
        xmlformdata += "</userName><userPass>" + self.company_branch_id.vsi_password + """</userPass>
                            </cancelInvNoPay>
                    </soap12:Body>
                </soap12:Envelope>
                """
        headers = {"Content-Type": "text/xml;charset=utf-8"}
        api_url = self.company_branch_id.business_service_domain
        result = requests.post(
            api_url, data=xmlformdata.encode('utf-8'), headers=headers)
        result_soup = BeautifulSoup(result.content.decode("utf- 8"), 'xml')
        readable_content = result_soup.cancelInvNoPayResult.text
        self.unconfirmPaymentbyFkey()
        if readable_content == "OK:":
            self.vsi_status = 'canceled'
            if len(self.account_move_ids) > 0:
                for account_move_id in self.account_move_ids:
                    account_move_id.vsi_status = 'canceled'
        else:
            raise UserError(
                "Lỗi khi phát hành hóa đơn " + readable_content)

    def confirmPaymentbyFkey(self):
        # Check config
        if len(self.company_branch_id) == 0:
            raise UserError(
                "Chưa chọn Cấu hình phát hành hóa đơn Company Branch")

        xmlformdata = """<?xml version="1.0" encoding="utf-8"?>
<soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
 xmlns:xsd="http://www.w3.org/2001/XMLSchema"
 xmlns:soap12="http://www.w3.org/2003/05/soap-envelope">
    <soap12:Body>
        <confirmPaymentFkey xmlns="http://tempuri.org/">
            <lstFkey>"""
        xmlformdata += self.fkey + \
            "</lstFkey><userName>" + self.company_branch_id.vsi_username
        xmlformdata += "</userName><userPass>" + self.company_branch_id.vsi_password + """</userPass>
                            </confirmPaymentFkey>
                    </soap12:Body>
                </soap12:Envelope>
                """
        headers = {"Content-Type": "text/xml;charset=utf-8"}
        api_url = self.company_branch_id.business_service_domain
        # requests.post(api_url, data=xmlformdata.encode('utf-8'), headers=headers)
        result = requests.post(api_url, data=xmlformdata.encode('utf-8'), headers=headers)
        soup = BeautifulSoup(result.content.decode("utf-8"), 'xml')
        readable_content = soup.confirmPaymentFkeyResult.text
        print("yyyyyyyyyyyyyyyyyy")
        print(readable_content)
        print("yyyyyyyyyyyyyyyyyy")

    def unconfirmPaymentbyFkey(self):
        # Check config
        if len(self.company_branch_id) == 0:
            raise UserError(
                "Chưa chọn Cấu hình phát hành hóa đơn Company Branch")

        xmlformdata = """<?xml version="1.0" encoding="utf-8"?>
<soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
xmlns:xsd="http://www.w3.org/2001/XMLSchema"
xmlns:soap12="http://www.w3.org/2003/05/soap-envelope">
    <soap12:Body>
        <UnConfirmPaymentFkey xmlns="http://tempuri.org/">
            <lstFkey>"""
        xmlformdata += self.fkey + \
            "</lstFkey><userName>" + self.company_branch_id.vsi_username
        xmlformdata += "</userName><userPass>" + self.company_branch_id.vsi_password + """</userPass>
                            </UnConfirmPaymentFkey>
                    </soap12:Body>
                </soap12:Envelope>
                """
        headers = {"Content-Type": "text/xml;charset=utf-8"}
        api_url = self.company_branch_id.business_service_domain
        requests.post(api_url, data=xmlformdata.encode('utf-8'), headers=headers)
        result = requests.post(api_url, data=xmlformdata.encode('utf-8'), headers=headers)
        soup = BeautifulSoup(result.content.decode("utf-8"), 'xml')
        readable_content = soup.UnConfirmPaymentFkeyResult.text
        print("xxxxxxxxxxxxxxxxx")
        print(readable_content)
        print("xxxxxxxxxxxxxxxxx")

    def reset_einvoice_status(self):
        self.insert_log("Click Reset trạng thái")
        self.get_seller_code()
        self.write({
            'vsi_status': 'draft'
        })

    def resend_vnpt_email(self):
        self.insert_log("Click Download và Gửi Lại Hóa Đơn")
        # check xem da download pdf chua
        if len(self.pdf_file) == 0:
            self.download_file_pdf()
        self.unconfirmPaymentbyFkey()
        self.confirmPaymentbyFkey()

    def send_email_create_invoice(self):
        partner_id_array = []
        partner_ids = []
        if len(self.account_move_ids) > 0:
            for account_move_id in self.account_move_ids:
                partner_ids.append(
                    (4, account_move_id.invoice_user_id.partner_id.id))
                partner_id_array.append(account_move_id.invoice_user_id.partner_id.id)
                account_move_id.invoice_user_id.partner_id.id

        partner_name = self.partner_id.name
        if self.partner_id.company_type == 'employer' \
                and self.partner_id.customerName is not False:
            partner_name = self.partner_id.customerName

        body_html = "Kính gửi Quý khách hàng, <br/>" + self.company_id.name + \
            " xin trân trọng cảm ơn Quý khách hàng đã sử dụng dịch vụ "
        body_html += "của chúng tôi. <br/><br/>"
        body_html += self.company_id.name + \
            " vừa phát hành hóa đơn điện tử đến Quý khách. <br/><br/>"
        body_html += """Hóa đơn của Quý khách hàng có thông tin như sau: <br/><br/>
                • Họ tên người mua hàng: """

        body_html += partner_name + "<br/> "

        if self.VAT is not False:
            body_html += "• Mã Số Thuế: " + self.VAT + "<br/>"

        body_html += "• Hóa đơn số: "
        body_html += self.name + " thuộc mẫu số " + \
            self.vsi_template + " và serial " + self.vsi_series

        body_html += "<br/><br/>Mọi thắc mắc xin vui lòng liên hệ " + \
            self.company_id.name
        body_html += "<br/>ĐC: " + self.company_id.street
        body_html += """<br/>
                Điện thoại : """
        body_html += self.company_id.phone
        body_html += """<br/>
                Trân trọng.<br/>
        """
        create_values = {
            'body_html': body_html,
            'email_from': 'invoice@nhanlucsieuviet.com',
            'subject': _("Phát hành hóa đơn điện tử %s ") % self.name,
            'recipient_ids': partner_ids,
            'attachment_ids': [(6, 0, [self.pdf_file.id])]
        }
        # mail = self.env['mail.mail'].sudo().create(create_values)
        # mail.send()
        # self.env['mail.thread'].message_notify(
        #     email_from='invoice@nhanlucsieuviet.com',
        #     body=create_values['body_html'],
        #     subject=['subject'],
        #     partner_ids=partner_id_array,
        #     attachment_ids=create_values['attachment_ids'],
        #     force_send=True)

        self.with_context({'force_write': True}).message_post(
            body=create_values['body_html'],
            subject=create_values['subject'],
            message_type='email',
            subtype_xmlid=None,
            partner_ids=partner_id_array,
            attachment_ids=[self.pdf_file.id],
            add_sign=True,
            model_description=False,
            mail_auto_delete=False
        )

    def insert_log(self, message):
        self.message_post(
            body=message,
            message_type='comment',
            author_id=self.env.user.partner_id.id if self.env.user.partner_id else None,
            subtype_xmlid='mail.mt_comment',
        )

    def get_seller_code(self):
        sellerCode = '11111111'
        for account_move_id in self.account_move_ids:
            seller = account_move_id.invoice_user_id
            sellerCode = seller.update_to_einvoice(self.company_branch_id)
            break
        return sellerCode

    def sendeinvoice(self):
        self.insert_log("Click Phát Hành Hóa Đơn")
        def get_selection_label(self, object, field_name, field_value):
            return _(dict(self.env[object].fields_get(allfields=[field_name])[field_name]['selection'])[field_value])
        self.with_context(force_write=True)
        # Check already created einvoice
        if self.vsi_status == 'created':
            raise UserError("Hóa đơn đã được tạo hóa đơn điện tử")
        elif self.vsi_status == 'creating':
            raise UserError("Hóa đơn đang được tạo hóa đơn điện tử")
        sellerCode = self.get_seller_code()
        self.vsi_status = "creating"
        self._cr.commit()

        loaichuyenkhoan = "TM/CK"
        if self.paymentType is not False:
            loaichuyenkhoan = get_selection_label(self, 'invoice.viettel',
                                                  'paymentType', self.paymentType)
        # Check config
        if len(self.company_branch_id) == 0:
            print("abc")
            raise UserError(
                "Chưa chọn Cấu hình phát hành hóa đơn Company Branch")

        invoiceDetails = []
        invoicedata = ""
        for invoice_line in self.invoice_line_ids:
            line_data = {
                "Code": "product_" + str(invoice_line.product_id.id),
                "ProdName": invoice_line.name,
                "ProdUnit": invoice_line.product_id.uom_id.name,
                "ProdQuantity": invoice_line.quantity,
                "ProdPrice": invoice_line.price_unit,
                "Total": invoice_line.price_total,
                'VATRate': invoice_line.vat_rate or 0,
                "VATAmount": invoice_line.vat_amount,
                "Amount": invoice_line.price_total,
                "Remark": "",
                "Extra1": "",
                "Extra2": ""
            }
            invoicex = dicttoxml({"Product": line_data}, attr_type=False, root=False)
            k = bytes.decode(invoicex)
            invoicedata += k
            invoiceDetails.append({"Product": line_data})
            products_xml = "<Products>" + invoicedata + "</Products>"

        partner_name = self.partner_id.name
        if self.partner_id.company_type == 'employer' \
                and self.partner_id.customerName is not False:
            partner_name = self.partner_id.customerName
        #
        # self.fkey = int(datetime.utcnow().timestamp())

        if self.company_branch_id.swap:
            buyer = self.buyerName or ""
            cusName = partner_name
        else:
            cusName = self.buyerName or ""
            buyer = partner_name

        invoicexml = {
            'Invoices': {
                'Inv': {
                    'key': self.fkey,
                    'Invoice': {
                        'CusCode': sellerCode,
                        'CusName': cusName,
                        'Buyer': buyer,
                        'CusAddress': self.street_partner or "",
                        'CusPhone': self.phone_partner or "",
                        'CusTaxCode': self.VAT or "",
                        'PaymentMethod': loaichuyenkhoan,
                        'CusBankNo': '',
                        'ContNo': '',
                        'ReferenceNo': 'ABC',
                        'PaymentTerm': 0,
                        'GrossValue': "",
                        'GrossValue0': "",
                        'GrossValue5': self.grossvalue5 or "",
                        'GrossValue10': self.grossvalue10 or "",
                        'VatAmount5': self.vatamount5 or "",
                        'VatAmount10': self.vatamount10 or "",
                        'Extra1': "",
                        'Extra2': "",
                        'DiscountAmount': "",
                        'Total': self.amount_untaxed,
                        'VATRate': 10,
                        'VATAmount': self.amount_tax or "",
                        'Amount': self.amount_total,
                        'AmountInWords': self.amountinwords,
                        'Extra': "",
                        'ArisingDate': self.date_invoice.strftime('%d/%m/%Y'),
                        'PaymentStatus': 0
                    }
                }
            }
        }

        dataxx = dicttoxml(invoicexml, attr_type=False, root=False)
        xmlformdata = """<?xml version="1.0" encoding="utf-8"?>
<soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
 xmlns:xsd="http://www.w3.org/2001/XMLSchema"
  xmlns:soap12="http://www.w3.org/2003/05/soap-envelope">
  <soap12:Body>
    <ImportAndPublishInv xmlns="http://tempuri.org/"><Account>"""

        xmlformdata += self.company_branch_id.account
        xmlformdata += "</Account><ACpass>"
        xmlformdata += self.company_branch_id.acpass + \
            "</ACpass><username>"
        xmlformdata += self.company_branch_id.vsi_username + \
            "</username><password>"
        xmlformdata += self.company_branch_id.vsi_password + \
            "</password><pattern>"
        xmlformdata += self.company_branch_id.vsi_template + \
            "</pattern><serial>" + self.company_branch_id.vsi_series
        xmlformdata += """</serial>
                      <convert>0</convert>
                    </ImportAndPublishInv>
                  </soap12:Body>
                </soap12:Envelope>
                """

        a = """      <xmlInvData>
        <![CDATA["""
        b = """]]>
        </xmlInvData>"""
        xmlinvdata = a + bytes.decode(dataxx) + b

        def insertChar(mystring, position, chartoinsert):
            mystring = mystring[:position] + chartoinsert + mystring[position:]
            return mystring

        xmldulieuchuan = insertChar(
            xmlformdata, xmlformdata.find('<username>'), xmlinvdata)
        xmldulieuchuan = insertChar(
            xmldulieuchuan, xmldulieuchuan.find('<GrossValue>'), products_xml)

        headers = {"Content-Type": "text/xml;charset=utf-8"}
        api_url = self.company_branch_id.vsi_domain
        if self.vsi_status == 'created':
            print(" already created einvoice")
            raise UserError(
                "Hóa đơn đã được tạo hóa đơn điện tử")

        print("push data ")
        _logger.info("Einvoice Content : " + xmldulieuchuan)

        self.insert_log("Bắt đầu kết nối VNPT và thực hiện phát hành HDDT")
        result = requests.post(
            api_url, data=xmldulieuchuan.encode('utf-8'), headers=headers)

        soup = BeautifulSoup(result.content.decode("utf-8"), 'xml')
        readable_content = soup.ImportAndPublishInvResult.text
        _logger.info("Einvoice Result : " + readable_content)
        self.insert_log("Kết thúc kết nối VNPT. Kết quả: " + readable_content)

        print("push data response " + readable_content)
        if self.vsi_status == 'created':
            print(" already created einvoice")
            raise UserError(
                "Hóa đơn đã được tạo hóa đơn điện tử")
        dodai = 7
        if readable_content.find('OK') >= 0:
            print("save einvoice " + readable_content)
            self.vsi_status = "created"
            index_shd = len(readable_content) - readable_content.find('_') - 1
            sohoadon = readable_content[-index_shd:]

            if len(sohoadon) < dodai:
                shd = ""
                for n in range(dodai - len(sohoadon)):
                    shd += "0"
                sohoadon = shd + sohoadon

            self.name = sohoadon
            time.sleep(2)
            self.confirmPaymentbyFkey()
            time.sleep(2)
            self.download_file_pdf()
            time.sleep(2)

            if len(self.account_move_ids) > 0:
                for account_move_id in self.account_move_ids:
                    account_move_id.vsi_template = self.vsi_template
                    account_move_id.vsi_series = self.vsi_series
                    account_move_id.vsi_number = sohoadon
                    account_move_id.einvoice_date = self.date_invoice
                    account_move_id.vsi_status = 'created'

                self.insert_log(" Cập nhật số hóa đơn thành công ")
            # self.send_email_create_invoice()
        else:
            raise UserError(
                "Lỗi khi phát hành hóa đơn " + readable_content)

    def adjust_einvoice(self):
        self.insert_log("Click Phát Hành Hóa Đơn Điều Chỉnh")
        # Check config
        if len(self.company_branch_id) == 0:
            print("abc")
            raise UserError(
                "Chưa chọn Cấu hình phát hành hóa đơn Company Branch")
        sellerCode = self.get_seller_code()
        invoiceDetails = []
        invoicedata = ""
        i = 0
        for invoice_line in self.invoice_line_ids:
            i += 1
            # chinh lai code cua product
            line_data = {
                "Code": "product_1",
                "ProdName": invoice_line.name,
                "ProdUnit": invoice_line.product_id.uom_id.name or '\\',
                "ProdQuantity": invoice_line.quantity,
                "ProdPrice": invoice_line.price_unit,
                "Amount": invoice_line.price_subtotal,
                'VATRate': invoice_line.vat_rate or 0,
                "Total": invoice_line.price_total,
                "VATAmount": invoice_line.vat_amount,
            }
            invoicex = dicttoxml({"Product": line_data},
                                 attr_type=False, root=False)
            k = bytes.decode(invoicex)
            invoicedata += k
            invoiceDetails.append({"Product": line_data})
            products_xml = "<Products>" + invoicedata + "</Products>"

        self.fkey = int(datetime.utcnow().timestamp())

        invoicexml = {
            'AdjustInv': {
                'key': self.fkey,
                'CusCode': sellerCode,
                'CusName': self.buyerName or "",
                'Buyer': self.partner_id.name,
                'CusAddress': self.street_partner,
                'CusPhone': self.phone_partner or "",
                'CusTaxCode': self.VAT or "",
                'PaymentMethod': 'TM/CK',
                'KindOfService': 2,
                'Type': 4,
                'DiscountAmount': "",
                'Total': self.amount_untaxed,
                'VATRate': "",
                'VATAmount': self.amount_tax or "",
                'Amount': self.amount_total,
                'AmountInWords': self.amountinwords,
                'Extra': "",
                'ArisingDate': self.date_invoice.strftime('%d/%m/%Y'),
                'PaymentStatus': 1,
            }
        }
        # dieu chinh lai thang hoa don

        dataxx = dicttoxml(invoicexml, attr_type=False, root=False)
        xmlformdata = """<?xml version="1.0" encoding="utf-8"?>
<soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
 xmlns:xsd="http://www.w3.org/2001/XMLSchema"
 xmlns:soap12="http://www.w3.org/2003/05/soap-envelope">
  <soap12:Body>
    <adjustInv xmlns="http://tempuri.org/"><Account>"""

        xmlformdata += self.company_branch_id.account
        xmlformdata += "</Account><ACpass>"
        xmlformdata += self.company_branch_id.acpass + "</ACpass><username>"
        xmlformdata += self.company_branch_id.vsi_username + \
            "</username><pass>"
        xmlformdata += self.company_branch_id.vsi_password + "</pass><fkey>"
        xmlformdata += self.origin_invoice.fkey
        xmlformdata += """</fkey>
                    </adjustInv>
                  </soap12:Body>
                </soap12:Envelope>
                """

        a = """      <xmlInvData>
        <![CDATA["""
        b = """]]>
        </xmlInvData>"""
        xmlinvdata = a + bytes.decode(dataxx) + b

        def insertChar(mystring, position, chartoinsert):
            mystring = mystring[:position] + chartoinsert + mystring[position:]
            return mystring

        xmldulieuchuan = insertChar(
            xmlformdata, xmlformdata.find('<username>'), xmlinvdata)
        xmldulieuchuan = insertChar(xmldulieuchuan,
                                    xmldulieuchuan.find('<DiscountAmount>'),
                                    products_xml)

        headers = {"Content-Type": "text/xml;charset=utf-8"}
        api_url = self.company_branch_id.business_service_domain
        result = requests.post(
            api_url, data=xmldulieuchuan.encode('utf-8'), headers=headers)
        soup = BeautifulSoup(result.content.decode("utf-8"), 'xml')
        readable_content = soup.adjustInvResult.text

        dodai = 7
        if readable_content.find('OK') >= 0:
            index_shd = len(readable_content) - readable_content.find('_') - 1
            sohoadon = readable_content[-index_shd:]

            if len(sohoadon) < dodai:
                shd = ""
                for n in range(dodai - len(sohoadon)):
                    shd += "0"
                sohoadon = shd + sohoadon

            self.name = sohoadon
            self.vsi_status = "created"
        else:
            raise UserError(
                "Phát hành hóa đơn không thành công: %s" % (readable_content))

    def unlink(self):
        for record in self:
            if record.vsi_status == 'created' and not self.env.context.get('force_write', False):
                raise UserError(_('This invoice ' + record.name +
                                  '(' + str(record.id) + ')' + ' is created, can not delete'))
        return super(InvoiceViettel, self).unlink()

    def write(self, vals):
        for record in self:
            if self.env.context.get('force_write', False) or record.adjustment_type or \
                record.is_adjustment_invoice or \
                    'vsi_status' in vals or 'adjustment_type' in vals or \
                    'amount_total' in vals or 'pdf_file' in vals or 'name' in vals:
                return super(InvoiceViettel, record).write(vals)
            elif record.vsi_status == 'created':
                raise UserError(_('This invoice ' + record.name + '(' + str(record.id) + ')' +
                                  ' is created. You can not update'))
        return super(InvoiceViettel, self).write(vals)

    def task_check_created_einvoice_at_vnpt(self):
        # Check config
        einvoices = self.env['invoice.viettel'].sudo().search([('vsi_status', '=', 'creating')])

        for einvoice in einvoices:
            if len(einvoice.company_branch_id) == 0:
                logging.info("Chưa chọn Cấu hình phát hành hóa đơn Company Branch")

            xmlformdata = """<?xml version="1.0" encoding="utf-8"?>
        <soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xmlns:xsd="http://www.w3.org/2001/XMLSchema"
         xmlns:soap12="http://www.w3.org/2003/05/soap-envelope">
            <soap12:Body>
                <listInvByCusFkey xmlns="http://tempuri.org/">"""
            xmlformdata += "<key>" + einvoice.fkey + \
                           "</key><fromDate></fromDate><toDate></toDate><userName>" + einvoice.company_branch_id.vsi_username
            xmlformdata += "</userName><userPass>" + einvoice.company_branch_id.vsi_password + """</userPass>
                                    </listInvByCusFkey>
                            </soap12:Body>
                        </soap12:Envelope>
                        """
            headers = {"Content-Type": "application/soap+xml; charset=utf-8"}

            api_url = einvoice.company_branch_id.portal_service_domain
            result = requests.post(
                api_url, data=xmlformdata, headers=headers)
            result_soup = BeautifulSoup(result.content.decode("utf- 8"), 'xml')
            readable_content = result_soup.listInvByCusFkeyResult.text
            if 'ERR' not in readable_content and BeautifulSoup(readable_content, 'xml').Data.Item != None:
                result_content_soup = BeautifulSoup(readable_content, 'xml').Data.Item
                invoice_no = result_content_soup.invNum.text
                einvoice.vsi_status = 'created'
                einvoice.name = invoice_no
                if len(einvoice.account_move_ids) > 0:
                    for account_move_id in einvoice.account_move_ids:
                        account_move_id.vsi_template = einvoice.vsi_template
                        account_move_id.vsi_series = einvoice.vsi_series
                        account_move_id.vsi_number = invoice_no
                        account_move_id.einvoice_date = einvoice.date_invoice
                        account_move_id.vsi_status = 'created'
                self._cr.commit()
            else:
                logging.info(
                    "Lỗi khi kiểm tra hóa đơn " + str(einvoice.id) + " Error" + readable_content)