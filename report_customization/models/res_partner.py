from odoo import api, fields, models

class ResPartner(models.Model):
    _inherit = "res.partner"

    x_annex = fields.Char('Annex')
    x_contact_name = fields.Char('Contact Name')
    x_contact_email = fields.Char('Contact email')
    x_contract = fields.Char('Contract')
    x_fax = fields.Char('Fax')
    x_termofpayment = fields.Char('Term of Payment')
    x_vendor_code = fields.Char('Vendor code')