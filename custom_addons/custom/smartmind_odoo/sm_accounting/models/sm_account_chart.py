from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError


class ShifaAccountChart(models.Model):
    _inherit = "account.account"

    internal_group = fields.Selection(related='user_type_id.internal_group', string="First Level", store=True,
                                      readonly=True)
    user_type_id = fields.Many2one('account.account.type', string='Second Level', required=True,
                                   help="Account Type is used for information purpose, to generate country-specific legal reports, and set the rules to close a fiscal year and generate opening entries.")
    group_id = fields.Many2one('account.group', compute='_compute_account_group', store=True, readonly=True,
                               string="Third Level")
    active = fields.Boolean(default=True)

