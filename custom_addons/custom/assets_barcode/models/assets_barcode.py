from odoo import api, fields, models, _
from random import choice
from string import digits


class AccountAssetAsset(models.Model):
    _inherit = 'account.asset.asset'

    barcode = fields.Char(string="Barcode", help="ID Asset identification.", copy=False)
    category_type_id = fields.Many2one('account.asset.category.type', string='Category type',
                                        domain="[('assets_category_id', '=', category_id)]")


    def generate_barcode(self):
        for asset in self:
            asset.barcode = '041'+"".join(choice(digits) for i in range(9))
