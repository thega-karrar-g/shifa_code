from odoo import api, fields, models, _
import datetime
from odoo.exceptions import UserError


class Journal(models.Model):
    _inherit = 'account.journal'
    analytic_account_id = fields.Many2one('account.analytic.account',string='Analytic Account')

    @api.constrains('analytic_account_id')
    def check_analytic_account_id(self):
        for rec in self:
            if not self.env.user.has_group('account.group_account_manager') and rec.analytic_account_id != self.env.user.analytic_account_id:
                raise UserError("Only users related to the group " + self.env.ref('account.group_account_manager').name + " can do this action!")