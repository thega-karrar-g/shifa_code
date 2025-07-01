from odoo import api, fields, models,tools

'''
This class used for package service settings for accounting parameters
    - product type
    - product category
    - journal
    - accounting fields(credit -debit -income)
'''
class PackageConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # Initial:Product type and accounts related to Package Product
    product_type = fields.Selection([
        ('consu', 'Consumable'),
        ('service', 'Service'),
        ('product', 'Storable Product')], string='Product Type', default='consu', required=True)

    product_categ_id = fields.Many2one(
        'product.category', 'Product Category',
        change_default=True,
        required=True, help="Select category for the current product")

    property_account_income_id = fields.Many2one('account.account', company_dependent=True,
        string="Deferred Income Account",
        domain="[('deprecated', '=', False), ('internal_type','=','other'), ('company_id', '=', current_company_id), ('is_off_balance', '=', False)]",
        help="Use this value to set product as Package service.")

    # Initial:Journal and accounts related to appointments
    journal_id = fields.Many2one('account.journal', string='Journal', required=True)
    debit_account_id = fields.Many2one(
        comodel_name='account.account', ondelete='restrict', string='Debit Account')

    credit_account_id = fields.Many2one(
        comodel_name='account.account', ondelete='restrict', string='Credit Account (HHC)')
    credit_account_phy_id = fields.Many2one(
        comodel_name='account.account', ondelete='restrict', string='Credit Account (Physiotherapy)')
    
    refund_account_hhc_id = fields.Many2one(
        comodel_name='account.account', ondelete='restrict', string='Refund Account (HHC)')

    refund_account_phy_id = fields.Many2one(
        comodel_name='account.account', ondelete='restrict', string='Refund Account (Physiotherapy)')        

    #  discount accounts
    credit_discount_id = fields.Many2one(
        "account.account",
        "Credit Discount Account",
        domain=[("internal_type", "not in", ["receivable", "payable"])],
    )

    debit_discount_id = fields.Many2one(
        "account.account",
        "Debit Discount Account",
        domain=[("internal_type", "not in", ["receivable", "payable"])],
    )

    # this function used to get package parameters fields values
    @api.model
    def get_values(self):
        res = super(PackageConfigSettings, self).get_values()
        ic = self.env['ir.config_parameter'].sudo()
        product_type = ic.get_param('smartmind_odoo.product_type')
        product_categ_id = ic.get_param('smartmind_odoo.product_categ_id')
        property_account_income_id = ic.get_param('smartmind_odoo.property_account_income_id')
        journal_id = ic.get_param('smartmind_odoo.journal_id')
        debit_account_id = ic.get_param('smartmind_odoo.debit_account_id')
        credit_account_id = ic.get_param('smartmind_odoo.credit_account_id')
        debit_discount_id = ic.get_param('smartmind_odoo.debit_discount_id')
        credit_discount_id = ic.get_param('smartmind_odoo.credit_discount_id')
        credit_account_phy_id = ic.get_param('smartmind_odoo.credit_account_phy_id')
        refund_account_hhc_id = ic.get_param('smartmind_odoo.refund_account_hhc_id')
        refund_account_phy_id = ic.get_param('smartmind_odoo.refund_account_phy_id')
        res.update(
            product_type=product_type,
            product_categ_id=int(product_categ_id),
            property_account_income_id=int(property_account_income_id),
            journal_id=int(journal_id),
            debit_account_id=int(debit_account_id),
            credit_account_id=int(credit_account_id),
            debit_discount_id=int(debit_discount_id),
            credit_discount_id=int(credit_discount_id),
            credit_account_phy_id=int(credit_account_phy_id),
            refund_account_hhc_id=int(refund_account_hhc_id),
            refund_account_phy_id=int(refund_account_phy_id)
        )
        return res

    # accountant requires the account value to be same as income account
    def debit_account_value(self):
        ic = self.env['ir.config_parameter'].sudo()
        current_account = int(ic.get_param('smartmind_odoo.property_account_income_id'))
        debit = 0
        if current_account == self.property_account_income_id.id:
            debit = self.debit_account_id.id
        else:
            debit = self.property_account_income_id.id
        return debit

    # this function used to set values for package parameters fields
    @api.model
    def set_values(self):
        res = super(PackageConfigSettings, self).set_values()
        debit = self.debit_account_value()
        self.env['ir.config_parameter'].set_param('smartmind_odoo.product_type', self.product_type)
        self.env['ir.config_parameter'].set_param('smartmind_odoo.product_categ_id', self.product_categ_id.id)
        self.env['ir.config_parameter'].set_param('smartmind_odoo.property_account_income_id', self.property_account_income_id.id)
        self.env['ir.config_parameter'].set_param('smartmind_odoo.journal_id', self.journal_id.id)
        self.env['ir.config_parameter'].set_param('smartmind_odoo.debit_account_id', debit)
        self.env['ir.config_parameter'].set_param('smartmind_odoo.credit_account_id', self.credit_account_id.id)
        self.env['ir.config_parameter'].set_param('smartmind_odoo.credit_discount_id', self.discount_id.id)
        self.env['ir.config_parameter'].set_param('smartmind_odoo.credit_account_phy_id', self.credit_account_phy_id.id)
        self.env['ir.config_parameter'].set_param('smartmind_odoo.debit_discount_id', self.debit_discount_id.id)
        self.env['ir.config_parameter'].set_param('smartmind_odoo.refund_account_hhc_id', self.refund_account_hhc_id.id)
        self.env['ir.config_parameter'].set_param('smartmind_odoo.refund_account_phy_id', self.refund_account_phy_id.id)
        return res
