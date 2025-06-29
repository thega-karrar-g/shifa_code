from odoo import api, fields, models, _
import datetime
from odoo.exceptions import UserError


class Purchase(models.Model):
    _inherit = 'purchase.order'
    analytic_account_id = fields.Many2one('account.analytic.account',string='Analytic Account',default=lambda self: self.env.user.analytic_account_id.id)

    @api.constrains('analytic_account_id')
    def check_analytic_account_id(self):
        for rec in self:
            if not self.env.user.has_group('account.group_account_manager') and rec.analytic_account_id != self.env.user.analytic_account_id:
                raise UserError("Only users related to the group " + self.env.ref('account.group_account_manager').name + " can do this action!")

    @api.onchange('analytic_account_id')
    def onchange_analytic_account_id(self):
        for rec in self:
            rec.order_line._compute_analytical_account()
            if rec.analytic_account_id:
                warehouse = self.env['stock.warehouse'].sudo().search([
                    ('analytic_account_id','=',rec.analytic_account_id.id),
                    ('company_id','=',rec.company_id.id),
                ],limit=1)
                if self.env.user.has_group('sm_user_warehouse_access.warehouse_limitation'):
                    warehouse = self.env['stock.warehouse'].sudo().search([
                        ('analytic_account_id','=',rec.analytic_account_id.id),
                        ('id','in',self.env.user.warehouse_ids.ids),
                        ('company_id','=',rec.company_id.id),
                    ],limit=1)
                if warehouse:
                    rec.sudo().write({'picking_type_id': warehouse.in_type_id.id})
        

    
    def _prepare_invoice(self):
        invoice_vals = super()._prepare_invoice()
        invoice_vals['analytic_account_id'] = self.analytic_account_id.id
        journal = self.env['account.journal'].sudo().search([
            ('type','=','purchase'),
            ('analytic_account_id','=',self.analytic_account_id.id),
            ('company_id','=',self.company_id.id),
        ],limit=1)
        if journal:
            invoice_vals['journal_id'] = journal.id
        return invoice_vals


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    account_analytic_id = fields.Many2one('account.analytic.account',compute="_compute_analytical_account",store=True,readonly=False)

    @api.depends('order_id.analytic_account_id')
    def _compute_analytical_account(self):
        for rec in self:
            rec.account_analytic_id = False
            if rec.order_id.analytic_account_id:
                rec.account_analytic_id = rec.order_id.analytic_account_id.id
