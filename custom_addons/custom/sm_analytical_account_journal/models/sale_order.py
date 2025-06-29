from odoo import api, fields, models, _
import datetime
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    analytic_account_id = fields.Many2one('account.analytic.account',default=lambda self: self.env.user.analytic_account_id.id)


    @api.constrains('analytic_account_id')
    def check_analytic_account_id(self):
        for rec in self:
            if not self.env.user.has_group('account.group_account_manager') and rec.analytic_account_id != self.env.user.analytic_account_id:
                raise UserError("Only users related to the group " + self.env.ref('account.group_account_manager').name + " can do this action!")
    
    
    def _prepare_invoice(self):
        invoice_vals = super()._prepare_invoice()
        invoice_vals['analytic_account_id'] = self.analytic_account_id.id if self.analytic_account_id.id else False
        journal = self.env['account.journal'].sudo().search([
            ('type','=','sale'),
            ('analytic_account_id','=',self.analytic_account_id.id),
            ('company_id','=',self.company_id.id),
        ],limit=1)
        if journal:
            invoice_vals['journal_id'] = journal.id
        return invoice_vals