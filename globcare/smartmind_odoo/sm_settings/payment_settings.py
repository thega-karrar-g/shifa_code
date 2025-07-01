from odoo import api, fields, models,tools

'''
This class used for Odoo payment journal  settings
'''
class PaymentConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # Initial:Payment journal for all payments types:-
    journal_cash = fields.Many2one('account.journal', string='Cash', required=True,
        check_company=True, domain="[('type', 'in', ['bank','cash'])]",)
    journal_point_sale = fields.Many2one('account.journal', string='Point of Sale', required=True,
        check_company=True, domain="[('type', 'in', ['bank','cash'])]",)
    journal_bank = fields.Many2one('account.journal', string='Bank Transfer', required=True,
        check_company=True, domain="[('type', 'in', ['bank','cash'])]",)
    journal_mobile = fields.Many2one('account.journal', string='Mobile App', required=True,
        check_company=True, domain="[('type', 'in', ['bank','cash'])]",)
    journal_portal = fields.Many2one('account.journal', string='Web portal', required=True,
        check_company=True, domain="[('type', 'in', ['bank','cash'])]",)

    # this function used to get journals fields values
    @api.model
    def get_values(self):
        res = super(PaymentConfigSettings, self).get_values()
        ic = self.env['ir.config_parameter'].sudo()
        journal_cash = ic.get_param('smartmind_odoo.journal_cash')
        journal_point_sale = ic.get_param('smartmind_odoo.journal_point_sale')
        journal_bank = ic.get_param('smartmind_odoo.journal_bank')
        journal_mobile = ic.get_param('smartmind_odoo.journal_mobile')
        journal_portal = ic.get_param('smartmind_odoo.journal_portal')
        res.update(
            journal_cash=int(journal_cash),
            journal_point_sale=int(journal_point_sale),
            journal_bank=int(journal_bank),
            journal_mobile=int(journal_mobile),
            journal_portal=int(journal_portal),
        )
        return res

    # this function used to set values for package parameters fields
    @api.model
    def set_values(self):
        res = super(PaymentConfigSettings, self).set_values()
        debit = self.debit_account_value()
        self.env['ir.config_parameter'].set_param('smartmind_odoo.journal_cash', self.journal_cash.id)
        self.env['ir.config_parameter'].set_param('smartmind_odoo.journal_point_sale', self.journal_point_sale.id)
        self.env['ir.config_parameter'].set_param('smartmind_odoo.journal_bank', self.journal_bank.id)
        self.env['ir.config_parameter'].set_param('smartmind_odoo.journal_mobile', self.journal_mobile.id)
        self.env['ir.config_parameter'].set_param('smartmind_odoo.journal_portal', self.journal_portal.id)
        return res
