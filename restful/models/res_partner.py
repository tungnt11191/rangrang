# Part of odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = "res.partner"
    _rec_name = "sv_calculated_name"

    customerName = fields.Char('SV Customer Name', index=True, copy=False)
    sv_calculated_name = fields.Char("Tên xuất hóa đơn",
                                     compute='_calculate_name')

    @api.depends('name', 'customerName')
    def _calculate_name(self):
        for record in self:
            name = record.name
            if record.company_type == 'employer':
                if record.customerName is not False:
                    name = record.customerName
            record.sv_calculated_name = name

    @api.depends('name', 'customerName')
    def name_get(self):
        res = []
        for record in self:
            name = record.name
            if record.company_type == 'employer':
                if record.customerName is not False:
                    name = record.customerName
            if not name or name == '':
                name = str(record.id) + ' Unknown Name'
            res.append((record.id, name))
        return res
