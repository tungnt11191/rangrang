# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date, timedelta, datetime
import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
import tempfile
from odoo.tools.misc import xlwt
import io
import base64
import time
from dateutil.relativedelta import relativedelta
from pytz import timezone
import xlwt as xw


class InventoryValuationWizard(models.Model):
    _name = 'bms.inventory.valuation.wizard'

    date_start = fields.Date("Ngày bắt đầu")
    date_end = fields.Date("Ngày kết thúc")
    location_ids = fields.Many2many(comodel_name="stock.location", string="Địa điểm", )

    def inventory_template_excel_report(self):

        filename = 'BẢNG TỔNG HỢP VẬT TƯ NHẬP XUẤT TỒN' + '.xls'
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('TONG HOP XNT')
        style = xlwt.easyxf('align: vert centre, horiz centre;font: bold 1, name Times New Roman, height 320;')
        style_table = xlwt.easyxf('align: vert centre, horiz centre;font: bold 1, name Times New Roman, height 280; borders:left 1,right 1,top 1,bottom 1;')
        style_bodytable = xlwt.easyxf('align: vert centre, horiz left;alignment: wrap True;font: name Times New Roman, height 280; borders:left 1,right 1,top 1,bottom 1;')
        style_lefttable = xlwt.easyxf('align: vert centre, horiz left;font: bold 1, name Times New Roman, height 280; borders:left 1,right 1,top 1,bottom 1;')
        style_futer = xlwt.easyxf('align: vert centre, horiz centre;font:bold 1, name Times New Roman, height 280;')
        style_price = xlwt.easyxf('align: vert centre, horiz right;font: name Times New Roman, height 280;alignment: wrap True;borders:left 1,right 1,top 1,bottom 1;')
        first_col = worksheet.col(0)
        col_2 = worksheet.col(1)
        col_3 = worksheet.col(2)
        col_4 = worksheet.col(3)
        col_5 = worksheet.col(4)
        col_6 = worksheet.col(5)
        col_7 = worksheet.col(6)
        col_8 = worksheet.col(7)
        col_9 = worksheet.col(8)
        col_10 = worksheet.col(9)
        col_11 = worksheet.col(10)
        col_12 = worksheet.col(11)
        first_col.width = 256 * 15
        col_2.width = 256 * 60
        col_3.width = 256 * 10
        col_4.width = 256 * 20
        col_5.width = 256 * 20
        col_6.width = 256 * 20
        col_7.width = 256 * 20
        col_8.width = 256 * 20
        col_9.width = 256 * 30
        col_10.width = 256 * 20
        col_11.width = 256 * 30
        col_12.width = 256 * 20
        worksheet.write(0, 0, "Tên đơn vị", style_futer)
        worksheet.write(0, 1, self.env.user.company_id.name, style_futer)
        worksheet.write(1, 1, self.env.user.company_id.street, style_futer)
        worksheet.write(1, 0, "Địa chỉ", style_futer)
        worksheet.write(2, 0, "MST", style_futer)
        worksheet.write_merge(4, 4, 0, 5, "BẢNG TỔNG HỢP VẬT TƯ NHẬP XUẤT TỒN", style)
        worksheet.write_merge(5, 5, 0, 5, "Từ ngày {} đến ngày {}".format(self.date_start.strftime("%d/%m/%Y"), self.date_end.strftime("%d/%m/%Y")), style_futer)
        worksheet.write_merge(7, 8, 0, 0, "Mã VT", style_lefttable)
        worksheet.write_merge(7, 8, 1, 1, "Tên vật tư", style_lefttable)
        worksheet.write_merge(7, 8, 2, 2, "ĐVT", style_lefttable)
        worksheet.write(7, 3, "Tồn đầu kỳ", style_table)
        worksheet.write(7, 4, "Nhập trong kỳ", style_table)
        worksheet.write(7, 5, "Xuất trong kỳ", style_table)
        worksheet.write(7, 6,"Tồn cuối kỳ", style_table)
        worksheet.write(8, 3, "Số lượng", style_table)
        worksheet.write(8, 4, "Số lượng", style_table)
        worksheet.write(8, 5, "Số lượng", style_table)
        worksheet.write(8, 6, "Số lượng", style_table)

        location = ""
        for i in self.location_ids:
            if location == "":
                location += "{}".format(i.display_name)
            else:
                location += ", {}".format(i.display_name)
        worksheet.write_merge(6, 6, 0, 6, "Kho: {}".format(location), xlwt.easyxf('font: bold 0, name Times New Roman, height 280;'))

        data = {}
        print("hiphip")
        print(self.date_end)
        print(self.location_ids.ids)
        print("hiphip")
        inventory_valuation_ids = self.env['bms.inventory.valuation'].search([('date', '=', self.date_end),
                                                    ('location_id', 'in', self.location_ids.ids)], order='date asc')
        if not inventory_valuation_ids:
            self.env['bms.inventory.valuation'].cron_inventory_valuation(True)

        inventory_valuation_ids = self.env['bms.inventory.valuation'].search([('date', '>=', self.date_start), ('date', '<=', self.date_end), ('location_id', 'in', self.location_ids.ids)], order='date asc')

        # print(inventory_valuation_ids)
        for inventory_valuation in inventory_valuation_ids:
            first_day = inventory_valuation_ids[0].date
            for line in inventory_valuation.line_ids:
                # print(data)
                if line.product_id.id not in data:
                    data[line.product_id.id] = {
                        'mvt': line.product_id.default_code or '',
                        'uom': line.product_id.uom_po_id.name,
                        "product": line.product_id.name,
                        "quantity_in": line.quantity_in,
                        "price_in": line.price_in,
                        "quantity_out": line.quantity_out,
                        "price_out": line.price_out,
                    }
                    data[line.product_id.id]['price'] = line.price
                    data[line.product_id.id]['quantity'] = line.quantity
                    first_day = line.date
                else:
                    data[line.product_id.id]['quantity_in'] = data[line.product_id.id]['quantity_in'] + line.quantity_in
                    data[line.product_id.id]['price_in'] = data[line.product_id.id]['price_in'] + line.price_in
                    data[line.product_id.id]['quantity_out'] = data[line.product_id.id]['quantity_out'] + line.quantity_out
                    data[line.product_id.id]['price_out'] = data[line.product_id.id]['price_out'] + line.price_out
                    if line.date == first_day:
                        data[line.product_id.id]['price'] = data[line.product_id.id]['price'] + line.price
                        data[line.product_id.id]['quantity'] = data[line.product_id.id]['quantity'] + line.quantity
        # print(data)
        row = 9
        for id in data:
            worksheet.write(row, 0, data[id]['mvt'], style_bodytable)
            worksheet.write(row, 1, data[id]['product'], style_bodytable)
            worksheet.write(row, 2, data[id]['uom'], style_bodytable)
            worksheet.write(row, 3, data[id]['quantity'], style_price)
            worksheet.write(row, 4, data[id]['quantity_in'], style_price)
            worksheet.write(row, 5, data[id]['quantity_out'], style_price)
            worksheet.write(row, 6, data[id]['quantity'] + data[id]['quantity_in'] - data[id]['quantity_out'], style_price)
            row += 1
        fp = io.BytesIO()
        workbook.save(fp)
        inventory_id = self.env['bms.inventory.excel.extended'].create(
            {'excel_file': base64.encodestring(fp.getvalue()), 'file_name': filename})
        fp.close()

        return {
            'view_mode': 'form',
            'res_id': inventory_id.id,
            'res_model': 'bms.inventory.excel.extended',
            'view_type': 'form',
            'type': 'ir.actions.act_window',
            'context': self._context,
            'target': 'new',
        }


class BmsInventoryExcelExtended(models.Model):
    _name = 'bms.inventory.excel.extended'
    _description = "Product Excel Extended"

    excel_file = fields.Binary('Download Report :- ')
    file_name = fields.Char('Excel File', size=64)
