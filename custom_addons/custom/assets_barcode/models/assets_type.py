from odoo import api, fields, models, _
from random import choice
from string import digits


class AccountAssetType(models.Model):
    _name = 'account.asset.category.type'

    name = fields.Char(string="Type", copy=False, translate=True)
    assets_category_id = fields.Many2one('account.asset.category', string="Assets Category", copy=False,required=True)
