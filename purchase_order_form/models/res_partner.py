from odoo import models, fields, api, _



class ResPartner(models.Model):
    _inherit = 'res.partner'


    x_contract = fields.Char(string=_('Contract'))
    x_annex = fields.Char(string=_('Annex'))