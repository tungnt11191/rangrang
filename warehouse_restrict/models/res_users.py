from odoo import api, fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    allowed_warehouse = fields.Many2many('stock.warehouse', string='Allowed Warehouse',
                                   help='Allowed Warehouse for this user')
    show_users = fields.Boolean(string="Show users of warehouse", default=True, help='Show users in dashboard ( for pos administrators only)')

    @api.model
    def create(self, vals):
        self.clear_caches()
        return super(ResUsers, self).create(vals)

    def write(self, vals):
        # for clearing out existing values and update with new values
        self.clear_caches()
        return super(ResUsers, self).write(vals)


class PosConfig(models.Model):
    _inherit = 'stock.warehouse'

    users_allowed = fields.Many2many('res.users', compute='get_allowed_users')

    def get_allowed_users(self):
        # computes the allowed users in warehouse
        for this in self:
            # checks is show_users is ticked in user settings
            if this.env.user.show_users:
                this.users_allowed = self.env['res.users'].search([('allowed_warehouse', '=', this.id)])
            else:
                this.users_allowed = None
