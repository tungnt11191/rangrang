# -*- coding: utf-8 -*-
# Part of Aktiv Software
# See LICENSE file for full copyright & licensing details.

from odoo import models

class PartnerXlsx(models.AbstractModel):
    _name = 'report.ak_sale_order_excel_report.sale_xlsx'
    _description = 'Sale Oder Excle Report'
    _inherit = 'report.report_xlsx.abstract'

    def format_date(self, input_date):
        '''
        Return date with custom format
        @param = date/datetime
        @return string
        '''
        format_date = {
            '1': 'st',
            '2': 'nd',
            '3': 'rd'
        }

        date = input_date.strftime("%d")
        date_suffix = ''
        if date[-1] in format_date.keys():
            date_suffix = format_date[date[-1]]
        if date_suffix == '':
            date_suffix = 'th'
        month = input_date.strftime("%b")
        year = input_date.strftime("%Y")
        date_output = month + " " + date + date_suffix + ", " + year

        return date_output

    def prepare_data(self, sale_order):
        data = []
        for line in sale_order.order_line:
            product = self.env['product.product'].search([('id', '=', line.product_id.id), '|', ('active', '=', False), ('active', '=', True)])
            line_data = {
                'code': product.barcode,
                'customer_code': product.description_sale,
                'description': line.name,
                'unit_price': line.price_unit,
                'finishing_color': line.finishing_color or '',
                'qty_per_pallet': product.pcs_per_pallet or 0
            }
            data.append(line_data)
        return data

    def write_line_data(self, worksheet, row, objects):
        data = self.prepare_data(objects)
        count = 1
        for line_data in data:
            worksheet.write(row, 0, count, worksheet.format_border_cell)
            worksheet.write(row, 1, line_data['code'], worksheet.format_border_cell)
            worksheet.write(row, 2, line_data['customer_code'], worksheet.format_border_cell)
            worksheet.merge_range(row, 3, row, 5, line_data['description'], worksheet.format_border_cell)
            worksheet.write(row, 6, line_data['unit_price'], worksheet.format_border_cell)
            worksheet.write(row, 7, line_data['finishing_color'], worksheet.format_border_cell)
            worksheet.write(row, 8, line_data['qty_per_pallet'], worksheet.format_border_cell)
            count += 1
            row += 1
        return row

    def generate_xlsx_report(self, workbook, data, objects):
        worksheet = workbook.add_worksheet('Sales Quotation')
        self.set_column_size(worksheet)
        self.set_row_size(worksheet)
        self.format_report(workbook, worksheet)

        contact_partner_lst = [record for record in objects.partner_id.child_ids]
        contact_warehouse_lst = [record for record in objects.warehouse_id.company_id.child_ids]
        contact_partner_str = ''
        contact_warehouse_str = ''
        for record in contact_partner_lst:
            if record.display_name == contact_partner_lst[0].display_name:
                contact_partner_str += record.display_name
            else:
                contact_partner_str += ' / ' + record.display_name

        for record in contact_warehouse_lst:
            if record.display_name == contact_warehouse_lst[0].display_name:
                contact_warehouse_str += record.display_name
            else:
                contact_warehouse_str += ' / ' + record.display_name

        worksheet.merge_range('B1:I1', 'ONP-VIETNAM, LLC', worksheet.format_company_title)
        worksheet.merge_range('B2:I2', 'Address: 38, Ham Nghi street, Thien Binh Quarter, Tam Phuoc Ward, Bien Hoa City, Dong Nai Province, '
                                       'VN.', worksheet.format_address_title)
        worksheet.merge_range('B3:I3', 'Tel:  +84 2516-281-979 ; Fax:  +84 2516-281-977', worksheet.format_phone_title)
        worksheet.merge_range('A5:I5', 'QUOTATION SHEET', worksheet.format_excel_title)

        row = 5
        worksheet.write(row, 0, 'FROM', worksheet.format_table_subject)
        worksheet.write(row, 1, objects.warehouse_id.company_id.display_name, worksheet.format_table_text)
        worksheet.merge_range(row, 5, row, 6,   'TO:', worksheet.format_table_subject_right)
        worksheet.merge_range(row, 7, row, 8, objects.partner_id.display_name, worksheet.format_table_text)

        row += 1
        worksheet.write(row, 0, 'Quotation No.', worksheet.format_table_subject)
        worksheet.write(row, 1, objects.name, worksheet.format_table_text)
        worksheet.merge_range(row, 5, row, 6, 'Address:', worksheet.format_table_subject_right)
        worksheet.merge_range(row, 7, row + 1, 8, objects.partner_id.street, worksheet.format_table_textarea)

        row += 1
        worksheet.write(row, 0, 'Quotation Date', worksheet.format_table_subject)
        create_date = self.format_date(objects.create_date)
        worksheet.write(row, 1, create_date, worksheet.format_table_text)
        worksheet.merge_range(row, 5, row, 6, '')

        row += 1
        worksheet.write(row, 0, 'Contact', worksheet.format_table_subject)
        worksheet.write(row, 1, contact_warehouse_str, worksheet.format_table_text)

        worksheet.merge_range(row, 5, row, 6, 'Contact person:', worksheet.format_table_subject_right)
        worksheet.merge_range(row, 7, row, 8, contact_partner_str, worksheet.format_table_text)

        row += 1
        worksheet.write(row, 0, 'Tel.', worksheet.format_table_subject)
        worksheet.write(row, 1, objects.warehouse_id.company_id.phone, worksheet.format_table_text)
        worksheet.merge_range(row, 5, row, 6, 'Tel.', worksheet.format_table_subject_right)
        worksheet.merge_range(row, 7, row, 8, objects.partner_id.phone, worksheet.format_table_text)

        row += 1

        worksheet.write(row, 0, 'Email', worksheet.format_table_subject)
        warehouse_row = row
        for contact in contact_warehouse_lst:
            worksheet.write(warehouse_row, 1, contact.email or '', worksheet.format_table_email)
            warehouse_row += 1

        worksheet.merge_range(row, 5, row, 6, 'Email:', worksheet.format_table_subject_right)
        partner_row = row
        for contact in contact_partner_lst:
            worksheet.merge_range(partner_row, 7, partner_row, 8, contact.email or '', worksheet.format_table_email)
            partner_row += 1


        row += 2
        worksheet.write(row, 0, 'No.', worksheet.format_table_header)
        worksheet.write(row, 1, 'ONP-VN code', worksheet.format_table_header)
        worksheet.write(row, 2, 'Customer code', worksheet.format_table_header)
        worksheet.merge_range(row, 3, row, 5, 'Description', worksheet.format_table_header)
        worksheet.write(row, 6, 'FOB price\n(USD)', worksheet.format_table_header)
        worksheet.write(row, 7, 'Finishing color', worksheet.format_table_header)
        worksheet.write(row, 8, 'Q\'ties per pallet', worksheet.format_table_header)

        # print table data
        row += 1
        self.write_line_data(worksheet, row, objects)


        row += 2
        worksheet.write(row, 0, 'REMARKS', worksheet.format_detail_header)
        row += 1
        worksheet.write(row, 0, 'All prices are given for a 40\'/ 20\' general container. We can combine several parts into a container.',
                        worksheet.format_detail_body)
        row += 1
        worksheet.write(row, 0, 'TERMS', worksheet.format_detail_header)
        row += 1
        worksheet.write(row, 0, 'FOB (Ho Chi Minh or Cai Mep port)', worksheet.format_detail_body)
        row += 1
        worksheet.write(row, 0, 'QUALITY', worksheet.format_detail_header)
        row += 1
        worksheet.write(row, 0, 'As quality agreement', worksheet.format_detail_body)
        row += 1
        worksheet.write(row, 0, 'PAYMENT', worksheet.format_detail_header)
        row += 1
        worksheet.write(row, 0, 'As payment request procedure.', worksheet.format_detail_body)
        row += 1
        worksheet.write(row, 0, 'VALIDITY', worksheet.format_detail_header)
        row += 1
        date_order = self.format_date(objects.date_order)
        worksheet.write(row, 0, 'Effective from %s until new quotation replacing.' % date_order, worksheet.format_detail_body)

        row += 1
        worksheet.merge_range(row, 0, row, 1, 'PREPARED BY', worksheet.format_signature)
        worksheet.merge_range(row, 3, row, 6, 'ONP-VIET NAM, LLC', worksheet.format_signature)
        worksheet.merge_range(row, 7, row, 8, 'ONP-US, LLC', worksheet.format_signature)


    def format_report(self, workbook, worksheet):
        default_style = {
            'font_name': 'Times New Roman',
            'font_color': '#000099'
        }
        worksheet.format_default = workbook.add_format(default_style)

        head_title = default_style.copy()
        head_title.update({
            'align': 'center',
            'bold': True,
        })

        format_company_title = head_title.copy()
        format_company_title.update({
            'font_size': 18
        })
        worksheet.format_company_title = workbook.add_format(format_company_title)

        format_address_title = head_title.copy()
        format_address_title.update({
            'font_size': 9
        })
        worksheet.format_address_title = workbook.add_format(format_address_title)

        format_phone_title = head_title.copy()
        format_phone_title.update({
            'font_size': 10
        })
        worksheet.format_phone_title = workbook.add_format(format_phone_title)

        format_excel_title = head_title.copy()
        format_excel_title.update({
            'font_size': 24,
            'underline': True
        })
        worksheet.format_excel_title = workbook.add_format(format_excel_title)

        format_table_subject = default_style.copy()
        format_table_subject.update({
            'font_size': 11,
            'align': 'left',
            'bold': True
        })
        worksheet.format_table_subject = workbook.add_format(format_table_subject)

        format_table_subject_right = default_style.copy()
        format_table_subject_right.update({
            'font_size': 11,
            'align': 'right',
            'bold': True
        })
        worksheet.format_table_subject_right = workbook.add_format(format_table_subject_right)

        worksheet.format_table_email = workbook.add_format({
            'font_name': 'Arial',
            'font_size': 8,
            'underline': True
        })

        format_table_text = default_style.copy()
        format_table_text.update({
            'font_size': 11
        })
        worksheet.format_table_text = workbook.add_format(format_table_text)

        format_table_textarea = default_style.copy()
        format_table_textarea.update({
            'text_wrap': True,
            'valign': 'top'
        })
        worksheet.format_table_textarea = workbook.add_format(format_table_textarea)

        format_table_header = default_style.copy()
        format_table_header.update({
            'bold': True,
            'text_wrap': True,
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'fg_color': '#e2efd9',
        })
        worksheet.format_table_header = workbook.add_format(format_table_header)

        format_detail_header = default_style.copy()
        format_detail_header.update({
            'font_size': 11,
            'underline': True,
            'bold': True
        })
        worksheet.format_detail_header = workbook.add_format(format_detail_header)

        format_detail_body = default_style.copy()
        format_detail_body.update({
            'font_size': 11,
            'text_wrap': False
        })
        worksheet.format_detail_body = workbook.add_format(format_detail_body)

        format_signature = default_style.copy()
        format_signature.update({
            'font_size': 12,
            'bold': True,
            'align': 'center'
        })
        worksheet.format_signature = workbook.add_format(format_signature)

        format_border_cell = format_table_text.copy()
        format_border_cell.update({
            'border': 1
        })
        worksheet.format_border_cell = workbook.add_format(format_border_cell)

    def set_column_size(self, worksheet):
        worksheet.set_column('A:A', 20)
        worksheet.set_column('B:B', 25)
        worksheet.set_column('C:I', 20)

    def set_row_size(self, worksheet):
        worksheet.set_row(0, 20)
        worksheet.set_row(4, 30)
        worksheet.set_row(12, 30)