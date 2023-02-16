# -*- coding: utf-8 -*-
from odoo import api, fields, models
from datetime import date, timedelta, datetime
import pytz

import logging
_logger = logging.getLogger(__name__)


class inventory_management_dashboard(models.Model):
    _name = 'inventory.management.dashboard'

    @api.model
    def get_all_locations(self):
        locations = self.env['stock.location'].search_read(
            [('company_id', '=', self.env.user.company_id.id)],
            ['id', 'display_name'])
        print(locations)
        print("890")
        data = {
            'locations': locations,
            'start_date': datetime.today().replace(day=1).date(),
            'end_date': (datetime.today() + timedelta(days=1)).date()
        }
        return data

    @api.model
    def get_web_base_url(self):
        return self.env['ir.config_parameter'].sudo().get_param('web.base.url')

    @api.model
    def get_product_information(self, product_id, location_id):
        finded_product = self.env['product.product'].search_read([
            ('id', '=', int(product_id))], ['id', 'name'])
        finded_location = self.env['stock.location'].search_read([
            ('id', '=', int(location_id))], ['id', 'name'])
        data = {
            'products': finded_product,
            'locations': finded_location,
            'start_date': datetime.today().replace(day=1).date(),
            'end_date': (datetime.today() + timedelta(days=1)).date()
        }
        return data

    @api.model
    def get_xnt_all_locations(self):
        group_manager = self.env.ref('dashboard_inventory.group_xnt_manager')
        if self.env.user.id in group_manager.users.ids:
            locations = self.env['stock.location'].search_read([
                ('company_id', '=', self.env.user.company_id.id)],
                ['id', 'display_name'])
            data = {
                'locations': locations,
                'start_date': datetime.today().replace(day=1).date(),
                'end_date': (datetime.today() + timedelta(days=1)).date()
            }
            return data
        group_nv = self.env.ref('dashboard_inventory.group_xnt_employee')
        if self.env.user.id in group_nv.users.ids:
            locations = self.env['stock.location'].search_read(
                ['|', '&', ('company_id', '=', self.env.user.company_id.id),
                 ('id', 'in', self.env.user.from_location_ids.ids),
                 ('id', 'in', self.env.user.location_dest_ids.ids)],
                ['id', 'display_name'])
            data = {
                'locations': locations,
                'start_date': datetime.today().replace(day=1).date(),
                'end_date': (datetime.today() + timedelta(days=1)).date()
            }
            return data

    @api.model
    def get_locations_dashboard_data(self, location_id, start_date, end_date):
        # Goi ham cronjob tong
        self.env['bms.inventory.valuation'].cron_inventory_valuation()
        inventory_valuation_ids = self.env['bms.inventory.valuation'].search(
            [('date', '>=', start_date), ('date', '<=', end_date),
             ('location_id', 'in', [int(location_id)])], order='date asc')
        dulieu = {}
        for inventory_valuation_id in inventory_valuation_ids:
            for line in inventory_valuation_id.line_ids:
                if line.product_id.id in dulieu:
                    dulieu[line.product_id.id]['quantity_out'] += \
                        line.quantity_out
                    dulieu[line.product_id.id]['quantity_in'] += \
                        line.quantity_in
                    dulieu[line.product_id.id]['quantity_end'] = \
                        line.quantity_end
                else:
                    dulieu[line.product_id.id] = {}
                    dulieu[line.product_id.id]['quantity'] = line.quantity
                    dulieu[line.product_id.id]['quantity_in'] = line.quantity_in
                    dulieu[line.product_id.id]['quantity_out'] = line.quantity_out
                    dulieu[line.product_id.id]['quantity_end'] = line.quantity_end
                    dulieu[line.product_id.id]['mvt'] = line.product_id.default_code or ''
                    dulieu[line.product_id.id]['uom'] = line.product_id.uom_id.name
                    dulieu[line.product_id.id]['product'] = line.product_id.name
        result = []
        for id in dulieu:
            dataline = {
                "Mã VT": dulieu[id]['mvt'],
                "Tên vật tư": dulieu[id]['product'],
                "ĐVT": dulieu[id]['uom'],
                "Tồn đầu kỳ": dulieu[id]['quantity'],
                "Nhập trong kỳ":  dulieu[id]['quantity_in'],
                "Xuất trong kỳ": dulieu[id]['quantity_out'],
                "Tồn cuối kỳ": dulieu[id]['quantity_end']
            }
            result.append(dataline)
        return result

    def vndate_to_datetimeutc(self, vn_date):
        # convert date to datetime
        if not type(vn_date) is datetime.date:
            vn_date = datetime.strptime(vn_date, '%Y-%m-%d')

        vn_datetime = datetime.combine(vn_date, datetime.min.time())
        # Set the time zone to 'Asia/Ho_Chi_Minh'
        vn_datetime = pytz.timezone('Asia/Ho_Chi_Minh').localize(vn_datetime)
        # Transform the time to UTC
        utc_datetime = vn_datetime.astimezone(pytz.utc)
        return utc_datetime

    @api.model
    def get_value_dashboard_data(self, location_id, start_date, end_date):
        # Goi ham cronjob tong
        print("get gia tri xuat nhap ton")
        self.env['bms.inventory.valuation'].cron_inventory_valuation()
        utc_start_date = self.vndate_to_datetimeutc(start_date)
        utc_end_date = self.vndate_to_datetimeutc(end_date)
        print("XXXXXXXXXXXXXXXXXXXXXXX")
        print(utc_start_date)
        print(utc_end_date)
        print("XXXXXXXXXXXXXXXXXXXXXXX")
        inventory_valuation_ids = self.env['bms.inventory.valuation'].search(
            [('date', '>=', start_date), ('date', '<=', end_date),
             ('location_id', 'in', [int(location_id)])], order='date asc')
        dulieu = {}
        for inventory_valuation_id in inventory_valuation_ids:
            for line in inventory_valuation_id.line_ids:
                if line.product_id.id in dulieu:
                    dulieu[line.product_id.id]['quantity_out'] += line.quantity_out
                    dulieu[line.product_id.id]['quantity_in'] += line.quantity_in
                    dulieu[line.product_id.id]['quantity_end'] = line.quantity_end
                    dulieu[line.product_id.id]['price_out'] += line.price_out
                    dulieu[line.product_id.id]['price_in'] += line.price_in
                    dulieu[line.product_id.id]['price_end'] = line.price_end
                else:
                    dulieu[line.product_id.id] = {}
                    dulieu[line.product_id.id]['quantity'] = line.quantity
                    dulieu[line.product_id.id]['quantity_in'] = line.quantity_in
                    dulieu[line.product_id.id]['quantity_out'] = line.quantity_out
                    dulieu[line.product_id.id]['quantity_end'] = line.quantity_end
                    dulieu[line.product_id.id]['price'] = line.price
                    dulieu[line.product_id.id]['price_in'] = line.price_in
                    dulieu[line.product_id.id]['price_out'] = line.price_out
                    dulieu[line.product_id.id]['price_end'] = line.price_end
                    dulieu[line.product_id.id]['mvt'] = line.product_id.default_code or ''
                    dulieu[line.product_id.id]['uom'] = line.product_id.uom_id.name
                    dulieu[line.product_id.id]['product'] = line.product_id.name
                    print(dulieu)

        result = []
        for id in dulieu:
            dataline = {
                "Mã VT": dulieu[id]['mvt'],
                "Tên vật tư": dulieu[id]['product'],
                "ĐVT": dulieu[id]['uom'],
                "SL Tồn Đầu": dulieu[id]['quantity'],
                "GT Tồn Đầu": dulieu[id]['price'],
                "SL Nhập":  dulieu[id]['quantity_in'],
                "GT Nhập":  dulieu[id]['price_in'],
                "SL Xuất": dulieu[id]['quantity_out'],
                "GT Xuất": dulieu[id]['price_out'],
                "SL Tồn Cuối": dulieu[id]['quantity_end'],
                "GT Tồn Cuối": dulieu[id]['price_end']
            }
            result.append(dataline)
        return result

    def find_sub(self, location_id):
        a = self.env['stock.location'].search([('id', '=', location_id)])
        sub_locations_ids = a.child_ids
        data_location_ids = sub_locations_ids.ids
        data = [location_id]
        if len(data_location_ids) > 0:
            for data_location_id in data_location_ids:
                data += self.find_sub(data_location_id)
            return data
        else:
            return data

    @api.model
    def get_multi_location_data(self, location_ids, start_date, end_date):

        result = []
        x = {}
        total_product_id = []
        for location_id in location_ids:
            result.append(self.env['stock.location'].browse(
                int(location_id)).name)
            x[int(location_id)] = self.get_raw_value_by_loction(
                int(location_id), start_date, end_date)
            total_product_id += list(x[int(location_id)])

        total_product_id = list(set(total_product_id))

        dulieulines = []

        columndata = []
        columndata.append({"data": "Mã VT"})
        columndata.append({"data": "Vật tư"})
        columndata.append({"data": "ĐVT"})
        columndata.append({"data": "0quantity"})
        columndata.append({"data": "0quantity_in"})
        columndata.append({"data": "0quantity_out"})
        columndata.append({"data": "0quantity_end"})

        for location_id in location_ids:
            quantity_location_id = str(location_id) + "quantity"
            quantity_in_location_id = str(location_id) + "quantity_in"
            quantity_out_location_id = str(location_id) + "quantity_out"
            quantity_end_location_id = str(location_id) + "quantity_end"
            columndata.append({"data": quantity_location_id})
            columndata.append({"data": quantity_in_location_id})
            columndata.append({"data": quantity_out_location_id})
            columndata.append({"data": quantity_end_location_id})

        for product_id in total_product_id:
            dataline = {}
            dataline.update({
                "Mã VT": self.env['product.product'].browse(product_id).default_code or
                self.env['product.product'].browse(product_id).barcode or '',
                "Vật tư": self.env['product.product'].browse(product_id).name,
                "ĐVT": self.env['product.product'].browse(product_id).uom_id.name,
                "0quantity": 0,
                "0quantity_in": 0,
                "0quantity_out": 0,
                "0quantity_end": 0,
            })
            for location_id in location_ids:
                quantity_location_id = str(location_id) + "quantity"
                quantity_in_location_id = str(location_id) + "quantity_in"
                quantity_out_location_id = str(location_id) + "quantity_out"
                quantity_end_location_id = str(location_id) + "quantity_end"

                if product_id in x[int(location_id)]:
                    dataline["0quantity"] += x[int(location_id)
                                               ][product_id]["quantity"]
                    dataline["0quantity_in"] += x[int(location_id)
                                                  ][product_id]["quantity_in"]
                    dataline["0quantity_out"] += x[int(location_id)
                                                   ][product_id]["quantity_out"]
                    dataline["0quantity_end"] += x[int(location_id)
                                                   ][product_id]["quantity_end"]
                    dataline.update({
                        quantity_location_id: format(x[int(location_id)][product_id]["quantity"], ","),
                        quantity_in_location_id: format(x[int(location_id)][product_id]["quantity_in"], ","),
                        quantity_out_location_id: format(x[int(location_id)][product_id]["quantity_out"], ","),
                        quantity_end_location_id: format(x[int(location_id)][product_id]["quantity_end"], ","),
                    })
                else:
                    dataline.update({
                        quantity_location_id: 0,
                        quantity_in_location_id: 0,
                        quantity_out_location_id: 0,
                        quantity_end_location_id: 0,
                    })
            dataline["0quantity"] = format(dataline["0quantity"], ",")
            dataline["0quantity_in"] = format(dataline["0quantity_in"], ",")
            dataline["0quantity_out"] = format(dataline["0quantity_out"], ",")
            dataline["0quantity_end"] = format(dataline["0quantity_end"], ",")
            dulieulines.append(dataline)

        dulieureturn = {
            "location_name_ids": result,
            "dulieulines": dulieulines,
            "columndata": columndata
        }
        return dulieureturn

    @api.model
    def get_locations_and_sub_data(self, location_id, start_date, end_date):
        # Goi ham cronjob tong
        self.env['bms.inventory.valuation'].cron_inventory_valuation()
        all_sub_location = self.find_sub(int(location_id))
        first_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        last_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        running_date = first_date
        dulieu = {}
        while running_date <= last_date:
            inventory_valuation_ids = self.env['bms.inventory.valuation'].search([
                ('date', '=', running_date),
                ('location_id', 'in', all_sub_location)])
            new_product_list = []
            for inventory_valuation_id in inventory_valuation_ids:
                for line in inventory_valuation_id.line_ids:
                    if line.product_id.id in dulieu:
                        dulieu[line.product_id.id]['quantity_out'] += line.quantity_out
                        dulieu[line.product_id.id]['quantity_in'] += line.quantity_in
                        if line.product_id.id in new_product_list:
                            dulieu[line.product_id.id]['quantity'] += line.quantity
                    else:
                        dulieu[line.product_id.id] = {}
                        dulieu[line.product_id.id]['quantity'] = line.quantity
                        dulieu[line.product_id.id]['quantity_in'] = line.quantity_in
                        dulieu[line.product_id.id]['quantity_out'] = line.quantity_out
                        dulieu[line.product_id.id]['quantity_end'] = line.quantity_end
                        dulieu[line.product_id.id]['mvt'] = line.product_id.default_code or ''
                        dulieu[line.product_id.id]['uom'] = line.product_id.uom_id.name
                        dulieu[line.product_id.id]['product'] = line.product_id.name
                        new_product_list.append(line.product_id.id)
            running_date += timedelta(days=1)
        # Tra du lieu theo format
        result = []
        for id in dulieu:
            dataline = {
                "Mã VT": dulieu[id]['mvt'],
                "Tên vật tư": dulieu[id]['product'],
                "ĐVT": dulieu[id]['uom'],
                "Tồn đầu kỳ": dulieu[id]['quantity'],
                "Nhập trong kỳ":  dulieu[id]['quantity_in'],
                "Xuất trong kỳ": dulieu[id]['quantity_out'],
                "Tồn cuối kỳ": dulieu[id]['quantity'] + dulieu[id]['quantity_in'] - dulieu[id]['quantity_out']
            }
            result.append(dataline)
        return result

    # lay du lieu xuat nhap ton tra ve chua xu ly format cho datatable
    @api.model
    def get_raw_value_by_loction(self, location_id, start_date, end_date):
        # Goi ham cronjob tong
        self.env['bms.inventory.valuation'].cron_inventory_valuation()
        all_sub_location = self.find_sub(int(location_id))

        first_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        last_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        running_date = first_date
        dulieu = {}
        while running_date <= last_date:
            inventory_valuation_ids = self.env['bms.inventory.valuation'].search([
                ('date', '=', running_date),
                ('location_id', 'in', all_sub_location)])
            new_product_list = []
            for inventory_valuation_id in inventory_valuation_ids:
                for line in inventory_valuation_id.line_ids:
                    if line.product_id.id in dulieu:
                        dulieu[line.product_id.id]['quantity_out'] += line.quantity_out
                        dulieu[line.product_id.id]['quantity_in'] += line.quantity_in
                        dulieu[line.product_id.id]['price_out'] += line.price_out
                        dulieu[line.product_id.id]['price_in'] += line.price_in
                        if line.product_id.id in new_product_list:
                            dulieu[line.product_id.id]['quantity'] += line.quantity
                            dulieu[line.product_id.id]['price'] += line.price
                    else:
                        dulieu[line.product_id.id] = {}
                        dulieu[line.product_id.id]['quantity'] = line.quantity
                        dulieu[line.product_id.id]['quantity_in'] = line.quantity_in
                        dulieu[line.product_id.id]['quantity_out'] = line.quantity_out
                        dulieu[line.product_id.id]['quantity_end'] = line.quantity_end
                        dulieu[line.product_id.id]['price'] = line.price
                        dulieu[line.product_id.id]['price_in'] = line.price_in
                        dulieu[line.product_id.id]['price_out'] = line.price_out
                        dulieu[line.product_id.id]['price_end'] = line.price_end
                        dulieu[line.product_id.id]['mvt'] = line.product_id.default_code or ''
                        dulieu[line.product_id.id]['uom'] = line.product_id.uom_id.name
                        dulieu[line.product_id.id]['product'] = line.product_id.name
                        new_product_list.append(line.product_id.id)
            running_date += timedelta(days=1)
        return dulieu

    @api.model
    def get_value_include_sub_dashboard_data(self, location_id, start_date, end_date):
        # Goi ham cronjob tong
        self.env['bms.inventory.valuation'].cron_inventory_valuation()
        all_sub_location = self.find_sub(int(location_id))

        first_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        last_date = datetime.strptime(end_date, '%Y-%m-%d').date()

        utc_start_date = self.vndate_to_datetimeutc(first_date)
        utc_end_date = self.vndate_to_datetimeutc(last_date)
        print("XXXXXXXXXXXXXXXXXXXXXXX")
        print(first_date)
        print(last_date)
        print(utc_start_date)
        print(utc_end_date)
        # query = """SELECT * FROM res_partner"""
        # query = """
        # SELECT
        #     COALESCE(SUM(amount),0) AS total
        # FROM
        #     payment
        # WHERE
        #     customer_id = 2000;
        # """
        # self.env.cr.execute(query)
        # mydatasql = self.env.cr.fetchall()
        # print(mydatasql)
        print("XXXXXXXXXXXXXXXXXXXXXXX")

        running_date = first_date
        dulieu = {}
        while running_date <= last_date:
            inventory_valuation_ids = self.env['bms.inventory.valuation'].search([
                ('date', '=', running_date),
                ('location_id', 'in', all_sub_location)])
            new_product_list = []
            for inventory_valuation_id in inventory_valuation_ids:
                for line in inventory_valuation_id.line_ids:
                    if line.product_id.id in dulieu:
                        dulieu[line.product_id.id]['quantity_out'] += line.quantity_out
                        dulieu[line.product_id.id]['quantity_in'] += line.quantity_in
                        dulieu[line.product_id.id]['price_out'] += line.price_out
                        dulieu[line.product_id.id]['price_in'] += line.price_in
                        if line.product_id.id in new_product_list:
                            dulieu[line.product_id.id]['quantity'] += line.quantity
                            dulieu[line.product_id.id]['price'] += line.price
                    else:
                        dulieu[line.product_id.id] = {}
                        dulieu[line.product_id.id]['quantity'] = line.quantity
                        dulieu[line.product_id.id]['quantity_in'] = line.quantity_in
                        dulieu[line.product_id.id]['quantity_out'] = line.quantity_out
                        dulieu[line.product_id.id]['quantity_end'] = line.quantity_end
                        dulieu[line.product_id.id]['price'] = line.price
                        dulieu[line.product_id.id]['price_in'] = line.price_in
                        dulieu[line.product_id.id]['price_out'] = line.price_out
                        dulieu[line.product_id.id]['price_end'] = line.price_end
                        dulieu[line.product_id.id]['mvt'] = line.product_id.default_code or ''
                        dulieu[line.product_id.id]['uom'] = line.product_id.uom_id.name
                        dulieu[line.product_id.id]['product'] = line.product_id.name
                        new_product_list.append(line.product_id.id)
            running_date += timedelta(days=1)

        # Tra du lieu theo format
        result = []
        for id in dulieu:
            # lay du lieu chi tiet xuat nhap ton cac san pham
            xnt_data = self.get_overview_dashboard_data(id, location_id, start_date, end_date)
            dataline = {
                "Mã VT": dulieu[id]['mvt'],
                "Tên vật tư": dulieu[id]['product'],
                "ĐVT": dulieu[id]['uom'],
                'ID': id,
                "SL Tồn Đầu": dulieu[id]['quantity'],
                "GT Tồn Đầu": dulieu[id]['price'],
                "SL Nhập":  xnt_data['tongnhap'],
                "GT Nhập":  xnt_data['gttongnhap'],
                "SL Xuất": xnt_data['tongxuat'],
                "GT Xuất": xnt_data['gttongxuat'],
                "SL Tồn Cuối": dulieu[id]['quantity'] + dulieu[id]['quantity_in'] - dulieu[id]['quantity_out'],
                "GT Tồn Cuối": dulieu[id]['price'] + dulieu[id]['price_in'] + dulieu[id]['price_out'],
                "tongnhapncc": xnt_data['tongnhapncc'],
                "gttongnhapncc": xnt_data['gttongnhapncc'],
                "trahangncc": xnt_data['trahangncc'],
                "gttrahangncc": xnt_data['gttrahangncc'],
                "xuatsanxuat": xnt_data['xuatsanxuat'],
                "gtxuatsanxuat": xnt_data['gtxuatsanxuat'],
                "slsanxuatra": xnt_data['slsanxuatra'],
                "gtslsanxuatra": xnt_data['gtslsanxuatra'],
                "xuathuy": xnt_data['xuathuy'],
                "gtxuathuy": xnt_data['gtxuathuy'],
                "boxuathuy": xnt_data['boxuathuy'],
                "gtboxuathuy": xnt_data['gtboxuathuy'],
                "xuathuysanxuat": xnt_data['xuathuysanxuat'],
                "gtxuathuysanxuat": xnt_data['gtxuathuysanxuat'],
                "xuathuykhac": xnt_data['xuathuykhac'],
                "gtxuathuykhac": xnt_data['gtxuathuykhac'],
                "thuakiemke": xnt_data['thuakiemke'],
                "gtthuakiemke": xnt_data['gtthuakiemke'],
                "thieukiemke": xnt_data['thieukiemke'],
                "gtthieukiemke": xnt_data['gtthieukiemke'],
                "xuatkhachhang": xnt_data['xuatkhachhang'],
                "gtxuatkhachhang": xnt_data['gtxuatkhachhang'],
                "nhapkhac": xnt_data['nhapkhac'],
                "gtnhapkhac": xnt_data['gtnhapkhac'],
                "xuatkhac": xnt_data['xuatkhac'],
                "gtxuatkhac": xnt_data['gtxuatkhac'],
                "slsanxuatnhapkho": xnt_data['slsanxuatnhapkho'],
                "gtslsanxuatnhapkho": xnt_data['gtslsanxuatnhapkho'],
                "nhapnvlsanxuat": xnt_data['nhapnvlsanxuat'],
                "gtnhapnvlsanxuat": xnt_data['gtnhapnvlsanxuat'],
                "xuatnoibo": xnt_data['xuatnoibo'],
                "gtxuatnoibo": xnt_data['gtxuatnoibo'],
            }
            result.append(dataline)
        return result

    def get_stock_move_date(self, location_id, start_date, end_date):
        all_sub_location = self.find_sub(location_id)
        # all_sub_location = [location_id]

        sql = "SELECT * FROM view_stock_move_line_by_location_date( '" + start_date + "', '" + end_date + "', " \
              + str( self.env.user.company_id.id) + ",ARRAY[" + (",".join([str(location_sub_id) for location_sub_id in all_sub_location])) + "])"
        self.env.cr.execute(sql)
        stock_moves = self.env.cr.fetchall()

        dulieu = {}
        for product_id, product_code, product_name, uom_name, uom_id, quantity, quantity_out, quantity_in, quantity_end, price, price_out, price_in, price_end in stock_moves:
            product = self.env['product.product'].browse(product_id)
            uom = self.env['uom.uom'].browse(uom_id)

            quantity_out = uom._compute_quantity(quantity_out, product.uom_id)
            quantity_in = uom._compute_quantity(quantity_in, product.uom_id)
            quantity_end = uom._compute_quantity(quantity_end, product.uom_id)

            if product_id in dulieu:
                dulieu[product_id]['quantity_out'] += quantity_out
                dulieu[product_id]['quantity_in'] += quantity_in
                dulieu[product_id]['quantity_end'] += quantity_end
                dulieu[product_id]['price_out'] += price_out
                dulieu[product_id]['price_in'] += price_in
                dulieu[product_id]['quantity'] += quantity
                dulieu[product_id]['price'] += price
            else:
                dulieu[product_id] = {}
                dulieu[product_id]['quantity'] = quantity
                dulieu[product_id]['quantity_in'] = quantity_in
                dulieu[product_id]['quantity_out'] = quantity_out
                dulieu[product_id]['quantity_end'] = quantity_end
                dulieu[product_id]['price'] = price
                dulieu[product_id]['price_in'] = price_in
                dulieu[product_id]['price_out'] = price_out
                dulieu[product_id]['price_end'] = price_end
                dulieu[product_id]['mvt'] = product_code
                dulieu[product_id]['uom'] = uom_name
                dulieu[product_id]['product'] = product_name
        return dulieu

    # type = 1: bao cao nhap xuat ton ; type = 2 : bao cao hao hut
    @api.model
    def get_value_include_sub_dashboard_data_tung(self, location_id, start_date, end_date, type=1):
        # res = self.env['stock.move.view'].sudo().search([])
        # 
        # for r in res:
        #     test_test = r.test_computes_field
        #     test = True
        # 
        # self._cr.execute("""
        #     SELECT * FROM view_stock_move_by_location_date(
        #         '2021-04-14',
        #         '2021-05-14',
        #         ARRAY[8, 9]
        #     )""")
        # res2 = self._cr.fetchall()
        # print(res2)

        last_date = datetime.strptime(start_date, '%Y-%m-%d').date() + timedelta(days=-1)

        initial_stock_moves = self.get_stock_move_date(int(location_id), '1970-01-01', last_date.strftime('%Y-%m-%d'))
        this_period_stock_moves = self.get_stock_move_date(int(location_id), start_date, end_date)

        # merge 2 dict
        dulieu = {**initial_stock_moves, **this_period_stock_moves}
        # Tra du lieu theo format
        result = []
        for id in dulieu:
            # gia tri ton dau
            initial_quantity = initial_stock_moves[id]['quantity_end'] if id in initial_stock_moves else 0
            initial_price = initial_stock_moves[id]['price_end'] if id in initial_stock_moves else 0

            # lay du lieu chi tiet xuat nhap ton cac san pham
            xnt_data = None
            if id in this_period_stock_moves:
                xnt_data = self.get_overview_dashboard_data_tung(id, location_id, start_date, end_date, type)
            print(dulieu[id]['product'])
            print(dulieu[id]['mvt'])
            dataline = {
                "Mã VT": dulieu[id]['mvt'],
                "Tên vật tư": dulieu[id]['product'],
                "ĐVT": dulieu[id]['uom'],
                'ID': id,
                "SL Tồn Đầu": initial_quantity,
                "GT Tồn Đầu": initial_price,
                "SL Nhập":  xnt_data['tongnhap'] if xnt_data else 0,
                "GT Nhập":  xnt_data['gttongnhap'] if xnt_data else 0,
                "SL Xuất": xnt_data['tongxuat'] if xnt_data else 0,
                "GT Xuất": xnt_data['gttongxuat'] if xnt_data else 0,
                "SL Tồn Cuối": initial_quantity
                               + (this_period_stock_moves[id]['quantity_in'] if id in this_period_stock_moves else 0)
                               - (this_period_stock_moves[id]['quantity_out'] if id in this_period_stock_moves else 0),
                "GT Tồn Cuối": initial_price
                               + (this_period_stock_moves[id]['price_in'] if id in this_period_stock_moves else 0)
                               - (this_period_stock_moves[id]['price_out'] if id in this_period_stock_moves else 0),
                "tongnhapncc": xnt_data['tongnhapncc'] if xnt_data else 0,
                "gttongnhapncc": xnt_data['gttongnhapncc'] if xnt_data else 0,
                "nhapnoibo": xnt_data['nhapnoibo'] if xnt_data else 0,
                "gtnhapnoibo": xnt_data['gtnhapnoibo'] if xnt_data else 0,
                "xuatdinhluong": xnt_data['xuatdinhluong'] if xnt_data else 0,
                "gtxuatdinhluong": xnt_data['gtxuatdinhluong'] if xnt_data else 0,
                "xuattra": xnt_data['xuattra'] if xnt_data else 0,
                "gtxuattra": xnt_data['gtxuattra'] if xnt_data else 0,
                "xuathuy": xnt_data['xuathuy'] if xnt_data else 0,
                "gtxuathuy": xnt_data['gtxuathuy'] if xnt_data else 0,
                "xuatkhac": xnt_data['xuatkhac'] if xnt_data else 0,
                "gtxuatkhac": xnt_data['gtxuatkhac'] if xnt_data else 0,
                "haohut": xnt_data['haohut'] if xnt_data else 0,
                "gthaohut": xnt_data['gthaohut'] if xnt_data else 0,
            }
            result.append(dataline)
        return result

    @api.model
    def get_import_dashboard_data(self, location_id, start_date, end_date):
        # Goi ham cronjob tong
        all_sub_location = self.find_sub(int(location_id))
        first_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        last_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        running_date = first_date
        result = []
        stock_picking_ids = self.env['stock.picking'].search([
            ('state', '=', "done"),
            ('purchase_id', '!=', False),
            ('code_of_transfer', '=', "incoming"),
            ('date', '>=', start_date),
            ('date', '<=', end_date),
            ('company_id', '=', self.env.user.company_id.id)
        ])
        for stock_picking_id in stock_picking_ids:
            # if len(stock_picking_id.)
            for line in stock_picking_id.move_ids_without_package:
                print("***********")
                print(stock_picking_id)
                print(stock_picking_id.purchase_id)
                print(line)
                print(line.account_move_ids)
                for account_move_id in line.account_move_ids:
                    print(account_move_id.name)

                print(line.account_move_line_ids)
                if len(line.account_move_line_ids) == 2:
                    for x in line.account_move_line_ids:
                        print(x.debit)
                        print(x.credit)
                        print(max(x.debit, x.credit))
                        tongdongia = max(x.debit, x.credit)
                        break
                else:
                    tongdongia = 0
                print("***********")
                dataline = {}
                dataline['tenncc'] = stock_picking_id.partner_id.name or ""
                dataline['mancc'] = stock_picking_id.partner_id.vat or ""
                dataline['diengiai'] = line.purpose or ""
                dataline['po'] = stock_picking_id.purchase_id.name
                dataline['ngaychungtu'] = stock_picking_id.date_done
                dataline['sopn'] = stock_picking_id.name
                dataline['mavt'] = line.product_id.default_code or ""
                dataline['tenvt'] = line.product_id.name
                dataline['dvt'] = line.product_uom.name
                dataline['makho'] = stock_picking_id.location_dest_id.display_name
                dataline['quantity'] = line.quantity_done
                if line.quantity_done == 0:
                    dataline['price'] = 0
                    dataline['thanhtien'] = 0
                else:
                    dataline['price'] = tongdongia / line.quantity_done
                    dataline['thanhtien'] = tongdongia
                result.append(dataline)
        return result

    @api.model
    def get_internal_dashboard_data(self, location_id, start_date, end_date):
        all_sub_location = self.find_sub(int(location_id))
        first_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        last_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        running_date = first_date
        result = []
        # while running_date <= last_date:
        stock_picking_ids = self.env['stock.picking'].search([
            ('state', '=', "done"),
            ('date_done', '>=', start_date),
            ('date_done', '<=', end_date),
            ('company_id', '=', self.env.user.company_id.id)])
        print("----------------")
        print(stock_picking_ids)
        for stock_picking_id in stock_picking_ids:
            for line in stock_picking_id.move_ids_without_package:
                dataline = {}
                dataline['sopn'] = stock_picking_id.name
                dataline['diengiai'] = line.purpose or ""
                dataline['dxvt'] = stock_picking_id.origin or ""
                dataline['ngaychungtu'] = stock_picking_id.date or ""
                dataline['mavt'] = line.product_id.default_code or ""
                dataline['tenvt'] = line.product_id.name
                dataline['makhonhap'] = stock_picking_id.location_dest_id.display_name
                dataline['makhoxuat'] = stock_picking_id.location_id.display_name
                dataline['quantity'] = line.quantity_done
                result.append(dataline)
        return result
    #
    # def convert_uom(self, uom_id, purchase_uom_id):
    #     print("convertxxxxxxxxxxxxxxxxxxxxxxxx")
    #
    #     print("convertxxxxxxxxxxxxxxxxxxxxxxxx")
    #     return 10

    @api.model
    def get_overview_dashboard_data(self, product_id, location_id, start_date, end_date):
        result = []
        all_sub_location = self.find_sub(int(location_id))
        tongnhapncc = 0
        gttongnhapncc = 0
        boxuathuy = 0
        gtboxuathuy = 0
        slsanxuatra = 0
        gtslsanxuatra = 0
        nhapkhac = 0
        gtnhapkhac = 0
        thuakiemke = 0
        gtthuakiemke = 0
        trahangncc = 0
        gttrahangncc = 0
        xuatsanxuat = 0
        gtxuatsanxuat = 0
        nhapnvlsanxuat = 0
        gtnhapnvlsanxuat = 0
        xuathuy = 0
        gtxuathuy = 0
        xuathuysanxuat = 0
        gtxuathuysanxuat = 0
        xuathuykhac = 0
        gtxuathuykhac = 0
        thieukiemke = 0
        gtthieukiemke = 0
        xuatkhachhang = 0
        gtxuatkhachhang = 0
        xuatkhac = 0
        gtxuatkhac = 0
        xuatnoibo = 0
        gtxuatnoibo = 0
        slsanxuatnhapkho = 0
        gtslsanxuatnhapkho = 0
        loaiphieu = ""

        stock_move_ids = self.env['stock.move'].search([
            '&', '&', '&', '&', '&',
            ('state', '=', "done"),
            ('date', '>=', start_date),
            ('date', '<=', end_date),
            ('product_id', '=', int(product_id)),
            ('company_id', '=', self.env.user.company_id.id),
            '|',
            ('location_id', 'in', all_sub_location),
            ('location_dest_id', 'in', all_sub_location)
        ])

        # firstly check the type of movement
        for stock_move_id in stock_move_ids:
            data_model = "stock.picking"
            data_model_id = stock_move_id.picking_id.id
            for line in stock_move_id.move_line_ids:
                print("account move lineeeeeeeeeeeeeeeeeeeeeeeeeeee")
                print(stock_move_id.account_move_ids)
                print(stock_move_id.account_move_line_ids)
                # Tinh toan gia cua cac but toan
                tongdongia = 0
                if len(stock_move_id.account_move_line_ids) == 2:
                    for x in stock_move_id.account_move_line_ids:
                        tongdongia = max(x.debit, x.credit)
                        break

                print("account move lineeeeeeeeeeeeeeeeeeeeeeeeeeee")
                loaiphieu = ""
                if (line.location_dest_id.id in all_sub_location) and \
                        (line.location_id.id in all_sub_location):
                    print("Check internal transter")
                    if line.location_id.scrap_location:
                        loaiphieu = "Nhập hàng hủy"
                        boxuathuy += line.qty_done

                        if line.product_uom_id == line.product_id.uom_id:
                            boxuathuy += line.qty_done
                        else:
                            uom = line.product_uom_id
                            boxuathuy = uom._compute_quantity(line.qty_done, line.product_id.uom_id)

                        gtboxuathuy += tongdongia
                    else:
                        # check hang huy noi bo
                        if line.location_dest_id.usage == "inventory":
                            loaiphieu = "Xuất hủy khác (X6)"

                            if line.product_uom_id == line.product_id.uom_id:
                                xuathuykhac += line.qty_done
                            else:
                                uom = line.product_uom_id
                                xuathuykhac = uom._compute_quantity(line.qty_done, line.product_id.uom_id)

                            gtxuathuykhac += tongdongia
                        else:
                            loaiphieu = "Chuyển nội bộ"

                            if line.product_uom_id == line.product_id.uom_id:
                                xuatnoibo += line.qty_done
                            else:
                                uom = line.product_uom_id
                                xuatnoibo = uom._compute_quantity(line.qty_done, line.product_id.uom_id)

                            gtxuatnoibo += tongdongia

                    dataline = {}
                    if line.product_uom_id == line.product_id.uom_id:
                        dataline['quantity'] = line.qty_done
                    else:
                        uom = line.product_uom_id
                        dataline['quantity'] = uom._compute_quantity(line.qty_done, line.product_id.uom_id)

                    dataline['dvt'] = line.product_id.uom_id.name

                    dataline['sopn'] = line.reference
                    dataline['diengiai'] = ""
                    # dataline['dvt'] = line.product_uom_id.name
                    dataline['giatri'] = tongdongia
                    dataline['dxvt'] = ""
                    dataline['ngaychungtu'] = line.date
                    dataline['loaiphieu'] = loaiphieu
                    dataline['mavt'] = line.product_id.default_code or ""
                    dataline['tenvt'] = line.product_id.name
                    dataline['makhonhap'] = line.location_dest_id.display_name
                    dataline['makhoxuat'] = line.location_id.display_name
                    # dataline['quantity'] = line.qty_done
                    dataline['ID'] = line.product_id.id
                    dataline['data_model'] = data_model
                    dataline['data_model_id'] = data_model_id
                    result.append(dataline)
                else:
                    if line.location_dest_id.id in all_sub_location:
                        loaiphieu = "Nhập khác"
                        print("line1------------------------------------")
                        print(line)
                        print(line.move_id.group_id)
                        print(line.move_id.group_id.name)
                        print("+++")
                        # odoo 15, stock move doesnt have inventory_id
                        # print(line.move_id.inventory_id)
                        # odoo 15, stock move doesnt have inventory_id
                        # print(line.move_id.inventory_id.name)
                        print("+++")

                        # check co phai lenh kiem ke khong
                        # odoo 15, stock move doesnt have inventory_id
                        # if len(line.move_id.inventory_id) > 0:
                        #     loaiphieu = "Kiểm kê tăng (N5)"
                        #     data_model = "stock.inventory"
                        #     data_model_id = line.move_id.inventory_id.id
                        #     thuakiemke += line.qty_done
                        #     gtthuakiemke += tongdongia
                        # else:
                        if len(line.move_id.scrap_ids) > 0:
                            print("huy san xuat --------------")
                            print(line.move_id.scrap_ids)
                            loaiphieu = "Hủy trong SX (X5)"
                            for scrap_id in line.move_id.scrap_ids:
                                print(scrap_id)
                                print(scrap_id.name)
                                xuathuysanxuat += scrap_id.scrap_qty
                                gtxuathuysanxuat += tongdongia
                                data_model = "stock.scrap"
                                data_model_id = scrap_id.id
                            print("huy san xuat --------------")
                            # xuathuysanxuat += stock_scrap_id.scrap_qty

                        # check co phai la lenh production hay khong dua theo procurement group
                        if len(line.move_id.group_id) > 0:
                            manufacture_order_id = self.env['mrp.production'].search(
                                [('procurement_group_id', '=', line.move_id.group_id.id)])

                            sale_order_ids = self.env['sale.order'].search(
                                [('procurement_group_id', '=', line.move_id.group_id.id)])

                            purchase_order_ids = self.env['purchase.order'].search(
                                [('group_id', '=', line.move_id.group_id.id)])

                            if len(manufacture_order_id) > 0:
                                print("sx----------------------------")
                                print(manufacture_order_id)
                                if line.product_id == manufacture_order_id.product_id:
                                    loaiphieu = "Sản xuất ra (N2)"
                                    # slsanxuatra += line.qty_done

                                    if line.product_uom_id == line.product_id.uom_id:
                                        slsanxuatra += line.qty_done
                                    else:
                                        uom = line.product_uom_id
                                        slsanxuatra = uom._compute_quantity(line.qty_done, line.product_id.uom_id)

                                    gtslsanxuatra += tongdongia
                                else:
                                    loaiphieu = "Nhập NVL SX"

                                    # nhapnvlsanxuat += line.qty_done

                                    if line.product_uom_id == line.product_id.uom_id:
                                        nhapnvlsanxuat += line.qty_done
                                    else:
                                        uom = line.product_uom_id
                                        nhapnvlsanxuat = uom._compute_quantity(
                                            line.qty_done, line.product_id.uom_id)

                                    gtnhapnvlsanxuat += tongdongia
                                print("sx----------------------------")

                            if len(purchase_order_ids) > 0:
                                loaiphieu = "Nhập NCC (N1)"
                                # tongnhapncc += line.qty_done

                                if line.product_uom_id == line.product_id.uom_id:
                                    tongnhapncc += line.qty_done
                                else:
                                    uom = line.product_uom_id
                                    tongnhapncc = uom._compute_quantity(
                                        line.qty_done, line.product_id.uom_id)

                                gttongnhapncc += tongdongia

                            if len(sale_order_ids) > 0:
                                loaiphieu = "Xuất khách hàng"
                                # xuatkhachhang += line.qty_done
                                if line.product_uom_id == line.product_id.uom_id:
                                    xuatkhachhang += line.qty_done
                                else:
                                    uom = line.product_uom_id
                                    xuatkhachhang = uom._compute_quantity(
                                        line.qty_done, line.product_id.uom_id)

                                gtxuatkhachhang += tongdongia

                        if loaiphieu == "Nhập khác":
                            # nhapkhac += line.qty_done
                            if line.product_uom_id == line.product_id.uom_id:
                                nhapkhac += line.qty_done
                            else:
                                uom = line.product_uom_id
                                nhapkhac = uom._compute_quantity(
                                    line.qty_done, line.product_id.uom_id)
                            gtnhapkhac += tongdongia

                        print(line.location_id.display_name)
                        print(line.location_dest_id.display_name)
                        print("line1------------------------------------")
                        dataline = {}
                        if line.product_uom_id == line.product_id.uom_id:
                            dataline['quantity'] = line.qty_done
                        else:
                            uom = line.product_uom_id
                            dataline['quantity'] = uom._compute_quantity(line.qty_done, line.product_id.uom_id)

                        dataline['dvt'] = line.product_id.uom_id.name

                        dataline['sopn'] = line.reference
                        dataline['diengiai'] = ""
                        # dataline['dvt'] = line.product_uom_id.name
                        dataline['giatri'] = tongdongia
                        dataline['dxvt'] = ""
                        dataline['ngaychungtu'] = line.date
                        dataline['loaiphieu'] = loaiphieu
                        dataline['mavt'] = line.product_id.default_code or ""
                        dataline['tenvt'] = line.product_id.name
                        dataline['makhonhap'] = line.location_dest_id.display_name
                        dataline['makhoxuat'] = line.location_id.display_name
                        # dataline['quantity'] = line.qty_done
                        dataline['ID'] = line.product_id.id
                        dataline['data_model'] = data_model
                        dataline['data_model_id'] = data_model_id
                        result.append(dataline)

                    if line.location_id.id in all_sub_location:
                        print("line2------------------------------------")
                        print(line)
                        print(line.move_id.group_id)
                        print(line.move_id.group_id.name)
                        loaiphieu = "Phiếu xuất kho (X4)"

                        # odoo 15, stock move doesnt have inventory_id
                        # if len(line.move_id.inventory_id) > 0:
                        #     loaiphieu = "Kiểm kê thiếu (X7)"
                        #     data_model = "stock.inventory"
                        #     data_model_id = line.move_id.inventory_id.id
                        #     thieukiemke += line.qty_done
                        #     gtthieukiemke += tongdongia
                        # else:
                        if len(line.move_id.scrap_ids) > 0:
                            print("huy san xuat --------------")
                            print(line.move_id.scrap_ids)
                            loaiphieu = "Hủy trong SX (X5)"
                            for scrap_id in line.move_id.scrap_ids:
                                print(scrap_id)
                                print(scrap_id.name)
                                xuathuysanxuat += scrap_id.scrap_qty
                                gtxuathuysanxuat += tongdongia
                            print("huy san xuat --------------")

                        # check co phai la lenh production hay khong dua theo procurement group
                        if len(line.move_id.group_id) > 0:
                            manufacture_order_id = self.env['mrp.production'].search(
                                [('procurement_group_id', '=', line.move_id.group_id.id)])

                            sale_order_ids = self.env['sale.order'].search(
                                [('procurement_group_id', '=', line.move_id.group_id.id)])

                            purchase_order_ids = self.env['purchase.order'].search(
                                [('group_id', '=', line.move_id.group_id.id)])

                            if len(purchase_order_ids) > 0:
                                loaiphieu = "Trả hàng NCC (X1)"
                                trahangncc += line.qty_done
                                gttrahangncc += tongdongia

                            if len(manufacture_order_id) > 0:
                                print("sxmu----------------------------")
                                print(manufacture_order_id)
                                if line.product_id == manufacture_order_id.product_id:
                                    loaiphieu = "Sản xuất ra nhập kho"
                                    # slsanxuatnhapkho += line.qty_done
                                    if line.product_uom_id == line.product_id.uom_id:
                                        slsanxuatnhapkho += line.qty_done
                                    else:
                                        uom = line.product_uom_id
                                        slsanxuatnhapkho = uom._compute_quantity(
                                            line.qty_done, line.product_id.uom_id)
                                    gtslsanxuatnhapkho += tongdongia
                                else:
                                    loaiphieu = "Xuất NVL SX (X2)"
                                    # xuatsanxuat += line.qty_done
                                    if line.product_uom_id == line.product_id.uom_id:
                                        xuatsanxuat += line.qty_done
                                    else:
                                        uom = line.product_uom_id
                                        xuatsanxuat = uom._compute_quantity(
                                            line.qty_done, line.product_id.uom_id)
                                    gtxuatsanxuat += tongdongia
                                print(line.qty_done)
                                print("sxmu----------------------------")

                            if len(sale_order_ids) > 0:
                                loaiphieu = "Xuất khách hàng"
                                # xuatkhachhang += line.qty_done
                                if line.product_uom_id == line.product_id.uom_id:
                                    xuatkhachhang += line.qty_done
                                else:
                                    uom = line.product_uom_id
                                    xuatkhachhang = uom._compute_quantity(
                                        line.qty_done, line.product_id.uom_id)
                                gtxuatkhachhang += tongdongia
                                print("xuat khach hang ................")
                                print(stock_move_id.picking_id)
                                print("xuat khach hang ................")

                        print("+++")
                        # odoo 15, stock move doesnt have inventory_id
                        # print(line.move_id.inventory_id)
                        # print(line.move_id.inventory_id.name)
                        print("+++")
                        print(line.location_id.display_name)
                        print(line.location_dest_id.display_name)
                        print("line2------------------------------------")

                        if loaiphieu == "Phiếu xuất kho (X4)":
                            # xuatkhac += line.qty_done
                            if line.product_uom_id == line.product_id.uom_id:
                                xuatkhac += line.qty_done
                            else:
                                uom = line.product_uom_id
                                xuatkhac = uom._compute_quantity(
                                    line.qty_done, line.product_id.uom_id)
                            gtxuatkhac += tongdongia

                        dataline = {}

                        if line.product_uom_id == line.product_id.uom_id:
                            dataline['quantity'] = line.qty_done
                        else:
                            uom = line.product_uom_id
                            dataline['quantity'] = uom._compute_quantity(line.qty_done, line.product_id.uom_id)

                        dataline['dvt'] = line.product_id.uom_id.name
                        dataline['sopn'] = line.reference
                        dataline['diengiai'] = ""
                        dataline['loaiphieu'] = loaiphieu
                        dataline['giatri'] = tongdongia
                        dataline['dxvt'] = ""
                        dataline['ngaychungtu'] = line.date
                        dataline['mavt'] = line.product_id.default_code or ""
                        dataline['tenvt'] = line.product_id.name
                        dataline['makhonhap'] = line.location_dest_id.display_name
                        dataline['makhoxuat'] = line.location_id.display_name

                        dataline['ID'] = line.product_id.id
                        dataline['data_model'] = data_model
                        dataline['data_model_id'] = data_model_id

                        result.append(dataline)

        tongnhap = tongnhapncc + boxuathuy + slsanxuatra + nhapkhac + thuakiemke + nhapnvlsanxuat
        gttongnhap = gttongnhapncc + gtboxuathuy + gtslsanxuatra + gtnhapkhac + gtthuakiemke + gtnhapnvlsanxuat
        tongxuat = trahangncc + xuatsanxuat + xuathuy + xuathuysanxuat + \
            xuathuykhac + thieukiemke + xuatkhachhang + xuatkhac + slsanxuatnhapkho
        gttongxuat = gttrahangncc + gtxuatsanxuat + gtxuathuy + gtxuathuysanxuat + \
            gtxuathuykhac + gtthieukiemke + gtxuatkhachhang + gtxuatkhac + gtslsanxuatnhapkho
        sodu = abs(tongnhap-tongxuat)
        gtsodu = abs(gttongnhap-gttongxuat)

        return_data = {
            'tongnhapncc': tongnhapncc,
            'gttongnhapncc': gttongnhapncc,
            'trahangncc': trahangncc,
            'gttrahangncc': gttrahangncc,
            'xuatsanxuat': xuatsanxuat,
            'gtxuatsanxuat': gtxuatsanxuat,
            'slsanxuatra': slsanxuatra,
            'gtslsanxuatra': gtslsanxuatra,
            'xuatnoibo': xuatnoibo,
            'gtxuatnoibo': gtxuatnoibo,
            'xuathuy': xuathuy,
            'gtxuathuy': gtxuathuy,
            'boxuathuy': boxuathuy,
            'gtboxuathuy': gtboxuathuy,
            'xuathuysanxuat': xuathuysanxuat,
            'gtxuathuysanxuat': gtxuathuysanxuat,
            'xuathuykhac': xuathuykhac,
            'gtxuathuykhac': gtxuathuykhac,
            'thuakiemke': thuakiemke,
            'gtthuakiemke': gtthuakiemke,
            'thieukiemke': thieukiemke,
            'gtthieukiemke': gtthieukiemke,
            'xuatkhachhang': xuatkhachhang,
            'gtxuatkhachhang': gtxuatkhachhang,
            'nhapkhac': nhapkhac,
            'gtnhapkhac': gtnhapkhac,
            'xuatkhac': xuatkhac,
            'gtxuatkhac': gtxuatkhac,
            'slsanxuatnhapkho': slsanxuatnhapkho,
            'gtslsanxuatnhapkho': gtslsanxuatnhapkho,
            'nhapnvlsanxuat': nhapnvlsanxuat,
            'gtnhapnvlsanxuat': gtnhapnvlsanxuat,
            'tongnhap': tongnhap,
            'gttongnhap': gttongnhap,
            'tongxuat': tongxuat,
            'gttongxuat': gttongxuat,
            'sodu': sodu,
            'gtsodu': gtsodu,
            'result': result
        }

        print("TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT")

        return return_data

    @api.model
    def get_overview_dashboard_data_tung(self, product_id, location_id, start_date, end_date, type=1):
        results = []
        all_sub_location = self.find_sub(int(location_id))

        domain = [
            '&', '&', '&', '&', '&',
            ('state', '=', 'done'),
            ('vn_date', '>=', datetime.strptime(start_date, '%Y-%m-%d').date()),
            ('vn_date', '<=', datetime.strptime(end_date, '%Y-%m-%d').date()),
            ('product_id', '=', int(product_id)),
            ('company_id', '=', self.env.user.company_id.id),
            '|',
            ('location_id', 'in', all_sub_location),
            ('location_dest_id', 'in', all_sub_location)
        ]

        stock_move_line_ids = self.env['stock.move.line.view'].sudo().search(domain)

        # firstly check the type of movement
        return_data = []
        tongnhapncc = 0
        gttongnhapncc = 0
        xuatdinhluong = 0
        gtxuatdinhluong = 0
        xuathuy = 0
        gtxuathuy = 0
        nhapnoibo = 0
        gtnhapnoibo = 0
        xuattra = 0
        gtxuattra = 0
        xuatkhac = 0
        gtxuatkhac = 0
        haohut = 0
        gthaohut = 0
        for line in stock_move_line_ids:
            data_model = "stock.picking"
            data_model_id = line.picking_id.id
            loaiphieu = ''
            # Tinh toan gia cua cac but toan
            tongdongia = line.total_amount
            soluong = 0
            if line.product_uom_id == line.product_id.uom_id:
                soluong = line.product_qty
            else:
                uom = line.product_uom_id
                soluong = uom._compute_quantity(line.product_qty, line.product_id.uom_id)

            if line.location_dest_id.id in all_sub_location:
                # manufacture_order_id = self.env['mrp.production'].search(
                #     [('procurement_group_id', '=', line.stock_move_id.group_id.id)])
                # purchase_order_ids = self.env['purchase.order'].search(
                #     [('group_id', '=', line.stock_move_id.group_id.id)])

                # kiem tra co phai la nhap tu ncc khong?
                if line.picking_type == 'incoming':
                    if line.has_purchase_order:
                        loaiphieu = "Nhập NCC (N1)"
                        tongnhapncc += soluong
                        gttongnhapncc += tongdongia

                #   kiem tra nhập noi bo
                if (line.picking_type == 'internal' and line.location_dest_type == 'internal' \
                        # and (len(line.stock_move_id.inventory_id) > 0
                        #      or line.location_type == 'production'
                        #      or line.has_manufacture_order > 0)
                )\
                        or (line.location_dest_type == 'internal' and line.location_type == 'production'):
                    loaiphieu = "Nhập nội bô (N2)"
                    nhapnoibo += soluong
                    gtnhapnoibo += tongdongia

                # kiem tra xuat dinh luong
                if line.picking_type == 'mrp_production' and line.location_dest_type == 'production':
                    if line.has_manufacture_order > 0:
                        # if line.product_id == manufacture_order_id.product_id:
                        loaiphieu = "Xuất định lượng (X1)"
                        xuatdinhluong += soluong
                        gtxuatdinhluong += tongdongia

                #   kiem tra xuat huy
                if line.picking_type == 'internal'\
                        and line.location_dest_type == 'inventory'\
                        and line.location_type == 'internal':
                    loaiphieu = "Xuất hủy (X3)"
                    xuathuy += soluong
                    gtxuathuy += tongdongia

            if line.location_id.id in all_sub_location:
                # purchase_order_ids = self.env['purchase.order'].search(
                #     [('group_id', '=', line.stock_move_id.group_id.id)])
                # sale_order_ids = self.env['sale.order'].search(
                #     [('procurement_group_id', '=', line.stock_move_id.group_id.id)])
                # manufacture_order_id = self.env['mrp.production'].search(
                #     [('procurement_group_id', '=', line.stock_move_id.group_id.id)])

                # kiem tra xuat tra
                if line.picking_type == 'outgoing' and line.has_purchase_order:
                    loaiphieu = "Xuất trả (X2)"
                    xuattra += soluong
                    gtxuattra += tongdongia

                # kiem tra xuat khac
                if (line.picking_type == 'internal' and line.location_type == 'internal'
                        and (
                                # # odoo 15, stock move doesnt have inventory_id
                                # len(line.stock_move_id.inventory_id) > 0 or
                             len(line.stock_move_id.scrap_ids) > 0
                             or line.has_sale_order
                             or line.location_dest_type == 'internal'
                        )
                    or (line.picking_type == 'outgoing' and line.location_dest_type == 'customer')
                ):
                    loaiphieu = "Xuất khác (X4)"
                    xuatkhac += soluong
                    gtxuatkhac += tongdongia
            # tinh toan them truong hop nhap noi bo co chung location cha
            if line.location_id.id in all_sub_location and line.location_dest_id.id in all_sub_location:
                nhapnoibo += soluong
                gtnhapnoibo += tongdongia

            dataline = {}
            dataline['dvt'] = line.uom_name
            dataline['sopn'] = line.reference
            dataline['diengiai'] = ""
            dataline['loaiphieu'] = loaiphieu
            dataline['giatri'] = tongdongia
            dataline['quantity'] = soluong
            dataline['ngaychungtu'] = line.vn_date
            dataline['mavt'] = line.product_code
            dataline['tenvt'] = line.product_name
            dataline['makhonhap'] = line.location_dest_name
            dataline['makhoxuat'] = line.location_name
            dataline['ID'] = line.product_id
            dataline['data_model'] = data_model
            dataline['data_model_id'] = data_model_id
            results.append(dataline)

            if type == 2:
                mrp_production_ids = self.env['mrp.production'].search([('procurement_group_id', '=', line.stock_move_id.group_id.id)])
                # tinh ti le hao hut tren 1 don vi thanh pham
                ti_le_hao_hut = 0
                for mrp_production_id in mrp_production_ids:
                    for mrp_bom_line in mrp_production_id.bom_id.bom_line_ids:
                        if mrp_bom_line.product_id.id == line.product_id.id:
                            ti_le_hao_hut = mrp_bom_line.haohut
                            break

                haohut += soluong * ti_le_hao_hut/100
                gthaohut += tongdongia * ti_le_hao_hut/100

        tongnhap = tongnhapncc + nhapnoibo
        gttongnhap = gttongnhapncc + gtnhapnoibo
        tongxuat = xuatdinhluong + xuattra + xuatkhac + xuathuy
        gttongxuat = gtxuatdinhluong + gtxuattra + gtxuatkhac + gtxuathuy
        sodu = abs(tongnhap - tongxuat)
        gtsodu = abs(gttongnhap - gttongxuat)

        return_data = {
            'tongnhapncc': tongnhapncc,
            'gttongnhapncc': gttongnhapncc,
            'nhapnoibo': nhapnoibo,
            'gtnhapnoibo': gtnhapnoibo,
            'xuatdinhluong': xuatdinhluong,
            'gtxuatdinhluong': gtxuatdinhluong,
            'xuattra': xuattra,
            'gtxuattra': gtxuattra,
            'xuathuy': xuathuy,
            'gtxuathuy': gtxuathuy,
            'xuatkhac': xuatkhac,
            'gtxuatkhac': gtxuatkhac,
            'tongnhap': tongnhap,
            'gttongnhap': gttongnhap,
            'tongxuat': tongxuat,
            'gttongxuat': gttongxuat,
            'sodu': sodu,
            'gtsodu': gtsodu,
            'result': results,
            'haohut': haohut,
            'gthaohut': gthaohut,
        }

        return return_data
