from odoo import api, fields, models, _
import datetime
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'
    analytic_account_id = fields.Many2one('account.analytic.account',string='Analytic Account',default=lambda self: self.env.user.analytic_account_id.id)

    @api.constrains('analytic_account_id')
    def check_analytic_account_id(self):
        for rec in self:
            if not self.env.user.has_group('account.group_account_manager') and rec.analytic_account_id != self.env.user.analytic_account_id:
                raise UserError("Only users related to the group " + self.env.ref('account.group_account_manager').name + " can do this action!")

    @api.onchange('analytic_account_id')
    def onchange_analytic_account_id(self):
        types = {
            'out_invoice': 'sale',
            'in_invoice': 'purchase',
        }
        for rec in self.filtered(lambda l: l.move_type in ['out_invoice','in_invoice']):
            if rec.analytic_account_id:
                rec.invoice_line_ids._compute_analytical_account()
                journal = self.env['account.journal'].sudo().search([
                    ('type','=',types[rec.move_type]),
                    ('analytic_account_id','=',rec.analytic_account_id.id),
                    ('company_id','=',rec.company_id.id),
                ],limit=1)
                if journal:
                    rec.journal_id = journal.id
                rec._onchange_journal()

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    analytic_account_id = fields.Many2one('account.analytic.account',compute="_compute_analytical_account",store=True,readonly=False)

    @api.depends('move_id.analytic_account_id')
    def _compute_analytical_account(self):
        for rec in self:
            rec.analytic_account_id = False
            if rec.move_id.analytic_account_id and not rec.exclude_from_invoice_tab:
                rec.analytic_account_id = rec.move_id.analytic_account_id.id
