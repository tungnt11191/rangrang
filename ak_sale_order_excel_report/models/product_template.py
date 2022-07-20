from odoo import fields, models, api, _



class Production(models.Model):
    _inherit = 'product.template'

    pcs_per_pallet = fields.Float(string=_('Pcs/Pallet'), store=True)