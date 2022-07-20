from odoo import fields, models, api, _



class PurchaseOrderFrom(models.Model):
    _inherit = 'purchase.order'

    x_contract_related = fields.Char(string=_('Contract'), readonly=True)
    x_annex_related = fields.Char(string=_('Annex'), readonly=True)
    x_purpose_using = fields.Text(string=_('Purpose using'))
    x_using_time = fields.Char(string=_('Using time'))

    @api.onchange('partner_id')
    def _get_contract_and_annex(self):
        self.x_contract_related = self.partner_id.x_contract
        self.x_annex_related = self.partner_id.x_annex