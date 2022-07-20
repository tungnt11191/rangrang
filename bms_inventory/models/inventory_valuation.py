# -*- coding: utf-8 -*-

from datetime import date, timedelta, datetime
import pytz

from odoo import models, fields


class BmsInventoryValuation(models.Model):
    _name = 'bms.inventory.valuation'

    location_id = fields.Many2one(comodel_name="stock.location", string="Địa điểm", required=False)
    line_ids = fields.One2many(comodel_name="bms.inventory.valuation.line",
                               inverse_name="inventory_valuation_id", string="", required=False)
    date = fields.Date("Ngày")

    def create_inventory_valuation(self, previous_date, inventory_valuation):
        data = {}
        # Tim cac stock move trong ngay
        stock_move = self.env['stock.move'].search(
            [('date', '>=', previous_date),
             ('date', '<', previous_date + timedelta(days=1))])

        product_ids = self.env['product.product'].search([])

        location_ids = self.env['stock.location'].search([])
        for location in location_ids:
            print("---------------Tinh te---------------")
            print(location.name)
            data[location.id] = {}
            for product in product_ids:
                data[location.id][product.id] = {
                    "product_id": product.id,
                    "date": previous_date,
                    "quantity": 0,
                    "quantity_in": 0,
                    "quantity_out": 0,
                    "price": 0,
                    "price_in": 0,
                    "price_out": 0,
                    "price_end": 0
                }
            # print(data)
            print("---------------Tinh te---------------")

        for line in stock_move:
            if line.state == "done":
                location_dest = line.location_dest_id.id
                location = line.location_id.id
                product = line.product_id.id
                amount = 0

                # cho nay xu ly gia tri cua hang ton kho
                # tam thoi an di
                for account_move in line.account_move_ids:
                    # v14 amount_total
                    amount += account_move.amount_total

                # số lượng, giá trị nhập
                data[location_dest][product]['quantity_in'] = data[location_dest][product]['quantity_in'] +\
                    line.product_uom_qty
                data[location_dest][product]['price_in'] += amount
                data[location_dest][product]['price_end'] += amount

                # số lượng, giá trị xuất
                data[location][product]['quantity_out'] = data[location][product]['quantity_out'] + \
                    line.product_uom_qty
                data[location][product]['price_out'] -= amount
                data[location][product]['price_end'] -= amount

        for valuation in inventory_valuation:
            for line in valuation.line_ids:
                data[valuation.location_id.id][line.product_id.id]['quantity'] = line.quantity_end
                data[valuation.location_id.id][line.product_id.id]['price'] = 0

        for location in data:
            data_line = list()
            for product in data[location]:
                if data[location][product]['quantity_in'] + data[location][product]['quantity_out'] +\
                        data[location][product]['quantity']:
                    data_line.append([0, 0, data[location][product]])
            if data_line:
                self.env['bms.inventory.valuation'].create({
                    'location_id': location,
                    'date': previous_date,
                    'line_ids': data_line,
                })

    def x_create_inventory_valuation(self, process_date):
        # chuyen doi ngay gio tu gio viet nam sang gio utc de tien hanh tim kiem
        start_utc_datetime = self.vndate_to_datetimeutc(process_date)
        end_utc_datetime = start_utc_datetime + timedelta(days=1)

        # doan nay lay gia tri cua so ton cuoi ngay truoc
        cron_check = self.env['bms.inventory.cron.check'].search([
            ('date', '=', process_date - timedelta(days=1))])

        if len(cron_check) == 0:
            data = {}
            # Quet ca stock move line trong ngay
            stock_move_ids = self.env['stock.move'].search([
                ('date', '>=', start_utc_datetime),
                ('date', '<', end_utc_datetime)])

            # set gia tri dau ngay truoc khi tinh phat sinh trong ngay
            for stock_move_id in stock_move_ids:
                for stock_move_line_id in stock_move_id.move_line_ids:

                    data[stock_move_line_id.location_id.id] = {}
                    data[stock_move_line_id.location_dest_id.id] = {}

            for stock_move_id in stock_move_ids:
                for stock_move_line_id in stock_move_id.move_line_ids:
                    data[stock_move_line_id.location_id.id][stock_move_line_id.product_id.id] = {
                        "product_id": stock_move_line_id.product_id.id,
                        "date": process_date,
                        "quantity": 0,
                        "quantity_in": 0,
                        "quantity_out": 0,
                        "quantity_end": 0,
                        "price": 0,
                        "price_in": 0,
                        "price_out": 0,
                        "price_end": 0
                    }
                    data[stock_move_line_id.location_dest_id.id][stock_move_line_id.product_id.id] = {
                        "product_id": stock_move_line_id.product_id.id,
                        "date": process_date,
                        "quantity": 0,
                        "quantity_in": 0,
                        "quantity_out": 0,
                        "quantity_end": 0,
                        "price": 0,
                        "price_in": 0,
                        "price_out": 0,
                        "price_end": 0
                    }

            for stock_move_id in stock_move_ids:

                # cho nay xu ly gia tri cua hang ton kho
                # tam thoi an di
                amount = 0
                for account_move in stock_move_id.account_move_ids:
                    # v14 amount_total
                    amount += account_move.amount_total

                for stock_move_line_id in stock_move_id.move_line_ids:
                    if stock_move_line_id.state == "done":
                        location_dest = stock_move_line_id.location_dest_id.id
                        location = stock_move_line_id.location_id.id
                        product = stock_move_line_id.product_id.id

                        data[location_dest][product]['quantity_in'] += stock_move_line_id.qty_done
                        data[location_dest][product]['price_in'] += amount
                        data[location_dest][product]['price_end'] += amount

                        # số lượng, giá trị xuất
                        data[location][product]['quantity_out'] += stock_move_line_id.qty_done
                        data[location_dest][product]['quantity_end'] += stock_move_line_id.qty_done
                        data[location][product]['quantity_end'] -= stock_move_line_id.qty_done
                        data[location][product]['price_out'] -= amount
                        data[location][product]['price_end'] -= amount

            for location in data:
                data_line = list()
                for product in data[location]:
                    data_line.append([0, 0, data[location][product]])
                self.env['bms.inventory.valuation'].create({
                    'location_id': location,
                    'date': process_date,
                    'line_ids': data_line,
                })
        else:
            # neu la ngay thu 2 bat dau chay cronjob
            data = {}
            # set gia tri dau ky
            inventory_valuation_ids = self.env['bms.inventory.valuation'].search(
                [('date', '=', process_date - timedelta(days=1))])
            for inventory_valuation_id in inventory_valuation_ids:
                location = inventory_valuation_id.location_id.id
                data[location] = {}
                for line in inventory_valuation_id.line_ids:
                    if line.quantity_end != 0:
                        data[location][line.product_id.id] = {}
                        data[location][line.product_id.id]['quantity'] = line.quantity_end
                        data[location][line.product_id.id]['quantity_in'] = 0
                        data[location][line.product_id.id]['quantity_out'] = 0
                        data[location][line.product_id.id]['quantity_end'] = 0
                        data[location][line.product_id.id]['product_id'] = line.product_id.id
                        data[location][line.product_id.id]['date'] = process_date
                        data[location][line.product_id.id]['price'] = line.price_end
                        data[location][line.product_id.id]['price_in'] = 0
                        data[location][line.product_id.id]['price_out'] = 0
                        data[location][line.product_id.id]['price_end'] = 0

            # check cac so luong xuat nhap trong ngay
            stock_move_ids = self.env['stock.move'].search([('date', '>=', start_utc_datetime),
                                                            ('date', '<', end_utc_datetime)])
            if len(stock_move_ids) > 0:
                for stock_move_id in stock_move_ids:
                    for stock_move_line_id in stock_move_id.move_line_ids:
                        if stock_move_line_id.location_id.id not in data:
                            data[stock_move_line_id.location_id.id] = {}
                        if stock_move_line_id.location_dest_id.id not in data:
                            data[stock_move_line_id.location_dest_id.id] = {}

                for stock_move_id in stock_move_ids:
                    for stock_move_line_id in stock_move_id.move_line_ids:
                        if stock_move_line_id.product_id.id not in data[stock_move_line_id.location_id.id]:
                            data[stock_move_line_id.location_id.id][stock_move_line_id.product_id.id] = {
                                "product_id": stock_move_line_id.product_id.id,
                                "date": process_date,
                                "quantity_in": 0,
                                "price_in": 0,
                                "quantity_end": 0,
                                "quantity_out": 0,
                                "price_out": 0,
                                "quantity": 0,
                                "price": 0,
                                "price_end": 0
                            }

                        if stock_move_line_id.product_id.id not in data[stock_move_line_id.location_dest_id.id]:
                            data[stock_move_line_id.location_dest_id.id][stock_move_line_id.product_id.id] = {
                                "product_id": stock_move_line_id.product_id.id,
                                "date": process_date,
                                "quantity": 0,
                                "quantity_in": 0,
                                "quantity_out": 0,
                                "quantity_end": 0,
                                "price": 0,
                                "price_in": 0,
                                "price_out": 0,
                                "price_end": 0
                            }

                for stock_move_id in stock_move_ids:
                    # cho nay xu ly gia tri cua hang ton kho
                    # tam thoi an di
                    amount = 0
                    for account_move in stock_move_id.account_move_ids:
                        # v14 amount_total
                        amount += account_move.amount_total

                    for stock_move_line_id in stock_move_id.move_line_ids:
                        if stock_move_line_id.state == "done":
                            location_dest = stock_move_line_id.location_dest_id.id
                            location = stock_move_line_id.location_id.id
                            product = stock_move_line_id.product_id.id
                            data[location_dest][product]['quantity_in'] += stock_move_line_id.qty_done
                            data[location_dest][product]['price_in'] += amount
                            data[location_dest][product]['price_end'] += amount
                            # số lượng, giá trị xuất
                            data[location][product]['quantity_out'] += stock_move_line_id.qty_done
                            data[location_dest][product]['quantity_end'] += stock_move_line_id.qty_done
                            data[location][product]['quantity_end'] -= stock_move_line_id.qty_done
                            data[location][product]['price_out'] -= amount
                            data[location][product]['price_end'] -= amount

            for location in data:
                data_line = list()
                for product in data[location]:
                    data_line.append([0, 0, data[location][product]])
                if len(data_line) > 0:
                    #     # Tao inventory valuation cua cong ty hien tai
                    self.env['bms.inventory.valuation'].create({
                        'location_id': location,
                        'date': process_date,
                        'line_ids': data_line,
                    })
        # Luu cronjob check cho cong ty nay
        bms_inventory_cron_check_id = self.env['bms.inventory.cron.check'].search(
            [('date', '=', process_date), ('name', '=', self.env.user.company_id.id)])
        if len(bms_inventory_cron_check_id) == 0:
            self.env['bms.inventory.cron.check'].create({
                'name': self.env.user.company_id.id,
                'date': process_date,
                'is_cron': True,
            })

    def vndate_to_datetimeutc(self, vn_date):
        # convert date to datetime
        vn_datetime = datetime.combine(vn_date, datetime.min.time())
        # Set the time zone to 'Asia/Ho_Chi_Minh'
        vn_datetime = pytz.timezone('Asia/Ho_Chi_Minh').localize(vn_datetime)
        # Transform the time to UTC
        utc_datetime = vn_datetime.astimezone(pytz.utc)
        return utc_datetime

    def vndatetimezone_to_utc(self, vn_datetime):
        # Set the time zone to 'Asia/Ho_Chi_Minh'
        vn_datetime = pytz.timezone('Asia/Ho_Chi_Minh').localize(vn_datetime)
        # Transform the time to UTC
        utc_datetime = vn_datetime.astimezone(pytz.utc)
        return utc_datetime

    # cron chay function nay
    def cron_inventory_valuation(self):
        # Find the first day of stock move
        VN_TZ = pytz.timezone('Asia/Ho_Chi_Minh')
        stock_move_line_id = self.env['stock.move.line'].search([], limit=1, order='create_date asc')
        # first date of stock move line chuyen ve mui gio viet nam
        first_date_sml = stock_move_line_id.date.astimezone(VN_TZ).date()
        # last date of stock move line chuyen ve mui gio viet nam
        stock_move_line_id = self.env['stock.move.line'].search([], limit=1, order='create_date desc')
        last_date_sml = stock_move_line_id.date.astimezone(VN_TZ).date()

        process_date = first_date_sml
        today_date = date.today()

        while process_date <= last_date_sml:
            # Check ngay chay co phai ngay hien tai khong, neu phai thi
            # xoa danh gia ngay hien tai va chay lai
            if process_date == today_date:
                # Xoa ngay hien tai
                self.env['bms.inventory.valuation'].sudo().search([('date', '=', process_date)]).unlink()
                self.env['bms.inventory.cron.check'].sudo().search([('date', '=', process_date)]).unlink()
                self.x_create_inventory_valuation(process_date)
            else:
                # Check xem ngay process_date da tao cronjob chua
                bms_inventory_cron_check_id = self.env['bms.inventory.cron.check'].search([
                    ('date', '=', process_date),
                    ('name', '=', self.env.user.company_id.id)])
                if len(bms_inventory_cron_check_id) == 0:
                    # Chay cronjob cho ngay nay
                    self.x_create_inventory_valuation(process_date)
            process_date += timedelta(days=1)
