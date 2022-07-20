# -*- coding: utf-8 -*-

from odoo import models, api, fields

class BmsInventoryCronCheck(models.Model):
    _name = 'bms.inventory.cron.check'

    name = fields.Many2one("res.company", string="Công Ty")
    date = fields.Date("Ngày")
    is_cron = fields.Boolean("Đã chạy cronjob")
